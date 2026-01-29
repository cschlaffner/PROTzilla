import logging
from pathlib import Path
import re

import pandas as pd

from protzilla.importing.ms_data_import import clean_protein_groups
from protzilla.constants.intensity_types import IntensityType


def peptide_import(file_path: Path, intensity_name: str, map_to_uniprot) -> dict:
    try:
        allowed = {item.value for item in IntensityType}
        assert intensity_name in allowed, f"Unknown intensity name: {intensity_name}"
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"
    except AssertionError as e:
        return dict(
            messages=[dict(level=logging.ERROR, msg=e)],
        )

    # We hardcode the intensity because for peptides we only ever have "Intensity" in the files. "iBAQ" and
    # "LFQ intensity" are only defined for proteins. However, ratios can be used for peptides.
    if (
        intensity_name == IntensityType.LFQ_INTENSITY.value
        or intensity_name == IntensityType.IBAQ.value
    ):
        intensity_name = IntensityType.INTENSITY.value

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
        disallowed_suffixes = r"(variability|count|type|peptides)"
        if intensity_name in (
            IntensityType.RATIO_HL.value,
            IntensityType.RATIO_LH.value,
        ):
            base_pattern = rf"^{re.escape(intensity_name)}\s(?!normalized\b)(?!.*\b{disallowed_suffixes}\b).*$"
        else:
            base_pattern = (
                rf"^{re.escape(intensity_name)}\s(?!.*\b{disallowed_suffixes}\b).*$"
            )

        intensity_df = df.filter(regex=base_pattern, axis=1)
        intensity_df.columns = [
            c[len(intensity_name) + 1 :] for c in intensity_df.columns
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


def evidence_import(file_path: Path, intensity_name: str, map_to_uniprot) -> dict:
    # TODO: add test that checks if Ratio H/L works?
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"Cannot find Peptide File at {file_path}")

    id_columns = [
        "Leading razor protein",
        "Sequence",
        intensity_name,
        "Modifications",
        "Modified sequence",
        "Missed cleavages",
        "Experiment",
        "PEP",
        "Raw file",
    ]

    # Apparently MaxQuant evidence file headers can be capitalized in title case or sentence case so we have to find
    # a way around it by using the select_column function. However, it's not as straightforward as just capitalizing,
    # so we need to define exceptions.
    column_exceptions = {
        "PEP",
        IntensityType.RATIO_HL.value,
        IntensityType.RATIO_LH.value,
        IntensityType.RATIO_HL_NORMALIZED.value,
        IntensityType.RATIO_LH_NORMALIZED.value,
    }

    def select_column(column):
        capitalized_column = (
            column.capitalize()
            if column not in column_exceptions and " " in column
            else column
        )
        return capitalized_column in id_columns

    df = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
        usecols=select_column,
    )
    if intensity_name not in df.columns:
        raise ValueError(
            f"{intensity_name} was not found in the provided file, please use another intensity and try again or "
            f"verify your file."
        )

    # TODO: maybe write test for this. It would probably be safer to convert all columns to lower case but that would
    #  require bigger changes in the code
    #   - maybe use headers of PXD014997_AML_phosphoproteome/txt_LF/peptides.txt and PXD014997_AML_phosphoproteome/txt_LF/evidence_full.txt
    df = df.rename(
        columns={
            c: c.capitalize() if c not in column_exceptions and " " in c else c
            for c in df.columns
        }
    )
    df = df.rename(
        columns={
            "Leading razor protein": "Protein ID",
            "Experiment": "Sample",
            intensity_name: "Intensity",
        }
    )

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
