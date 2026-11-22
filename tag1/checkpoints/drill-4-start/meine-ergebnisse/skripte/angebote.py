# -*- coding: utf-8 -*-
"""Erzeugt dashboard-daten/angebote.js für den Reiter „Angebote“.

Liest je Vorgang die Datei dashboard-daten/angebote/<Vorgang>.json (Kopfdaten und Regelpfad)
und den Volltext der Vorlage meine-ergebnisse/<vorlage>.md. Schreibt nur angebote.js.
Vorlagen und Vorgangsdateien werden nie verändert; ein neuer Vorgang kommt als neue JSON-Datei dazu."""
import glob
import json
import os

ERGEBNISSE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PFADE = os.path.join(ERGEBNISSE, "dashboard-daten", "angebote")
ZIEL = os.path.join(ERGEBNISSE, "dashboard-daten", "angebote.js")


def main():
    vorgaenge = []
    for datei in sorted(glob.glob(os.path.join(PFADE, "A-*.json"))):
        with open(datei, encoding="utf-8") as f:
            v = json.load(f)
        with open(os.path.join(ERGEBNISSE, v["vorlage"]), encoding="utf-8") as f:
            v["volltext"] = f.read()
        vorgaenge.append(v)
    daten = {
        "stichtag": "28.02.2027",
        "stand": "01.03.2027",
        "quelle": "Angebotseingang Tender Desk, Angebots- und Freigaberichtlinie RL-ANG-2026, Kompetenzordnung KO-2026",
        "vorgaenge": vorgaenge,
    }
    with open(ZIEL, "w", encoding="utf-8") as f:
        f.write("/* erzeugt von skripte/angebote.py, nicht von Hand ändern */\n")
        f.write("var ANGEBOTE_DATEN = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n")
    print("Vorgänge:", [v["id"] for v in vorgaenge], "->", os.path.basename(ZIEL))


if __name__ == "__main__":
    main()
