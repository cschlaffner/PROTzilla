"""
This module contains the code to parse a file containing crosslinking data.
"""

import logging
from pathlib import Path
from collections import defaultdict
import pandas as pd
import traceback
import requests
import re
import zipfile
import io
import json

from backend.protzilla.utilities import format_trace
from backend.protzilla.importing.import_utils import (
    columns_in_crosslinking_df,
    rename_columns_csm_format,
    rename_columns_proteomediscoverer_xlinkx_format,
)


def aggregate_data(df: pd.DataFrame, column: str) -> set:
    """
    Extract unique values from two DataFrame columns and return them as a set.

    :param df: Input DataFrame
    :type df: pd.DataFrame
    :param column: Column name
    :type column: str
    :return: Unique values from the column
    :rtype: set
    """
    return set(
        df[[column + "1", column + "2"]].stack().dropna().astype(str).str.strip()
    )


def validate_data_before_lookup(
    data_for_lookup: set, validator_function, error_code: str
):
    """
    Split input values into valid and invalid ones.
    Invalid values are directly written to the results with the given error code.

    :param data_for_lookup: Set of input values to be validated
    :type data_for_lookup: set[str]
    :param validator_function: Validation function applied to each value.
                               Must accept a single string and return ``True`` if valid,
                               otherwise ``False``.
    :type validator_function: Callable[[str], bool]
    :param error_code: Error code assigned to invalid values
    :type error_code: str

    :return: Tuple containing valid data and validation results
    :rtype: tuple[set[str], dict[str, tuple[bool, None, str]]]

    :returns valid_data: Set of values that passed validation
    :returns results: Mapping of invalid values to ``(False, None, error_code)``
    """
    valid_data = set()
    results = {}

    if not data_for_lookup:
        return valid_data, results

    for data in data_for_lookup:
        if validator_function(data):
            valid_data.add(data)
        else:
            results[data] = (False, None, error_code)

    return valid_data, results


def build_uniprot_search_params(
    data_for_lookup: set,
    field_of_existing_data: str,
    *,
    extra_query: str | None = None,
    response_format: str,
    fields: str,
    include_isoforms: bool = False,
):
    """
    Build the UniProt search URL and query parameters for a batch of identifiers.

    :param data_for_lookup: Set of values to look up (e.g., UniProt IDs or gene names)
    :type data_for_lookup: set[str]
    :param field_of_existing_data: Field name in UniProt to search for (e.g., "accession" or "gene_exact")
    :type field_of_existing_data: str
    :param extra_query: Optional additional query string to filter results
    :type extra_query: str or None
    :param response_format: Desired response format (e.g., "json", "tsv")
    :type response_format: str
    :param fields: Comma-separated list of fields to return (e.g., "accession,id,protein_name")
    :type fields: str
    :param include_isoforms: Whether to include isoform entries in the results
    :type include_isoforms: bool

    :return: Tuple containing the UniProt search URL and the query parameters dictionary
    :rtype: tuple[str, dict[str, str]]

    :returns uniprot_search_url: Base URL for UniProt REST API search
    :returns params: Dictionary of query parameters for the request
    """
    uniprot_search_url = "https://rest.uniprot.org/uniprotkb/search"

    base_query = " OR ".join(
        f"{field_of_existing_data}:{data}" for data in data_for_lookup
    )

    if extra_query:
        base_query = f"({base_query}) AND {extra_query}"

    params = {
        "query": base_query,
        "format": response_format,
        "fields": fields,
    }

    if include_isoforms:
        params["includeIsoform"] = "true"

    return uniprot_search_url, params


