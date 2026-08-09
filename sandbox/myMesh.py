import numpy as np
import plotly.graph_objects as go
from scipy.spatial import Delaunay

# Example: n x 3 matrix (replace with your own)
points = np.array([
    [0, 0, 0],
    [1, 0, 1],
    [0, 1, 1],
    [1, 1, 0],
    [0.5, 0.5, 2]
])

# Triangulate in XY plane
tri = Delaunay(points[:, :2])

# Build mesh
fig = go.Figure(data=[
    go.Mesh3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        i=tri.simplices[:, 0],
        j=tri.simplices[:, 1],
        k=tri.simplices[:, 2],
        color='lightblue',
        opacity=0.50
    )
])

fig.update_layout(
    title="Simple Mesh from n×3 Matrix",
    scene=dict(aspectmode='data')
)

fig.show()
