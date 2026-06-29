"""
This module contains the code to parse a file containing crosslinking data.
"""

import logging
from pathlib import Path
import pandas as pd
import traceback
import requests
import re
from io import StringIO
from itertools import islice
from functools import partial
from typing import Callable, Optional
from enum import Enum

from backend.protzilla.utilities.utilities import format_trace
from backend.protzilla.importing.import_utils import (
    columns_in_crosslinking_df,
    rename_columns_csm_format,
    rename_columns_proteomediscoverer_xlinkx_format,
    rename_columns_universal_format,
)


class ProteinLookupError(Enum):
    NOT_A_VALID_PROTEIN_ID = "NOT_A_VALID_PROTEIN_ID"
    IS_DECOY_PROTEIN = "IS_DECOY_PROTEIN"
    NO_PROTEIN_ID_FOUND = "NO_PROTEIN_ID_FOUND"
    NO_GENE_NAME_FOUND = "NO_GENE_NAME_FOUND"
    TIMEOUT = "TIMEOUT"
    HTTP_ERROR = "HTTP_ERROR"
    REQUEST_ERROR = "REQUEST_ERROR"
    NOT_LOOKED_UP = "NOT_LOOKED_UP"


class ProteinDesignationLookupMode(Enum):
    gene_name_to_id = "gene_name_to_id"
    id_to_gene_name = "id_to_gene_name"


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
    data_for_lookup: set[str],
    validator_function: Callable[[str], bool],
    error_code: str,
) -> tuple[set[str], dict[str, tuple[bool, None, str]]]:
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


def split_data_in_batches(data: "iterable") -> "iterable":
    """
    Split an iterable into consecutive batches of fixed maximum size.

    The function yields lists containing up to 25 elements from the input iterable.
    The final batch may contain fewer elements.

    :param data: Iterable containing input elements to be batched
    :type data: iterable

    :return: Iterator yielding batches of input elements as lists
    :rtype: iterable

    :yields: Lists of at most 25 elements
    :yield type: list
    """
    max_allowed_uniprot_batch_size = 25
    iterable = iter(data)
    while batch := list(islice(iterable, max_allowed_uniprot_batch_size)):
        yield batch


