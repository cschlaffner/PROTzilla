import itertools

import math

import pandas as pd
import numpy as np
import re
import logging

from plotly.graph_objects import Figure

from backend.protzilla.data_preprocessing.plots import (
    create_histograms,
    create_bar_plot,
)
from protzilla.data_analysis.plots import add_vertical_line_with_annotation_in_legend


def get_reactive_atom_of_amino_acid_residue(amino_acid_type: str) -> str:
    """
    Returns the atom of an amino acid residue that is considered reactive for
    cross-linking. Currently, this always returns the central alpha carbon (CA).

    :param amino_acid_type: code of the amino acid

    :return: the atom identifier of the reactive atom as a string
    """
    # right now we always return the central C atom
    # later we might want to return the reactive atom of the amino acid residue of the specific amino acid type
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
    amino_acid_type1: str,
    amino_acid_type2: str,
    cif_df: pd.DataFrame,
) -> float:
    """
    Calculates the Euclidean distance in Ångström between two amino acid residues
    based on the coordinates of their reactive atoms in the AlphaFold/predicted structure.

    :param amino_acid_position1: 1-based position of the first amino acid residue
    :param amino_acid_position2: 1-based position of the second amino acid residue
    :param amino_acid_type1: amino acid type at the first position
    :param amino_acid_type2: amino acid type at the second position
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :return: the distance between the two residues in Ångström
    """

    pos1 = np.array(
        get_coordinates_of_atom_crosslinker_bound_to(
            amino_acid_position1, amino_acid_type1, cif_df
        ),
        dtype=float,
    )

    pos2 = np.array(
        get_coordinates_of_atom_crosslinker_bound_to(
            amino_acid_position2, amino_acid_type2, cif_df
        ),
        dtype=float,
    )

    return float(np.linalg.norm(pos2 - pos1))


