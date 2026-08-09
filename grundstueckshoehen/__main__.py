import argparse

from .data import get_terrain_points
from .mesh import create_mesh, compute_triangle_slopes, create_mesh_triangles
from .plot import plot_terrain, plot_terrain_interactive, plot_mesh


def main():
    parser = argparse.ArgumentParser(description="Generiere ein Gelände-Mesh und visualisiere Steigungen.")
    parser.add_argument("--output", default="terrain_mesh.png", help="Dateipfad zum gespeicherten Bild oder HTML")
    parser.add_argument("--show", action="store_true", help="Zeige die Matplotlib-Grafik interaktiv an")
    parser.add_argument("--interactive", action="store_true", help="Erzeuge eine interaktive Plotly-HTML-Ausgabe")
    parser.add_argument("--open", action="store_true", help="Öffne die interaktive HTML-Ausgabe automatisch im Browser")
    args = parser.parse_args()

    if args.demo:
        # simple demo using a regular grid (matches sandbox/myMesh behaviour)
        import numpy as np

        xs = np.linspace(0, 10, 12)
        ys = np.linspace(0, 8, 10)
        xv, yv = np.meshgrid(xs, ys)
        zv = np.sin(xv / 2) * np.cos(yv / 3) * 0.5
        points = np.column_stack([xv.ravel(), yv.ravel(), zv.ravel()])
        triangles = create_mesh_triangles(points)
        fig, _ = plot_mesh(points, triangles, show=args.show, save_path=(None if args.show else args.output))
        if not args.show:
            print(f"Demo mesh saved to {args.output}")
        return fig

    points = get_terrain_points()
    triangles = create_mesh(points)
    slopes = compute_triangle_slopes(points, triangles)

    if args.interactive:
        fig = plot_terrain_interactive(points, triangles, slopes, save_path=args.output, open_html=args.open)
        print(f"Interaktives HTML gespeichert in: {args.output}")
    else:
        fig, _ = plot_terrain(points, triangles, slopes, save_path=args.output)
        print(f"Mesh erzeugt und gespeichert in: {args.output}")
        if args.show:
            fig.show()

    return fig


if __name__ == "__main__":
    main()
