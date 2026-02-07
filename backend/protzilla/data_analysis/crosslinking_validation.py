import pandas as pd
import numpy as np
import re
import logging
from plotly.graph_objects import Figure

from protzilla.importing.alphafold_protein_structure_load import (
    fetch_alphafold_protein_structure,
)
from protzilla.data_preprocessing.plots import create_bar_plot


def get_reactive_atom_of_amino_acid_residue(amino_acid_type: str) -> str:
    """
    Returns the atom of an amino acid residue that is considered reactive for
    cross-linking. Currently, this always returns the central alpha carbon (CA).

    :param amino_acid_type: code of the amino acid

    :return: the atom identifier of the reactive atom as a string
    """
    # right now we always return the central C atom
    # later we might want to return the reactive atom of the amino acid residue of the specific amino acid kind
    # as soon as we change this, we will need to change the test test_validate_with_angstrom_deviation
    return "CA"


def get_coordinates_of_atom_crosslinker_bound_to(
    amino_acid_position_where_crosslinker_bound: int,
    amino_acid_type: str,
    cif_df: pd.DataFrame,
) -> tuple[float, float, float]:
    """
    Returns the Cartesian coordinates of the atom to which the cross-linker is
    bound for a given amino acid residue in a protein structure.

    :param amino_acid_position_where_crosslinker_bound: 1-based position of the amino acid residue
    :param amino_acid_type: amino acid type at the given position
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :return: a tuple (x, y, z) containing the Cartesian coordinates of the atom in Ångström
    :raises ValueError: if the specified atom cannot be found in the CIF data
    """

    relevant_atom = get_reactive_atom_of_amino_acid_residue(amino_acid_type)

    # Filter to the exact reactive atom of the amino acid residue
    # where the crosslinker is bound (e.g. CA at position 45)
    cif_df = cif_df[
        (cif_df["_atom_site.label_atom_id"] == relevant_atom)
        & (
            cif_df["_atom_site.label_seq_id"].astype(int)
            == amino_acid_position_where_crosslinker_bound
        )
    ]

    if cif_df.empty:
        raise ValueError(
            f"No {relevant_atom} atom found for amino acid at position {amino_acid_position_where_crosslinker_bound}."
        )

    row = cif_df.iloc[0]

    x = float(row["_atom_site.Cartn_x"])
    y = float(row["_atom_site.Cartn_y"])
    z = float(row["_atom_site.Cartn_z"])

    return x, y, z


def get_distance_between_two_amino_acids_in_angstrom(
    amino_acid_position1: int,
    amino_acid_position2: int,
    amino_acid_kind1: str,
    amino_acid_kind2: str,
    cif_df: pd.DataFrame,
) -> float:
    """
    Calculates the Euclidean distance in Ångström between two amino acid residues
    based on the coordinates of their reactive atoms in the AlphaFold/predicted structure.

    :param amino_acid_position1: 1-based position of the first amino acid residue
    :param amino_acid_position2: 1-based position of the second amino acid residue
    :param amino_acid_kind1: amino acid type at the first position
    :param amino_acid_kind2: amino acid type at the second position
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :return: the distance between the two residues in Ångström
    """

    pos1 = np.array(
        get_coordinates_of_atom_crosslinker_bound_to(
            amino_acid_position1, amino_acid_kind1, cif_df
        ),
        dtype=float,
    )

    pos2 = np.array(
        get_coordinates_of_atom_crosslinker_bound_to(
            amino_acid_position2, amino_acid_kind2, cif_df
        ),
        dtype=float,
    )

    return float(np.linalg.norm(pos2 - pos1))


def _add_positions_of_amino_acid_where_crosslinker_bound_to_df(
    crosslinking_df: pd.DataFrame, protein_sequence: str
) -> list[dict]:
    # 0-based
    crosslinking_df["crosslinker_position1"] = pd.Series(
        [pd.NA] * len(crosslinking_df), dtype="Int64"
    )
    crosslinking_df["crosslinker_position2"] = pd.Series(
        [pd.NA] * len(crosslinking_df), dtype="Int64"
    )
    rows_to_duplicate = {}
    rows_to_delete = []
    messages = []
    for idx, crosslinker_row in crosslinking_df.iterrows():
        peptide_sequence1 = crosslinker_row.Peptide1
        peptide_sequence2 = crosslinker_row.Peptide2
        peptide1_positions = [
            m.start() for m in re.finditer(f"(?={peptide_sequence1})", protein_sequence)
        ]
        peptide2_positions = [
            m.start() for m in re.finditer(f"(?={peptide_sequence2})", protein_sequence)
        ]
        all_position_combinations = [
            (
                pos1 + crosslinker_row.CL_position_within_peptide1,
                pos2 + crosslinker_row.CL_position_within_peptide2,
            )
            for pos1 in peptide1_positions
            for pos2 in peptide2_positions
        ]
        if not all_position_combinations:
            msg = f"At least one of the peptide sequences ({peptide_sequence1}, {peptide_sequence2}) of crosslink entry {idx} was not found in the protein sequence. The entry was deleted."
            messages.append(dict(level=logging.WARNING, msg=msg))
            rows_to_delete.append(idx)
            continue
        crosslinking_df.at[idx, "crosslinker_position1"] = all_position_combinations[0][
            0
        ]
        crosslinking_df.loc[idx, "crosslinker_position2"] = all_position_combinations[
            0
        ][1]
        if len(all_position_combinations) > 1:
            rows_to_duplicate[idx] = all_position_combinations[1:]
    if not rows_to_duplicate:
        return messages
    for row_to_duplicate_idx, potential_positions in rows_to_duplicate.items():
        for potential_cl_position1, potential_cl_position2 in potential_positions:
            new_row = crosslinking_df.loc[row_to_duplicate_idx].copy()
            new_row["crosslinker_position1"] = potential_cl_position1
            new_row["crosslinker_position2"] = potential_cl_position2
            crosslinking_df = pd.concat(
                [crosslinking_df, new_row.to_frame().T], ignore_index=True
            )
        messages.append(
            dict(
                level=logging.WARNING,
                msg=f"Row {row_to_duplicate_idx} was duplicated {len(potential_positions)} times due to several matches between peptide sequence and protein sequence.",
            )
        )

    return messages


