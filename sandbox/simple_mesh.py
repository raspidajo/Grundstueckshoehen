import argparse
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import Delaunay
from typing import Optional

# Ensure the repository root is on sys.path when running this script directly.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Optional Plotly for interactive HTML output
try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    HAS_PLOTLY = True
except Exception:
    go = None
    pyo = None
    HAS_PLOTLY = False


from grundstueckshoehen.data import get_terrain_points, HOUSE_POINTS, HOUSE_EDGE_POINTS, ADDITIONAL_POINTS, get_house_loop, get_custom_points_array


def create_mesh_triangles(points: np.ndarray):
    """Return triangle vertex indices from Delaunay triangulation of XY."""
    xy = points[:, :2]
    tri = Delaunay(xy)
    return tri.simplices


def compute_vertex_gradients(points: np.ndarray, triangles: np.ndarray):
    """Estimate per-vertex gradient (dz/dx, dz/dy) by fitting a plane to local neighbors.

    Returns (gradients, magnitudes) where `gradients` is (N,2) and `magnitudes` is (N,).
    """
    n = points.shape[0]
    grads = np.zeros((n, 2), dtype=float)
    mags = np.zeros(n, dtype=float)

    # build a list of triangle indices per vertex
    tri_by_vertex = [[] for _ in range(n)]
    for t_idx, tri in enumerate(triangles):
        for v in tri:
            tri_by_vertex[v].append(t_idx)

    for i in range(n):
        tri_idxs = tri_by_vertex[i]
        if not tri_idxs:
            continue
        neigh = np.unique(triangles[tri_idxs].ravel())
        coords = points[neigh]
        if coords.shape[0] < 3:
            continue
        A = np.column_stack([coords[:, 0], coords[:, 1], np.ones(coords.shape[0])])
        z = coords[:, 2]
        try:
            coeffs, *_ = np.linalg.lstsq(A, z, rcond=None)
        except Exception:
            continue
        a, b, _ = coeffs
        grads[i, 0] = a
        grads[i, 1] = b
        mags[i] = float(np.hypot(a, b))

    return grads, mags


def slice_mesh_at_z(points: np.ndarray, triangles: np.ndarray, z_level: float):
    """Return list of line segments (p0,p1) where the mesh intersects the horizontal plane z=z_level."""
    segs = []
    for tri in triangles:
        verts = points[tri]
        zs = verts[:, 2]
        # determine which edges cross the plane
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            za, zb = zs[a], zs[b]
            if (za < z_level and zb > z_level) or (za > z_level and zb < z_level):
                t = (z_level - za) / (zb - za)
                pa = verts[a]
                pb = verts[b]
                pts.append(pa + t * (pb - pa))
        if len(pts) == 2:
            segs.append((pts[0], pts[1]))
    return segs


