import itertools
import ast
import math

from multiprocessing.sharedctypes import Value
from typing import TYPE_CHECKING, Callable

from numpy.testing import assert_

from backend.protzilla.constants.option_types import CrosslinkingValidationCriterion
import pandas as pd
import numpy as np
import re
import logging

from plotly.graph_objects import Figure

from backend.protzilla.data_preprocessing.plots import (
    create_histograms,
    create_bar_plot,
)
from backend.protzilla.constants.protzilla_logging import logger
from backend.protzilla.data_analysis.plots import (
    add_vertical_line_with_annotation_in_legend,
)
from backend.protzilla.steps import OutputItem, OutputType


def get_reactive_atom_of_amino_acid_residue(amino_acid_type: str) -> str:
    """
    Returns the atom of an amino acid residue that is considered reactive for
    crosslinking. Currently, this always returns the central alpha carbon (CA).

    :param amino_acid_type: code of the amino acid

    :return: the atom identifier of the reactive atom as a string
    """
    # right now we always return the central C atom
    # later we might want to return the reactive atom of the amino acid residue of the specific amino acid type
    # as soon as we change this, we will need to change the test test_validate_with_angstrom_deviation (and the visualization)
    return "CA"


def get_coordinates_of_atom_crosslinker_bound_to(
    amino_acid_position_where_crosslinker_bound: int,
    amino_acid_type: str,
    cif_df: pd.DataFrame,
    chain_id: str,
) -> tuple[float, float, float]:
    """
    Returns the Cartesian coordinates of the atom to which the crosslinker is
    bound for a given amino acid residue in a protein structure.

    :param amino_acid_position_where_crosslinker_bound: 1-based position of the amino acid residue
    :param amino_acid_type: amino acid type at the given position
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :param chain_id: ID of the chain of the atom the crosslinker bounds to
    :return: a tuple (x, y, z) containing the Cartesian coordinates of the atom in Ångström
    :raises ValueError: if the specified atom cannot be found in the CIF data
    """

    relevant_atom = get_reactive_atom_of_amino_acid_residue(amino_acid_type)
    seq_ids = pd.to_numeric(cif_df["_atom_site.label_seq_id"], errors="coerce")

    # Filter to the exact reactive atom of the amino acid residue
    # where the crosslinker is bound (e.g. CA at position 45)
    cif_df = cif_df[
        (cif_df["_atom_site.label_atom_id"] == relevant_atom)
        & (seq_ids == amino_acid_position_where_crosslinker_bound)
        & (cif_df["_atom_site.auth_asym_id"] == chain_id)
    ]

    if cif_df.empty:
        raise ValueError(
            f"No {relevant_atom} atom found for amino acid at position {amino_acid_position_where_crosslinker_bound} in chain {chain_id}."
        )

    row = cif_df.iloc[0]

    x = float(row["_atom_site.Cartn_x"])
    y = float(row["_atom_site.Cartn_y"])
    z = float(row["_atom_site.Cartn_z"])

    return x, y, z


def get_distance_between_two_amino_acids_in_angstrom(
    amino_acid_position1: int,
    amino_acid_position2: int,
    amino_acid_type1: str,
    amino_acid_type2: str,
    cif_df: pd.DataFrame,
    chain_id1: str,
    chain_id2: str,
) -> float:
    """
    Calculates the Euclidean distance in Ångström between two amino acid residues
    based on the coordinates of their reactive atoms in the AlphaFold/predicted structure.

    :param amino_acid_position1: 1-based position of the first amino acid residue
    :param amino_acid_position2: 1-based position of the second amino acid residue
    :param amino_acid_type1: amino acid type at the first position
    :param amino_acid_type2: amino acid type at the second position
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :param chain_id1: ID of the chain of the first amino acid residue in which crosslinker binds
    :param chain_id2: ID of the chain of the second amino acid residue in which crosslinker binds
    :return: the distance between the two residues in Ångström
    """

    pos1 = np.array(
        get_coordinates_of_atom_crosslinker_bound_to(
            amino_acid_position1,
            amino_acid_type1,
            cif_df,
            chain_id1,
        ),
        dtype=float,
    )

    pos2 = np.array(
        get_coordinates_of_atom_crosslinker_bound_to(
            amino_acid_position2,
            amino_acid_type2,
            cif_df,
            chain_id2,
        ),
        dtype=float,
    )

    return float(np.linalg.norm(pos2 - pos1))


def get_protein_sequence_from_df(
    amino_acid_sequences_df: pd.DataFrame, protein_id: str
) -> str:
    """
    Returns the amino acid sequence for a given protein ID from a DataFrame.

    If the provided protein ID does not contain an isoform suffix, the default suffix "-1"
    is appended to match the format used in the DataFrame (e.g. "O43242" becomes "O43242-1").

    :param amino_acid_sequences_df: DataFrame containing at least the columns
    "Protein ID" and "Protein Sequence"
    :param protein_id: UniProt protein identifier, with or without isoform suffix
    :return: the corresponding amino acid sequence as a string, or an empty string
    if the protein ID is not found
    """
    # because protein ids like O43242 are saved as O43242-1 in amino_acid_sequences_df
    if "-" not in protein_id:
        protein_id = f"{protein_id}-1"

    matches = amino_acid_sequences_df.loc[
        amino_acid_sequences_df["Protein ID"] == protein_id, "Protein Sequence"
    ]

    if matches.empty:
        raise KeyError("Protein ID not found in the given fasta file.")

    return matches.iloc[0]


