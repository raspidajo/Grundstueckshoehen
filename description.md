Requests:

Allgemein:
- Angabe von Koordinaten von
    * Grundstückshöhen
    * Grundstücksgrenzen
    * Hausposition
    * zusätzlichen Punkten
    * Es soll einfach sein, die Koordinaten zu bearbeiten und zu erweitern
- Einzeichnen von Grundstück, Haus, zusätzlichen Punkten
    * Umriss von Haus und Grundstück soll in 3D Koordinaten-System eingezeichnet werden
        + Koordinaten Haus: A_H, B_H, C_H, D_H
        + Koordinaten Grundstück: A_G, B_G, C_G, D_G
    * Einzeichnen von zusätzlichen Punkten
        + Koordinaten zusätzliche Punkte: h_1, h_2, ...

- Erzeugen von Mesh
    * soll aus den angegeben Koordinaten ein Mesh erzeugen
    * soll Steigungen/ Gefälle farbig darstellen
        + Farbwahl nach Steigung
        + Farbwahl ob Steigung / Gefälle hin zum Haus
        

Technisches:
- Koordinaten
    * Koordinaten sind 3-D
- Mesh
    * Geht steigung hin zum haus, so soll diese rötlich sein
    * geht Steigung weg vom Haus, so soll diese grünlich sein
        + definiere dazu farbscala
        + gefälle die gegen 0 gehen, sollen richtung blau gehen
        + gib auf Farbscala das zugehörige Gefälle in prozent an
    * ist keine Steigung vorhanden, so soll dies bläulich sein
        + Komplett eben: rgb-farbe (0,200,255)


Koordinaten:

    h_E = 515.10

    A_G = (0,0,514.74-h_E)
    B_G = (18.46, 0.65, 514.80-h_E)
    C_G = (18.42, 34.98, 515.21-h_E)
    D_G = (0, 34.95, 515.21-h_E)

    A_H = (4.3, 10.51 , 0)
    B_H = (15.2, 10.51 , 0)
    C_H = (15.2 , 26.52, 0)
    D_H = (4.3 , 26.52, 0)

Umsetzung:
- Erzeuge das Mesh mittels python
    * Alternativ auch gerne anderes Tool, falls geeigneter
- Falls Python, dann erzeuge ein modular aufgebautes projekt, das sich gut erweitern lässt



