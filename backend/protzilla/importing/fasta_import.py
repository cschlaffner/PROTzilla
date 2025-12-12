"""
This module contains the code to parse a fasta file containing protein sequences and their ids.
"""

import logging

import pandas as pd
from Bio import SeqIO
from pandas import DataFrame


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
        raise ValueError("The provided fasta file does not contain protein sequences for all of the protein ids.")

    fasta_sequences = pd.DataFrame(
        {"Protein ID": protein_ids, "Protein Sequence": protein_sequences}
    )
    return {"fasta_df": fasta_sequences}
