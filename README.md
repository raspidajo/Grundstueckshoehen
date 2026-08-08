# Grundstueckshoehen

Python-Projekt zum Visualisieren eines Grundstücks und Hausumrisses als 3D-Mesh mit farbcodierter Steigungsdarstellung.

## Installation

1. Python 3.10+ installieren
2. Im Projektverzeichnis ein virtuelles Environment anlegen:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Nutzung

```bash
python -m grundstueckshoehen --output terrain_mesh.png --show
```

## Projektstruktur

- `grundstueckshoehen/data.py` – Koordinaten, Basisdaten und Punktdefinitionen
- `grundstueckshoehen/mesh.py` – Mesherzeugung und Steigungsberechnung
- `grundstueckshoehen/plot.py` – 3D-Visualisierung und Farbskala
- `grundstueckshoehen/__main__.py` – CLI zum Erzeugen und Anzeigen

## Erweiterung

- Weitere `ADDITIONAL_POINTS` in `grundstueckshoehen/data.py` einfügen
- Eigene Mesh-Filter oder Triangulationslogik ergänzen
- Farbskala oder Ausgabedateiformat anpassen
