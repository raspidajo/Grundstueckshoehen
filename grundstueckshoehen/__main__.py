import argparse

from .data import get_terrain_points
from .mesh import create_mesh, compute_triangle_slopes
from .plot import plot_terrain, plot_terrain_interactive


def main():
    parser = argparse.ArgumentParser(description="Generiere ein Gelände-Mesh und visualisiere Steigungen.")
    parser.add_argument("--output", default="terrain_mesh.png", help="Dateipfad zum gespeicherten Bild oder HTML")
    parser.add_argument("--show", action="store_true", help="Zeige die Matplotlib-Grafik interaktiv an")
    parser.add_argument("--interactive", action="store_true", help="Erzeuge eine interaktive Plotly-HTML-Ausgabe")
    parser.add_argument("--open", action="store_true", help="Öffne die interaktive HTML-Ausgabe automatisch im Browser")
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()