def execute_uniprot_request(url, params, valid_data, results):
    """
    Execute a UniProt HTTP request with error handling and update the results for failed queries.

    :param url: UniProt REST API URL to send the request to
    :type url: str
    :param params: Dictionary of query parameters for the request
    :type params: dict[str, str]
    :param valid_data: Set of input values that were intended to be queried
    :type valid_data: set[str]
    :param results: Dictionary to store lookup results; failed lookups are updated here
                    as ``data -> (False, None, error_code)``
    :type results: dict[str, tuple[bool, None, str]]

    :return: The HTTP response object if the request succeeded, otherwise None
    :rtype: requests.Response or None

    :raises requests.exceptions.Timeout: If the request times out
    :raises requests.exceptions.HTTPError: If the server returns an HTTP error
    :raises requests.exceptions.RequestException: For other request-related errors

    :note: On failure, all entries in `valid_data` are updated in `results` with the
           corresponding error code:
             - "TIMEOUT" for a timeout
             - "HTTP_<status_code>" for HTTP errors
             - "REQUEST_ERROR" for other request failures
    """
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response

    except requests.exceptions.Timeout:
        error = "TIMEOUT"
    except requests.exceptions.HTTPError as e:
        error = f"HTTP_{e.response.status_code}"
    except requests.exceptions.RequestException:
        error = "REQUEST_ERROR"

    for data in valid_data:
        results[data] = (False, None, error)
    return None


def process_uniprot_response_containing_gene_names(response, results):
    """
    Process a UniProt API response containing gene name information and update the results dictionary.

    :param response: HTTP response object returned by a UniProt request
    :type response: requests.Response
    :param results: Dictionary to store lookup results. Each protein ID will be updated as:
                    ``protein_id -> (success, gene_name, error_code)``
    :type results: dict[str, tuple[bool, str | None, str | None]]

    :return: None (updates `results` in-place)
    :rtype: None

    :note: For each entry in the response:
           - If a gene name is found, ``results[protein_id] = (True, gene_name, None)``
           - If no gene name is found, ``results[protein_id] = (False, None, "NO_GENE_NAME_FOUND")``
    """
    data = response.json()

    for entry in data.get("results", []):
        protein_id = entry.get("primaryAccession")
        output = entry.get("genes", [{}])
        gene_name = output[0].get("geneName", {}).get("value") if output else None

        if gene_name:
            results[protein_id] = (True, gene_name, None)
        else:
            results[protein_id] = (False, None, "NO_GENE_NAME_FOUND")


def process_uniprot_response_containing_protein_ids(
    response, valid_input, is_fallback: bool
):
    """
    Process a UniProt TSV response containing protein IDs and map them to gene names.

    :param response: HTTP response object returned by a UniProt request in TSV format
    :type response: requests.Response
    :param valid_input: Set of gene names to extract protein IDs for
    :type valid_input: set[str]
    :param is_fallback: True if the response comes from a fallback individual UniProt request
                        instead of the standard UniProt batch request
    :type is_fallback: bool

    :return: Dictionary mapping gene_name -> protein information
    :rtype: dict[str, dict[str, list[str]]]

    :returns output: Dictionary with the following structure:
                     {
                         gene_name: {
                             "protein_ids": List of protein IDs without isoform suffix,
                             "list_of_protein_isoforms": List of protein IDs with isoform suffix
                         }
                     }

    :note: For each line in the TSV response:
           - Protein IDs with a dash ("-") are considered isoforms and added to
             "list_of_protein_isoforms"
           - Other protein IDs are added to "protein_ids"
           - Only gene names present in `valid_input` are considered, unless `is_fallback` is True
    """
    output = defaultdict(lambda: {"protein_ids": [], "list_of_protein_isoforms": []})

    lines = response.text.strip().split("\n")
    header = lines[0].split("\t")
    protein_id_idx = header.index("Entry")
    gene_name_idx = header.index("Gene Names (primary)")

    for line in lines[1:]:
        parts = line.split("\t")
        protein_id = parts[protein_id_idx]
        output_gene_names = parts[gene_name_idx].split()

        for gene_name in output_gene_names:
            if gene_name in valid_input:
                if "-" in protein_id:
                    output[gene_name]["list_of_protein_isoforms"].append(protein_id)
                else:
                    output[gene_name]["protein_ids"].append(protein_id)
            elif is_fallback:
                if "-" in protein_id:
                    output[valid_input]["list_of_protein_isoforms"].append(protein_id)
                else:
                    output[valid_input]["protein_ids"].append(protein_id)
    return output


