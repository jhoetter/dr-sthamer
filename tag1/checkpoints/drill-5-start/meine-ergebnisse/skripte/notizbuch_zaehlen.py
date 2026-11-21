# -*- coding: utf-8 -*-
"""Zählt die Notizen je Ordner und sammelt alle Aufgabenzeilen (Checkboxen) des Notizbuchs.
Nur lesen, nichts am Notizbuch ändern. Ausgabe: meine-ergebnisse/_sim/notizbuch-aufgaben.txt"""
import os
import re
from collections import OrderedDict

ROOT = "notizbuch"
AUS = os.path.join("meine-ergebnisse", "skripte", "notizbuch-aufgaben.txt")

zaehler = OrderedDict()
aufgaben = []
for pfad, ordner, dateien in os.walk(ROOT):
    ordner.sort()
    for d in sorted(dateien):
        if not d.endswith(".md"):
            continue
        rel = os.path.relpath(os.path.join(pfad, d), ROOT)
        teile = rel.split(os.sep)
        gruppe = teile[0] if len(teile) > 1 else "(Wurzel)"
        zaehler[gruppe] = zaehler.get(gruppe, 0) + 1
        with open(os.path.join(pfad, d), encoding="utf-8-sig") as f:
            for nr, zeile in enumerate(f, 1):
                if re.match(r"\s*- \[( |x)\]", zeile):
                    aufgaben.append((rel, nr, zeile.rstrip()))

gesamt = sum(zaehler.values())
zeilen = ["Notizen je Ordner:"]
for k, v in zaehler.items():
    zeilen.append("  %s: %d" % (k, v))
zeilen.append("Gesamt: %d" % gesamt)
zeilen.append("")
zeilen.append("Aufgabenzeilen insgesamt: %d (offen: %d, abgehakt: %d)" % (
    len(aufgaben),
    sum(1 for a in aufgaben if "[ ]" in a[2]),
    sum(1 for a in aufgaben if "[x]" in a[2])))
for rel, nr, z in aufgaben:
    zeilen.append("%s:%d: %s" % (rel, nr, z.strip()))

with open(AUS, "w", encoding="utf-8") as f:
    f.write("\n".join(zeilen) + "\n")
print("\n".join(zeilen[:12]))