def add_protein_crosslink_positions_to_df(
    input_crosslinking_df: pd.DataFrame,
    amino_acid_sequences_df: pd.DataFrame,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Add protein-level crosslink residue positions to a crosslinking DataFrame.

     For each row, this function finds the 1-based residue positions in the full protein
     sequence(s) that correspond to the crosslinked residue within each peptide. The
     protein-level positions are written to two new columns:

     - 'crosslinker_position1': 1-based residue position in Protein_id1 for Peptide1.
     - 'crosslinker_position2': 1-based residue position in Protein_id2 for Peptide2.

     If a peptide occurs multiple times in the corresponding protein sequence, all
     combinations of (position1, position2) are generated. The first combination is
     kept in the original row and the row is duplicated for each additional combination.

     If either peptide cannot be matched in its corresponding protein sequence, the row
     is removed and a warning message is recorded.

     :param input_crosslinking_df: DataFrame containing crosslinking data with at least the following columns:
                            - 'Peptide1': first peptide sequence
                            - 'Peptide2': second peptide sequence
                            - 'CL_position_within_peptide1': 0-based crosslinker position within Peptide1
                            - 'CL_position_within_peptide2': 0-based crosslinker position within Peptide2
     :param amino_acid_sequences_df: Dataframe that contains all amino acid sequences
     :return: tuple (updated_crosslinking_df, messages)
              - updated_crosslinking_df: input DataFrame with two new columns:
                  - 'crosslinker_position1': 1-based crosslinker position in Peptide1
                  - 'crosslinker_position2': 1-based crosslinker position in Peptide2
                  Rows are duplicated for multiple peptide matches.
              - messages: list of warning dictionaries if the peptide was not found or a row was duplicated
    """
    crosslinking_df = input_crosslinking_df.copy()
    crosslinking_df["crosslinker_position1"] = pd.Series(dtype="Int64")
    crosslinking_df["crosslinker_position2"] = pd.Series(dtype="Int64")
    rows_to_duplicate = {}
    rows_to_delete = []
    messages = []

    def get_crosslink_positions_in_protein(
        peptide: str, protein_id: str, cl_position_within_peptide: int
    ) -> list:
        """
        Returns the 1-based positions of the crosslinked residue within the full
        protein sequence for all occurrences of a given peptide.

        :param peptide: peptide sequence to search for in the protein
        :param protein_id: UniProt protein identifier
        :param cl_position_within_peptide: 1-based position of the crosslinked residue within the peptide
        :return: list of 1-based residue positions in the protein sequence
        """
        protein_sequence = get_protein_sequence_from_df(
            amino_acid_sequences_df=amino_acid_sequences_df, protein_id=protein_id
        )
        positions = [
            m.start() + cl_position_within_peptide + 1
            for m in re.finditer(f"(?={peptide})", protein_sequence)
        ]
        return positions

    for idx, crosslinker_row in crosslinking_df.iterrows():
        peptide_sequence1 = re.escape(crosslinker_row.Peptide1)
        peptide_sequence2 = re.escape(crosslinker_row.Peptide2)
        protein_id1 = crosslinker_row.Protein_id1
        protein_id2 = crosslinker_row.Protein_id2

        peptide1_positions = get_crosslink_positions_in_protein(
            peptide_sequence1, protein_id1, crosslinker_row.CL_position_within_peptide1
        )
        peptide2_positions = get_crosslink_positions_in_protein(
            peptide_sequence2, protein_id2, crosslinker_row.CL_position_within_peptide2
        )

        all_position_combinations = list(
            itertools.product(peptide1_positions, peptide2_positions)
        )
        if not all_position_combinations:
            if not peptide1_positions and not peptide2_positions:
                msg = f"Peptide sequences {peptide_sequence1} and {peptide_sequence2} of crosslink entry {idx} were not found in the protein sequences. The entry was deleted."
            else:
                msg = f"Peptide sequence {peptide_sequence1 if not peptide1_positions else peptide_sequence2} of crosslink entry {idx} was not found in the protein sequences. The entry was deleted."
            messages.append(dict(level=logging.WARNING, msg=msg))
            rows_to_delete.append(idx)
            continue
        crosslinker_position1, crosslinker_position2 = all_position_combinations[0]

        crosslinking_df.at[idx, "crosslinker_position1"] = crosslinker_position1
        crosslinking_df.at[idx, "crosslinker_position2"] = crosslinker_position2
        if len(all_position_combinations) > 1:
            rows_to_duplicate[idx] = all_position_combinations[1:]

    crosslinking_df.drop(rows_to_delete, inplace=True)

    if not rows_to_duplicate:
        return crosslinking_df, messages
    new_rows = []
    for row_to_duplicate_idx, potential_positions in rows_to_duplicate.items():
        for potential_cl_position1, potential_cl_position2 in potential_positions:
            new_row = crosslinking_df.loc[row_to_duplicate_idx].copy()
            new_row["crosslinker_position1"] = potential_cl_position1
            new_row["crosslinker_position2"] = potential_cl_position2
            new_rows.append(new_row)
        messages.append(
            dict(
                level=logging.WARNING,
                msg=f"Row {row_to_duplicate_idx} was duplicated {len(potential_positions)} times due to several matches between peptide sequence and protein sequence.",
            )
        )
    if new_rows:
        crosslinking_df = pd.concat(
            [crosslinking_df, pd.DataFrame(new_rows)], ignore_index=True
        )

    return crosslinking_df, messages


def get_chains(
    cif_df: pd.DataFrame,
    valid_ids: dict,
    protein_id: str,
    id_column_name: str,
) -> list:
    """
    Returns a list of unique chain IDs belonging to a given protein
    in an mmCIF-derived DataFrame.

    :param cif_df: mmCIF data as a pandas DataFrame.
    :param valid_ids: dictionary of valid IDs.
    :param protein_id: identifier of the protein you want to query.
    :param id_column_name: column name to check against valid_ids.
    :return: list of unique chain IDs.
    """
    target_ids = valid_ids.get(protein_id, [])
    if not target_ids:
        return []
    target_ids_as_strings = [str(i) for i in target_ids]
    relevant_df = cif_df[cif_df[id_column_name].astype(str).isin(target_ids_as_strings)]
    chain_ids = relevant_df["_atom_site.auth_asym_id"].dropna().unique().tolist()
    return chain_ids


def _get_structure_entry_id(structure_metadata_df: pd.DataFrame) -> list[str]:
    if "entry_id" in structure_metadata_df.columns:
        return structure_metadata_df["entry_id"].iloc[0]
    else:
        raise ValueError("Metadata must contain 'entry_id'.")


def expand_crosslinks_to_chain_combinations(
    relevant_crosslinks_df: pd.DataFrame,
    chains_per_protein: dict[str, dict[str, int]],
) -> pd.DataFrame:
    """
    Duplicate each crosslink row so that all possible chain combinations
    are represented.


    :param relevant_crosslinks_df: dataframe that contains information on the crosslinks between the proteins
    :param chains_per_protein: dictionary that contains all chain_ids in a list for each protein id
    return: crosslinks dataframe with the additional columns of Chain_id1 and Chain_id2
    """
    expanded_rows = []

    for _, crosslink in relevant_crosslinks_df.iterrows():
        protein_id1 = crosslink["Protein_id1"]
        protein_id2 = crosslink["Protein_id2"]

        chain_ids1 = chains_per_protein[protein_id1]
        chain_ids2 = chains_per_protein[protein_id2]

        if not chain_ids1 or not chain_ids2:
            continue

        # we do not want the same combination twice if the protein_ids are the same
        # e.g.: protein 1 chain A - protein 1 chain B and protein 1 chain B - protein 1 chain A
        if protein_id1 == protein_id2:
            chain_pairs = itertools.combinations_with_replacement(chain_ids1, 2)
        else:
            chain_pairs = itertools.product(chain_ids1, chain_ids2)

        for chain_id1, chain_id2 in chain_pairs:
            new_row = crosslink.copy()
            new_row["Chain_id1"] = chain_id1
            new_row["Chain_id2"] = chain_id2
            expanded_rows.append(new_row)

    if not expanded_rows:
        return pd.DataFrame(
            columns=list(relevant_crosslinks_df.columns) + ["Chain_id1", "Chain_id2"]
        )

    return pd.DataFrame(expanded_rows).reset_index(drop=True)


def monomer_validation(
    crosslinking_df: pd.DataFrame,
    structure_metadata_df: pd.DataFrame,
    crosslinker_information: dict[str, list[float]],
    cif_df: pd.DataFrame,
    amino_acid_sequences_df: pd.DataFrame,
    pae_matrix: np.ndarray[tuple[int, int]],
    plddt_df: pd.DataFrame,
    validation_criterion: CrosslinkingValidationCriterion,
) -> dict:
    """
    Validates crosslinking data for a monomeric protein structure by checking
    distance deviations (in Angstroms).

    :param crosslinking_df: DataFrame containing the full set of crosslinks.
    :param structure_metadata_df: DataFrame containing structural metadata.
    :param crosslinker_information: Dictionary mapping crosslinker names to their
                                    allowed distance boundaries (e.g., [min_dist, max_dist]).
    :param cif_df: DataFrame containing mmCIF information.
    :param amino_acid_sequences_df: DataFrame containing known amino acid sequences.
    :param pae_matrix: NumPy 2D array containing AlphaFold PAE data.
    :param plddt_df: DataFrame containing AlphaFold pLDDT data.
    :return: A dictionary containing the validation results and distance metrics.
    """
    protein_id = structure_metadata_df["uniprot_accession"].iloc[0]
    valid_ids = {protein_id: [protein_id]}
    return validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        crosslinker_information=crosslinker_information,
        structure_metadata_df=structure_metadata_df,
        cif_df=cif_df,
        amino_acid_sequences_df=amino_acid_sequences_df,
        pae_matrix=pae_matrix,
        plddt_df=plddt_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.pdbx_sifts_xref_db_acc",
        structures_to_validate=[protein_id],
        validation_criterion=validation_criterion,
    )


def get_protein_id_from_sequence(amino_acid_sequences_df, target_sequence):
    """
    Finds the Protein ID(s) for a given exact protein sequence.

    :param amino_acid_sequences_df: Dataframe that contains all amino acid sequences
    :param target_sequence: The protein sequence you want to find the protein id of.
    :return: the Protein ID that matches the sequence. (Should only be one, therefore we take the first one)
    """
    matching_rows = amino_acid_sequences_df[
        amino_acid_sequences_df["Protein Sequence"] == target_sequence
    ]
    if not matching_rows.empty:
        return matching_rows["Protein ID"].iloc[0]
    else:
        return None


def get_valid_ids_per_protein_id_from_job_request(
    amino_acid_sequences_df: pd.DataFrame, job_request_df: pd.DataFrame
) -> dict:
    """
    Extracts protein sequences from an AlphaFold Server job request and assigns
    them their protein ID based on the given amino sequences df. It then checks the count
    and collects all ids that will later be used in the cif file to identify the proteins
    instead of their protein ids (because there are no protein ids in the cif file given)

    :param amino_acid_sequences_df: Dataframe that contains all amino acid sequences.
    :param job_request_df: DataFrame containing the loaded AlphaFold job request JSON,
                           which must include a 'sequences' column.
    :return: A dictionary mapping Protein IDs to a list of their assigned unique integer
             chain IDs. Example: {'P12345': [1, 2], 'Q67890': [3]}
    """
    valid_ids = {}
    unique_id = 1

    sequences_list = job_request_df["sequences"].iloc[0]
    if isinstance(sequences_list, str):
        sequences_list = ast.literal_eval(sequences_list)

    for item in sequences_list:
        if "proteinChain" in item:
            seq_string = item["proteinChain"]["sequence"]
            count = item["proteinChain"]["count"]
            protein_id = get_protein_id_from_sequence(
                amino_acid_sequences_df, seq_string
            )
            if protein_id is not None:
                # Remove the specific isoform/variant suffix because we do not use it in the crosslinking df
                protein_id = protein_id.replace("-1", "")
                for _ in range(count):
                    valid_ids.setdefault(protein_id, []).append(unique_id)
                    unique_id += 1
    return valid_ids


def get_global_residue_index(
    position_within_protein: int,  # 1-based index
    chain_id: str,
    cif_df: pd.DataFrame,
):
    """
    For multimer PAE lookup: For a position within a given protein in a chain,
    get the global 0-based residue index used to find that position in the PAE matrix.

    Note: This assumes that the order of AAs in the _atom_site table corresponds
    to the order of residues in the pae matrix and thus the other residue-based tables in
    the cif.

    :param position_within_protein: index of the amino acid within the protein (1-based)
    :param chain_id: the chain ID of the protein within the complex
    :param cif_df: DataFrame containing the _atom_site table of the complex structure
    """

    # Get table with only unique chain and sequence IDs and infer global index
    index_lookup_df = (
        cif_df[["_atom_site.label_asym_id", "_atom_site.label_seq_id"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    index_lookup_df.reset_index(inplace=True)

    index_lookup_df = index_lookup_df[
        index_lookup_df["_atom_site.label_asym_id"] == chain_id
    ]
    index_lookup_df = index_lookup_df[
        index_lookup_df["_atom_site.label_seq_id"] == position_within_protein
    ]

    if len(index_lookup_df) != 1:
        raise ValueError(
            "Invalid input: CIF contains multiple atoms mapped to same chain/sequence ID pair!"
        )

    return index_lookup_df["index"].iloc[0]


def multimer_validation(
    crosslinking_df: pd.DataFrame,
    structure_metadata_df: pd.DataFrame,
    crosslinker_information: dict[str, list[float]],
    cif_df: pd.DataFrame,
    amino_acid_sequences_df: pd.DataFrame,
    job_request_df: pd.DataFrame,
    plddt_df: pd.DataFrame,
    pae_matrix: np.ndarray[tuple[int, int]],
    validation_criterion: CrosslinkingValidationCriterion,
) -> dict:
    """
    Validates crosslinking data for a multimeric protein complex by checking
    distance deviations (in Angstroms).

    This function maps sequences from an AlphaFold Server job request to determine
    valid chain IDs, filters the crosslinking dataset to include only interactions
    between these valid structures, and delegates the structural distance calculation.

    :param crosslinking_df: DataFrame containing the full set of crosslinks.
    :param structure_metadata_df: DataFrame containing structural metadata.
                                  (Note: Passed for pipeline consistency, but unused in this step).
    :param crosslinker_information: Dictionary mapping crosslinker names to their
                                    allowed distance boundaries (e.g., [min_dist, max_dist]).
    :param cif_df: DataFrame containing mmCIF information.
    :param amino_acid_sequences_df: DataFrame containing known amino acid sequences.
    :param job_request_df: DataFrame containing the loaded AlphaFold job request JSON.
    :param plddt_df: DataFrame containing per-residue pLDDT values.
    :param pae_matrix: NumPy 2D array containing the PAE values for each residue pair.
    :return: A dictionary containing the validation results and distance metrics.
    """
    valid_ids = get_valid_ids_per_protein_id_from_job_request(
        amino_acid_sequences_df=amino_acid_sequences_df, job_request_df=job_request_df
    )
    structures_to_validate = list(valid_ids.keys())

    return validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        crosslinker_information=crosslinker_information,
        structure_metadata_df=structure_metadata_df,
        cif_df=cif_df,
        amino_acid_sequences_df=amino_acid_sequences_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.label_entity_id",
        structures_to_validate=structures_to_validate,
        pae_matrix=pae_matrix,
        plddt_df=plddt_df,
        validation_criterion=validation_criterion,
    )


def validate_with_angstrom_deviation(
    crosslinking_df: pd.DataFrame,
    crosslinker_information: dict[str, list[float]],
    structure_metadata_df: pd.DataFrame,
    cif_df: pd.DataFrame,
    amino_acid_sequences_df: pd.DataFrame,
    valid_ids: dict[str, list[int]],
    id_column_name: str,
    structures_to_validate: list,
    validation_criterion: CrosslinkingValidationCriterion,
    plddt_df: pd.DataFrame | None = None,
    pae_matrix: np.ndarray[tuple[int, int]] | None = None,
) -> dict:
    """
    Validates crosslinks by comparing the crosslinker lengths with the distances between the linked
    amino acids in the AlphaFold protein structure. A crosslink is regarded as valid if it matches the AlphaFold data,
    so if the distance between the connected amino acids in AlphaFold is less than (crosslinker length + the upper allowed deviation)
    and more than (crosslinker length - the lower allowed deviation). If one of the bounds is zero only the other bound will be applied.

    :param crosslinking_df: DataFrame containing the crosslinking data to validate.
    :param crosslinker_information: Dictionary mapping crosslinker names to a list of three floats:
                                    [crosslinker_length, upper_accepted_deviation, lower_accepted_deviation].
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms).
    :param plddt_df: DataFrame containing the local AlphaFold pLDDT values for each residue.
    :param pae_matrix: NumPy 2D array containing the PAE values for each residue pair.
    :param amino_acid_sequences_df: Dataframe that contains all known amino acid sequences.
    :param valid_ids: Dictionary mapping protein IDs to their valid chain/entity identifiers in the CIF data.
    :param id_column_name: The column name in the cif_df to use for matching against valid_ids.
    :param structures_to_validate: List of protein IDs to validate.
    :return: A dictionary containing:
             - 'crosslinking_result_df': DataFrame containing the validated rows augmented with alphafold distances,
               validation booleans, crosslinker positions, and link types (intra/inter).
             - 'messages': List of dictionaries containing log levels and warning/info messages.
    :raises KeyError: If a required crosslinker field is missing in crosslinker_information.
    :raises ValueError: If peptide sequences cannot be matched to the protein sequence.
    """

    all_crosslinks_df = crosslinking_df.copy()
    mask = (all_crosslinks_df["Protein_id1"].isin(structures_to_validate)) & (
        all_crosslinks_df["Protein_id2"].isin(structures_to_validate)
    )
    relevant_crosslinks_df = all_crosslinks_df[mask]

    # Check if dataframe is empty
    if relevant_crosslinks_df.empty:
        msg = "There are no crosslinks between the structures to validate."
        messages = [dict(level=logging.WARNING, msg=msg)]
        logger.warning(msg)
        return dict(crosslinking_result_df=pd.DataFrame(), messages=messages)

    chains_per_protein = {}
    for protein_id in structures_to_validate:
        chains_per_protein[protein_id] = get_chains(
            cif_df=cif_df,
            valid_ids=valid_ids,
            protein_id=protein_id,
            id_column_name=id_column_name,
        )

    relevant_crosslinks_df = expand_crosslinks_to_chain_combinations(
        relevant_crosslinks_df=relevant_crosslinks_df,
        chains_per_protein=chains_per_protein,
    )

    if relevant_crosslinks_df.empty:
        msg = "There are no crosslinks between the structures to validate."
        messages = [dict(level=logging.WARNING, msg=msg)]
        logger.warning(msg)
        return dict(crosslinking_result_df=pd.DataFrame(), messages=messages)

    relevant_crosslinks_df, messages = add_protein_crosslink_positions_to_df(
        relevant_crosslinks_df, amino_acid_sequences_df
    )

    def check_crosslink(crosslink: pd.Series) -> pd.Series:
        protein_id1 = crosslink.Protein_id1
        protein_id2 = crosslink.Protein_id2
        protein_sequence1 = get_protein_sequence_from_df(
            amino_acid_sequences_df=amino_acid_sequences_df, protein_id=protein_id1
        )
        protein_sequence2 = get_protein_sequence_from_df(
            amino_acid_sequences_df=amino_acid_sequences_df, protein_id=protein_id2
        )

        def get_site_plddts(crosslink: pd.Series):
            if plddt_df is None:
                return np.nan, np.nan

            plddt_at_position1 = float(
                plddt_df.query(
                    "residueNumber == @crosslink.crosslinker_position1 and "
                    + "chainID == @crosslink.Chain_id1"
                ).iloc[0]["confidenceScore"]
            )
            plddt_at_position2 = float(
                plddt_df.query(
                    "residueNumber == @crosslink.crosslinker_position2 and "
                    + "chainID == @crosslink.Chain_id2"
                ).iloc[0]["confidenceScore"]
            )

            return plddt_at_position1, plddt_at_position2

        def get_paes():
            if pae_matrix is None:
                return np.nan, np.nan

            pae_index_pos1 = get_global_residue_index(
                crosslink.crosslinker_position1, crosslink.Chain_id1, cif_df
            )
            pae_index_pos2 = get_global_residue_index(
                crosslink.crosslinker_position2, crosslink.Chain_id2, cif_df
            )
            pae_x_position1 = pae_matrix[
                pae_index_pos1, pae_index_pos2
            ]  # Using position1 as scored residue
            pae_x_position2 = pae_matrix[
                pae_index_pos2, pae_index_pos1
            ]  # Using position2 as scored residue

            return pae_x_position1, pae_x_position2

        plddt_at_position1, plddt_at_position2 = get_site_plddts(crosslink)
        pae_x_position1, pae_x_position2 = get_paes()

        predicted_distance = get_distance_between_two_amino_acids_in_angstrom(
            amino_acid_position1=crosslink.crosslinker_position1,
            amino_acid_position2=crosslink.crosslinker_position2,
            amino_acid_type1=protein_sequence1[crosslink.crosslinker_position1 - 1],
            amino_acid_type2=protein_sequence2[crosslink.crosslinker_position2 - 1],
            cif_df=cif_df,
            chain_id1=crosslink.Chain_id1,
            chain_id2=crosslink.Chain_id2,
        )
        try:
            (
                crosslinker_length,
                accepted_deviation_upper_bound,
                accepted_deviation_lower_bound,
            ) = crosslinker_information[crosslink.Crosslinker]
        except KeyError:
            raise KeyError(
                f"Missing required information regarding crosslinker length "
                f"and/or accepted deviation for crosslinker '{crosslink.Crosslinker}'."
            )

        accepted_distance_lower_bound: float = 0.0
        accepted_distance_upper_bound: float = 0.0

        match validation_criterion:
            case CrosslinkingValidationCriterion.manual_bounds.value:
                # Fallback to default deviation bounds when not explicitly provided
                accepted_distance_lower_bound = crosslinker_length - (
                    accepted_deviation_lower_bound or crosslinker_length
                )
                accepted_distance_upper_bound = (
                    accepted_deviation_upper_bound or float("inf")
                ) + crosslinker_length

            case CrosslinkingValidationCriterion.max_pae.value:
                if np.isnan(pae_x_position1) or np.isnan(pae_x_position2):
                    raise ValueError("No PAE data given.")

                pae_tolerance = max(pae_x_position1, pae_x_position2)
                accepted_distance_lower_bound = float(
                    max(crosslinker_length - pae_tolerance, 0.0)
                )
                accepted_distance_upper_bound = float(
                    crosslinker_length + pae_tolerance
                )

            case CrosslinkingValidationCriterion.min_pae.value:
                if np.isnan(pae_x_position1) or np.isnan(pae_x_position2):
                    raise ValueError("No PAE data given.")
                pae_x_position1, pae_x_position2 = get_paes()
                pae_tolerance = min(pae_x_position1, pae_x_position2)
                accepted_distance_lower_bound = float(
                    max(crosslinker_length - pae_tolerance, 0.0)
                )
                accepted_distance_upper_bound = float(
                    crosslinker_length + pae_tolerance
                )

            case CrosslinkingValidationCriterion.plddt_adjusted.value:
                if np.isnan(plddt_at_position1) or np.isnan(plddt_at_position2):
                    raise ValueError("No pLDDT data given.")

                get_plddt_factor: Callable[[float], float] = lambda plddt: 1 - (
                    plddt / 100
                )

                plddt_factor_pos1 = get_plddt_factor(plddt_at_position1)
                plddt_factor_pos2 = get_plddt_factor(plddt_at_position2)

                max_half_tolerance = crosslinker_length  # Note: This is quite lenient
                tolerance_pos1 = plddt_factor_pos1 * max_half_tolerance
                tolerance_pos2 = plddt_factor_pos2 * max_half_tolerance

                accepted_distance_lower_bound = max(
                    crosslinker_length - tolerance_pos1 - tolerance_pos2, 0
                )
                accepted_distance_upper_bound = (
                    crosslinker_length + tolerance_pos1 + tolerance_pos2
                )

            case _:
                raise ValueError("Invalid validation strategy")

        valid = (
            accepted_distance_lower_bound
            <= predicted_distance
            <= accepted_distance_upper_bound
        )

        return pd.Series(
            {
                "alphafold_distance": predicted_distance,
                "valid_crosslink": valid,
                "crosslinker_position1": crosslink.crosslinker_position1,
                "crosslinker_position2": crosslink.crosslinker_position2,
                "plddt_at_position1": plddt_at_position1,
                "plddt_at_position2": plddt_at_position2,
                "pae_x_position1": pae_x_position1,
                "pae_x_position2": pae_x_position2,
            }
        )

    # adding the distance in alphafold, the result of the validation and the crosslinker positions to all relevant crosslinks
    new_columns = [
        "alphafold_distance",
        "valid_crosslink",
        "crosslinker_position1",
        "crosslinker_position2",
        "plddt_at_position1",
        "plddt_at_position2",
        "pae_x_position1",
        "pae_x_position2",
    ]

    relevant_crosslinks_df["crosslinker_position1"] = relevant_crosslinks_df[
        "crosslinker_position1"
    ].astype("Int64")
    relevant_crosslinks_df["crosslinker_position2"] = relevant_crosslinks_df[
        "crosslinker_position2"
    ].astype("Int64")

    relevant_crosslinks_df[new_columns] = relevant_crosslinks_df.apply(
        check_crosslink, axis=1
    )

    # removing all crosslinks that weren't checked from the df
    checked_crosslinks_df = relevant_crosslinks_df[
        relevant_crosslinks_df["valid_crosslink"].notna()
    ]

    checked_crosslinks_df["link_type"] = checked_crosslinks_df.apply(
        lambda row: "intra" if row["Chain_id1"] == row["Chain_id2"] else "inter",
        axis=1,
    )

    structure_entry_id = _get_structure_entry_id(structure_metadata_df)
    data_for_visualization = {
        "structure_entry_id": structure_entry_id,
        "cif_df": cif_df,
        "crosslinking_df": checked_crosslinks_df,
    }

    return dict(
        crosslinking_result_df=checked_crosslinks_df,
        messages=messages,
        visualization=OutputItem(
            output_type=OutputType.VISUALIZATION, value=data_for_visualization
        ),
    )


def diagrams_of_crosslinking_validation_data(
    validated_df: pd.DataFrame,
    structures_to_validate: str,
    crosslinker_information: pd.DataFrame,
) -> list[Figure]:
    """
    Creates for each crosslinker histogram plots summarizing the distribution of valid and invalid
    crosslinks based on the (AlphaFold-)predicted distances compared to crosslinker lengths and
    allowed deviations.

    For each crosslinker, two histograms are generated:
    - One covering the full distance range.
    - One restricted to the range of mean ± 2 standard deviations of the predicted distances.

    Both histograms include vertical reference lines indicating the
    crosslinker length and, if applicable, the upper and/or lower accepted deviation bounds.

    Additionally, a bar plot is created summarizing the total number of crosslinks that match
    or do not match the predicted structure across all analyzed crosslinkers.

    :param crosslinking_df: DataFrame containing crosslinking data, including AlphaFold-predicted
                            distances, crosslinker identifiers, and validation results.
    :param structure_metadata_df: Dataframe containing metadata.
    :param crosslinker_information: Contains for each Crosslinker:
                   - length_of_<Crosslinker>: float
                   - lower_accepted_deviation_for_<Crosslinker>: float
                   - upper_accepted_deviation_for_<Crosslinker>: float
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :param amino_acid_sequences_df: DataFrame containing the protein sequence
    :return: List of Plotly Figure objects. For each crosslinker, the list contains two histogram
             figures (mean ± 2 standard deviations first, full range second), followed by a final
             bar plot summarizing valid and invalid crosslinks across all crosslinkers.
    :raises KeyError: If a required crosslinker entry is missing in crosslinker_information.
    """
    if validated_df.empty:
        return {}
    validated_df = validated_df.dropna(subset=["valid_crosslink"])

    figures = []

    structures_to_validate_str = ", ".join(structures_to_validate)

    for crosslinker, crosslinker_df in validated_df.groupby("Crosslinker"):
        distances_valid = crosslinker_df.loc[
            crosslinker_df["valid_crosslink"] == True, "alphafold_distance"
        ]
        distances_invalid = crosslinker_df.loc[
            crosslinker_df["valid_crosslink"] == False, "alphafold_distance"
        ]
        df_valid = pd.DataFrame({"alphafold_distance": distances_valid})
        df_invalid = pd.DataFrame({"alphafold_distance": distances_invalid})

        # Count intra/inter for valid and invalid crosslinks
        valid_mask = crosslinker_df["valid_crosslink"]
        invalid_mask = ~crosslinker_df["valid_crosslink"]
        valid_intra = ((valid_mask) & (crosslinker_df["link_type"] == "intra")).sum()
        valid_inter = ((valid_mask) & (crosslinker_df["link_type"] == "inter")).sum()
        invalid_intra = (
            (invalid_mask) & (crosslinker_df["link_type"] == "intra")
        ).sum()
        invalid_inter = (
            (invalid_mask) & (crosslinker_df["link_type"] == "inter")
        ).sum()

        (
            crosslinker_length,
            accepted_deviation_upper_bound,
            accepted_deviation_lower_bound,
        ) = crosslinker_information[crosslinker]
        histogram = create_histograms(
            dataframe_a=df_valid,
            dataframe_b=df_invalid,
            name_a=f"Valid Crosslinks (intra: {valid_intra}, inter: {valid_inter})",
            name_b=f"Invalid Crosslinks (intra: {invalid_intra}, inter: {invalid_inter})",
            heading=f"Predicted distances for {structures_to_validate_str} with crosslinker {crosslinker}",
            x_title="Distance (Å)",
            y_title="Count",
            overlay=True,
            visual_transformation="linear",
            relevant_column_a="alphafold_distance",
            relevant_column_b="alphafold_distance",
            one_bin_per_int=True,
        )
        add_vertical_line_with_annotation_in_legend(
            fig=histogram,
            dash="solid",
            annotation=f"{crosslinker} length",
            x_value=crosslinker_length,
        )

        mean_of_predicted_lengths = crosslinker_df["alphafold_distance"].mean()
        if len(crosslinker_df) == 1:
            standard_deviation_predicted_lengths = 0.0
        else:
            standard_deviation_predicted_lengths = crosslinker_df[
                "alphafold_distance"
            ].std()
        mean_plus_two_std = (
            mean_of_predicted_lengths + 2 * standard_deviation_predicted_lengths
        )
        mean_minus_two_std = max(
            0, mean_of_predicted_lengths - 2 * standard_deviation_predicted_lengths
        )

        histogram_two_standard_deviations = create_histograms(
            dataframe_a=df_valid,
            dataframe_b=df_invalid,
            name_a=f"Valid Crosslinks (intra: {valid_intra}, inter: {valid_inter})",
            name_b=f"Invalid Crosslinks (intra: {invalid_intra}, inter: {invalid_inter})",
            heading=f"Predicted distances for {structures_to_validate_str} with crosslinker {crosslinker}, mean +/- 2 σ",
            x_title="Distance (Å)",
            y_title="Count",
            overlay=True,
            visual_transformation="linear",
            relevant_column_a="alphafold_distance",
            relevant_column_b="alphafold_distance",
            min_value=mean_minus_two_std,
            max_value=mean_plus_two_std,
            one_bin_per_int=True,
        )
        add_vertical_line_with_annotation_in_legend(
            fig=histogram_two_standard_deviations,
            dash="solid",
            annotation=f"{crosslinker} length",
            x_value=crosslinker_length,
        )

        if accepted_deviation_upper_bound != 0:
            add_vertical_line_with_annotation_in_legend(
                fig=histogram,
                dash="dash",
                annotation=f"allowed deviation upper bound",
                x_value=crosslinker_length + accepted_deviation_upper_bound,
            )
            if (
                math.floor(mean_minus_two_std)
                <= crosslinker_length + accepted_deviation_upper_bound
                <= math.ceil(mean_plus_two_std)
            ):
                add_vertical_line_with_annotation_in_legend(
                    fig=histogram_two_standard_deviations,
                    dash="dash",
                    annotation=f"allowed deviation upper bound",
                    x_value=crosslinker_length + accepted_deviation_upper_bound,
                )
        if accepted_deviation_lower_bound != 0:
            add_vertical_line_with_annotation_in_legend(
                fig=histogram,
                dash="dash",
                annotation=f"allowed deviation lower bound",
                x_value=crosslinker_length - accepted_deviation_lower_bound,
            )
            if (
                math.floor(mean_minus_two_std)
                <= crosslinker_length - accepted_deviation_lower_bound
                <= math.ceil(mean_plus_two_std)
            ):
                add_vertical_line_with_annotation_in_legend(
                    fig=histogram_two_standard_deviations,
                    dash="dash",
                    annotation=f"allowed deviation lower bound",
                    x_value=crosslinker_length - accepted_deviation_lower_bound,
                )

        figures.append(histogram_two_standard_deviations)
        figures.append(histogram)

    valid_crosslinks = (validated_df["valid_crosslink"]).sum()
    invalid_crosslinks = (~validated_df["valid_crosslink"]).sum()
    valid_intra_total = (
        (validated_df["valid_crosslink"]) & (validated_df["link_type"] == "intra")
    ).sum()
    valid_inter_total = (
        (validated_df["valid_crosslink"]) & (validated_df["link_type"] == "inter")
    ).sum()
    invalid_intra_total = (
        (~validated_df["valid_crosslink"]) & (validated_df["link_type"] == "intra")
    ).sum()
    invalid_inter_total = (
        (~validated_df["valid_crosslink"]) & (validated_df["link_type"] == "inter")
    ).sum()

    bar_plot_over_all_checked_crosslinks = create_bar_plot(
        values_of_sectors=[
            valid_crosslinks,
            invalid_crosslinks,
        ],
        names_of_sectors=[
            f"Crosslinks matching predicted data (intra: {valid_intra_total}, inter: {valid_inter_total})",
            f"Crosslinks not matching predicted data (intra: {invalid_intra_total}, inter: {invalid_inter_total})",
        ],
        heading=f"All Crosslinks used for validation of {structures_to_validate_str}",
        y_title="Number of Crosslinks",
    )
    figures.append(bar_plot_over_all_checked_crosslinks)

    return figures


def monomer_diagrams(
    output_crosslinking_result_df: pd.DataFrame,
    structure_metadata_df: pd.DataFrame,
    crosslinker_information: dict[str, list[float]],
    validation_criterion: CrosslinkingValidationCriterion
) -> list[Figure]:
    """
    Generates visual diagrams to evaluate crosslinking validation results
    for a monomeric protein structure.

    :param output_crosslinking_result_df: DataFrame containing the CL validation results.
    :param structure_metadata_df: DataFrame containing structural metadata; the
                                  first row's 'uniprot_accession' is used as the target.
    :param crosslinker_information: Dictionary mapping crosslinker names to a list of
                                    three floats: [length, upper_bound, lower_bound].
    :return: A list of Figure objects visualizing the crosslinking validation data.
    """
    structures_to_validate = [structure_metadata_df["uniprot_accession"].iloc[0]]

    match validation_criterion:
        case CrosslinkingValidationCriterion.manual_bounds.value:
            return diagrams_of_crosslinking_validation_data(
                validated_df=output_crosslinking_result_df,
                structures_to_validate=structures_to_validate,
                crosslinker_information=crosslinker_information,
            )

        # TODO: Separate Issue #429
        case CrosslinkingValidationCriterion.max_pae.value | CrosslinkingValidationCriterion.min_pae.value:
            return diagrams_of_crosslinking_validation_data(
                validated_df=output_crosslinking_result_df,
                structures_to_validate=structures_to_validate,
                crosslinker_information=crosslinker_information,
            )

        # TODO: Separate Issue #429
        case CrosslinkingValidationCriterion.plddt_adjusted.value:
            return diagrams_of_crosslinking_validation_data(
                validated_df=output_crosslinking_result_df,
                structures_to_validate=structures_to_validate,
                crosslinker_information=crosslinker_information,
            )

        case _:
            return []


def multimer_diagrams(
    crosslinking_df: pd.DataFrame,
    structure_metadata_df: pd.DataFrame,
    crosslinker_information: dict[str, list[float]],
    cif_df: pd.DataFrame,
    amino_acid_sequences_df: pd.DataFrame,
    job_request_df: pd.DataFrame,
) -> list[Figure]:
    """
    Generates visual diagrams to evaluate crosslinking validation results
    for a multimeric protein complex.

    This function parses an AlphaFold job request to determine the valid chain
    compositions. It then runs `multimer_validation` to filter and validate
    the relevant crosslinks, extracting the result to generate structural
    distance and validation plots.

    :param crosslinking_df: DataFrame containing the full set of crosslinks.
    :param structure_metadata_df: DataFrame containing structural metadata.
    :param crosslinker_information: Dictionary mapping crosslinker names to a list of
                                    three floats: [length, upper_bound, lower_bound].
    :param cif_df: DataFrame containing parsed mmCIF structural coordinate data.
    :param amino_acid_sequences_df: DataFrame containing known amino acid sequences.
    :param job_request_df: DataFrame containing the loaded AlphaFold job request JSON.
    :return: A list of Figure objects visualizing the crosslinking validation data.
    """
    valid_ids = get_valid_ids_per_protein_id_from_job_request(
        amino_acid_sequences_df=amino_acid_sequences_df, job_request_df=job_request_df
    )
    structures_to_validate = list(valid_ids.keys())

    validated_df = multimer_validation(
        crosslinking_df,
        structure_metadata_df,
        crosslinker_information,
        cif_df,
        amino_acid_sequences_df,
        job_request_df,
    )["crosslinking_result_df"]

    return diagrams_of_crosslinking_validation_data(
        validated_df=validated_df,
        structures_to_validate=structures_to_validate,
        crosslinker_information=crosslinker_information,
    )
