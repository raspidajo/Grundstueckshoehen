import numpy as np
import pyvista as pv

# Create a triangular surface mesh
mesh = pv.Sphere(theta_resolution=50, phi_resolution=50).triangulate()

# Scalar field sampled at each vertex
x, y, z = mesh.points.T
mesh["f"] = x**2 + y**2 + 2.0 * z

# Compute the gradient at mesh points
gradient_mesh = mesh.compute_derivative(
    scalars="f",
    gradient="grad_f",
    preference="point",
)

gradient = gradient_mesh["grad_f"]
gradient_mesh["gradient_magnitude"] = np.linalg.norm(gradient, axis=1)

# Show the derivative as mesh colors and arrows
plotter = pv.Plotter()

plotter.add_mesh(
    gradient_mesh,
    scalars="gradient_magnitude",
    cmap="viridis",
    show_edges=True,
    scalar_bar_args={"title": "|grad f|"},
)

# Reduce the number of arrows for readability
if gradient_mesh.n_points == 0:
    raise RuntimeError("Gradient mesh contains no points to sample.")

# select a subset of point indices (every 30th point)
indices = np.arange(0, gradient_mesh.n_points, 30)

# build a lightweight PolyData containing only the selected coordinates
selected_coords = gradient_mesh.points[indices]
sample = pv.PolyData(selected_coords)

# copy required point arrays (scale/orientation) into the sampled PolyData
if "gradient_magnitude" in gradient_mesh.point_data:
    sample["gradient_magnitude"] = gradient_mesh["gradient_magnitude"][indices]
elif "gradient_magnitude" in gradient_mesh.cell_data:
    # fallback: try to map cell data to points (not ideal)
    sample["gradient_magnitude"] = np.repeat(gradient_mesh["gradient_magnitude"].ravel()[:1], indices.size)

if "grad_f" in gradient_mesh.point_data:
    sample["grad_f"] = gradient_mesh["grad_f"][indices]
elif "grad_f" in gradient_mesh.cell_data:
    sample["grad_f"] = np.tile(gradient_mesh["grad_f"].ravel()[:3], (indices.size, 1))

arrows = sample.glyph(
    orient="grad_f",
    scale="gradient_magnitude",
    factor=0.08,
)

plotter.add_mesh(arrows, color="red")
plotter.show()
