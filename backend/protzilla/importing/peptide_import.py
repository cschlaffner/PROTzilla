import logging
from pathlib import Path
import re
import traceback

import pandas as pd

from backend.protzilla.importing.ms_data_import import clean_protein_groups
from backend.protzilla.constants.intensity_types import IntensityType
from backend.protzilla.utilities import format_trace


def peptide_import(file_path: Path, intensity_name: str, map_to_uniprot) -> dict:
    messages = []
    try:
        allowed = {item.value for item in IntensityType}
        assert intensity_name in allowed, f"Unknown intensity name: {intensity_name}"
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"

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
            # Ensure required id columns are present
            missing = [c for c in id_columns if c not in df.columns]
            if missing:
                msg = f"Peptide file is missing required columns: {missing}"
                return dict(messages=[dict(level=logging.ERROR, msg=msg)])

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

            if intensity_df.empty:
                msg = (
                    f"{intensity_name} was not found in the provided file, please use another intensity and try again or verify your file."
                )
                return dict(messages=[dict(level=logging.ERROR, msg=msg)])

            intensity_df.columns = [
                c[len(intensity_name) + 1 :] for c in intensity_df.columns
            ]
            tidy_peptide_df = pd.melt(
                pd.concat([id_df, intensity_df], axis=1),
                id_vars=id_columns,
                var_name="Sample",
                value_name="Intensity",
            )

        else:
            if "Proteins" not in df.columns:
                msg = "Peptide file with 'Sample' column requires 'Proteins' column"
                return dict(messages=[dict(level=logging.ERROR, msg=msg)])

            final_df = df.rename(columns={"Proteins": "Protein ID"})
            required = ["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]
            missing = [c for c in required if c not in final_df.columns]
            if missing:
                msg = f"Peptide file is missing required columns: {missing}"
                return dict(messages=[dict(level=logging.ERROR, msg=msg)])

            tidy_peptide_df = final_df[required]

        tidy_peptide_df = tidy_peptide_df.rename(columns={"Leading razor protein": "Protein ID"})
        tidy_peptide_df = tidy_peptide_df[["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]]
        tidy_peptide_df = tidy_peptide_df.dropna(subset=["Protein ID"])
        tidy_peptide_df = tidy_peptide_df.sort_values(
            by=["Sample", "Protein ID"], ignore_index=True
        )

        new_groups, _filtered_proteins = clean_protein_groups(
            tidy_peptide_df["Protein ID"].tolist(), map_to_uniprot
        )
        cleaned = tidy_peptide_df.assign(**{"Protein ID": new_groups})

        msg = (
            f"Successfully imported {cleaned['Protein ID'].nunique()} protein groups "
            f"for {cleaned['Sample'].nunique()} samples."
        )
        messages.append(dict(level=logging.INFO, msg=msg))

        return dict(peptide_df=cleaned, messages=messages)

    except AssertionError as e:
        return dict(messages=[dict(level=logging.ERROR, msg=str(e))])
    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid peptide file."
        return dict(
            messages=[
                dict(level=logging.ERROR, msg=msg, trace=format_trace(traceback.format_exception(e)))
            ]
        )


def evidence_import(file_path: Path, map_to_uniprot) -> dict:
    try:
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"
    except AssertionError as e:
        return dict(messages=[dict(level=logging.ERROR, msg=str(e))])

    id_columns = [
        "Leading razor protein",
        "Sequence",
        "Intensity",
        "Modifications",
        "Modified sequence",
        "Missed cleavages",
        "Experiment",
        "PEP",
        "Raw file",
    ]

    def select_column(column):
        # Check for whitespace in the column name to not capitalize "PEP" which should stay all-caps.
        capitalized_column = column.capitalize() if " " in column else column
        return capitalized_column in id_columns

    df = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
        usecols=select_column,
    )

    # Apparently MaxQuant evidence file headers can be capitalized in title case or sentence case
    # TODO: maybe write test for this. It would probably be safer to convert all columns to lower case but that would
    #  require bigger changes in the code
    df = df.rename(columns={c: c.capitalize() if " " in c else c for c in df.columns})
    df = df.rename(
        columns={"Leading razor protein": "Protein ID", "Experiment": "Sample"}
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