def fallback_single_lookup(query: str, query_type: str, results):
    """
    Perform a fallback UniProt lookup for a single gene or protein ID and update the results.

    :param query: The gene name or UniProt ID to look up
    :type query: str
    :param query_type: Type of lookup to perform. Either:
                       - "get_gene_name": Retrieve the primary gene name for a UniProt ID
                       - "get_protein_ids": Retrieve UniProt accession IDs for a gene
    :type query_type: str
    :param results: Dictionary to store lookup results. Will be updated in-place.
                    Entries are stored as ``key -> (success, data, error_code)``
    :type results: dict[str, tuple[bool, Any, str | None]]

    :return: HTTP response object from the UniProt request if successful, otherwise None
    :rtype: requests.Response or None

    :note: This function constructs the appropriate UniProt REST API request depending on
           `query_type` and uses `execute_uniprot_request` to perform the request and handle errors.
    """
    if query_type == "get_gene_name":
        url = f"https://rest.uniprot.org/uniprotkb/{query}"
        params = {"fields": "gene_primary", "format": "json"}
    elif query_type == "get_protein_ids":
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": f"gene_exact:{query}",
            "format": "tsv",
            "fields": "accession,gene_primary",
        }
    return execute_uniprot_request(url, params, query, results)


def get_gene_name_from_protein_ids(protein_ids: set):
    """
    Retrieve the gene names for a given set of Protein IDs in a batch from UniProt.

    :param protein_ids: Set of UniProt accession IDs (e.g., {"Q92878", "P51587"})
    :type protein_ids: set[str]

    :return: Mapping of protein_id to a tuple containing lookup result, gene name, and error
    :rtype: dict[str, tuple[bool, str | None, str | None]]

    :returns success: True if the lookup for that protein_id succeeded, False otherwise
    :returns gene_name: Official gene name if successful, else None
    :returns error: Error code or message if the lookup failed, else None
    """
    # Regex for valid accession input directly from UniProt
    # A batch request containing an id that doesn't match this regex,
    # leads to an http 400 for the whole request.
    valid_id_pattern = re.compile(
        r"^(?:"
        r"[OPQ][0-9][A-Z0-9]{3}[0-9]"
        r"|"
        r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}"
        r")$"
    )

    valid_ids, results = validate_data_before_lookup(
        protein_ids,
        validator_function=lambda pid: bool(valid_id_pattern.match(pid)),
        error_code="NOT_A_VALID_PROTEIN_ID",
    )

    if not valid_ids:
        return results

    url, params = build_uniprot_search_params(
        valid_ids,
        field_of_existing_data="accession",
        response_format="json",
        fields="accession,gene_primary",
    )

    response = execute_uniprot_request(url, params, valid_ids, results)
    if response is None:
        return results

    process_uniprot_response_containing_gene_names(response, results)

    for pid in valid_ids:
        if pid not in results:

            response = fallback_single_lookup(pid, "get_gene_name", results)
            data = response.json()
            processed_data = data.get("genes", [])
            gene_name = (
                processed_data[0].get("geneName", {}).get("value")
                if processed_data
                else None
            )

            if gene_name:
                results[pid] = (True, gene_name, None)
            else:
                results[pid] = (False, None, "PROTEIN_ID_NOT_FOUND")

    return results


