import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap, Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# Plotly is an optional dependency used for interactive HTML output.
# Import it lazily so the package still works without Plotly installed.
try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    HAS_PLOTLY = True
except Exception:
    go = None
    pyo = None
    HAS_PLOTLY = False

from .data import get_ground_loop, get_house_loop, ADDITIONAL_POINTS
from .mesh import MAX_SLOPE_PERCENT
from typing import Optional


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


def plot_terrain_interactive(points, triangles, slopes, save_path=None, open_html=False):
    if not HAS_PLOTLY:
        raise ImportError(
            "Plotly is not installed. Install it with 'pip install plotly' or 'pip install -r requirements.txt', and ensure VS Code uses the same Python interpreter."
        )

    x, y, z = points.T
    i, j, k = triangles.T

    cmap = [[0.0, "green"], [0.5, "blue"], [1.0, "red"]]
    mesh = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        intensity=slopes,
        colorscale=cmap,
        intensitymode="cell",
        flatshading=True,
        showscale=True,
        colorbar=dict(title="Steigung (%)", tickvals=[-MAX_SLOPE_PERCENT, 0, MAX_SLOPE_PERCENT], ticktext=[f"-{MAX_SLOPE_PERCENT}%", "0%", f"+{MAX_SLOPE_PERCENT}%"]),
    )

    boundary = go.Scatter3d(
        x=get_ground_loop()[:, 0],
        y=get_ground_loop()[:, 1],
        z=get_ground_loop()[:, 2],
        mode="lines",
        line=dict(color="black", width=5),
        name="Grundstücksgrenze",
    )

    house = go.Scatter3d(
        x=get_house_loop()[:, 0],
        y=get_house_loop()[:, 1],
        z=get_house_loop()[:, 2],
        mode="lines",
        line=dict(color="orange", width=5),
        name="Hausumriss",
    )

    data = [mesh, boundary, house]
    for label, point in ADDITIONAL_POINTS.items():
        data.append(
            go.Scatter3d(
                x=[point[0]],
                y=[point[1]],
                z=[point[2]],
                mode="markers+text",
                marker=dict(size=5, color="magenta"),
                text=[label],
                textposition="top center",
                name=label,
            )
        )

    fig = go.Figure(data=data)
    fig.update_layout(
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m) relative to h_E",
            aspectmode="data",
        ),
        title="Interaktives Gelände-Mesh",
    )

    if save_path:
        pyo.plot(fig, filename=save_path, auto_open=open_html)
    elif open_html:
        pyo.plot(fig, auto_open=True)

    return fig


def plot_mesh(points: np.ndarray, triangles: np.ndarray, show: bool = True, save_path: Optional[str] = None):
    """Simple Matplotlib mesh plot for Nx3 `points` and triangle indices `triangles`.

    Behaves like the sandbox `simple_mesh.plot_mesh` for consistency.
    """
    mesh_triangles = points[triangles]
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    poly = Poly3DCollection(mesh_triangles, facecolors="lightgrey", edgecolors="k", linewidths=0.3, alpha=0.9)
    ax.add_collection3d(poly)
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], color="red", s=20)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.auto_scale_xyz(points[:, 0], points[:, 1], points[:, 2])

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax
