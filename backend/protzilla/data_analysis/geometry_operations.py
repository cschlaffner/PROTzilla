from __future__ import annotations

import numpy as np
import pandas as pd
import trimesh

from backend.protzilla.constants.van_der_waals import vdw_radii

COORDINATE_COLUMNS = [
    "_atom_site.Cartn_x",
    "_atom_site.Cartn_y",
    "_atom_site.Cartn_z",
]


def resolve_chain_column(cif_df: pd.DataFrame) -> str | None:
    """
    Return the preferred chain identifier column if present in the CIF DataFrame.
    """

    if "_atom_site.label_asym_id" in cif_df.columns:
        return "_atom_site.label_asym_id"
    if "_atom_site.auth_asym_id" in cif_df.columns:
        return "_atom_site.auth_asym_id"
    return None


def extract_points_from_cif(
    cif_df: pd.DataFrame,
    residue_range: tuple[int, int],
    chain_id: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract Cartesian atom coordinates in a residue range from a CIF DataFrame.

    :param cif_df: DataFrame containing mmCIF atom_site coordinates
    :param residue_range: inclusive residue interval as [start, end]
    :param chain_id: optional chain identifier. If given, the function will filter by
    _atom_site.label_asym_id or _atom_site.auth_asym_id when available.
    :return: array of n points und x, y, z coordinates. (n, 3)
    :raises ValueError: if required columns are missing or too few points remain
    """

    required_columns = {
        "_atom_site.label_seq_id",
        "_atom_site.type_symbol",
        "_atom_site.Cartn_x",
        "_atom_site.Cartn_y",
        "_atom_site.Cartn_z",
    }
    missing_columns = sorted(required_columns - set(cif_df.columns))
    if missing_columns:
        raise ValueError(
            f"CIF DataFrame is missing required columns for 3D extraction: {missing_columns}"
        )

    start, end = residue_range
    if start > end:
        raise ValueError(
            f"Invalid residue range {residue_range}. Start must be smaller than or equal to end."
        )

    filtered_df = cif_df.copy()

    chain_column = resolve_chain_column(filtered_df)
    if chain_id is not None:
        if chain_column is None:
            raise ValueError(
                "A chain_id was provided, but the CIF DataFrame has no chain identifier column."
            )
        filtered_df = filtered_df[filtered_df[chain_column] == chain_id]

    residue_ids = filtered_df["_atom_site.label_seq_id"].astype(int)
    filtered_df = filtered_df[(residue_ids >= start) & (residue_ids <= end)]

    atom_data = filtered_df[
        [
            "_atom_site.Cartn_x",
            "_atom_site.Cartn_y",
            "_atom_site.Cartn_z",
            "_atom_site.type_symbol",
        ]
    ].drop_duplicates()

    points = (
        atom_data[
            [
                "_atom_site.Cartn_x",
                "_atom_site.Cartn_y",
                "_atom_site.Cartn_z",
            ]
        ]
        .astype(float)
        .to_numpy()
    )
    elements = (
        atom_data["_atom_site.type_symbol"]
        .astype(str)
        .str.strip()
        .str.capitalize()
        .to_numpy()
    )

    if len(points) == 0:
        raise ValueError("No atom coordinates found.")

    return points, elements


def build_convex_hull(points: np.ndarray) -> trimesh.Trimesh:
    """
    Build a 3D convex hull mesh from a point cloud.
    """

    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(
            f"Expected points with shape (n, 3), got array with shape {points.shape}."
        )

    if len(points) < 4:
        raise ValueError(
            "At least four distinct points are required to build a 3D convex hull."
        )

    return trimesh.convex.convex_hull(points, qhull_options="QJ")


def mesh_to_polyhedron(mesh: trimesh.Trimesh) -> dict:
    return {
        "vertices": mesh.vertices.tolist(),
        "faces": mesh.faces.tolist(),
    }


def point_cloud_to_polyhedron(points: np.ndarray) -> dict:
    return mesh_to_polyhedron(build_convex_hull(points))


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


def find_farthest_point_vdw(
    points: np.ndarray, elements: np.ndarray, reference_point: np.ndarray
) -> tuple[np.ndarray, float]:
    """
    Calculate the point, whose fdw-"Bubble" is most distant to a reference point.
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

    radii = np.array([vdw_radii[element] for element in elements], dtype=float)

    distances = np.linalg.norm(points - reference_point, axis=1) + radii
    max_index = np.argmax(distances)
    return points[max_index], float(distances[max_index])


def find_intersecting_spheres(
    spheres: list[dict],
    reference_sphere: dict,
) -> list[dict]:
    reference_center = np.array(reference_sphere["center"], dtype=float)
    reference_radius = float(reference_sphere["radius"])

    intersecting_spheres = []
    for sphere in spheres:
        center = np.array(sphere["center"], dtype=float)
        radius = float(sphere["radius"])
        distance = np.linalg.norm(center - reference_center)

        if distance <= reference_radius + radius:
            intersecting_spheres.append(sphere)

    return intersecting_spheres


def meshes_intersect(
    mesh_a: trimesh.Trimesh,
    mesh_b: trimesh.Trimesh,
    distance_tolerance: float = 1e-9,
) -> bool:
    """
    Determine whether two meshes intersect or touch.
    """

    from trimesh.collision import CollisionManager

    manager = CollisionManager()
    manager.add_object("mesh_a", mesh_a)
    return manager.min_distance_single(mesh_b) <= distance_tolerance


def meshes_distance(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh) -> float:
    """
    Calculate the minimum euclidean distance between two meshes.
    """

    from trimesh.collision import CollisionManager

    manager = CollisionManager()
    manager.add_object("mesh_a", mesh_a)
    distance = float(manager.min_distance_single(mesh_b))
    return max(distance, 0.0)
