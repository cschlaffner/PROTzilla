"""
This module contains the code to parse a fasta file containing protein sequences and their ids.
"""

import logging

import pandas as pd
from Bio import SeqIO
from pandas import DataFrame
import requests

from backend.protzilla.constants.data_types import DataKey


def parse_fasta_id(fasta_id: str) -> str:
    """
    Parse the fasta id to get the protein name from the fasta id string

    :param fasta_id: The fasta id string (string above the sequence in the fasta file)

    :return: The protein name
    """
    metadata = fasta_id.split("|")
    if len(metadata) < 2:
        raise ValueError(
            "Fasta file metadata is invalid. It has to include a protein id"
        )
    return metadata[1]


def fasta_import(
    file_path: str,
) -> dict[str, list[dict[str, int | str]]] | dict[str, DataFrame]:
    """
    Import a fasta file and return a DataFrame with the protein sequences and their protein ids

    :param file_path: The path to the fasta file

    :return: A dictionary with a DataFrame containing the protein sequences and their protein ids
    """
    with open(file_path, encoding="utf-8") as f:
        fasta_iterator = SeqIO.parse(f, "fasta")
        protein_ids = []
        protein_sequences = []
        for fasta_sequence in fasta_iterator:
            protein_id, sequence = parse_fasta_id(fasta_sequence.id), str(
                fasta_sequence.seq
            )
            # Make sure that the protein id has an isoform suffix even if it's the canonical isoform
            if "-" not in protein_id:
                protein_id = f"{protein_id}-1"
            protein_ids.append(protein_id)
            protein_sequences.append(sequence)

    if not protein_ids:
        raise ValueError("The provided fasta file is empty.")

    if not all(protein_sequences):
        raise ValueError(
            "The provided fasta file does not contain protein sequences for all of the protein ids."
        )

    fasta_sequences = pd.DataFrame(
        {"Protein ID": protein_ids, "Protein Sequence": protein_sequences}
    )
    return {DataKey.FASTA_DF.value: fasta_sequences}


def fasta_generation(protein_df: pd.DataFrame):
    protein_ids_from_input = protein_df["Protein ID"].unique()
    protein_ids = []
    protein_sequences = []
    for i in range(0, len(protein_ids_from_input), 1000):
        url = f"https://rest.uniprot.org/uniprotkb/accessions?accessions={','.join(protein_ids_from_input[i:min(i + 1000, len(protein_ids_from_input))])}&format=fasta"
        try:
            response = requests.get(url, timeout=20)
            if response.status_code != 200:
                return dict(
                    messages=dict(
                        level=logging.ERROR, msg="At least one uniprot request failed"
                    )
                )
            fasta = []
            current_id = None
            for line in response.text.splitlines():
                if line.startswith(">"):
                    if current_id is not None:
                        # Make sure that the protein id has an isoform suffix even if it's the canonical isoform
                        if "-" not in current_id:
                            current_id = f"{current_id}-1"
                        protein_ids.append(current_id)
                        protein_sequences.append("".join(fasta))
                    fasta = []
                    current_id = line.split("|")[1]
                else:
                    fasta.append(line.strip())
            if current_id is not None:
                # Make sure that the protein id has an isoform suffix even if it's the canonical isoform
                if "-" not in current_id:
                    current_id = f"{current_id}-1"
                protein_ids.append(current_id)
                protein_sequences.append("".join(fasta))

        except requests.Timeout:
            return dict(
                messages=dict(
                    level=logging.ERROR, msg="At least one uniprot request timed out."
                )
            )
        except Exception:
            return dict(
                messages=dict(
                    level=logging.ERROR, msg="The uniprot rest api was not reachable."
                )
            )
    messages = []
    if len(protein_ids) != len(protein_ids_from_input):
        messages.append(
            dict(
                level=logging.WARNING,
                msg=f"{len(protein_ids_from_input) - len(protein_ids)} protein ids were not found in uniprot and therefore not added to the fasta.",
            )
        )
    return dict(
        fasta_df=pd.DataFrame(
            {"Protein ID": protein_ids, "Protein Sequence": protein_sequences}
        ),
        messages=messages,
    )