def plot_mesh(points: np.ndarray, triangles: np.ndarray, extra_points: Optional[dict] = None, vertex_gradients: Optional[np.ndarray] = None, gradient_magnitudes: Optional[np.ndarray] = None, show: bool = True, save_path: Optional[str] = None, z_scale: float = 10.0, num_arrows: int = 80, z_slices: Optional[list] = None):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    mesh_triangles = points[triangles].copy()
    # apply vertical exaggeration only for plotting (do not change triangulation)
    if z_scale != 1.0:
        mesh_triangles[:, :, 2] = mesh_triangles[:, :, 2] * z_scale
    facecolors = "lightgrey"
    poly = Poly3DCollection(mesh_triangles, facecolors=facecolors, edgecolors="k", linewidths=0.3, alpha=0.9)
    ax.add_collection3d(poly)

    # plot base vertices: color by gradient magnitude if available
    z_vals = points[:, 2] * z_scale
    if gradient_magnitudes is not None:
        sc = ax.scatter(points[:, 0], points[:, 1], z_vals, c=gradient_magnitudes, cmap='viridis', s=30, label='vertices')
        cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label('|grad z|')
    else:
        ax.scatter(points[:, 0], points[:, 1], z_vals, color="grey", s=20, label="vertices")

    # plot any extra point groups (house, additional) with distinct markers
    if extra_points:
        for name, pts in extra_points.items():
            if pts is None or len(pts) == 0:
                continue
            color = 'orange' if name.lower().startswith('house') else 'purple'
            ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2] * z_scale, label=name, color=color, s=30, marker='^')

    # draw horizontal slice intersections if requested
    if z_slices:
        for zc in z_slices:
            segs = slice_mesh_at_z(points, triangles, zc)
            for p0, p1 in segs:
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [zc * z_scale, zc * z_scale], color='blue', linewidth=1)

    ax.legend()

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.auto_scale_xyz(points[:, 0], points[:, 1], points[:, 2] * z_scale)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    # draw gradient arrows projected in XY if available
    if vertex_gradients is not None:
        # sample for readability using target number of arrows
        n = points.shape[0]
        step = max(1, n // max(1, num_arrows))
        idx = np.arange(0, n, step)
        xs = points[idx, 0]
        ys = points[idx, 1]
        zs = points[idx, 2] * z_scale
        u = vertex_gradients[idx, 0]
        v = vertex_gradients[idx, 1]
        # scale arrows for visibility relative to XY extents
        xy_range = max(points[:, 0].ptp(), points[:, 1].ptp(), 1e-6)
        arrow_scale = xy_range * 0.05
        ax.quiver(xs, ys, zs, u, v, np.zeros_like(u), length=arrow_scale, normalize=True, color='red', linewidth=0.5)


def example_points():
    # simple hill-like sample
    xs = np.linspace(0, 10, 8)
    ys = np.linspace(0, 8, 6)
    xv, yv = np.meshgrid(xs, ys)
    zv = np.sin(xv / 2) * np.cos(yv / 3) * 0.5
    pts = np.column_stack([xv.ravel(), yv.ravel(), zv.ravel()])
    return pts


def main(show: bool = True, use_data: bool = True, triangulate_all: bool = True, z_scale: float = 1.0, aspect_z: Optional[float] = None, z_range_pad: float = 0.2, num_arrows: int = 80, z_slices: Optional[list] = None):
    """Run sandbox demo. By default uses coordinates from `grundstueckshoehen.data`.

    Set `use_data=False` to use the internal example grid instead.
    """

    if use_data:
        terrain_pts = get_terrain_points()
        house_pts = np.stack(list(HOUSE_POINTS.values())) if len(HOUSE_POINTS) else np.empty((0, 3))
        house_edge_pts = np.vstack(list(HOUSE_EDGE_POINTS.values())) if len(HOUSE_EDGE_POINTS) else np.empty((0, 3))

        # build full point set for triangulation (include house points and house edge points)
        pts = terrain_pts
        if house_pts.size:
            pts = np.vstack([pts, house_pts])
        if house_edge_pts.size:
            pts = np.vstack([pts, house_edge_pts])

        # prepare extra groups for highlighted plotting (house, house edge, additional)
        additional_pts = np.vstack(list(ADDITIONAL_POINTS.values())) if len(ADDITIONAL_POINTS) else np.empty((0, 3))
        custom_pts = get_custom_points_array()
        extra = {}
        if house_pts.size:
            extra['house'] = house_pts
        if house_edge_pts.size:
            extra['house_edge'] = house_edge_pts
        if additional_pts.size:
            extra['additional'] = additional_pts
        if custom_pts.size:
            extra['custom'] = custom_pts
    else:
        pts = example_points()
        extra = None

    tris = create_mesh_triangles(pts)

    # estimate per-vertex gradients and magnitudes for visualization
    vertex_grads, grad_mags = compute_vertex_gradients(pts, tris)

    save = "sandbox_mesh_example.png" if not show else None
    save_html = "sandbox_mesh_example.html" if not show else None
    plot_mesh(pts, tris, extra_points=extra, vertex_gradients=vertex_grads, gradient_magnitudes=grad_mags, show=show, save_path=save, z_scale=z_scale, num_arrows=num_arrows, z_slices=z_slices)

    if HAS_PLOTLY and extra is not None:
        plot_mesh_interactive(pts, tris, extra_points=extra, open_html=show, save_path=save_html, z_scale=z_scale, aspect_z=aspect_z, z_range_pad=z_range_pad)
    elif HAS_PLOTLY and extra is None:
        plot_mesh_interactive(pts, tris, open_html=show, save_path=save_html, z_scale=z_scale, aspect_z=aspect_z, z_range_pad=z_range_pad)
    else:
        if save_html is not None:
            print("Plotly not installed; skipping interactive HTML output.")

    if save:
        print(f"Saved example mesh to {save}")


def plot_mesh_interactive(points: np.ndarray, triangles: np.ndarray, extra_points: Optional[dict] = None, open_html: bool = False, save_path: Optional[str] = None, z_scale: float = 1.0, aspect_z: Optional[float] = None, z_range_pad: float = 0.2):
    """Create an interactive HTML Plotly mesh from Nx3 points and triangle indices.

    Raises ImportError if Plotly is not available.
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly is not installed. Install with 'pip install plotly'.")

    x, y, z = points.T
    i, j, k = triangles.T
    # apply vertical exaggeration only for plotting
    z = z * z_scale
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

    pts_scatter = go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=3, color='grey'), name='vertices')

    data_traces = [mesh, pts_scatter]
    # add extra point groups as separate scatter traces
    if extra_points:
        for name, pts in extra_points.items():
            if pts is None or len(pts) == 0:
                continue
            px, py, pz = pts.T
            pz = pz * z_scale
            color = 'orange' if name.lower().startswith('house') else 'purple'
            data_traces.append(go.Scatter3d(x=px, y=py, z=pz, mode='markers', marker=dict(size=4, color=color), name=name))

    # if house exists, add a connected outline (closed loop) using the canonical house loop
    if extra_points and 'house' in extra_points:
        try:
            house_loop = get_house_loop()
            hx, hy, hz = house_loop.T
            hz = hz * z_scale
            data_traces.append(go.Scatter3d(x=hx, y=hy, z=hz, mode='lines', line=dict(color='orange', width=4), name='house_outline'))
        except Exception:
            # fall back to connecting the provided house points in order
            pts = extra_points.get('house')
            if pts is not None and len(pts) > 1:
                px, py, pz = pts.T
                data_traces.append(go.Scatter3d(x=px, y=py, z=pz, mode='lines', line=dict(color='orange', width=4), name='house_outline'))

    fig = go.Figure(data=data_traces)

    # configure scene: aspect ratio or z axis range padding
    scene = {'aspectmode': 'data'}

    # if user supplied an explicit z aspect scale, use manual aspectratio
    if aspect_z is not None:
        scene['aspectmode'] = 'manual'
        scene['aspectratio'] = dict(x=1, y=1, z=float(aspect_z))

    # optionally pad z axis range to visually extend the axis
    if z_range_pad is not None:
        zmin = float(z.min())
        zmax = float(z.max())
        if zmax == zmin:
            pad = 1.0
        else:
            pad = (zmax - zmin) * float(z_range_pad)
        scene.setdefault('zaxis', {})
        scene['zaxis']['range'] = [zmin - pad, zmax + pad]
        scene['zaxis']['title'] = 'Z (scaled)'

    fig.update_layout(title='Interactive sandbox mesh', scene=scene)

    if save_path:
        pyo.plot(fig, filename=save_path, auto_open=open_html)
    elif open_html:
        pyo.plot(fig, auto_open=True)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sandbox mesh plotter for Grundstueckshoehen")
    parser.add_argument("--show", action="store_true", help="Show the Matplotlib plot interactively instead of saving a PNG")
    parser.add_argument("--no-show", dest="show", action="store_false", help="Do not show the plot; instead save PNG/HTML output")
    parser.set_defaults(show=False)
    parser.add_argument("--use-data", dest="use_data", action="store_true", help="Use coordinates from grundstueckshoehen.data")
    parser.add_argument("--no-use-data", dest="use_data", action="store_false", help="Use the example built-in points instead of package data")
    parser.set_defaults(use_data=True)
    parser.add_argument("--triangulate-all", dest="triangulate_all", action="store_true", help="Include house and additional points in the mesh triangulation")
    parser.add_argument("--no-triangulate-all", dest="triangulate_all", action="store_false", help="Triangulate only the terrain points")
    parser.set_defaults(triangulate_all=True)
    parser.add_argument("--z-scale", type=float, default=1.0, help="Vertical exaggeration factor for Z axis")
    parser.add_argument("--aspect-z", type=float, default=None, help="Plotly Z aspect ratio scaling")
    parser.add_argument("--z-range-pad", type=float, default=0.2, help="Plotly Z-axis padding as fraction of the data range")
    parser.add_argument("--num-arrows", type=int, default=80, help="Target number of gradient arrows to draw")
    parser.add_argument("--z-slices", type=float, nargs='+', default=None, help="Space-separated Z slice levels to intersect and plot (e.g. --z-slices -0.1 0.0 0.1)")
    args = parser.parse_args()
    z_slices = args.z_slices if args.z_slices else None
    main(
        show=args.show,
        use_data=args.use_data,
        triangulate_all=args.triangulate_all,
        z_scale=args.z_scale,
        aspect_z=args.aspect_z,
        z_range_pad=args.z_range_pad,
        num_arrows=args.num_arrows,
        z_slices=z_slices,
    )
