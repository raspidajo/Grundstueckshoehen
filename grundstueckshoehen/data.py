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

ADDITIONAL_POINTS = {
    # Extra terrain sampling points can be added here.
    # Example:
    # "h_1": np.array([9.0, 5.0, -0.05]),
}

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