def add_positions_of_amino_acid_where_crosslinker_bound_to_df(
    input_crosslinking_df: pd.DataFrame, protein_sequence: str
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Adds for each crosslink the 1-based positions of amino acids where the crosslink bound to a crosslinking DataFrame.
    If a peptide sequence occurs multiple times in the protein, the row is duplicated for each
    additional combination of positions.
    If a peptide sequence can't be matched the row will be deleted and a warning emitted.

    :param input_crosslinking_df: DataFrame containing cross-linking data with at least the following columns:
                           - 'Peptide1': first peptide sequence
                           - 'Peptide2': second peptide sequence
                           - 'CL_position_within_peptide1': 0-based crosslinker position within Peptide1
                           - 'CL_position_within_peptide2': 0-based crosslinker position within Peptide2
    :param protein_sequence: Full protein sequence in which the peptides are located.
    :return: tuple (updated_crosslinking_df, messages)
             - updated_crosslinking_df: input DataFrame with two new columns:
                 - 'crosslinker_position1': 1-based crosslinker position in Peptide1
                 - 'crosslinker_position2': 1-based crosslinker position in Peptide2
                 Rows are duplicated for multiple peptide matches.
             - messages: list of warning dictionaries with if the peptide was not found or a row was duplicated
    """
    crosslinking_df = input_crosslinking_df.copy()
    crosslinking_df["crosslinker_position1"] = pd.Series(dtype="Int64")
    crosslinking_df["crosslinker_position2"] = pd.Series(dtype="Int64")
    rows_to_duplicate = {}
    rows_to_delete = []
    messages = []
    for idx, crosslinker_row in crosslinking_df.iterrows():
        peptide_sequence1 = crosslinker_row.Peptide1
        peptide_sequence2 = crosslinker_row.Peptide2
        peptide1_positions = [
            m.start() + crosslinker_row.CL_position_within_peptide1 + 1
            for m in re.finditer(f"(?={peptide_sequence1})", protein_sequence)
        ]
        peptide2_positions = [
            m.start() + crosslinker_row.CL_position_within_peptide2 + 1
            for m in re.finditer(f"(?={peptide_sequence2})", protein_sequence)
        ]
        all_position_combinations = list(
            itertools.product(peptide1_positions, peptide2_positions)
        )
        if not all_position_combinations:
            if not peptide1_positions and not peptide2_positions:
                msg = f"Peptide sequences {peptide_sequence1} and {peptide_sequence2} of crosslink entry {idx} were not found in the protein sequence. The entry was deleted."
            else:
                msg = f"Peptide sequence {peptide_sequence1 if not peptide1_positions else peptide_sequence2} of crosslink entry {idx} was not found in the protein sequence. The entry was deleted."
            messages.append(dict(level=logging.WARNING, msg=msg))
            rows_to_delete.append(idx)
            continue
        crosslinking_df.at[idx, "crosslinker_position1"] = all_position_combinations[0][
            0
        ]
        crosslinking_df.at[idx, "crosslinker_position2"] = all_position_combinations[0][
            1
        ]
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


def validate_with_angstrom_deviation(
    crosslinking_df: pd.DataFrame,
    protein_to_validate: str,
    crosslinker_information: dict[str, list[float]],
    cif_df: pd.DataFrame,
    amino_acid_sequence_df: pd.DataFrame,
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
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :param amino_acid_sequence_df: DataFrame containing the protein sequence
    :return: dict (crosslinking_df_result, messages), crosslinking_df_result contains the relevant rows (rows of intra-crosslinks within the
    protein to validate) of crosslinking_df and two more columns containing the distances in AlphaFold and whether the crosslink matches the
    AlphaFold data or not
    :raises KeyError: If a required crosslinker field is missing in crosslinker_information.
    :raises ValueError: If peptide sequences cannot be matched to the protein sequence.
    """
    protein_sequence = amino_acid_sequence_df.at[0, "Protein Sequence"]

    all_crosslinks_df = crosslinking_df.copy()

    # we are only interested in intra-crosslinks of the protein we want to validate
    mask = (all_crosslinks_df.Protein_id1 == protein_to_validate) & (
        all_crosslinks_df.Protein_id2 == protein_to_validate
    )
    relevant_crosslinks_df = all_crosslinks_df[mask].copy()

    relevant_crosslinks_df, messages = (
        add_positions_of_amino_acid_where_crosslinker_bound_to_df(
            relevant_crosslinks_df, protein_sequence
        )
    )

    def check_crosslink(crosslink: pd.Series) -> pd.Series:
        predicted_distance = get_distance_between_two_amino_acids_in_angstrom(
            amino_acid_position1=crosslink.crosslinker_position1,
            amino_acid_position2=crosslink.crosslinker_position2,
            amino_acid_type1=protein_sequence[crosslink.crosslinker_position1 - 1],
            amino_acid_type2=protein_sequence[crosslink.crosslinker_position2 - 1],
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
            {
                "alphafold_distance": predicted_distance,
                "valid_crosslink": valid,
                "crosslinker_position1": crosslink.crosslinker_position1,
                "crosslinker_position2": crosslink.crosslinker_position2,
            }
        )

    # adding the distance in alphafold, the result of the validation and the crosslinker positions to all relevant crosslinks
    new_columns = [
        "alphafold_distance",
        "valid_crosslink",
        "crosslinker_position1",
        "crosslinker_position2",
    ]
    relevant_crosslinks_df[new_columns] = relevant_crosslinks_df.apply(
        check_crosslink, axis=1
    )

    # removing all crosslinks that weren't checked from the df
    checked_crosslinks_df = relevant_crosslinks_df[
        relevant_crosslinks_df["valid_crosslink"].notna()
    ]

    return dict(crosslinking_result_df=checked_crosslinks_df, messages=messages)


def diagrams_of_crosslinking_validation_data(
    crosslinking_df: pd.DataFrame,
    protein_to_validate: str,
    crosslinker_information: dict[str, list[float]],
    cif_df: pd.DataFrame,
    amino_acid_sequence_df: pd.DataFrame,
) -> list[Figure]:
    """
    Creates for each crosslinker histogram plots summarizing the distribution of valid and invalid
    cross-links based on the (AlphaFold-)predicted distances compared to crosslinker lengths and
    allowed deviations.

    For each crosslinker, two histograms are generated:
    - One covering the full distance range.
    - One restricted to the range of mean ± 2 standard deviations of the predicted distances.

    Both histograms include vertical reference lines indicating the
    crosslinker length and, if applicable, the upper and/or lower accepted deviation bounds.

    Additionally, a bar plot is created summarizing the total number of cross-links that match
    or do not match the predicted structure across all analyzed crosslinkers.

    :param crosslinking_df: DataFrame containing cross-linking data, including AlphaFold-predicted
                            distances, crosslinker identifiers, and validation results.
    :param protein_to_validate: UniProt ID of the protein to validate.
    :param crosslinker_information: Contains for each Crosslinker:
                   - length_of_<Crosslinker>: float
                   - lower_accepted_deviation_for_<Crosslinker>: float
                   - upper_accepted_deviation_for_<Crosslinker>: float
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :param amino_acid_sequence_df: DataFrame containing the protein sequence
    :return: List of Plotly Figure objects. For each crosslinker, the list contains two histogram
             figures (mean ± 2 standard deviations first, full range second), followed by a final
             bar plot summarizing valid and invalid cross-links across all crosslinkers.
    :raises KeyError: If a required crosslinker entry is missing in crosslinker_information.
    """
    validated_df = validate_with_angstrom_deviation(
        crosslinking_df,
        protein_to_validate,
        crosslinker_information,
        cif_df,
        amino_acid_sequence_df,
    )["crosslinking_result_df"]
    validated_df = validated_df.dropna(subset=["valid_crosslink"])

    figures = []

    for crosslinker, crosslinker_df in validated_df.groupby("Crosslinker"):
        distances_valid = crosslinker_df.loc[
            crosslinker_df["valid_crosslink"] == True, "alphafold_distance"
        ]
        distances_invalid = crosslinker_df.loc[
            crosslinker_df["valid_crosslink"] == False, "alphafold_distance"
        ]
        df_valid = pd.DataFrame({"alphafold_distance": distances_valid})
        df_invalid = pd.DataFrame({"alphafold_distance": distances_invalid})

        (
            crosslinker_length,
            accepted_deviation_upper_bound,
            accepted_deviation_lower_bound,
        ) = crosslinker_information[crosslinker]

        histogram = create_histograms(
            dataframe_a=df_valid,
            dataframe_b=df_invalid,
            name_a="Valid Crosslinks",
            name_b="Invalid Crosslinks",
            heading=f"Predicted distances for {protein_to_validate}",
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

        mean_predicted_lengths = crosslinker_df["alphafold_distance"].mean()
        standard_deviation_predicted_lengths = crosslinker_df[
            "alphafold_distance"
        ].std()
        mean_plus_minus_two_std_range = (
            max(0, mean_predicted_lengths - 2 * standard_deviation_predicted_lengths),
            mean_predicted_lengths + 2 * standard_deviation_predicted_lengths,
        )
        histogram_two_standard_deviations = create_histograms(
            dataframe_a=df_valid,
            dataframe_b=df_invalid,
            name_a="Valid Crosslinks",
            name_b="Invalid Crosslinks",
            heading=f"Predicted distances for {protein_to_validate}, mean +- 2 standard deviations",
            x_title="Distance (Å)",
            y_title="Count",
            overlay=True,
            visual_transformation="linear",
            relevant_column_a="alphafold_distance",
            relevant_column_b="alphafold_distance",
            min_value=mean_plus_minus_two_std_range[0],
            max_value=mean_plus_minus_two_std_range[1],
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
                math.floor(mean_plus_minus_two_std_range[0])
                <= crosslinker_length + accepted_deviation_upper_bound
                <= math.ceil(mean_plus_minus_two_std_range[1])
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
                math.floor(mean_plus_minus_two_std_range[0])
                <= crosslinker_length - accepted_deviation_lower_bound
                <= math.ceil(mean_plus_minus_two_std_range[1])
            ):
                add_vertical_line_with_annotation_in_legend(
                    fig=histogram_two_standard_deviations,
                    dash="dash",
                    annotation=f"allowed deviation lower bound",
                    x_value=crosslinker_length - accepted_deviation_lower_bound,
                )

        figures.append(histogram_two_standard_deviations)
        figures.append(histogram)

    valid_crosslinks = (validated_df["Is_intra_crosslink"] == True).sum()
    invalid_crosslinks = (validated_df["Is_intra_crosslink"] == False).sum()

    bar_plot_over_all_checked_crosslinks = create_bar_plot(
        values_of_sectors=[
            valid_crosslinks,
            invalid_crosslinks,
        ],
        names_of_sectors=[
            "Cross-Links matching predicted data",
            "Cross-Links not matching predicted data",
        ],
        heading=f"All Cross-Links used for validation of {protein_to_validate}",
        y_title="Number of Cross-Links",
    )
    figures.append(bar_plot_over_all_checked_crosslinks)

    return figures
