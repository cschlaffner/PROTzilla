from __future__ import annotations

import numpy as np
import pandas as pd
import trimesh

from backend.protzilla.data_analysis.geometry_operations import (
    calculate_centroid,
    extract_points_from_cif,
    find_farthest_point,
    mesh_to_polyhedron,
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
        residue_points = extract_points_from_cif(
            cif_df,
            residue_range=(residue_position, residue_position),
            chain_id=chain_id,
        )
        center = calculate_centroid(residue_points)
        furthest_point = find_farthest_point(residue_points, center)
        radius = float(np.linalg.norm(furthest_point - center))

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
