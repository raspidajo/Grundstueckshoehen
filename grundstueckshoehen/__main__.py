import argparse

from .data import get_terrain_points
from .mesh import create_mesh, compute_triangle_slopes
from .plot import plot_terrain


def main():
    parser = argparse.ArgumentParser(description="Generiere ein Gelände-Mesh und visualisiere Steigungen.")
    parser.add_argument("--output", default="terrain_mesh.png", help="Dateipfad zum gespeicherten Bild")
    parser.add_argument("--show", action="store_true", help="Zeige die Grafik interaktiv an")
    args = parser.parse_args()

    points = get_terrain_points()
    triangles = create_mesh(points)
    slopes = compute_triangle_slopes(points, triangles)
    fig, _ = plot_terrain(points, triangles, slopes, save_path=args.output)

    print(f"Mesh erzeugt und gespeichert in: {args.output}")
    if args.show:
        fig.show()


if __name__ == "__main__":
    main()
