import pandas as pd
from backend.protzilla.utilities.ptm_helper import (
    get_all_ptm_atoms_with_coordinates,
    get_center_points_and_radius_for_each_ptm,
)
import pytest
import numpy as np


def test_get_all_ptm_atoms_with_coordinates():
    data = {
        "_chem_comp.mon_nstd_flag": [True, True, False, False],
        "_atom_site.label_asym_id": ["A", "A", "B", "B"],
        "_atom_site.label_seq_id": [10, 10, 42, 42],
        "_atom_site.label_comp_id": ["MET", "MET", "SEP", "SEP"],
        "_atom_site.label_atom_id": ["N", "CA", "P", "O1P"],
        "_atom_site.type_symbol": ["N", "C", "P", "O"],
        "_atom_site.Cartn_x": [1.0, 2.0, 10.0, 11.0],
        "_atom_site.Cartn_y": [1.1, 2.1, 10.1, 11.1],
        "_atom_site.Cartn_z": [1.2, 2.2, 10.2, 11.2],
    }
    cif_df = pd.DataFrame(data)

    result = get_all_ptm_atoms_with_coordinates(cif_df)

    assert len(result) == 1

    ptm = result[0]
    assert ptm["ptm_name"] == "SEP"
    assert ptm["chain"] == "B"
    assert ptm["position"] == 42

    atoms = ptm["atoms"]
    assert len(atoms) == 2

    assert atoms[0] == {
        "atom_name": "P",
        "element": "P",
        "x": 10.0,
        "y": 10.1,
        "z": 10.2,
    }

    assert atoms[1] == {
        "atom_name": "O1P",
        "element": "O",
        "x": 11.0,
        "y": 11.1,
        "z": 11.2,
    }


def test_get_center_points_and_radius_for_each_ptm():
    ptm_list = [
        {
            "ptm_name": "SYM",
            "chain": "A",
            "position": 1,
            "atoms": [
                {"atom_name": "A1", "x": 1.0, "y": 0.0, "z": 0.0},
                {"atom_name": "A2", "x": -1.0, "y": 0.0, "z": 0.0},
                {"atom_name": "A3", "x": 0.0, "y": 1.0, "z": 0.0},
                {"atom_name": "A4", "x": 0.0, "y": -1.0, "z": 0.0},
            ],
        },
        {
            "ptm_name": "SGL",
            "chain": "B",
            "position": 2,
            "atoms": [
                {"atom_name": "A1", "x": 5.0, "y": 5.0, "z": 5.0},
            ],
        },
        {
            "ptm_name": "AB",
            "chain": "C",
            "position": 3,
            "atoms": [
                {"atom_name": "A1", "x": 12.0, "y": 10.0, "z": 8.0},
                {"atom_name": "A2", "x": 8.0, "y": 10.0, "z": 7.0},
                {"atom_name": "A3", "x": 10.0, "y": 10.0, "z": 15.0},
            ],
        },
    ]
    for ptm in ptm_list:
        for atom in ptm["atoms"]:
            atom["element"] = "C"

    result_list = get_center_points_and_radius_for_each_ptm(ptm_list)

    ptm_1 = result_list[0]

    result_list = get_center_points_and_radius_for_each_ptm(ptm_list)

    ptm_1 = result_list[0]
    np.testing.assert_allclose(ptm_1["center_point"], [0.0, 0.0, 0.0], atol=1e-6)
    assert pytest.approx(ptm_1["radius"], 1e-6) == 2.77

    ptm_2 = result_list[1]
    np.testing.assert_allclose(ptm_2["center_point"], [5.0, 5.0, 5.0], atol=1e-6)
    assert pytest.approx(ptm_2["radius"], 1e-6) == 1.77

    ptm_3 = result_list[2]

    expected_center = [10.0, 10.0, 10.0]
    np.testing.assert_allclose(ptm_3["center_point"], expected_center, atol=1e-6)

    assert pytest.approx(ptm_3["radius"], 1e-6) == 6.77
