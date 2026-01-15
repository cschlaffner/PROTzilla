"""
This module contains the code to parse a file containing cross linking data.
"""

import logging
from pathlib import Path 
from collections import defaultdict
import pandas as pd
import traceback
import requests
import re

from backend.protzilla.utilities import format_trace
from backend.protzilla.importing.import_utils import (
    columns_in_cross_linking_df,
    rename_columns_csm_format,
    rename_columns_proteomediscoverer_xlinkx_format,
)

"""
def get_protein_designation(designation_lookup_cache, protein_designation, uniprot_lookup_func):
    if designation_lookup_cache[protein_designation]:
        success, new_protein_designation, error = True, designation_lookup_cache[protein_designation], None
    else:
        success, new_protein_designation, error = uniprot_lookup_func(protein_designation)
        if success:
            designation_lookup_cache[protein_designation] = new_protein_designation
    return success, new_protein_designation, error
"""


def aggregate_data(df: pd.DataFrame, column: str) -> set:
    """
    Extracts unique values from two DataFrame columns and returns them as a set.

    Parameters:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name

    Returns:
        set: Unique values from the columns
    """
    return set(
        df[[column + "1", column + "2"]]
        .stack()
        .dropna()
        .astype(str)
        .str.strip()
    )


def get_gene_name_from_protein_ids(protein_ids: set):
    """
    Retrieves the gene names for a given set of Protein IDs in a batch from UniProt.

    Parameters:
        protein_ids (set): Set of UniProt accession IDs (e.g. {"Q92878", "P51587"}).

    Returns:
        dict: Mapping protein_id -> (success, gene_name, error) 
            success (bool): True if the lookup for that protein_id succeeded, False otherwise
            gene_name (str or None): Official gene name if successful, else None
            error (str or None): Error code/message if failed, else None
    """
    #return "placeholder"

    results = {}
    if not protein_ids:
        return results 
    
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

    valid_ids = set()
    for pid in protein_ids:
        if valid_id_pattern.match(pid):
            valid_ids.add(pid)
        else:
            results[pid] = (False, None, "NOT_A_VALID_PROTEIN_ID")

    if not valid_ids:
        return results
    
    url = f"https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": " OR ".join(f"accession:{pid}" for pid in valid_ids),
        "fields": "accession,gene_primary", 
        "format": "json"
    }

    try: 
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status() 
        data = response.json()

        for entry in data.get("results", []):
            protein_id = entry.get("primaryAccession")
            output = entry.get("genes", [{}])
            gene_name = output[0].get("geneName", {}).get("value") if output else None

        #gene_name = data.get("genes", [{}])[0].get("geneName", {}).get("value")

            # If there is more than one protein id for a gene name, 
            # we only store the last one that was found. 
            if gene_name: 
                results[protein_id] = (True, gene_name, None)
                #return True, gene_name, None
            else:
                results[protein_id] = (False, None, "NO_GENE_NAME_FOUND")
                #return False, None, "NO_GENE_NAME_FOUND"

        for pid in valid_ids: 
            if pid not in results: 
                results[pid] = (False, None, "PROTEIN_ID_NOT_FOUND")
        
    except requests.exceptions.Timeout:
        for pid in valid_ids:
            results[pid] = (False, None, "TIMEOUT")
        #return False, None, "TIMEOUT"
    
    except requests.exceptions.HTTPError as e:
        for pid in valid_ids:
            results[pid] = (False, None, f"HTTP_{e.response.status_code}")
        #return False, None, f"HTTP_{e.response.status_code}"
    
    except requests.exceptions.RequestException:
        for pid in valid_ids:
            results[pid] = (False, None, "REQUEST_ERROR")
        #return False, None, "REQUEST_ERROR"
    
    except ValueError:
        for pid in valid_ids:
            results[pid] = (False, None, "INVALID_JSON")
        #return False, None, "INVALID_JSON"

    return results 


def get_protein_ids_from_gene_name(gene_names: set):
    """
    Retrieves UniProt protein IDs for a given set of human gene names as a batch query.

    Parameters: 
        gene_names (set): Set of gene symbols to look up (e.g. {"RAD50", "MRE11"})
    
    Returns:
        dict: Mapping gene_name -> (success, data, error)
            success (bool): True if lookup for this gene_name succeeded, False otherwise
            data (dict or None): {
                "protein_ids" (list of str): all protein IDs without any isoform information, 
                "list_of_protein_isoforms" (list of str): all isomform IDs
                } if success else None
            error (str or None): error code/message if failed, else None
    """
    #return "placeholder"

    results = {}
    if not gene_names:
        return results 
    
    # Filter decoy Proteins, because we cannot process them decently? 
    valid_gene_names = set()
    for name in gene_names:
        if name.startswith("decoy:"):
            results[name] = (False, None, "IS_DECOY_PROTEIN")
        else: 
            valid_gene_names.add(name)

    if not valid_gene_names:
        return results
    
    query = " OR ".join(f"gene:{g}" for g in valid_gene_names)

    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"({query}) AND organism_id:9606 AND reviewed:true",
        "format": "tsv",
        "fields": "accession,gene_primary",
        "includeIsoform": "true",
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status() 

        output = defaultdict(lambda: {
            "protein_ids": [],
            "list_of_protein_isoforms": []
        }) 

        lines = response.text.strip().split("\n")
        header = lines[0].split("\t") 
        protein_id_idx = header.index("Entry")
        gene_name_idx = header.index("Gene Names (primary)")

        for line in lines[1:]:
            parts = line.split("\t")
            protein_id = parts[protein_id_idx]
            output_gene_names = parts[gene_name_idx].split()

            for g in output_gene_names:
                if g in valid_gene_names:
                    if "-" in protein_id:
                        output[g]["list_of_protein_isoforms"].append(protein_id)
                    else:
                        output[g]["protein_ids"].append(protein_id)

        for gn in valid_gene_names:
            data = output.get(gn) 

            if not data or not data["protein_ids"]: 
                results[gn] = (False, None, "NO_PROTEIN_ID_FOUND")
                #return False, None, "NO_PROTEIN_ID_FOUND"
            else:
                results[gn] = (True, data, None)
                #return True, {
                #    "protein_ids": protein_ids, 
                #    "list_of_protein_isoforms": list_of_protein_isoforms
                #}, None 

        return results 
    
    except requests.exceptions.Timeout: 
        for g in valid_gene_names:
            results[g] = (False, None, "TIMEOUT")
        return results 
        #return False, None, "TIMEOUT"
    
    except requests.exceptions.HTTPError as e: 
        for g in valid_gene_names:
            results[g] = (False, None, f"HTTP_{e.response.status_code}")
        return results 
        #return False, None, f"HTTP_{e.response.status_code}"
    
    except requests.exceptions.RequestException: 
        for g in valid_gene_names:
            results[g] = (False, None, "REQUEST_ERROR")
        return results 
        #return False, None, "REQUEST_ERROR"
    
    