def get_protein_ids_from_gene_name(gene_names: set):
    """
    Retrieve UniProt protein IDs for a given set of human gene names as a batch query.

    :param gene_names: Set of gene symbols to look up (e.g., {"RAD50", "MRE11"})
    :type gene_names: set[str]

    :return: Mapping of gene_name to a tuple containing lookup result, data, and error
    :rtype: dict[str, tuple[bool, dict[str, list[str]] | None, str | None]]

    :returns success: True if the lookup for this gene_name succeeded, False otherwise
    :returns data: Dictionary with protein information if successful, else None.
                Contains:
                    - "protein_ids" (list of str): All protein IDs without any isoform information
                    - "list_of_protein_isoforms" (list of str): All isoform IDs
    :returns error: Error code or message if the lookup failed, else None
    """
    # Filter decoy Proteins, because we cannot process them decently
    valid_gene_names, results = validate_data_before_lookup(
        gene_names,
        validator_function=lambda name: not name.startswith("decoy:"),
        error_code="IS_DECOY_PROTEIN",
    )

    if not valid_gene_names:
        return results

    url, params = build_uniprot_search_params(
        valid_gene_names,
        field_of_existing_data="gene_exact",
        extra_query="organism_id:9606 AND reviewed:true",
        response_format="tsv",
        fields="accession,gene_primary",
        include_isoforms=True,
    )

    response = execute_uniprot_request(url, params, valid_gene_names, results)
    if response is None:
        return results

    output = process_uniprot_response_containing_protein_ids(
        response, valid_gene_names, False
    )

    for gene_name in valid_gene_names:
        data = output.get(gene_name)
        if not data or not data["protein_ids"]:

            response = fallback_single_lookup(gene_name, "get_protein_ids", results)
            if response is not None:
                new_output = process_uniprot_response_containing_protein_ids(
                    response, gene_name, True
                )
                protein_id = new_output.get(gene_name)
            else:
                protein_id = None
            if protein_id:
                results[gene_name] = (True, protein_id, None)
            else:
                results[gene_name] = (False, None, "NO_PROTEIN_ID_FOUND")

        else:
            results[gene_name] = (True, data, None)

    return results


def iterate_for_protein_designation(
    df,
    existing_designation,
    new_designation,
    uniprot_lookup_results,
    value_extractor=lambda x: x,
):
    """
    Iterate over a DataFrame and add missing protein designations using precomputed lookup results.
    Either protein IDs or gene names are included in the DataFrame, and the other is added
    to the DataFrame in this function.

    :param df: Input DataFrame
    :type df: pandas.DataFrame
    :param existing_designation: Column name in `df` containing existing protein designation
                                 (e.g., "Protein_id" or "Protein")
    :type existing_designation: str
    :param new_designation: Column name to store the newly added protein designation
    :type new_designation: str
    :param uniprot_lookup_results: Mapping of key -> (success, data, error)
                                   Contains precomputed lookup results
    :type uniprot_lookup_results: dict
    :param value_extractor: Function that extracts the value to store in the DataFrame cell
                            from `data`. Default is identity function.
                            Signature: ``value_extractor(data) -> Any``
    :type value_extractor: Callable[[Any], Any]

    :return: Tuple containing rows with successful lookups and rows with lookup errors
    :rtype: tuple[pandas.DataFrame, pandas.DataFrame]

    :returns good_df: Rows with successful lookups
    :returns failed_df: Rows with lookup errors
    """
    good_rows = []
    failed_rows = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        success1, data1, error1 = uniprot_lookup_results.get(
            row[existing_designation + "1"], (False, None, "NOT_LOOKED_UP")
        )
        success2, data2, error2 = uniprot_lookup_results.get(
            row[existing_designation + "2"], (False, None, "NOT_LOOKED_UP")
        )

        errors_occurred = {}
        if not success1:
            errors_occurred["Protein1_error"] = error1
        if not success2:
            errors_occurred["Protein2_error"] = error2

        if errors_occurred:
            failed_row = row_dict.copy()
            failed_row.update(errors_occurred)
            failed_rows.append(failed_row)
        else:
            row_dict[new_designation + "1"] = value_extractor(data1)
            row_dict[new_designation + "2"] = value_extractor(data2)
            good_rows.append(row_dict)

    good_df = normalize_crosslinking_df(pd.DataFrame(good_rows))
    failed_df = pd.DataFrame(failed_rows)

    return good_df, failed_df


