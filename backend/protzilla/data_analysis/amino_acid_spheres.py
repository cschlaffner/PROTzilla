from __future__ import annotations

import numpy as np
import pandas as pd
import trimesh

from backend.protzilla.constants.cif_columns import (
    ATOM_SITE_COLUMNS,
    CHEM_COMP_COLUMNS,
)
from backend.protzilla.data_analysis.geometry_operations import (
    calculate_center_point,
    extract_points_from_cif,
    find_farthest_point_vdw,
    find_intersecting_spheres,
    mesh_to_polyhedron,
    resolve_chain_column,
)
from backend.protzilla.utilities.ptm_helper import (
    get_all_ptm_atoms_with_coordinates,
    get_center_points_and_radius_for_each_ptm,
)


def _calculate_residue_spheres(
    cif_df: pd.DataFrame, chain_id: str | None = None
) -> list[dict]:
    residue_df = cif_df
    chain_column = resolve_chain_column(cif_df)
    if chain_id is not None and chain_column is not None:
        residue_df = cif_df[cif_df[chain_column] == chain_id]

    residue_positions = (
        pd.to_numeric(residue_df[ATOM_SITE_COLUMNS.LABEL_SEQ_ID], errors="coerce")
        .dropna()
        .astype(int)
        .drop_duplicates()
        .sort_values()
    )

    spheres = []
    for residue_position in residue_positions:
        residue_points, residue_elements = extract_points_from_cif(
            cif_df,
            residue_range=(residue_position, residue_position),
            chain_id=chain_id,
        )
        center = calculate_center_point(residue_points)
        _, radius = find_farthest_point_vdw(residue_points, residue_elements, center)

        spheres.append(
            {
                "chain": chain_id,
                "position": residue_position,
                "center": center.tolist(),
                "radius": float(radius),
            }
        )

    return spheres


def calculate_amino_acid_spheres(
    cif_df: pd.DataFrame,
    chain_id: str | None = None,
    color: int = 0xFF8C00,
    alpha: float = 0.25,
    subdivisions: int = 1,
    only_intersecting_ptms: bool = False,
    ignored_neighbors: int = 0,
) -> list[dict]:
    if only_intersecting_ptms:
        residue_spheres = []
        seen_residues = set()
        for collision in find_ptm_amino_acid_sphere_collisions(
            cif_df, ignored_neighbors=ignored_neighbors, chain_id=chain_id
        ):
            for residue_sphere in collision["collisions"]:
                residue_key = (residue_sphere["chain"], residue_sphere["position"])
                if residue_key not in seen_residues:
                    seen_residues.add(residue_key)
                    residue_spheres.append(residue_sphere)
    else:
        residue_spheres = _calculate_residue_spheres(cif_df, chain_id)

    spheres = []
    for residue_sphere in residue_spheres:
        sphere = trimesh.creation.icosphere(
            subdivisions=subdivisions, radius=residue_sphere["radius"]
        )
        sphere.apply_translation(residue_sphere["center"])

        spheres.append(
            {
                "label": f"Residue {residue_sphere['position']} sphere",
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
    if CHEM_COMP_COLUMNS.MON_NSTD_FLAG not in cif_df.columns:
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


def find_ptm_amino_acid_sphere_collisions(
    cif_df: pd.DataFrame,
    ignored_neighbors: int = 0,
    chain_id: str | None = None,
) -> list[dict]:
    if CHEM_COMP_COLUMNS.MON_NSTD_FLAG not in cif_df.columns:
        return []

    amino_acid_df = cif_df[cif_df[CHEM_COMP_COLUMNS.MON_NSTD_FLAG] == True]
    chain_column = resolve_chain_column(amino_acid_df)
    if chain_id is not None:
        chains = [chain_id]
    elif chain_column is not None:
        chains = amino_acid_df[chain_column].dropna().drop_duplicates()
    else:
        chains = [None]
    amino_acid_spheres = [
        sphere
        for chain in chains
        for sphere in _calculate_residue_spheres(amino_acid_df, chain)
    ]

    ptms = get_center_points_and_radius_for_each_ptm(
        get_all_ptm_atoms_with_coordinates(cif_df)
    )
    if chain_id is not None:
        ptms = [ptm for ptm in ptms if ptm["chain"] == chain_id]

    collisions = []
    for ptm in ptms:
        ptm_sphere = {
            "ptm_name": ptm["ptm_name"],
            "chain": ptm["chain"],
            "position": int(ptm["position"]),
            "center": ptm["center_point"],
            "radius": float(ptm["radius"]),
        }
        checked_spheres = [
            sphere
            for sphere in amino_acid_spheres
            if not (
                sphere["chain"] == ptm_sphere["chain"]
                and 0
                < abs(sphere["position"] - ptm_sphere["position"])
                <= ignored_neighbors
            )
        ]
        intersecting_spheres = find_intersecting_spheres(checked_spheres, ptm_sphere)

        collisions.append(
            {
                **ptm_sphere,
                "collisions": intersecting_spheres,
            }
        )

    return collisions
