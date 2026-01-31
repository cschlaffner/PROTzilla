import pandas as pd
import math
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
    x1, y1, z1 = get_coordinates_of_atom_crosslinker_bound_to(
        amino_acid_position1, amino_acid_kind1, cif_df
    )
    x2, y2, z2 = get_coordinates_of_atom_crosslinker_bound_to(
        amino_acid_position2, amino_acid_kind2, cif_df
    )

    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    return distance


def get_position_of_amino_acid_crosslinker_bound_to(
    protein_sequence: str,
    peptide_sequence: str,
    crosslinker_position_within_peptide: int,
) -> int:
    """
    Determines the position of the amino acid to which the cross-linker bound.

    :param protein_sequence: full protein amino acid sequence
    :param peptide_sequence: peptide sequence containing the amino acid the cross-linker bound to
    :param crosslinker_position_within_peptide: 1-based position of the cross-linker within the peptide
    :return: 1-based position of the amino acid residue in the protein sequence
    :raises ValueError: if the peptide sequence cannot be found in the protein sequence
    """
    peptide_start_position = protein_sequence.find(peptide_sequence)
    if peptide_start_position == -1:
        raise ValueError(
            f"Peptide {peptide_sequence} was not found in protein sequence"
        )
    return peptide_start_position + crosslinker_position_within_peptide


def get_distance_between_crosslinker_connected_amino_acids_in_alphafold(
    fasta_df: pd.DataFrame, cif_df: pd.DataFrame, crosslink: pd.Series
) -> float:
    """
    Calculates the distance in Ångström between two amino acid residues connected
    by a cross-linker using a predicted protein structure (e.g. from AlphaFold).

    :param fasta_df: DataFrame containing the protein sequence
    :param cif_df: DataFrame containing CIF information (predicted coordinates of all the protein's atoms)
    :param crosslink: Series describing a cross-link, including cross-linker positions
    :return: the distance between the cross-linked amino acids in Ångström
    """
    protein_sequence = fasta_df.at[0, "Protein Sequence"]
    amino_acid_position_crosslinker1_is_bound_to = (
        get_position_of_amino_acid_crosslinker_bound_to(
            protein_sequence=protein_sequence,
            peptide_sequence=crosslink.Peptide1,
            crosslinker_position_within_peptide=crosslink.CL_position1,
        )
    )
    amino_acid_position_crosslinker2_is_bound_to = (
        get_position_of_amino_acid_crosslinker_bound_to(
            protein_sequence=protein_sequence,
            peptide_sequence=crosslink.Peptide2,
            crosslinker_position_within_peptide=crosslink.CL_position2,
        )
    )
    distance_in_alphafold = get_distance_between_two_amino_acids_in_angstrom(
        amino_acid_position_crosslinker1_is_bound_to,
        amino_acid_position_crosslinker2_is_bound_to,
        protein_sequence[amino_acid_position_crosslinker1_is_bound_to - 1],
        protein_sequence[amino_acid_position_crosslinker2_is_bound_to - 1],
        cif_df,
    )
    return distance_in_alphafold


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
    fasta_df = alphafold_data["sequence_df"]

    all_crosslinks_df = crosslinking_df.copy()

    # we are only interested in intra-crosslinks of the protein we want to validate
    mask = (all_crosslinks_df.Protein_id1 == protein_to_validate) & (
        all_crosslinks_df.Protein_id2 == protein_to_validate
    )
    relevant_crosslinks_df = all_crosslinks_df[mask].copy()

    def check_crosslink(crosslink: pd.Series) -> pd.Series:
        distance = get_distance_between_crosslinker_connected_amino_acids_in_alphafold(
            fasta_df, cif_df, crosslink
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
            accepted_deviation_upper_bound or 1e9
        ) + crosslinker_length

        valid = (
            accepted_distance_lower_bound <= distance <= accepted_distance_upper_bound
        )

        return pd.Series({"alphafold_distance": distance, "valid_crosslink": valid})

    # adding the distance in alphafold and the result of the validation to all relevant crosslinks
    all_crosslinks_df.loc[mask, ["alphafold_distance", "valid_crosslink"]] = (
        relevant_crosslinks_df.apply(check_crosslink, axis=1)
    )

    # removing all crosslinks that weren't checked from the df
    checked_crosslinks_df = all_crosslinks_df[
        all_crosslinks_df["valid_crosslink"].notna()
    ]

    return dict(crosslinking_result_df=checked_crosslinks_df, messages={})


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
    )["crosslinking_df_result"]

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
