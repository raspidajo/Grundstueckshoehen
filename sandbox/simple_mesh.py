import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import Delaunay
from typing import Optional

# Optional Plotly for interactive HTML output
try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    HAS_PLOTLY = True
except Exception:
    go = None
    pyo = None
    HAS_PLOTLY = False


from grundstueckshoehen.data import get_terrain_points


def create_mesh_triangles(points: np.ndarray):
    """Return triangle vertex indices from Delaunay triangulation of XY."""
    xy = points[:, :2]
    tri = Delaunay(xy)
    return tri.simplices


def plot_mesh(points: np.ndarray, triangles: np.ndarray, show: bool = True, save_path: Optional[str] = None):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    mesh_triangles = points[triangles]
    facecolors = "lightgrey"
    poly = Poly3DCollection(mesh_triangles, facecolors=facecolors, edgecolors="k", linewidths=0.3, alpha=0.9)
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


def example_points():
    # simple hill-like sample
    xs = np.linspace(0, 10, 8)
    ys = np.linspace(0, 8, 6)
    xv, yv = np.meshgrid(xs, ys)
    zv = np.sin(xv / 2) * np.cos(yv / 3) * 0.5
    pts = np.column_stack([xv.ravel(), yv.ravel(), zv.ravel()])
    return pts


def main(show: bool = True, use_data: bool = True):
    """Run sandbox demo. By default uses coordinates from `grundstueckshoehen.data`.

    Set `use_data=False` to use the internal example grid instead.
    """
    if use_data:
        pts = get_terrain_points()
    else:
        pts = example_points()

    tris = create_mesh_triangles(pts)
    save = "sandbox_mesh_example.png" if not show else None
    save_html = "sandbox_mesh_example.html" if not show else None
    plot_mesh(pts, tris, show=show, save_path=save)

    if HAS_PLOTLY:
        plot_mesh_interactive(pts, tris, open_html=show, save_path=save_html)
    else:
        if save_html is not None:
            print("Plotly not installed; skipping interactive HTML output.")

    if save:
        print(f"Saved example mesh to {save}")


def plot_mesh_interactive(points: np.ndarray, triangles: np.ndarray, open_html: bool = False, save_path: Optional[str] = None):
    """Create an interactive HTML Plotly mesh from Nx3 points and triangle indices.

    Raises ImportError if Plotly is not available.
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly is not installed. Install with 'pip install plotly'.")

    x, y, z = points.T
    i, j, k = triangles.T
    # Use z as intensity (height) for simple coloring
    mesh = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        intensity=z,
        colorscale=[[0, 'green'], [0.5, 'blue'], [1, 'red']],
        intensitymode='vertex',
        flatshading=True,
        showscale=True,
    )

    pts_scatter = go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=3, color='red'))

    fig = go.Figure(data=[mesh, pts_scatter])
    fig.update_layout(title='Interactive sandbox mesh', scene=dict(aspectmode='data'))

    if save_path:
        pyo.plot(fig, filename=save_path, auto_open=open_html)
    elif open_html:
        pyo.plot(fig, auto_open=True)

    return fig


if __name__ == "__main__":
    # default non-blocking example: save image
    main(show=False)
