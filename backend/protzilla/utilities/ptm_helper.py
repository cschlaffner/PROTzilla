import pandas as pd
import numpy as np

from backend.protzilla.data_analysis.geometry_operations import find_farthest_point_vdw


def get_all_ptm_atoms_with_coordinates(cif_df: pd.DataFrame) -> list:
    """
    Extracts all non-standard residues (PTMs) and their atomic coordinates
    from a parsed mmCIF DataFrame.
    """
    ptm_list = []

    is_non_standard = cif_df["_chem_comp.mon_nstd_flag"] == False
    ptm_atoms_df = cif_df[is_non_standard]

    grouped_ptms = ptm_atoms_df.groupby(
        ["_atom_site.label_asym_id", "_atom_site.label_seq_id"]
    )

    for (chain_id, seq_id), atom_group in grouped_ptms:
        comp_id = atom_group["_atom_site.label_comp_id"].iloc[0]
        atoms_subset = atom_group[
            [
                "_atom_site.label_atom_id",
                "_atom_site.type_symbol",
                "_atom_site.Cartn_x",
                "_atom_site.Cartn_y",
                "_atom_site.Cartn_z",
            ]
        ].rename(
            columns={
                "_atom_site.label_atom_id": "atom_name",
                "_atom_site.type_symbol": "element",
                "_atom_site.Cartn_x": "x",
                "_atom_site.Cartn_y": "y",
                "_atom_site.Cartn_z": "z",
            }
        )
        atoms_subset["element"] = (
            atoms_subset["element"].astype(str).str.strip().str.capitalize()
        )

        atoms_data = atoms_subset.to_dict(orient="records")

        ptm_list.append(
            {
                "ptm_name": comp_id,
                "chain": chain_id,
                "position": seq_id,
                "atoms": atoms_data,
            }
        )

    return ptm_list


def calculate_center_point(points: np.ndarray) -> np.ndarray:
    """
    Calculate the center point of a point cloud.
    """
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"Expected points with shape (n, 3), got {points.shape}.")
    if len(points) == 0:
        raise ValueError("At least one point is required to calculate a centroid.")

    return points.mean(axis=0)


def find_farthest_point(points: np.ndarray, reference_point: np.ndarray) -> np.ndarray:
    """
    Calculate the farthest point inside a point cloud from a reference point.
    """
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"Expected points with shape (n, 3), got {points.shape}.")
    if len(points) == 0:
        raise ValueError(
            "At least one point is required to calculate a maximum distance."
        )
    if reference_point.shape != (3,):
        raise ValueError(
            f"Expected reference_point with shape (3,), got {reference_point.shape}."
        )

    distances = np.linalg.norm(points - reference_point, axis=1)
    return points[np.argmax(distances)]


def get_center_points_and_radius_for_each_ptm(ptm_list: list) -> list:
    for ptm in ptm_list:
        coords = [[atom["x"], atom["y"], atom["z"]] for atom in ptm["atoms"]]
        elements = [atom["element"] for atom in ptm["atoms"]]

        coords_array = np.array(coords, dtype=np.float32)
        elements_array = np.array(elements)

        center_point = calculate_center_point(coords_array)
        _, radius = find_farthest_point_vdw(
            coords_array, elements_array, center_point
        )

        ptm["center_point"] = center_point.tolist()
        ptm["radius"] = float(radius)

    return ptm_list