def build_uniprot_search_params(
    data_for_lookup: set[str],
    field_of_existing_data: str,
    extra_query: str | None = None,
    extra_fields: str | None = None,
) -> tuple[str, dict[str, str]]:
    """
    Build the UniProt search URL and query parameters for a batch of identifiers.

    :param data_for_lookup: Set of values to look up (e.g., UniProt IDs or gene names)
    :type data_for_lookup: set[str]
    :param field_of_existing_data: Field name in UniProt to search for (e.g., "accession" or "gene_exact")
    :type field_of_existing_data: str
    :param extra_query: Optional additional query string to filter results
    :type extra_query: str or None
    :param extra_fields: Comma-separated list of additional fields to return (e.g., "id,protein_name")
    :type extra_fields: str or None

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

    fields = "accession,gene_primary"
    if extra_fields:
        fields = fields + "," + extra_fields

    params = {
        "query": base_query,
        "format": "tsv",
        "fields": fields,
    }

    return uniprot_search_url, params


def execute_uniprot_request(
    url: str,
    params: dict[str, str],
    valid_data: set[str],
    results: dict[str, tuple[bool, None, str]],
) -> Optional[requests.Response]:
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
        error = ProteinLookupError.TIMEOUT.value
    except requests.exceptions.HTTPError as e:
        error = f"{ProteinLookupError.HTTP_ERROR.value}_{e.response.status_code}"
    except requests.exceptions.RequestException:
        error = ProteinLookupError.REQUEST_ERROR.value

    for data in valid_data:
        results[data] = (False, None, error)
    return None


def process_uniprot_response(
    response: requests.Response,
    results: dict[str, tuple[bool, str | None, None | str]],
    input_data: set[str],
    mode: ProteinDesignationLookupMode,
) -> None:
    """
    Process a UniProt API response and update the results dictionary.

    The function reads a TSV response from UniProt, extracts the requested data
    (gene name or protein ID depending on mode), and updates the results dictionary
    with valid lookups. In `gene_name_to_id` mode, it also checks alternative gene names.

    :param response: The HTTP response object returned from a UniProt request
    :type response: requests.Response
    :param results: Dictionary to store lookup results; updated in place
                    as ``existing_data -> (True, requested_data, None)``
    :type results: dict[str, tuple[bool, str | None, str | None]]
    :param input_data: Set of input values that were originally queried
    :type input_data: set[str]
    :param mode: Lookup mode, either mapping IDs to gene names or gene names to IDs
    :type mode: ProteinDesignationLookupMode

    :return: None (results dictionary is updated in place)
    :rtype: None
    """
    df = pd.read_csv(StringIO(response.text), sep="\t")

    for _, row in df.iterrows():
        protein_id = row.get("Entry")
        primary_gene_name = row.get("Gene Names (primary)")

        if mode == ProteinDesignationLookupMode.id_to_gene_name.value:
            existing_data = protein_id
            requested_data = primary_gene_name
        elif mode == ProteinDesignationLookupMode.gene_name_to_id.value:
            existing_data = primary_gene_name
            requested_data = protein_id

        if pd.notna(requested_data) and requested_data != "":
            if existing_data in input_data:
                results[existing_data] = (True, requested_data, None)
            elif mode == ProteinDesignationLookupMode.gene_name_to_id.value:
                alternative_gene_names = str(row.get("Gene Names", "")).split()
                for gene_name in alternative_gene_names:
                    if gene_name in input_data:
                        results[gene_name] = (True, requested_data, None)
                        break


def uniprot_lookup(
    input_data: set[str],
    mode: ProteinDesignationLookupMode,
    results: dict[str, tuple[bool, Optional[str], Optional[str]]],
    organism_id: Optional[str] = None,
) -> None:
    """
    Perform a UniProt lookup for a batch of input data, updating the results dictionary.

    Depending on the mode, the function either maps protein IDs to gene names
    or gene names to protein IDs. The function handles batching, requests, and
    response processing. Any input values that do not return results are marked
    as failed in the results dictionary with an appropriate error code.

    :param input_data: Set of input values to look up (protein IDs or gene names)
    :type input_data: set[str]
    :param mode: Lookup mode, either "id_to_gene_name" or "gene_name_to_id"
    :type mode: ProteinDesignationLookupMode
    :param results: Dictionary to store lookup results; updated in place
                    with ``existing_data -> (success, value, error_code)``
    :type results: dict[str, tuple[bool, str | None, str | None]]
    :param organism_id: Required only for 'gene_name_to_id' mode to filter queries
    :type organism_id: str, optional

    :return: None (results dictionary is updated in place)
    :rtype: None
    """
    if mode == ProteinDesignationLookupMode.id_to_gene_name.value:
        field_of_existing_data = "accession"
        extra_query = None
        extra_fields = None
    elif mode == ProteinDesignationLookupMode.gene_name_to_id.value:
        field_of_existing_data = "gene_exact"
        extra_query = f"organism_id:{organism_id} AND reviewed:true"
        extra_fields = "gene_names"

    for batch in split_data_in_batches(data=input_data):

        url, params = build_uniprot_search_params(
            data_for_lookup=batch,
            field_of_existing_data=field_of_existing_data,
            extra_query=extra_query,
            extra_fields=extra_fields,
        )

        response = execute_uniprot_request(
            url=url, params=params, valid_data=batch, results=results
        )
        if response is None:
            continue

        process_uniprot_response(
            response=response, results=results, input_data=batch, mode=mode
        )


def get_gene_name_from_protein_ids(
    protein_ids: set[str],
) -> dict[str, tuple[bool, Optional[str], Optional[str]]]:
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
    # (extended to include isoforms)
    # A batch request containing an id that doesn't match this regex,
    # leads to an http 400 for the whole request.
    valid_id_pattern = re.compile(
        r"^(?:"
        r"[OPQ][0-9][A-Z0-9]{3}[0-9]"
        r"|"
        r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}"
        r")"
        r"(?:-.+)?$"
    )

    valid_ids, results = validate_data_before_lookup(
        data_for_lookup=protein_ids,
        validator_function=lambda pid: bool(valid_id_pattern.match(pid)),
        error_code=ProteinLookupError.NOT_A_VALID_PROTEIN_ID.value,
    )

    if not valid_ids:
        return results

    valid_ids_without_isoform = {x.split("-", 1)[0] for x in valid_ids}

    uniprot_lookup(
        input_data=valid_ids_without_isoform,
        mode=ProteinDesignationLookupMode.id_to_gene_name.value,
        results=results,
        organism_id=None,
    )

    for protein_id in valid_ids_without_isoform:
        if protein_id not in results:
            results[protein_id] = (
                False,
                None,
                ProteinLookupError.NO_GENE_NAME_FOUND.value,
            )

    return results


def get_protein_ids_from_gene_name(
    gene_names: set[str], organism_ids: list[str]
) -> dict[str, tuple[bool, Optional[str], Optional[str]]]:
    """
    Retrieve UniProt protein IDs for a given set of human gene names as a batch query.

    :param gene_names: Set of gene symbols to look up (e.g., {"RAD50", "MRE11"})
    :type gene_names: set[str]
    :param organism_ids: list of organism identifiers for filtering UniProt queries (e.g., "9606" for human)
    :type organism_ids: list[str]

    :return: Dictionary mapping each gene name to a tuple of (success, protein_id, error)
    :rtype: dict[str, tuple[bool, str | None, str | None]]

    :returns success: True if the lookup for this gene name succeeded, False otherwise
    :returns protein_id: The first valid protein ID found for the gene, or None if lookup failed
    :returns error: Error code or message if the lookup failed, else None
    """
    # Filter decoy Proteins, because we cannot process them decently
    valid_gene_names, results = validate_data_before_lookup(
        data_for_lookup=gene_names,
        validator_function=lambda name: not name.startswith("decoy:"),
        error_code=ProteinLookupError.IS_DECOY_PROTEIN.value,
    )

    if not valid_gene_names:
        return results

    remaining_gene_names = set(valid_gene_names)
    for single_organism_id in organism_ids:

        if not remaining_gene_names:
            continue

        uniprot_lookup(
            input_data=remaining_gene_names,
            mode=ProteinDesignationLookupMode.gene_name_to_id.value,
            results=results,
            organism_id=single_organism_id,
        )

        for gene_name in list(remaining_gene_names):
            if gene_name in results:
                remaining_gene_names.discard(gene_name)

    for gene_name in valid_gene_names:
        if gene_name not in results:
            results[gene_name] = (
                False,
                None,
                ProteinLookupError.NO_GENE_NAME_FOUND.value,
            )

    return results


def iterate_for_protein_designation(
    df: pd.DataFrame,
    existing_designation: str,
    new_designation: str,
    uniprot_lookup_results: dict[str, tuple[bool, Optional[str], Optional[str]]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
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

    :return: Tuple containing rows with successful lookups and rows with lookup errors
    :rtype: tuple[pandas.DataFrame, pandas.DataFrame]

    :returns good_df: Rows with successful lookups
    :returns failed_df: Rows with lookup errors
    """
    good_rows = []
    failed_rows = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        protein_id1 = row[existing_designation + "1"].split("-", 1)[0]
        protein_id2 = row[existing_designation + "2"].split("-", 1)[0]

        success1, data1, error1 = uniprot_lookup_results.get(
            protein_id1, (False, None, ProteinLookupError.NOT_LOOKED_UP.value)
        )
        success2, data2, error2 = uniprot_lookup_results.get(
            protein_id2, (False, None, ProteinLookupError.NOT_LOOKED_UP.value)
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
            row_dict[new_designation + "1"] = data1
            row_dict[new_designation + "2"] = data2
            good_rows.append(row_dict)

    good_df = pd.DataFrame(good_rows)
    failed_df = pd.DataFrame(failed_rows)

    return good_df, failed_df


def get_missing_protein_designation(
    df: pd.DataFrame,
    existing_column: str,
    missing_column: str,
    uniprot_lookup_function: Callable[
        [set[str]], dict[str, tuple[bool, str | None, str | None]]
    ],
) -> tuple[pd.DataFrame, pd.DataFrame]:
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

    :return: Tuple of DataFrames containing rows with successful lookups and rows with errors
    :rtype: tuple[pandas.DataFrame, pandas.DataFrame]

    :returns good_df: Rows where missing protein designations were successfully populated
    :returns failed_df: Rows where the lookup failed
    """
    unique_existing_designations = aggregate_data(df=df, column=existing_column)
    uniprot_lookup_results = uniprot_lookup_function(unique_existing_designations)
    good_df, failed_df = iterate_for_protein_designation(
        df=df,
        existing_designation=existing_column,
        new_designation=missing_column,
        uniprot_lookup_results=uniprot_lookup_results,
    )

    return good_df, failed_df


def remove_brackets_from_peptide(peptide: str) -> str:
    return peptide.replace("[", "").replace("]", "")


def get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format(
    peptide: str,
) -> int:
    return peptide.find("[") + 1  # 1-based index


def read_ProteomeDiscoverer_XlinkX_file(
    file_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
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

    df["CL_position_within_peptide1"] = df["Peptide1"].apply(
        get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format
    )
    df["CL_position_within_peptide2"] = df["Peptide2"].apply(
        get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format
    )

    df["Peptide1"] = df["Peptide1"].apply(remove_brackets_from_peptide).astype("string")
    df["Peptide2"] = df["Peptide2"].apply(remove_brackets_from_peptide).astype("string")

    df["Is_intra_crosslink"] = df["Is_intra_crosslink"].eq("Intra")

    good_df, failed_df = get_missing_protein_designation(
        df=df,
        existing_column="Protein_id",
        missing_column="Protein",
        uniprot_lookup_function=get_gene_name_from_protein_ids,
    )
    if not good_df.empty:
        good_df = normalize_crosslinking_df(good_df)

    return good_df, failed_df


def read_csm_file(
    file_path: Path, organism_ids: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
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
    :param organism_ids: list of organism identifiers used for UniProt lookups (e.g., "9606" for human)
    :type organism_id: list[str]

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

    uniprot_lookup_function_with_organism_ids = partial(
        get_protein_ids_from_gene_name, organism_ids=organism_ids
    )
    good_df, failed_df = get_missing_protein_designation(
        df=df,
        existing_column="Protein",
        missing_column="Protein_id",
        uniprot_lookup_function=uniprot_lookup_function_with_organism_ids,
    )
    if not good_df.empty:
        good_df = normalize_crosslinking_df(good_df)

    return good_df, failed_df


def normalize_crosslinking_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.astype(
        {
            "Protein1": "string",
            "Protein2": "string",
            "Protein_id1": "string",
            "Protein_id2": "string",
            "Is_intra_crosslink": "bool",
            "Crosslinker": "string",
            "Peptide1": "string",
            "Peptide2": "string",
            "CL_position_within_peptide1": "int",
            "CL_position_within_peptide2": "int",
            "Q_value": "Float64",
        }
    )
    return df.loc[:, columns_in_crosslinking_df]


def process_organism_id_from_text_field(
    organism_ids: str,
) -> tuple[bool, Optional[list[str]], Optional[list[str]], Optional[str]]:
    """
    Validates a comma-separated string of NCBI Taxonomy IDs.
    Returns False immediately if any ID is invalid.
    Otherwise returns True, the list of cleaned IDs, and the corresponding scientific names.

    param organism_ids: Comma-separated string of NCBI Taxonomy IDs (e.g., "9606,10090,10116")
    :type organism_ids: str

    :return: A tuple containing:
        - success (bool): True if all IDs are valid, False if any ID is invalid
        - ids (list[str] | None): List of cleaned IDs in input order if successful, None if failed or the cause of the fail
        - names (list[str] | None): List of scientific names corresponding to IDs if successful, None if failed
    """
    organism_ids_list: list[str] = [
        id.strip() for id in organism_ids.split(",") if id.strip()
    ]
    if not organism_ids_list:
        return False, None, None, "EMPTY_INPUT"

    organism_ids_for_request = ",".join(organism_ids_list)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&id={organism_ids_for_request}&retmode=json"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return False, None, None, "NCBI_TAXONOMY_REQUEST_FAILED"
        data = response.json()
    except requests.Timeout:
        return False, None, None, "NCBI_TAXONOMY_TIMEOUT"
    except Exception:
        return False, None, None, "NCBI_TAXONOMY_SERVICE_UNAVAILABLE"

    result = data.get("result", {})
    if not result or "uids" not in result:
        return False, None, None, "NCBI_TAXONOMY_RESPONSE_INVALID"
    valid_organism_ids = result.get("uids", [])
    organism_names = []

    for id in organism_ids_list:
        if id not in valid_organism_ids:
            # Abort at the first invalid id
            return False, id, None, "ORGANISM_ID_NOT_FOUND"
        name = result[id].get("scientificname")
        if not name:
            return False, id, None, "MISSING_SCIENTIFIC_NAME"
        organism_names.append(name)

    return True, organism_ids_list, organism_names, None


def aggregate_failed_proteins_for_display(failed_df: pd.DataFrame) -> str:
    """
    Aggregate failed protein lookups into a human-readable string.

    For each row in `failed_df`, this function pairs protein values with their
    corresponding error codes and returns a sorted, newline-separated string.

    The function checks for the presence of either "Protein1"/"Protein2" columns
    or "Protein_id1"/"Protein_id2" columns to determine which values to process.

    :param failed_df: DataFrame containing rows with failed protein lookups
                      Must include columns for proteins and their error codes
    :type failed_df: pandas.DataFrame

    :return: String summarizing all failed protein lookups in the format
             "Protein_value -> ERROR_CODE", sorted alphabetically and separated by newlines
    :rtype: str
    """
    protein_with_error_set = set()

    if "Protein1" in failed_df.columns and "Protein2" in failed_df.columns:
        protein_columns = ["Protein1", "Protein2"]
    elif "Protein_id1" in failed_df.columns and "Protein_id2" in failed_df.columns:
        protein_columns = ["Protein_id1", "Protein_id2"]

    error_columns = ["Protein1_error", "Protein2_error"]

    for protein_col, error_col in zip(protein_columns, error_columns):
        for protein_val, error_val in zip(failed_df[protein_col], failed_df[error_col]):
            if pd.notna(error_val):
                protein_with_error_set.add(f"{protein_val} -> {error_val}")

    return "\n".join(sorted(protein_with_error_set))


def error_output(msg, trace: str | None = None) -> dict:
    return dict(
        crosslinking_df=pd.DataFrame(),
        imported_rows_with_errors_df=pd.DataFrame(),
        messages=[
            dict(
                level=logging.ERROR,
                msg=msg,
                trace=trace,
            )
        ],
    )


def crosslinking_import(file_path: Path, organism_ids: str) -> dict:
    file_type = file_path.suffix.lower()
    try:
        scientific_organism_names: list[str] = None
        if file_type == ".csv":
            success, organism_ids_list, scientific_organism_names, error = (
                process_organism_id_from_text_field(organism_ids)
            )
            if not success:
                if organism_ids_list:
                    msg = f"Unsupported organism id: {organism_ids_list}. \nOrganism id validation failed with error: {error}. \nPlease provide all valid taxonomy ids."
                else:
                    msg = f"An error occurred while reading the organism ids: {error}. \nPlease provide all valid taxonomy ids, separated by a comma."
                return error_output(msg)
            good_df, failed_df = read_csm_file(file_path, organism_ids_list)
        elif file_type == ".xlsx":
            good_df, failed_df = read_ProteomeDiscoverer_XlinkX_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid crosslinking file."
        return error_output(msg, trace=format_trace(traceback.format_exception(e)))

    def base_message():
        if file_type == ".csv":
            organism_names_string = ", ".join(scientific_organism_names)
            return (
                f"{len(good_df)} crosslinks for the {organism_names_string} organism(s)"
            )
        return f"{len(good_df)} crosslinks"

    if good_df.empty:
        msg = f"No crosslinks could be processed from this file. File was read successfully, but the data of {base_message()} could be imported."
        messages = [dict(level=logging.ERROR, msg=msg)]
    elif failed_df.empty:
        msg = f"Successfully imported data of {base_message()}."
        messages = [dict(level=logging.INFO, msg=msg)]
    else:
        msg = f"Warning: {len(failed_df)} rows failed to import, however {base_message()} were successfully imported."
        messages = [
            dict(level=logging.WARNING, msg=msg),
            dict(
                level=logging.WARNING,
                msg=f"Failed proteins:\n{aggregate_failed_proteins_for_display(failed_df)}",
            ),
        ]

    return dict(
        crosslinking_df=good_df,
        imported_rows_with_errors_df=failed_df,
        messages=messages,
    )


def universal_crosslinking_import(file_path: Path, organism_ids: str) -> dict:
    try:
        file_type = file_path.suffix.lower()
        if file_type == ".xlsx":
            df = pd.read_excel(file_path).rename(
                columns=rename_columns_universal_format
            )
        elif file_type == ".csv":
            df = pd.read_csv(file_path, low_memory=False).rename(
                columns=rename_columns_universal_format
            )
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        initial_columns = set(df.columns)

        if {"Is_intra_crosslink"} <= initial_columns:
            content = df["Is_intra_crosslink"].astype("string").str.strip().str.lower()
            df["Is_intra_crosslink"] = (
                content.str.contains("intra", na=False) | content.eq("true")
            ).astype("boolean")
        else:
            df["Is_intra_crosslink"] = df["Protein1"].eq(df["Protein2"])

        if (
            not {"CL_position_within_peptide1", "CL_position_within_peptide2"}
            <= initial_columns
        ):
            df["CL_position_within_peptide1"] = df["Peptide1"].apply(
                get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format
            )
            df["CL_position_within_peptide2"] = df["Peptide2"].apply(
                get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format
            )
            df["Peptide1"] = (
                df["Peptide1"].apply(remove_brackets_from_peptide).astype("string")
            )
            df["Peptide2"] = (
                df["Peptide2"].apply(remove_brackets_from_peptide).astype("string")
            )

        has_gene_names = {"Protein1", "Protein2"} <= initial_columns
        has_protein_ids = {"Protein_id1", "Protein_id2"} <= initial_columns

        if not has_gene_names:
            if not has_protein_ids:
                return error_output(
                    "The file must contain either Gene Names or Protein Ids."
                )
            good_df, failed_df = get_missing_protein_designation(
                df=df,
                existing_column="Protein_id",
                missing_column="Protein",
                uniprot_lookup_function=get_gene_name_from_protein_ids,
            )

        if not has_protein_ids:
            success, organism_ids_list, scientific_organism_names, error = (
                process_organism_id_from_text_field(organism_ids)
            )
            if not success:
                if organism_ids_list:
                    msg = f"Unsupported organism id: {organism_ids_list}. \nOrganism id validation failed with error: {error}. \nPlease provide all valid taxonomy ids."
                else:
                    msg = f"An error occurred while reading the organism ids: {error}. \nPlease provide all valid taxonomy ids, separated by a comma."
                return error_output(msg)

            uniprot_lookup_function_with_organism_ids = partial(
                get_protein_ids_from_gene_name, organism_ids=organism_ids_list
            )
            good_df, failed_df = get_missing_protein_designation(
                df=df,
                existing_column="Protein",
                missing_column="Protein_id",
                uniprot_lookup_function=uniprot_lookup_function_with_organism_ids,
            )

        for column in columns_in_crosslinking_df:
            if column not in good_df.columns:
                good_df[column] = pd.NA

        if not good_df.empty:
            good_df = normalize_crosslinking_df(good_df)

    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid crosslinking file."
        return error_output(msg, trace=format_trace(traceback.format_exception(e)))

    def base_message():
        if file_type == ".csv":
            organism_names_string = ", ".join(scientific_organism_names)
            return (
                f"{len(good_df)} crosslinks for the {organism_names_string} organism(s)"
            )
        return f"{len(good_df)} crosslinks"

    if good_df.empty:
        msg = f"No crosslinks could be processed from this file. File was read successfully, but the data of {base_message()} could be imported."
        messages = [dict(level=logging.ERROR, msg=msg)]
    elif failed_df.empty:
        msg = f"Successfully imported data of {base_message()}."
        messages = [dict(level=logging.INFO, msg=msg)]
    else:
        msg = f"Warning: {len(failed_df)} rows failed to import, however {base_message()} were successfully imported."
        messages = [
            dict(level=logging.WARNING, msg=msg),
            dict(
                level=logging.WARNING,
                msg=f"Failed proteins:\n{aggregate_failed_proteins_for_display(failed_df)}",
            ),
        ]

    return dict(
        crosslinking_df=good_df,
        imported_rows_with_errors_df=failed_df,
        messages=messages,
    )
