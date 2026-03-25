import logging

import numpy as np
import pandas as pd
import pytest

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.intensity_types import IntensityType
from backend.protzilla.importing import peptide_import
from backend.tests.paths import TEST_PEPTIDES_PATH


def peptide_df(intensity_name):
    # sample, protein id, sequence, intensity, pep
    peptide_protein_list = (
        ["Sample01", "P46459", "AAQSTAMNR", 0.0013764],
        ["Sample02", "P46459", "AAQSTAMNR", 0.0013764],
        ["Sample03", "P46459", "AAQSTAMNR", 0.0013764],
        ["Sample04", "P46459", "AAQSTAMNR", 0.0013764],
        ["Sample05", "P46459", "AAQSTAMNR", 0.0013764],
        ["Sample01", "Q13748", "EDLAALEK", 0.037779],
        ["Sample02", "Q13748", "EDLAALEK", 0.037779],
        ["Sample03", "Q13748", "EDLAALEK", 0.037779],
        ["Sample04", "Q13748", "EDLAALEK", 0.037779],
        ["Sample05", "Q13748", "EDLAALEK", 0.037779],
    )

    peptide_df = pd.DataFrame(
        data=peptide_protein_list, columns=["Sample", "Protein ID", "Sequence", "PEP"]
    )

    intensity_name_to_intensities = {
        "LFQ intensity": [
            np.nan,
            np.nan,
            253840.0,
            1371200.0,
            3048300.0,
            3957900.0,
            np.nan,
            8533900.0,
            np.nan,
            6923600.0,
        ],
        "Intensity": [
            253840.0,
            1371200.0,
            3048300.0,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            6923600.0,
            np.nan,
            37440000.0,
        ],
        "Ratio H/L normalized": [
            0.65486,
            0.85897,
            0.82652,
            np.nan,
            np.nan,
            0.55418,
            np.nan,
            np.nan,
            np.nan,
            1.626,
        ],
        "Ratio L/H normalized": [
            0.65486,
            0.85897,
            0.82652,
            np.nan,
            np.nan,
            0.55418,
            np.nan,
            np.nan,
            np.nan,
            1.626,
        ],
        "Ratio L/H": [
            0.65486,
            0.85897,
            0.82652,
            np.nan,
            np.nan,
            0.55418,
            np.nan,
            np.nan,
            np.nan,
            1.626,
        ],
        "Ratio H/L": [
            0.65486,
            0.85897,
            0.82652,
            np.nan,
            np.nan,
            0.55418,
            np.nan,
            np.nan,
            np.nan,
            1.626,
        ],
    }

    peptide_df["Intensity"] = intensity_name_to_intensities[intensity_name]
    peptide_df = peptide_df[["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]]
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    return peptide_df


def psm_df():
    # sample, protein id, sequence, intensity, pep
    peptide_protein_list = (
        [
            "AD01_C1_INSOLUBLE_02",
            "P36578",
            "AAAAAAALQAK",
            1362600,
            "Unmodified",
            "_AAAAAAALQAK_",
            None,
            0.05224,
            "AD01_BA39-Cohort1_INSOLUBLE_02",
        ],
        [
            "AD06_C1_INSOLUBLE_01",
            "P36578",
            "AAAAAAALQAK",
            5739600,
            "Unmodified",
            "_AAAAAAALQAK_",
            None,
            0.01578,
            "AD06_BA39-Cohort1_INSOLUBLE_01",
        ],
        [
            "CTR17_C2_INSOLUBLE_01",
            "O75822-2",
            "AAAAAAAGDSDSWDADAFSVEDPVRK",
            13249000,
            "Acetyl (Protein N-term)",
            "_(Acetyl (Protein N-term))AAAAAAAGDSDSWDADAFSVEDPVRK_",
            1.00000,
            0.00000,
            "CTR17_BA39-Cohort2_INSOLUBLE_01",
        ],
    )

    peptide_df = pd.DataFrame(
        data=peptide_protein_list,
        columns=[
            "Sample",
            "Protein ID",
            "Sequence",
            "Intensity",
            "Modifications",
            "Modified sequence",
            "Missed cleavages",
            "PEP",
            "Raw file",
        ],
    )

    peptide_df.sort_values(
        by=["Sample", "Protein ID", "Sequence", "Modifications"],
        ignore_index=True,
        inplace=True,
    )

    return peptide_df


def evidence_ratio_df(intensity_name):
    # sample, protein id, sequence, intensity, pep
    peptide_protein_list = (
        [
            "P2",
            "O60341",
            "AAAAAAAAAAAATGTEAGPGTAGGSENGSEVAAQPAGLSGPAEVGPGAVGER",
            "Unmodified",
            "_AAAAAAAAAAAATGTEAGPGTAGGSENGSEVAAQPAGLSGPAEVGPGAVGER_",
            None,
            0.02820,
            "20160219_AML-SS_P2a_x1",
        ],
        [
            "P23",
            "O60341",
            "AAAAAAAAAAAATGTEAGPGTAGGSENGSEVAAQPAGLSGPAEVGPGAVGER",
            "Unmodified",
            "_AAAAAAAAAAAATGTEAGPGTAGGSENGSEVAAQPAGLSGPAEVGPGAVGER_",
            None,
            0.018737,
            "20160218_AML-SS_P23_x1",
        ],
    )
    intensity_name_to_intensities = {
        "Ratio H/L normalized": [1.2907, 0.83188],
        "Ratio H/L": [1.0161, 0.51728],
    }

    peptide_df = pd.DataFrame(
        data=peptide_protein_list,
        columns=[
            "Sample",
            "Protein ID",
            "Sequence",
            "Modifications",
            "Modified sequence",
            "Missed cleavages",
            "PEP",
            "Raw file",
        ],
    )

    peptide_df["Intensity"] = intensity_name_to_intensities[intensity_name]

    peptide_df.sort_values(
        by=["Sample", "Protein ID", "Sequence", "Modifications"],
        ignore_index=True,
        inplace=True,
    )

    return peptide_df


@pytest.mark.parametrize(
    "intensity_name", [intensity.value for intensity in IntensityType]
)
def test_peptide_import(intensity_name):
    if (
        intensity_name == IntensityType.LFQ_INTENSITY.value
        or intensity_name == IntensityType.IBAQ.value
    ):
        intensity_name = IntensityType.INTENSITY.value
    outputs = peptide_import.peptide_import(
        file_path=TEST_PEPTIDES_PATH / "peptides_vsmall.txt",
        intensity_name=intensity_name,
        map_to_uniprot=False,
    )

    if "messages" in outputs and outputs["messages"]:
        for message in outputs["messages"]:
            if message["level"] == logging.ERROR:
                assert False, message["msg"]
    pd.testing.assert_frame_equal(
        outputs["peptide_df"], peptide_df(intensity_name), check_dtype=False
    )


def test_peptide_import_contaminant_reverse_removal():
    outputs = peptide_import.peptide_import(
        file_path=TEST_PEPTIDES_PATH / "peptides_vsmall_con_rev.txt",
        intensity_name=IntensityType.INTENSITY.value,
        map_to_uniprot=False,
    )

    original_proteins = peptide_df(IntensityType.INTENSITY.value)["Protein ID"].unique()
    new_proteins = ["O76009"] + list(original_proteins)
    assert outputs["peptide_df"]["Protein ID"].nunique() == len(new_proteins)
    assert set(outputs["peptide_df"]["Protein ID"].unique()) == set(new_proteins)
    assert not any(outputs["peptide_df"]["Protein ID"].str.contains("REV"))
    assert not any(outputs["peptide_df"]["Protein ID"].str.contains("CON"))
    assert not any(outputs["peptide_df"]["Protein ID"] == "")

    assert outputs["messages"][0]["level"] == logging.INFO
    assert (
        f"Successfully imported {len(new_proteins)} protein groups"
        in outputs["messages"][0]["msg"]
    )


@pytest.mark.parametrize(
    "intensity_name,expected_intensity_name",
    [
        (intensity.value, intensity.value)
        for intensity in IntensityType
        if intensity not in (IntensityType.IBAQ, IntensityType.LFQ_INTENSITY)
    ]
    + [
        (IntensityType.IBAQ.value, IntensityType.INTENSITY.value),
        (IntensityType.LFQ_INTENSITY.value, IntensityType.INTENSITY.value),
    ],
)
def test_peptide_import_invalid_intensity_name(
    intensity_name: str, expected_intensity_name: str
):
    outputs = peptide_import.peptide_import(
        file_path=TEST_PEPTIDES_PATH / "peptides_vsmall_wrong_intensity_cols.txt",
        intensity_name=intensity_name,
        map_to_uniprot=False,
    )

    assert "peptide_df" not in outputs
    assert "messages" in outputs
    assert len(outputs["messages"]) == 1
    assert outputs["messages"][0]["level"] == logging.ERROR
    assert (
        f"{expected_intensity_name} was not found in the provided file"
        in outputs["messages"][0]["msg"]
    )


@pytest.mark.parametrize(
    "intensity_name,file_name,df",
    [
        (IntensityType.INTENSITY.value, "evidence_vsmall.txt", psm_df()),
        (
            IntensityType.RATIO_HL_NORMALIZED.value,
            "evidence_ratio_hl.txt",
            evidence_ratio_df(IntensityType.RATIO_HL_NORMALIZED.value),
        ),
        (
            IntensityType.RATIO_HL.value,
            "evidence_ratio_hl.txt",
            evidence_ratio_df(IntensityType.RATIO_HL.value),
        ),
    ],
)
def test_evidence_import(intensity_name: str, file_name: str, df: pd.DataFrame):
    outputs = peptide_import.evidence_import(
        file_path=TEST_PEPTIDES_PATH / file_name,
        intensity_name=intensity_name,
        map_to_uniprot=False,
    )

    if "messages" in outputs and outputs["messages"]:
        for message in outputs["messages"]:
            if message["level"] == logging.ERROR:
                assert False, message["msg"]

    assert np.allclose(
        outputs[DataKey.PSM_DF]["PEP"],
        df["PEP"],
        rtol=1e-02,  # Relative tolerance
        atol=1e-04,  # Absolute tolerance
    )

    pd.testing.assert_frame_equal(
        outputs[DataKey.PSM_DF].drop(columns=["PEP"]).sort_index(axis=1),
        df.drop(columns=["PEP"]).sort_index(axis=1),
        check_dtype=False,
    )


@pytest.mark.parametrize(
    "intensity_name",
    [
        intensity.value
        for intensity in IntensityType
        if intensity not in (IntensityType.IBAQ, IntensityType.LFQ_INTENSITY)
    ],
)
def test_evidence_import_invalid_intensity_name(intensity_name: str):
    outputs = peptide_import.evidence_import(
        file_path=TEST_PEPTIDES_PATH / "evidence_vsmall_wrong_intensity_cols.txt",
        intensity_name=intensity_name,
        map_to_uniprot=False,
    )

    assert "peptide_df" not in outputs
    assert "messages" in outputs
    assert len(outputs["messages"]) == 1
    assert outputs["messages"][0]["level"] == logging.ERROR
    assert (
        f"{intensity_name} was not found in the provided file"
        in outputs["messages"][0]["msg"]
    )


@pytest.mark.parametrize(
    "intensity_name",
    [
        IntensityType.INTENSITY.value,
        IntensityType.RATIO_HL.value,
        IntensityType.RATIO_HL_NORMALIZED.value,
    ],
)
def test_evidence_import_different_column_capitalization(intensity_name: str):
    outputs = peptide_import.evidence_import(
        file_path=TEST_PEPTIDES_PATH / "evidence_different_column_capitalization.txt",
        intensity_name=intensity_name,
        map_to_uniprot=False,
    )

    assert "psm_df" in outputs
    assert IntensityType.INTENSITY.value in outputs["psm_df"].columns


def test_evidence_import_contaminant_reverse_removal():
    outputs = peptide_import.evidence_import(
        file_path=TEST_PEPTIDES_PATH / "evidence_vsmall_con_rev.txt",
        intensity_name=IntensityType.INTENSITY.value,
        map_to_uniprot=False,
    )

    assert len(outputs["psm_df"]) == 4
    assert not any(outputs["psm_df"]["Protein ID"].str.contains("REV"))
    assert not any(outputs["psm_df"]["Protein ID"].str.contains("CON"))
    assert not any(outputs["psm_df"]["Protein ID"] == "")

    assert outputs["messages"][0]["level"] == logging.INFO
    assert f"Successfully imported 3 protein groups" in outputs["messages"][0]["msg"]