def validate_with_angstrom_deviation(
    crosslinking_df: pd.DataFrame,
    protein_to_validate: str,
    crosslinker_information: dict[str, list[float]],
) -> dict:
    """
    Validates cross-links by comparing the cross-linker lengths with the distances between the linked
    amino acids in the AlphaFold protein structure. A cross-link is regarded as valid if it matches the AlphaFold data,
    so if the distance between the connected amino acids in AlphaFold is less than (cross-linker length + the upper allowed deviation)
    and more than (cross-linker length - the lower allowed deviation). If one of the bounds is zero only the other bound will be applied.

    :param crosslinking_df: DataFrame containing cross-linking data.
    :param protein_to_validate: UniProt ID of the protein to validate.
    :param crosslinker_information: Contains for each Crosslinker:
                   - length_of_<Crosslinker>: float
                   - lower_accepted_deviation_for_<Crosslinker>: float
                   - upper_accepted_deviation_for_<Crosslinker>: float
    :return: dict (crosslinking_df_result, messages), crosslinking_df_result contains the relevant rows (rows of intra-crosslinks within the
    protein to validate) of crosslinking_df and two more colums containing the distances in AlphaFold and wheter the crosslink matches the
    AlphaFold data or not
    :raises KeyError: If a required crosslinker field is missing in crosslinker_information.
    :raises ValueError: If peptide sequences cannot be matched to the protein sequence.
    """
    alphafold_data = fetch_alphafold_protein_structure(
        uniprot_id=protein_to_validate, persist_uploads=False
    )
    cif_df = alphafold_data["cif_df"]
    protein_sequence = alphafold_data["sequence_df"].at[0, "Protein Sequence"]

    all_crosslinks_df = crosslinking_df.copy()

    # we are only interested in intra-crosslinks of the protein we want to validate
    mask = (all_crosslinks_df.Protein_id1 == protein_to_validate) & (
        all_crosslinks_df.Protein_id2 == protein_to_validate
    )
    relevant_crosslinks_df = all_crosslinks_df[mask].copy()

    messages = _add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        relevant_crosslinks_df, protein_sequence
    )

    def check_crosslink(crosslink: pd.Series) -> pd.Series:
        predicted_distance = get_distance_between_two_amino_acids_in_angstrom(
            amino_acid_position1=crosslink.crosslinker_position1,
            amino_acid_position2=crosslink.crosslinker_position2,
            amino_acid_kind1=protein_sequence[crosslink.crosslinker_position1],
            amino_acid_kind2=protein_sequence[crosslink.crosslinker_position2],
            cif_df=cif_df,
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
        # Fallback to default deviation bounds when not explicitly provided
        accepted_distance_lower_bound = crosslinker_length - (
            accepted_deviation_lower_bound or crosslinker_length
        )
        accepted_distance_upper_bound = (
            accepted_deviation_upper_bound or float("inf")
        ) + crosslinker_length

        valid = (
            accepted_distance_lower_bound
            <= predicted_distance
            <= accepted_distance_upper_bound
        )

        return pd.Series(
            {"alphafold_distance": predicted_distance, "valid_crosslink": valid}
        )

    # adding the distance in alphafold and the result of the validation to all relevant crosslinks
    all_crosslinks_df.loc[mask, ["alphafold_distance", "valid_crosslink"]] = (
        relevant_crosslinks_df.apply(check_crosslink, axis=1)
    )

    # removing all crosslinks that weren't checked from the df
    checked_crosslinks_df = all_crosslinks_df[
        all_crosslinks_df["valid_crosslink"].notna()
    ]

    return dict(crosslinking_result_df=checked_crosslinks_df, messages=messages)


def bar_plot_of_valid_crosslinks(
    crosslinking_df: pd.DataFrame,
    protein_to_validate: str,
    crosslinker_information: dict[str, list[float]],
) -> list[Figure]:
    """
    Creates a bar plot summarizing the number of valid and invalid cross-links
    based on their distances in the AlphaFold structure compared to cross-linker
    lengths and allowed deviations.

    :param crosslinking_df: DataFrame containing cross-linking data.
    :param protein_to_validate: UniProt ID of the protein to validate.
    :param crosslinker_information: Contains for each Crosslinker:
                   - length_of_<Crosslinker>: float
                   - lower_accepted_deviation_for_<Crosslinker>: float
                   - upper_accepted_deviation_for_<Crosslinker>: float
    :return: List containing a single bar plot object representing counts of
             valid and invalid cross-links.
    :raises KeyError: If a required crosslinker field is missing in crosslinker_information.
    """
    validated_df = validate_with_angstrom_deviation(
        crosslinking_df, protein_to_validate, crosslinker_information
    )["crosslinking_result_df"]

    evaluated = validated_df["valid_crosslink"].dropna()

    valid_crosslinks = (evaluated == True).sum()
    invalid_crosslinks = (evaluated == False).sum()

    return [
        create_bar_plot(
            values_of_sectors=[
                valid_crosslinks,
                invalid_crosslinks,
            ],
            names_of_sectors=["Valid Cross-Links", "Invalid Cross-Links"],
            heading="Cross-Links used for Validation",
            y_title="Number of Cross-Links",
        )
    ]
