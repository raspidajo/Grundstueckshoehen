import numpy as np
from scipy.spatial import Delaunay

from .data import get_house_centroid

MAX_SLOPE_PERCENT = 20.0


def create_mesh(points: np.ndarray) -> np.ndarray:
    if points.shape[1] != 3:
        raise ValueError("Points must be Nx3 array")
    xy = points[:, :2]
    delaunay = Delaunay(xy)
    return delaunay.simplices


def compute_triangle_slopes(points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    centroid_xy = np.mean(points[triangles, :2], axis=1)
    centroid_z = np.mean(points[triangles, 2], axis=1)
    house_center = get_house_centroid()
    house_z = 0.0

    direction = house_center[np.newaxis, :] - centroid_xy
    distance = np.linalg.norm(direction, axis=1)
    distance = np.maximum(distance, 1e-3)

    slope_to_house = (house_z - centroid_z) / distance
    slope_percent = slope_to_house * 100.0
    slope_percent = np.clip(slope_percent, -MAX_SLOPE_PERCENT, MAX_SLOPE_PERCENT)
    return slope_percent
