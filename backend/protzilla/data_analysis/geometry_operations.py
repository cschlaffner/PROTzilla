from __future__ import annotations

import numpy as np
import pandas as pd
import trimesh

from backend.protzilla.constants.cif_columns import ATOM_SITE_COLUMNS
from backend.protzilla.constants.van_der_waals import vdw_radii

COORDINATE_COLUMNS = [
    ATOM_SITE_COLUMNS.CARTN_X,
    ATOM_SITE_COLUMNS.CARTN_Y,
    ATOM_SITE_COLUMNS.CARTN_Z,
]


def resolve_chain_column(cif_df: pd.DataFrame) -> str | None:
    """
    Return the preferred chain identifier column if present in the CIF DataFrame.

    :param cif_df: DataFrame containing mmCIF atom_site data
    :return: label chain column, author chain column as fallback, or None
    """

    if ATOM_SITE_COLUMNS.LABEL_ASYM_ID in cif_df.columns:
        return ATOM_SITE_COLUMNS.LABEL_ASYM_ID
    if ATOM_SITE_COLUMNS.AUTH_ASYM_ID in cif_df.columns:
        return ATOM_SITE_COLUMNS.AUTH_ASYM_ID
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
        ATOM_SITE_COLUMNS.LABEL_SEQ_ID,
        ATOM_SITE_COLUMNS.TYPE_SYMBOL,
        *COORDINATE_COLUMNS,
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

    residue_ids = filtered_df[ATOM_SITE_COLUMNS.LABEL_SEQ_ID].astype(int)
    filtered_df = filtered_df[(residue_ids >= start) & (residue_ids <= end)]

    atom_data = filtered_df[
        [*COORDINATE_COLUMNS, ATOM_SITE_COLUMNS.TYPE_SYMBOL]
    ].drop_duplicates()

    points = atom_data[COORDINATE_COLUMNS].astype(float).to_numpy()
    elements = (
        atom_data[ATOM_SITE_COLUMNS.TYPE_SYMBOL]
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

    :param points: point coordinates with shape (n, 3)
    :return: convex hull
    :raises ValueError: if the param points have an invalid shape or contain fewer than
    four points
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

    :param points: point coordinates with shape (n, 3)
    :return: arithmetic mean of all points
    :raises ValueError: if the param points have an invalid shape or are empty
    """
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"Expected points with shape (n, 3), got {points.shape}.")
    if len(points) == 0:
        raise ValueError("At least one point is required to calculate a centroid.")

    return points.mean(axis=0)


def find_farthest_point(points: np.ndarray, reference_point: np.ndarray) -> np.ndarray:
    """
    Calculate the farthest point inside a point cloud from a reference point.

    :param points: point coordinates with shape (n, 3)
    :param reference_point: point from which distances are calculated
    :return: point with the greatest distance from the reference point
    :raises ValueError: if the reference point or the param points have an invalid shape or are empty
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

    :param points: atom coordinates with shape (n, 3)
    :param elements: element symbol mapping to each atom coordinate
    :param reference_point: point from which distances are calculated
    :return: farthest atom coordinate and its distance including the van der Waals radius
    :raises ValueError: if the reference point or the param points have an invalid shape or are empty
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
    """
    Find spheres that intersect or touch a reference sphere.

    :param spheres: spheres represented by center coordinates and radius
    :param reference_sphere: sphere against which intersections are checked
    :return: spheres intersecting or touching the reference sphere
    """
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

    :param mesh_a: first mesh
    :param mesh_b: second mesh
    :param distance_tolerance: maximum distance at which meshes count as touching
    (standard is 1e-9 because of floating point error)
    :return: whether the meshes intersect or are within the distance tolerance
    """

    from trimesh.collision import CollisionManager

    manager = CollisionManager()
    manager.add_object("mesh_a", mesh_a)
    return manager.min_distance_single(mesh_b) <= distance_tolerance


def meshes_distance(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh) -> float:
    """
    Calculate the minimum euclidean distance between two meshes.

    :param mesh_a: first mesh
    :param mesh_b: second mesh
    :return: minimum Euclidean distance between the meshes
    """

    from trimesh.collision import CollisionManager

    manager = CollisionManager()
    manager.add_object("mesh_a", mesh_a)
    distance = float(manager.min_distance_single(mesh_b))
    return max(distance, 0.0)
