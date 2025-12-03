import logging

import numpy as np
import pandas as pd
import pytest

from backend.tests.paths import TEST_DATA_PATH
from backend.protzilla.importing import peptide_import
from backend.protzilla.constants.intensity_type import IntensityType


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


def evidence_df():
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
        file_path=f"{TEST_DATA_PATH}/peptides/peptides-vsmall.txt",
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


def test_evidence_import():
    outputs = peptide_import.evidence_import(
        file_path=f"{TEST_DATA_PATH}/peptides/evidence-vsmall.txt",
        map_to_uniprot=False,
    )

    if "messages" in outputs and outputs["messages"]:
        for message in outputs["messages"]:
            if message["level"] == logging.ERROR:
                assert False, message["msg"]

    assert np.allclose(
        outputs["peptide_df"]["PEP"],
        evidence_df()["PEP"],
        rtol=1e-02,  # Relative tolerance
        atol=1e-04,  # Absolute tolerance
    )

    pd.testing.assert_frame_equal(
        outputs["peptide_df"].drop(columns=["PEP"]).sort_index(axis=1),
        evidence_df().drop(columns=["PEP"]).sort_index(axis=1),
        check_dtype=False,
    )
