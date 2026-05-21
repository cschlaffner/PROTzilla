from __future__ import annotations

import numpy as np
import pandas as pd
import trimesh

from backend.protzilla.data_analysis.geometry_operations import (
    calculate_center_point,
    extract_points_from_cif,
    find_farthest_point_vdw,
    mesh_to_polyhedron,
)
from backend.protzilla.utilities.ptm_helper import (
    get_all_ptm_atoms_with_coordinates,
    get_center_points_and_radius_for_each_ptm,
)


def calculate_amino_acid_spheres(
    cif_df: pd.DataFrame,
    chain_id: str | None = None,
    color: int = 0xFF8C00,
    alpha: float = 0.25,
    subdivisions: int = 1,
) -> list[dict]:
    residue_positions = (
        pd.to_numeric(cif_df["_atom_site.label_seq_id"], errors="coerce")
        .dropna()
        .astype(int)
        .drop_duplicates()
        .sort_values()
    )

    spheres = []
    for residue_position in residue_positions: # TODO: This can certainly be made more efficient
        residue_points, residue_elements = extract_points_from_cif(
            cif_df,
            residue_range=(residue_position, residue_position),
            chain_id=chain_id,
        )
        center = calculate_center_point(residue_points)
        _, radius = find_farthest_point_vdw(residue_points, residue_elements, center)

        sphere = trimesh.creation.icosphere(subdivisions=subdivisions, radius=radius)
        sphere.apply_translation(center)

        spheres.append(
            {
                "label": f"Residue {residue_position} sphere",
                "mesh": mesh_to_polyhedron(sphere),
                "color": color,
                "alpha": alpha,
            }
        )

    return spheres


def calculate_ptm_spheres(
    cif_df: pd.DataFrame,
    color: int = 0x00A6A6,
    alpha: float = 0.35,
    subdivisions: int = 1,
) -> list[dict]:
    if "_chem_comp.mon_nstd_flag" not in cif_df.columns:
        return []

    ptms = get_all_ptm_atoms_with_coordinates(cif_df)
    ptms = get_center_points_and_radius_for_each_ptm(ptms)

    spheres = []
    for ptm in ptms:
        center = np.array(ptm["center_point"], dtype=float)
        radius = float(ptm["radius"])

        sphere = trimesh.creation.icosphere(subdivisions=subdivisions, radius=radius)
        sphere.apply_translation(center)

        spheres.append(
            {
                "label": f"PTM {ptm['ptm_name']} {ptm['chain']}:{ptm['position']} sphere",
                "mesh": mesh_to_polyhedron(sphere),
                "color": color,
                "alpha": alpha,
            }
        )

    return spheres
