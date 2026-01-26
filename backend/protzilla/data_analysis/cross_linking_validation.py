import pandas as pd
import math
from plotly.graph_objects import Figure

from protzilla.importing.alphafold_protein_structure_load import (
    fetch_alphafold_protein_structure,
)
from protzilla.data_preprocessing.plots import create_bar_plot


def get_coordinates_of_ca_atom_from_cif_df(
    cif_df: pd.DataFrame, amino_acid_position: int
) -> tuple[float, float, float]:
    """
    Extract the 3D coordinates of the C-alpha (CA) atom for a given amino acid
    position from CIF-derived DataFrame.

    :param cif_df: DataFrame containing atomic data parsed from a CIF file. Must include the columns
           "_atom_site.label_atom_id", "_atom_site.label_seq_id",
           "_atom_site.Cartn_x", "_atom_site.Cartn_y", and "_atom_site.Cartn_z".
    :param amino_acid_position: The sequence position of the amino acid whose C-alpha (CA) atom
                                coordinates should be extracted.
    :return: A tuple (x, y, z) of floats representing the Cartesian coordinates of the C-alpha atom.
    :raises ValueError: If no C-alpha atom is found for the given amino acid position.
    """
    cif_df = cif_df[cif_df["_atom_site.label_atom_id"] == "CA"]

    cif_df = cif_df[
        cif_df["_atom_site.label_seq_id"].astype(int) == amino_acid_position
    ]

    if cif_df.empty:
        raise ValueError(
            f"No central Ca atom found for amino acid at position {amino_acid_position}."
        )

    row = cif_df.iloc[0]

    x = float(row["_atom_site.Cartn_x"])
    y = float(row["_atom_site.Cartn_y"])
    z = float(row["_atom_site.Cartn_z"])

    return x, y, z


def get_distance_between_two_amino_acids_in_angstrom(
    position1: int, position2: int, cif_df: pd.DataFrame
) -> float:
    x1, y1, z1 = get_coordinates_of_ca_atom_from_cif_df(cif_df, position1)
    x2, y2, z2 = get_coordinates_of_ca_atom_from_cif_df(cif_df, position2)

    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    return distance


def get_position_of_amino_acid_crosslinker_bound_to(
    protein_sequence: str,
    peptide_sequence: str,
    crosslinker_position_within_peptide: int,
) -> int:
    """Returns which amino acid the cross-linker bound to, 1-based."""
    peptide_start_position = protein_sequence.find(peptide_sequence) + 1
    if peptide_start_position == 0:
        raise ValueError(
            f"Peptide {peptide_sequence} was not found in protein sequence"
        )
    return peptide_start_position + crosslinker_position_within_peptide - 1


def get_distance_between_crosslinker_connected_amino_acids_in_alphafold(
    fasta_df: pd.DataFrame, cif_df: pd.DataFrame, crosslink
) -> float:
    amino_acid_crosslinker1_is_bound_to = (
        get_position_of_amino_acid_crosslinker_bound_to(
            protein_sequence=fasta_df.at[0, "Protein Sequence"],
            peptide_sequence=crosslink.Peptide1,
            crosslinker_position_within_peptide=crosslink.CL_position1,
        )
    )
    amino_acid_crosslinker2_is_bound_to = (
        get_position_of_amino_acid_crosslinker_bound_to(
            protein_sequence=fasta_df.at[0, "Protein Sequence"],
            peptide_sequence=crosslink.Peptide2,
            crosslinker_position_within_peptide=crosslink.CL_position2,
        )
    )
    distance_in_alphafold = get_distance_between_two_amino_acids_in_angstrom(
        amino_acid_crosslinker1_is_bound_to,
        amino_acid_crosslinker2_is_bound_to,
        cif_df,
    )
    return distance_in_alphafold


def validate_with_angstrom_deviation(
    crosslinking_df: pd.DataFrame,
    protein_to_validate: str,
    crosslinker_information: dict[str, list[float]],
) -> dict:
    """
    Validates cross-links by comparing the cross-linker
    lengths with the distances between the linked amino acids in the AlphaFold
    protein structure. A cross-link is regarded as valid if the distance between the connected amino acids in AlphaFold
    is less than the cross-linker length + the allowed deviation.

    :param crosslinking_df: DataFrame containing cross-linking data.
    :param protein_to_validate: UniProt ID of the protein to validate.
    :param crosslinker_information: Contains for each Crosslinker:
                   - length_of_<Crosslinker>: float
                   - accepted_deviation_for_<Crosslinker>: float
    :return: Tuple (valid_cross_links, invalid_cross_links), counts of cross-links that
             pass or fail the distance validation.
    :raises KeyError: If a required crosslinker field is missing in crosslinker_information.
    :raises ValueError: If peptide sequences cannot be matched to the protein sequence.
    """
    alphafold_data = fetch_alphafold_protein_structure(
        uniprot_id=protein_to_validate, persist_uploads=False
    )
    cif_df = alphafold_data["cif_df"]
    fasta_df = alphafold_data["sequence_df"]
    df = crosslinking_df.copy()  # TODO: really necessary?

    mask = (df.Protein_id1 == protein_to_validate) & (
        df.Protein_id2 == protein_to_validate
    )
    relevant_crosslinks_df = df[mask]

    def check_crosslink(crosslink):
        distance = get_distance_between_crosslinker_connected_amino_acids_in_alphafold(
            fasta_df, cif_df, crosslink
        )
        try:
            crosslinker_length, accepted_deviation = crosslinker_information[
                crosslink.Crosslinker
            ]
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(
                f"Missing required field '{missing_key}' for crosslinker '{crosslink.Crosslinker}'."
            )
        return distance <= (crosslinker_length + accepted_deviation)

    df.loc[mask, "valid_crosslink"] = relevant_crosslinks_df.apply(
        check_crosslink, axis=1
    )

    return dict(crosslinking_df_result=df, messages={})


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
                   - accepted_deviation_for_<Crosslinker>: float
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
