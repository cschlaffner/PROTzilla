"""
This module contains the code to parse a fasta file containing protein sequences and their ids.
"""
import logging

import pandas as pd
from Bio import SeqIO


def parse_fasta_id(fasta_id: str) -> str:
    """
    Parse the fasta id to get the protein name from the fasta id string

    :param fasta_id: The fasta id string (string above the sequence in the fasta file)

    :return: The protein name
    """
    metadata = fasta_id.split("|")[1]
    if len(metadata) < 2:
        # TODO: should we raise an error here instead? or at least include in messages?
        # TODO: whatever we do, we should test this
        logging.warning(f"Metadata too short: {metadata}")
        return ""
    return metadata


def fasta_import(file_path: str) -> dict[str, pd.DataFrame]:
    """
    Import a fasta file and return a DataFrame with the protein sequences and their protein ids

    :param file_path: The path to the fasta file

    :return: A dictionary with a DataFrame containing the protein sequences and their protein ids
    """
    fasta_iterator = SeqIO.parse(open(file_path), "fasta")
    protein_ids = []
    protein_sequences = []
    for fasta_sequence in fasta_iterator:
        protein_id, sequence = parse_fasta_id(fasta_sequence.id), str(fasta_sequence.seq)
        # Make sure that the protein id has an isoform suffix even if it's the canonical isoform
        # TODO: test
        if "-" not in protein_id:
            protein_id = f"{protein_id}-1"
        protein_ids.append(protein_id)
        protein_sequences.append(sequence)

    fasta_sequences = pd.DataFrame(
        {"Protein ID": protein_ids, "Protein Sequence": protein_sequences}
    )
    return {"fasta_df": fasta_sequences}