def get_missing_protein_designation(
    df: pd.DataFrame,
    existing_column: str,
    missing_column: str,
    uniprot_lookup_function,
    value_extractor=lambda x: x,
):
    """
    Fill missing protein designations in a DataFrame using a UniProt lookup function.

    This function aggregates unique values from the existing column, performs a batch
    lookup using `uniprot_lookup_function`, and populates the missing column. The resulting
    rows are split into successful and failed lookups.

    :param df: Input DataFrame containing existing protein designations
    :type df: pandas.DataFrame
    :param existing_column: Name of the column with existing protein designations
    :type existing_column: str
    :param missing_column: Name of the column to populate with missing designations
    :type missing_column: str
    :param uniprot_lookup_function: Function that performs a batch UniProt lookup.
                                    Should accept a set of values and return results
                                    as a dictionary ``key -> (success, data, error_code)``
    :type uniprot_lookup_function: Callable[[set[str]], dict[str, tuple[bool, Any, str | None]]]
    :param value_extractor: Function to extract the value to store in the missing column
                            from the lookup data. Default is the identity function.
    :type value_extractor: Callable[[Any], Any]

    :return: Tuple of DataFrames containing rows with successful lookups and rows with errors
    :rtype: tuple[pandas.DataFrame, pandas.DataFrame]

    :returns good_df: Rows where missing protein designations were successfully populated
    :returns failed_df: Rows where the lookup failed
    """
    unique_existing_designations = aggregate_data(df, existing_column)
    uniprot_lookup_results = uniprot_lookup_function(unique_existing_designations)
    good_df, failed_df = iterate_for_protein_designation(
        df, existing_column, missing_column, uniprot_lookup_results, value_extractor
    )
    return good_df, failed_df


def remove_isoform_from_protein_id(protein_id: str) -> str:
    return protein_id.split("-", 1)[0]


def remove_brackets_from_peptide(peptide: str) -> str:
    return peptide.replace("[", "").replace("]", "")


def get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format(
    peptide: str,
) -> int:
    return peptide.find("[") + 1  # 1-based index


def read_ProteomeDiscoverer_XlinkX_file(file_path: Path) -> pd.DataFrame:
    """
    Read and process a ProteomeDiscoverer XlinkX Excel file:
    1. Reads the Excel file and renames columns to a standard format.
    2. Extracts crosslink positions for both peptides.
    3. Cleans peptide sequences by removing brackets and converting to string type.
    4. Converts intra-crosslink annotations to boolean.
    5. Removes isoform suffixes from protein IDs.
    6. Fills missing protein designations using UniProt gene name lookup.
    7. Splits the resulting DataFrame into successful and failed lookups.

    :param file_path: Path to the ProteomeDiscoverer XlinkX Excel file
    :type file_path: pathlib.Path

    :return: Tuple of DataFrames containing rows with successfully mapped proteins and rows where lookup failed
    :rtype: tuple[pandas.DataFrame, pandas.DataFrame]

    :returns good_df: Rows where missing protein designations were successfully populated
    :returns failed_df: Rows where protein lookup failed
    """
    df = pd.read_excel(file_path).rename(
        columns=rename_columns_proteomediscoverer_xlinkx_format
    )

    df["CL_position1"] = df["Peptide1"].apply(
        get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format
    )
    df["CL_position2"] = df["Peptide2"].apply(
        get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format
    )

    df["Peptide1"] = df["Peptide1"].apply(remove_brackets_from_peptide).astype("string")
    df["Peptide2"] = df["Peptide2"].apply(remove_brackets_from_peptide).astype("string")

    df["Is_intra_crosslink"] = df["Is_intra_crosslink"].eq("Intra")

    # Right now we remove the isoform ending from every protein_id (if necessary),
    # because we cannot process isoforms properly.
    # If we ever wanted to add an "Isoforms" column, we need to store the original value from
    # the "Protein_id1/2" column in the "Isoforms" column first, before removing the isoform ending.
    df["Protein_id1"] = (
        df["Protein_id1"].apply(remove_isoform_from_protein_id).astype("string")
    )
    df["Protein_id2"] = (
        df["Protein_id2"].apply(remove_isoform_from_protein_id).astype("string")
    )

    good_df, failed_df = get_missing_protein_designation(
        df=df,
        existing_column="Protein_id",
        missing_column="Protein",
        uniprot_lookup_function=get_gene_name_from_protein_ids,
        value_extractor=lambda x: x,
    )

    return good_df, failed_df


