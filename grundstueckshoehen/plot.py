import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap, Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from .data import get_ground_loop, get_house_loop, ADDITIONAL_POINTS
from .mesh import MAX_SLOPE_PERCENT


def get_slope_colormap():
    cmap = LinearSegmentedColormap.from_list(
        "slope_cm",
        ["green", "blue", "red"],
    )
    norm = Normalize(vmin=-MAX_SLOPE_PERCENT, vmax=MAX_SLOPE_PERCENT)
    return cmap, norm


def plot_terrain(points, triangles, slopes, save_path=None):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    cmap, norm = get_slope_colormap()
    facecolors = cmap(norm(slopes))

    mesh_triangles = points[triangles]
    surface = Poly3DCollection(mesh_triangles, facecolors=facecolors, edgecolors="k", linewidths=0.4, alpha=0.9)
    ax.add_collection3d(surface)

    ground_loop = get_ground_loop()
    ax.plot(ground_loop[:, 0], ground_loop[:, 1], ground_loop[:, 2], color="black", linewidth=2, label="Grundstücksgrenze")

    house_loop = get_house_loop()
    ax.plot(house_loop[:, 0], house_loop[:, 1], house_loop[:, 2], color="orange", linewidth=2, label="Hausumriss")

    if ADDITIONAL_POINTS:
        extras = list(ADDITIONAL_POINTS.values())
        extras = [point for point in extras]
        extras = zip(ADDITIONAL_POINTS.keys(), extras)
        for label, point in extras:
            ax.scatter([point[0]], [point[1]], [point[2]], color="magenta", s=60)
            ax.text(point[0], point[1], point[2], label, color="magenta")

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m) relative to h_E")
    ax.set_title("Gelände-Mesh mit Steigungsdarstellung")
    ax.legend(loc="upper left")

    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array(slopes)
    cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=12, pad=0.1)
    cbar.set_label("Steigung zur Hausmitte (%)")
    cbar.set_ticks([-MAX_SLOPE_PERCENT, -MAX_SLOPE_PERCENT/2, 0, MAX_SLOPE_PERCENT/2, MAX_SLOPE_PERCENT])
    cbar.set_ticklabels([
        f"-{MAX_SLOPE_PERCENT:.0f}%",
        f"-{MAX_SLOPE_PERCENT/2:.0f}%",
        "0% (eben)",
        f"+{MAX_SLOPE_PERCENT/2:.0f}%",
        f"+{MAX_SLOPE_PERCENT:.0f}%",
    ])

    ax.set_box_aspect((1, 1, 0.3))
    ax.view_init(elev=30, azim=-120)

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")

    return fig, ax