def iterate_for_protein_designation(
        df, 
        existing_designation,
        new_designation, 
        uniprot_lookup_results,
        value_extractor=lambda x: x
):
    """
    Iterates over a DataFrame and adds the missing protein designations to the dataframe using
    precomputed lookup results. (either protein ids or gene names are included in the imported 
    data and the other is added to the data frame here)

    Parameters:
        df (pd.DataFrame)
        protein_designation (str): existing protein designation, e.g. "Protein_id" or "Protein"
        uniprot_lookup_results (dict):
            Mapping key -> (success, data, error)
        value_extractor (callable):
            function(data) -> value to store in DataFrame cell

    Returns:
        good_df (pd.DataFrame): Rows with successful lookups
        failed_df (pd.DataFrame): Rows with lookup errors
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

    #print(df.columns)


    good_df = normalize_crosslinking_df(pd.DataFrame(good_rows))
    failed_df = pd.DataFrame(failed_rows)

    return good_df, failed_df


def remove_brackets_from_peptide(peptide: str) -> str:
    return peptide.replace("[", "").replace("]", "")


def get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format(
    peptide: str,
) -> int:
    return peptide.find("[") + 1  # 1-based index


def read_ProteomeDiscoverer_XlinkX_file(file_path: Path) -> pd.DataFrame:
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

    #unique_protein_ids = set(df[["Protein_id1", "Protein_id2"]].stack().astype(str).str.strip())
    unique_protein_ids = aggregate_data(df, "Protein_id")
    uniprot_lookup_results = get_gene_name_from_protein_ids(unique_protein_ids)
    good_df, failed_df = iterate_for_protein_designation(
        df, 
        "Protein_id", 
        "Protein",
        uniprot_lookup_results,
        value_extractor=lambda x: x
    )

    return good_df, failed_df


def read_csm_file(file_path: Path) -> pd.DataFrame:
    """    
    Returns two DataFrames:
        - good_df: only rows with successful UniProt lookups
        - failed_df: rows where UniProt lookup failed, including error messages
    """
    df = pd.read_csv(file_path, low_memory=False).rename(
        columns=rename_columns_csm_format
    )

    df["Is_intra_crosslink"] = df["Protein1"].eq(df["Protein2"])

    unique_gene_names = aggregate_data(df, "Protein")
    uniprot_lookup_results = get_protein_ids_from_gene_name(unique_gene_names)
    # In our UniProt lookup we already get all isoforms of the respective gene name. 
    # Right now we only store the protein id without any isoform information in our dataframe to keep it consistent. 
    # If we ever need the isoform information we just have to change what the value extractor stores in our dataframe. 
    good_df, failed_df = iterate_for_protein_designation(
        df, 
        "Protein", 
        "Protein_id",
        uniprot_lookup_results,
        value_extractor=lambda x: x["protein_ids"][0] if x else None     
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
    return df.loc[:, columns_in_cross_linking_df]


def cross_linking_import(file_path: Path) -> dict:
    try:
        if file_path.suffix == ".csv":
            good_df, failed_df = read_csm_file(file_path)
            #df = read_csm_file(file_path)
        elif file_path.suffix == ".xlsx":
            good_df, failed_df = read_ProteomeDiscoverer_XlinkX_file(file_path)
            #df = read_ProteomeDiscoverer_XlinkX_file(file_path)
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
        msg = f"Successfully imported data of {len(good_df)} cross-links."
        messages = [dict(level=logging.INFO, msg=msg)]
    else: 
        msg = f"Warning: {len(failed_df)} rows failed to import, however {len(good_df)} cross-links were successfully imported."
        messages = [
            dict(level=logging.WARNING, msg=msg),
            dict(level=logging.WARNING, msg=f"Failed rows:\n{failed_df}")
        ]
    
    return dict(
        crosslinking_df=good_df, 
        messages=messages
        #crosslinking_df=df,
        #messages=[dict(level=logging.INFO, msg=msg)],
    )
