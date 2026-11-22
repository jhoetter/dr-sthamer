"""Notfall-Lieferungen September 2026 aus der Auftragstabelle (nur Lesen)."""
import csv
from collections import OrderedDict

GEBINDE = {"IBC": 1000, "Fass": 200, "Kanister": 20}

zeilen = []
with open("daten/auftraege.csv", encoding="utf-8-sig", newline="") as f:
    for z in csv.DictReader(f):
        if z["auftragsart"] == "Notfall" and z["lieferdatum"].startswith("2026-09"):
            zeilen.append(z)

print("Positionen Notfall im September 2026:", len(zeilen))
# Doppelimporte: gleiche Auftragsnummer + Position nur einmal
gesehen = OrderedDict()
for z in zeilen:
    gesehen.setdefault((z["auftrag_id"], z["position"]), z)
print("nach Entfernen von Doppelimporten:", len(gesehen))

je_tag = OrderedDict()
for (aid, pos), z in gesehen.items():
    try:
        liter = float(z["menge_l"]) if z["menge_l"] else None
    except ValueError:
        liter = None
    if liter is None:
        liter = float(z["menge"]) * GEBINDE.get(z["einheit"], 0)
    k = (z["lieferdatum"], z["auftrag_id"], z["kunde_id"], z["quellsystem"])
    je_tag[k] = je_tag.get(k, 0) + liter

for k, l in je_tag.items():
    print(k, "Liter:", l)
