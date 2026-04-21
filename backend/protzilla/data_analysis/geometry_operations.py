import numpy as np
import pandas as pd
import trimesh
from trimesh import Trimesh
from trimesh.collision import CollisionManager


def _resolve_chain_column(cif_df: pd.DataFrame) -> str | None:
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
) -> np.ndarray:
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

    chain_column = _resolve_chain_column(filtered_df)
    if chain_id is not None:
        if chain_column is None:
            raise ValueError(
                "A chain_id was provided, but the CIF DataFrame has no chain identifier column."
            )
        filtered_df = filtered_df[filtered_df[chain_column] == chain_id]

    residue_ids = filtered_df["_atom_site.label_seq_id"].astype(int)
    filtered_df = filtered_df[(residue_ids >= start) & (residue_ids <= end)]

    points = (
        filtered_df[
            [
                "_atom_site.Cartn_x",
                "_atom_site.Cartn_y",
                "_atom_site.Cartn_z",
            ]
        ]
        .astype(float)
        .drop_duplicates()
        .to_numpy()
    )

    if len(points) == 0:
        raise ValueError("No atom coordinates found.")

    return points


def build_convex_hull(points: np.ndarray) -> Trimesh:
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

    return trimesh.convex.convex_hull(points, qhull_options="QJ") # Maybe QJ is stupid here? Ill have to look into it


def meshes_intersect(
    mesh_a: Trimesh, mesh_b: Trimesh, distance_tolerance: float = 1e-9
) -> bool:
    """
    Determine whether two triangle meshes intersect or touch.
    """

    manager = CollisionManager()
    manager.add_object("mesh_a", mesh_a)
    return manager.min_distance_single(mesh_b) <= distance_tolerance


def meshes_distance(mesh_a: Trimesh, mesh_b: Trimesh) -> float:
    """
    Calculate the minimum euclidean distance between two triangle meshes.
    """

    manager = CollisionManager()
    manager.add_object("mesh_a", mesh_a)
    distance = float(manager.min_distance_single(mesh_b))
    return max(distance, 0.0)


def bodies_intersect_from_cif(
    cif_df: pd.DataFrame,
    residue_range_a: tuple[int, int],
    residue_range_b: tuple[int, int],
    chain_id: str | None = None,
) -> dict:
    """
    Build two convex bodies from CIF residue ranges and test whether they intersect.

    :param cif_df: DataFrame containing mmCIF atom_site coordinates
    :param residue_range_a: inclusive residue range for the first body
    :param residue_range_b: inclusive residue range for the second body
    :param chain_id: optional chain identifier used for both bodies
    :return: summary dictionary with hull sizes and the intersection result
    """

    points_a = extract_points_from_cif(cif_df, residue_range_a, chain_id=chain_id)
    points_b = extract_points_from_cif(cif_df, residue_range_b, chain_id=chain_id)

    hull_a = build_convex_hull(points_a)
    hull_b = build_convex_hull(points_b)

    return {
        "intersects": meshes_intersect(hull_a, hull_b),
        "n_atoms_a": len(points_a),
        "n_atoms_b": len(points_b),
        "n_hull_vertices_a": len(hull_a.vertices),
        "n_hull_vertices_b": len(hull_b.vertices),
    }


def bodies_distance_from_cif(
    cif_df: pd.DataFrame,
    residue_range_a: tuple[int, int],
    residue_range_b: tuple[int, int],
    chain_id: str | None = None,
) -> dict:
    """
    Build two convex bodies from CIF residue ranges and calculate their distance.

    :param cif_df: DataFrame containing mmCIF atom_site coordinates
    :param residue_range_a: inclusive residue range for the first body
    :param residue_range_b: inclusive residue range for the second body
    :param chain_id: optional chain identifier used for both bodies
    :return: summary dictionary with hull sizes and the minimum distance
    """

    points_a = extract_points_from_cif(cif_df, residue_range_a, chain_id=chain_id)
    points_b = extract_points_from_cif(cif_df, residue_range_b, chain_id=chain_id)

    hull_a = build_convex_hull(points_a)
    hull_b = build_convex_hull(points_b)

    return {
        "distance": meshes_distance(hull_a, hull_b),
        "n_atoms_a": len(points_a),
        "n_atoms_b": len(points_b),
        "n_hull_vertices_a": len(hull_a.vertices),
        "n_hull_vertices_b": len(hull_b.vertices),
    }
