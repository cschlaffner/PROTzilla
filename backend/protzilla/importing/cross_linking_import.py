"""
This module contains the code to parse a file containing cross linking data.
"""

import logging
from pathlib import Path
import pandas as pd
import traceback
import requests

from backend.protzilla.utilities import format_trace
from backend.protzilla.importing.import_utils import (
    columns_in_cross_linking_df,
    rename_columns_csm_format,
    rename_columns_proteomediscoverer_xlinkx_format,
)


def get_gene_name_from_protein_id(protein_id):
    return "placeholder"
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}"
    params = {"fields": "gene_names", "format": "json"}

    response = requests.get(url, params=params)
    response.raise_for_status()  # Fehler werfen, wenn etwas schief geht

    data = response.json()

    gene_name = data["genes"][0]["geneName"]["value"]

    return gene_name


def get_protein_ids_from_gene_name(gene_name):
    return "placeholder"
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene:{gene_name} AND organism_id:9606 AND reviewed:true",
        "format": "list",
        "includeIsoform": "true",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Fehler werfen, wenn etwas schief geht

    all_ids = response.text.strip().split("\n")
    protein_ids = [i for i in all_ids if "-" not in i]
    list_of_protein_isoforms = [i for i in all_ids if "-" in i]

    return protein_ids, list_of_protein_isoforms


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

    df["Protein1"] = df["Protein_id1"].apply(get_gene_name_from_protein_id)
    df["Protein2"] = df["Protein_id2"].apply(get_gene_name_from_protein_id)

    df["Is_intra_crosslink"] = df["Is_intra_crosslink"].eq("Intra")

    return normalize_crosslinking_df(df)


def read_csm_file(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False).rename(
        columns=rename_columns_csm_format
    )

    df["Protein_id1"] = df["Protein1"].apply(get_protein_ids_from_gene_name)
    df["Protein_id2"] = df["Protein2"].apply(get_protein_ids_from_gene_name)

    df["Is_intra_crosslink"] = df["Protein1"].eq(df["Protein2"])

    return normalize_crosslinking_df(df)


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
            df = read_csm_file(file_path)
        elif file_path.suffix == ".xlsx":
            df = read_ProteomeDiscoverer_XlinkX_file(file_path)
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
    msg = f"Successfully imported data of {len(df)} cross-links."
    return dict(
        crosslinking_df=df,
        messages=[dict(level=logging.INFO, msg=msg)],
    )
