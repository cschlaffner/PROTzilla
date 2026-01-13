"""
This module contains the code to parse a file containing cross linking data.
"""

import logging
from pathlib import Path
from typing import Callable, Tuple 
import pandas as pd
import traceback
import requests

from backend.protzilla.utilities import format_trace
from backend.protzilla.importing.import_utils import (
    columns_in_cross_linking_df,
    rename_columns_csm_format,
    rename_columns_proteomediscoverer_xlinkx_format,
)


def get_protein_designation(designation_lookup_cache, protein_designation, uniprot_lookup_func):
    if designation_lookup_cache[protein_designation]:
        success, new_protein_designation, error = True, designation_lookup_cache[protein_designation], None
    else:
        success, new_protein_designation, error = uniprot_lookup_func(protein_designation)
        if success:
            designation_lookup_cache[protein_designation] = new_protein_designation
    return success, new_protein_designation, error


def get_gene_name_from_protein_id(protein_id):
    """
    Retrieves the gene name for a given Protein ID from UniProt.

    Parameters:
        protein_id (str): The UniProt accession ID (e.g. "Q92878").

    Returns:
        success (bool): True if the lookup succeeded, False otherwise
        gene_name (str or None): Official gene name if successful, else None
        error (str or None): Error code/message if failed, else None
    """
    #return "placeholder"
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}"
    params = {"fields": "gene_names", "format": "json"}

    try: 
        response = requests.get(url, params=params)
        response.raise_for_status() 

        data = response.json()
        gene_name = data.get("genes", [{}])[0].get("geneName", {}).get("value")

        if gene_name: 
            return True, gene_name, None
        else:
            return False, None, "NO_GENE_NAME_FOUND"
        
    except requests.exceptions.Timeout:
        return False, None, "TIMEOUT"
    
    except requests.exceptions.HTTPError as e:
        return False, None, f"HTTP_{e.response.status_code}"
    
    except requests.exceptions.RequestException:
        return False, None, "REQUEST_ERROR"
    
    except ValueError:
        return False, None, "INVALID_JSON"


def get_protein_ids_from_gene_name(gene_name):
    """
    Retrieves UniProt protein IDs for a given human gene name.

    Parameters: 
        gene_name (str): The gene symbol to look up (e.g. "RAD50")
    
    Returns:
        success (bool): True if lookup succeeded, False otherwise
        data (dict or None): {
            "protein_ids" (list of str): all protein IDs without any isoform information, 
            "list_of_protein_isoforms" (list of str): all isomform IDs
            } if success else None
        error (str or None): error code/message if failed, else None
    """
    #return "placeholder"
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene:{gene_name} AND organism_id:9606 AND reviewed:true",
        "format": "list",
        "includeIsoform": "true",
    }
    try:
        response = requests.get(url, params=params, timeout=1)
        response.raise_for_status()  

        all_ids = response.text.strip().split("\n")
        protein_ids = [i for i in all_ids if "-" not in i]
        list_of_protein_isoforms = [i for i in all_ids if "-" in i]

        if not protein_ids: 
            return False, None, "NO_PROTEIN_ID_FOUND"
        else:
            return True, {
                "protein_ids": protein_ids, 
                "list_of_protein_isoforms": list_of_protein_isoforms
            }, None 
    
    except requests.exceptions.Timeout: 
        return False, None, "TIMEOUT"
    
    except requests.exceptions.HTTPError as e: 
        return False, None, f"HTTP_{e.response.status_code}"
    
    except requests.exceptions.RequestException: 
        return False, None, "REQUEST_ERROR"
    

def iterate_for_protein_designation(df, protein_designation, uniprot_lookup_func):
    good_rows = []
    failed_rows = []
    protein_designation_cache = {}

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        success1, new_protein_designation1, error1 = get_protein_designation(protein_designation_cache, row[protein_designation + "1"], uniprot_lookup_func)
        success2, new_protein_designation2, error2 = get_protein_designation(protein_designation_cache, row[protein_designation + "2"], uniprot_lookup_func)

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
            row_dict[protein_designation + "1"] = new_protein_designation1
            row_dict[protein_designation + "2"] = new_protein_designation2

        good_rows.append(row_dict)

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

    """good_rows = []
    failed_rows = []
    gene_names_cache = {}

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        success1, gene_name1, error1 = get_protein_designation(gene_names_cache, row["Protein_id1"])
        success2, gene_name2, error2 = get_protein_designation(gene_names_cache, row["Protein_id2"])

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
            row_dict["Protein_id1"] = gene_name1
            row_dict["Protein_id2"] = gene_name2

        good_rows.append(row_dict)

    #df["Protein1"] = df["Protein_id1"].apply(get_gene_name_from_protein_id)
    #df["Protein2"] = df["Protein_id2"].apply(get_gene_name_from_protein_id)

    good_df = normalize_crosslinking_df(pd.DataFrame(good_rows))
    failed_df = pd.DataFrame(failed_rows)"""

    good_df, failed_df = iterate_for_protein_designation(df, "Protein_id", get_gene_name_from_protein_id)

    return good_df, failed_df


def read_csm_file(file_path: Path) -> pd.DataFrame:
    """    
    Returns two DataFrames:
        - normalized_df: only rows with successful UniProt lookups
        - failed_df: rows where UniProt lookup failed, including error messages
    """
    df = pd.read_csv(file_path, low_memory=False).rename(
        columns=rename_columns_csm_format
    )

    df["Is_intra_crosslink"] = df["Protein1"].eq(df["Protein2"])

    """good_rows = []
    failed_rows = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        success1, data1, error1 = get_protein_ids_from_gene_name(row["Protein1"])
        success2, data2, error2 = get_protein_ids_from_gene_name(row["Protein2"])

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
            row_dict["Protein_id1"] = data1
            row_dict["Protein_id2"] = data2

        #row_dict["Is_intra_crosslink"] = row["Protein1"] == row["Protein2"]

        good_rows.append(row_dict)

    good_df = normalize_crosslinking_df(pd.DataFrame(good_rows))
    failed_df = pd.DataFrame(failed_rows)"""

    good_df, failed_df = iterate_for_protein_designation(df, "Protein", get_protein_ids_from_gene_name)

    #df["Protein_id1"] = df["Protein1"].apply(get_protein_ids_from_gene_name)
    #df["Protein_id2"] = df["Protein2"].apply(get_protein_ids_from_gene_name)

    #df["Is_intra_crosslink"] = df["Protein1"].eq(df["Protein2"])

    #return normalize_crosslinking_df(df)
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
