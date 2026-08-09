import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import Delaunay


def create_mesh_triangles(points: np.ndarray):
    """Return triangle vertex indices from Delaunay triangulation of XY."""
    xy = points[:, :2]
    tri = Delaunay(xy)
    return tri.simplices


def plot_mesh(points: np.ndarray, triangles: np.ndarray, show: bool = True, save_path: str | None = None):
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


def main(show: bool = True):
    pts = example_points()
    tris = create_mesh_triangles(pts)
    save = "sandbox_mesh_example.png" if not show else None
    plot_mesh(pts, tris, show=show, save_path=save)
    if save:
        print(f"Saved example mesh to {save}")


if __name__ == "__main__":
    # default non-blocking example: save image
    main(show=False)
