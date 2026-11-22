# -*- coding: utf-8 -*-
"""Zählt die Seiten von meine-ergebnisse/praesentation.pdf und die Folien-Abschnitte im HTML (Standardbibliothek)."""
import os
import re

basis = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "meine-ergebnisse")
with open(os.path.join(basis, "praesentation.pdf"), "rb") as f:
    daten = f.read()
seiten = len(re.findall(rb"/Type\s*/Page[^s]", daten))
print("PDF-Größe:", len(daten), "Bytes | Seiten:", seiten)
m = re.findall(rb"/MediaBox\s*\[([^\]]*)\]", daten)
print("Seitenformat (erste):", m[:1])
with open(os.path.join(basis, "praesentation.html"), encoding="utf-8") as f:
    h = f.read()
i = h.index('<main class="buehne"')
j = h.index("</main>")
print("Folien im main-Block:", h[i:j].count('<section class="folie"'))
print("Notizblöcke:", h[i:j].count('<aside class="notizen">'))
zeiten = re.findall(r"Zeit: (\d+) Minute", h[i:j])
print("Zeiten je Folie:", zeiten, "Summe:", sum(int(z) for z in zeiten))
print("eckige Klammern im main-Block (Platzhalter?):", len(re.findall(r"\[[A-Za-zÄÖÜ]", h[i:j])))
