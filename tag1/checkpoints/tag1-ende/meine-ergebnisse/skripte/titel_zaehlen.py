# -*- coding: utf-8 -*-
"""Zählt Wörter und Zeichen (mit Leerzeichen) der Folientitel aus meine-ergebnisse/skripte/d5/titel.txt (ein Titel je Zeile)."""
import os
import sys

basis = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
pfad = sys.argv[1] if len(sys.argv) > 1 else os.path.join(basis, "meine-ergebnisse", "skripte", "d5", "titel.txt")
with open(pfad, encoding="utf-8") as f:
    zeilen = [z.strip() for z in f if z.strip()]
for i, t in enumerate(zeilen, 1):
    t = t.replace(" ", " ")
    print(i, len(t.split()), "Wörter", len(t), "Zeichen |", t)
