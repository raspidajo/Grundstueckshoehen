import numpy as np

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

def _generate_house_edge_points(n: int = 20, distance: float = 1.0, height: float = -0.05) -> dict:
    house = np.stack(list(HOUSE_POINTS.values()))[:, :2]
    num_edges = house.shape[0]
    points_per_edge = [n // num_edges] * num_edges
    for idx in range(n % num_edges):
        points_per_edge[idx] += 1

    additional_points = {}
    index = 1
    for edge_index, count in enumerate(points_per_edge):
        p0 = house[edge_index]
        p1 = house[(edge_index + 1) % num_edges]
        edge_vec = p1 - p0
        length = np.linalg.norm(edge_vec)
        if length == 0:
            continue
        normal = np.array([edge_vec[1], -edge_vec[0]])
        normal = normal / np.linalg.norm(normal)

        for step in range(1, count + 1):
            fraction = step / (count + 1)
            point_xy = p0 + edge_vec * fraction + normal * distance
            additional_points[f"house_edge_{index}"] = np.array([point_xy[0], point_xy[1], height])
            index += 1

    return additional_points

ADDITIONAL_POINTS = _generate_house_edge_points()


def get_house_centroid() -> np.ndarray:
    house = np.stack(list(HOUSE_POINTS.values()))
    return np.mean(house[:, :2], axis=0)

def get_terrain_points() -> np.ndarray:
    terrain_points = [*GROUND_POINTS.values(), *ADDITIONAL_POINTS.values()]
    if len(terrain_points) == 0:
        raise ValueError("At least one terrain point is required.")
    return np.vstack(terrain_points)

def get_house_loop() -> np.ndarray:
    house = np.stack(list(HOUSE_POINTS.values()))
    return np.vstack([house, house[0]])

def get_ground_loop() -> np.ndarray:
    ground = np.stack(list(GROUND_POINTS.values()))
    return np.vstack([ground, ground[0]])
