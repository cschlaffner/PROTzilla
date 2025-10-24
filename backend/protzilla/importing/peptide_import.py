import logging
from pathlib import Path

import pandas as pd

from backend.protzilla.importing.ms_data_import import clean_protein_groups
from protzilla.importing.import_utils import IntensityType


def peptide_import(file_path: Path, map_to_uniprot) -> dict:
    try:
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"
    except AssertionError as e:
        return dict(
            messages=[dict(level=logging.ERROR, msg=e)],
        )
    peptide_intensity_name = IntensityType.INTENSITY.value

    id_columns = ["Leading razor protein", "Sequence", "Missed cleavages", "PEP"]
    df = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )

    if "Sample" not in df.columns:
        id_df = df[id_columns]
        intensity_df = df.filter(regex=f"^{peptide_intensity_name} ", axis=1)
        intensity_df.columns = [
            c[len(peptide_intensity_name) + 1:] for c in intensity_df.columns
        ]
        molten = pd.melt(
            pd.concat([id_df, intensity_df], axis=1),
            id_vars=id_columns,
            var_name="Sample",
            value_name="Intensity",
        )

    else:
        final_df = df.rename(columns={"Proteins": "Protein ID"})
        ordered = final_df[["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]]

    molten = molten.rename(columns={"Leading razor protein": "Protein ID"})
    ordered = molten[["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]]
    ordered.dropna(subset=["Protein ID"], inplace=True)
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    new_groups, filtered_proteins = clean_protein_groups(
        ordered["Protein ID"].tolist(), map_to_uniprot
    )
    cleaned = ordered.assign(**{"Protein ID": new_groups})

    return dict(peptide_df=cleaned)


def evidence_import(file_path: Path, map_to_uniprot) -> dict:
    try:
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"
    except AssertionError as e:
        return dict(messages=[dict(level=logging.ERROR, msg=e)])

    id_columns = [
        "Experiment",
        "Leading razor protein",
        "Sequence",
        "Intensity",
        "Modifications",
        "Modified sequence",
        "Missed cleavages",
        "PEP",
        "Raw file",
    ]

    df = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
        usecols=lambda x: x.capitalize() in id_columns
    )

    # Apparently MaxQuant evidence file headers can be capitalized in title case or sentence case
    # TODO: maybe write test for this
    df = df.rename(columns={c: c.capitalize() for c in df.columns})
    df = df.rename(columns={
        "Leading razor protein": "Protein ID",
        "Experiment": "Sample"
    })

    df.dropna(subset=["Protein ID"], inplace=True)
    df.sort_values(
        by=["Sample", "Protein ID", "Sequence", "Modifications"],
        ignore_index=True,
        inplace=True,
    )

    new_groups, filtered_proteins = clean_protein_groups(
        df["Protein ID"].tolist(), map_to_uniprot
    )
    df = df.assign(**{"Protein ID": new_groups})

    return dict(peptide_df=df)