def read_csm_file(file_path: Path) -> pd.DataFrame:
    """
    Read and process a CSM CSV file:
    1. Reads the CSV file and renames columns to a standard format.
    2. Determines intra-crosslinks by comparing Protein1 and Protein2.
    3. Normalizes gene names in the specified protein columns.
    4. Uses UniProt lookups to fill missing protein IDs, storing only the first protein ID
       for each gene.
    5. Splits the resulting DataFrame into successful and failed lookups.

    :param file_path: Path to the CSM CSV file
    :type file_path: pathlib.Path

    :return: Tuple of DataFrames containing rows with successfully mapped protein IDs
             and rows where lookup failed
    :rtype: tuple[pandas.DataFrame, pandas.DataFrame]

    :returns good_df: Rows where missing protein IDs were successfully populated
    :returns failed_df: Rows where the UniProt lookup failed, including error messages
    """
    df = pd.read_csv(file_path, low_memory=False).rename(
        columns=rename_columns_csm_format
    )

    df["Is_intra_crosslink"] = df["Protein1"].eq(df["Protein2"])

    # In our UniProt lookup we already get all isoforms of the respective gene name.
    # Right now we only store the protein id without any isoform information in our dataframe to keep it consistent.
    # If we ever need the isoform information we just have to change what the value extractor stores in our dataframe.
    good_df, failed_df = get_missing_protein_designation(
        df=df,
        existing_column="Protein",
        missing_column="Protein_id",
        uniprot_lookup_function=get_protein_ids_from_gene_name,
        value_extractor=lambda x: x["protein_ids"][0] if x else None,
    )

    return good_df, failed_df


def normalize_crosslinking_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.astype(
        {
            "Protein1": "string",
            "Protein2": "string",
            "Is_intra_crosslink": "bool",
            "Crosslinker": "string",
            "Peptide1": "string",
            "Peptide2": "string",
            "Q_value": "Float64",
        }
    )
    return df.loc[:, columns_in_crosslinking_df]


def process_organism_id_from_text_field(organism_id: str): 
    cleaned_organism_id = organism_id.strip().replace(" ", "")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&id={cleaned_organism_id}&retmode=json"
    response = requests.get(url)
    if response.status_code != 200:
        return False, None
    data = response.json()
    output_ids = data.get("result", {})
    if cleaned_organism_id not in output_ids:
        return False, None
    name = output_ids[cleaned_organism_id].get("scientificname")
    return True, name


def aggregate_failed_proteins_for_display(failed_df: pd.DataFrame) -> str: 
    protein_with_error_set = set()  

    if "Protein1" in failed_df.columns and "Protein2" in failed_df.columns:
        protein_cols = ["Protein1", "Protein2"]
    elif "Protein_id1" in failed_df.columns and "Protein_id2" in failed_df.columns:
        protein_cols = ["Protein_id1", "Protein_id2"]

    error_cols = ["Protein1_error", "Protein2_error"]

    for prot_col, err_col in zip(protein_cols, error_cols):
        for protein_val, error_val in zip(failed_df[prot_col], failed_df[err_col]):
            if pd.notna(error_val):
                protein_with_error_set.add(f"{protein_val} -> {error_val}")

    return "\n".join(sorted(protein_with_error_set))


def crosslinking_import(file_path: Path, organism_id: str) -> dict:
    success, scientific_organism_name = process_organism_id_from_text_field(organism_id)
    if not success: 
        msg = f"Unsupported organism id: {organism_id}. Please provide a valid taxonomy id."
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=msg,
                )
            ]
        )
    try:
        if file_path.suffix == ".csv":
            good_df, failed_df = read_csm_file(file_path)
        elif file_path.suffix == ".xlsx":
            good_df, failed_df = read_ProteomeDiscoverer_XlinkX_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid cross linking file."
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            ]
        )
    if failed_df.empty:
        msg = f"Successfully imported data of {len(good_df)} cross-links for the {scientific_organism_name} organism."
        messages = [dict(level=logging.INFO, msg=msg)]
    else:
        msg = f"Warning: {len(failed_df)} rows failed to import, however {len(good_df)} cross-links for the {scientific_organism_name} organism were successfully imported."
        messages = [
            dict(level=logging.WARNING, msg=msg),
            dict(level=logging.WARNING, msg=f"Failed proteins:\n{aggregate_failed_proteins_for_display(failed_df)}"),
        ]

    return dict(crosslinking_df=good_df, imported_rows_with_errors_df=failed_df, messages=messages)
