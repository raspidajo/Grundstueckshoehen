import numpy as np
from typing import Optional

H_E = 515.10

GROUND_POINTS = {
    "A_G": np.array([0.0, 0.0, 514.74 - H_E]),
    "B_G": np.array([18.46, 0.65, 514.80 - H_E]),
    "C_G": np.array([18.42, 34.98, 515.21 - H_E]),
    "D_G": np.array([0.0, 34.95, 515.21 - H_E]),
}

HOUSE_POINTS = {
    "A_H": np.array([4.3, 10.51, 0.0]),
    "B_H": np.array([15.2, 10.51, 0.0]),
    "C_H": np.array([15.2, 26.52, 0.0]),
    "D_H": np.array([4.3, 26.52, 0.0]),
}

SURROUNDING_POINTS = {
    "A_S": np.array([3.3, 9.51, -0.16]),
    "B_S": np.array([16.2, 9.51, -0.16]),
    "C_S": np.array([16.2, 27.52, -0.05]),
    "D_S": np.array([3.3, 27.52, -0.01]),
}

HOUSE_EDGE_POINTS_PER_EDGE = 5

def _generate_edge_points_xy(edge_points: np.ndarray, points_per_edge: int = HOUSE_EDGE_POINTS_PER_EDGE, distance: float = 1.0, height: Optional[float] = None, prefix: str = "edge") -> dict:
    edge_points = np.asarray(edge_points)
    if edge_points.ndim != 2 or edge_points.shape[1] not in (2, 3):
        raise ValueError("edge_points must be a 2D array with 2 or 3 columns")

    xy = edge_points[:, :2]
    has_z = edge_points.shape[1] == 3
    if height is None and not has_z:
        raise ValueError("Cannot interpolate height when input points have no z coordinate")

    num_edges = xy.shape[0]
    distances = np.asarray(distance)
    if distances.ndim == 0:
        distances = np.full(num_edges, distances)
    elif distances.shape != (num_edges,):
        raise ValueError(f"distance must be scalar or length {num_edges}")

    additional_points = {}
    index = 1

    for edge_index in range(num_edges):
        p0 = xy[edge_index]
        p1 = xy[(edge_index + 1) % num_edges]
        edge_vec = p1 - p0
        length = np.linalg.norm(edge_vec)
        if length == 0:
            continue

        normal = np.array([edge_vec[1], -edge_vec[0]])
        normal = normal / np.linalg.norm(normal)
        edge_distance = float(distances[edge_index])

        if height is None:
            z0 = float(edge_points[edge_index, 2])
            z1 = float(edge_points[(edge_index + 1) % num_edges, 2])

        for step in range(1, points_per_edge + 1):
            fraction = step / (points_per_edge + 1)
            point_xy = p0 + edge_vec * fraction + normal * edge_distance
            if height is None:
                point_z = z0 + fraction * (z1 - z0)
            else:
                point_z = float(height)
            additional_points[f"{prefix}_{index}"] = np.array([point_xy[0], point_xy[1], point_z])
            index += 1

    return additional_points


def _generate_edge_points(edge_points, points_per_edge: int = HOUSE_EDGE_POINTS_PER_EDGE, distance=1.0, height: Optional[float] = -0.05, prefix: str = "edge") -> dict:
    if isinstance(edge_points, dict):
        original_points = dict(edge_points)
        edge_points = np.stack(list(edge_points.values()))
    else:
        edge_points = np.asarray(edge_points)
        original_points = {
            f"{prefix}_orig_{idx + 1}": np.asarray(pt, dtype=float)
            for idx, pt in enumerate(edge_points)
        }

    generated_points = _generate_edge_points_xy(edge_points, points_per_edge=points_per_edge, distance=distance, height=height, prefix=prefix)
    original_points.update(generated_points)
    return original_points


def _generate_house_edge_points(points_per_edge: int = HOUSE_EDGE_POINTS_PER_EDGE, distance: float = 1.0, height: float = -0.05) -> dict:
    return _generate_edge_points(HOUSE_POINTS, points_per_edge=points_per_edge, distance=distance, height=height, prefix="house_edge")


def _generate_house_edge_points_on_edges(points_per_edge: int = HOUSE_EDGE_POINTS_PER_EDGE) -> dict:
    return _generate_edge_points(HOUSE_POINTS, points_per_edge=points_per_edge, distance=0.0, height=0.0, prefix="house_edge_on")

HOUSE_EDGE_POINTS = _generate_house_edge_points_on_edges(points_per_edge=HOUSE_EDGE_POINTS_PER_EDGE)

# ADDITIONAL_POINTS = _generate_house_edge_points(points_per_edge=5)
ADDITIONAL_POINTS = _generate_edge_points(SURROUNDING_POINTS, points_per_edge=HOUSE_EDGE_POINTS_PER_EDGE, distance=0, height=None, prefix="surrounding_edge")

# user-supplied custom points (dict of name->(x,y,z) arrays)
# define default custom points here (these will be included in the mesh)
CUSTOM_POINTS = {
    "p1": np.array([17.0, 30.0, 515.30 - H_E]),
    "p2": np.array([3.0, 30.0, 515.30 - H_E]),
}


def register_custom_points(points: dict, *, replace: bool = False) -> None:
    """Register custom named points to be included in terrain.

    - `points` should be a dict mapping name->(x,y,z)-like sequences or numpy arrays.
    - If `replace` is True, existing custom points are replaced; otherwise they are merged.
    """
    global CUSTOM_POINTS
    if replace:
        CUSTOM_POINTS = {}
    for k, v in points.items():
        CUSTOM_POINTS[k] = np.asarray(v, dtype=float)


def add_custom_point(name: str, point) -> None:
    """Add or replace a single custom point by name."""
    CUSTOM_POINTS[name] = np.asarray(point, dtype=float)


def clear_custom_points() -> None:
    """Remove all registered custom points."""
    CUSTOM_POINTS.clear()


def get_custom_points_array() -> np.ndarray:
    """Return Nx3 array of registered custom points (empty array if none)."""
    if not CUSTOM_POINTS:
        return np.empty((0, 3))
    return np.vstack(list(CUSTOM_POINTS.values()))

def get_house_centroid() -> np.ndarray:
    house = np.stack(list(HOUSE_POINTS.values()))
    return np.mean(house[:, :2], axis=0)

def get_terrain_points() -> np.ndarray:
    terrain_points = [*GROUND_POINTS.values(), *ADDITIONAL_POINTS.values(), *CUSTOM_POINTS.values()]
    if len(terrain_points) == 0:
        raise ValueError("At least one terrain point is required.")
    return np.vstack(terrain_points)

def get_house_loop() -> np.ndarray:
    house = np.stack(list(HOUSE_POINTS.values()))
    return np.vstack([house, house[0]])

def get_ground_loop() -> np.ndarray:
    ground = np.stack(list(GROUND_POINTS.values()))
    return np.vstack([ground, ground[0]])
