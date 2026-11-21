# Reiter „Überblick“: erzeugt dashboard-daten/ueberblick.js
# Definitionen: siehe kennzahlen.json (Fluorfrei-Anteil, aktiver Kunde); Kunden nach Notiz Drill 0
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lese_csv, lade_positionen, absatz, BASIS

pos, stat = lade_positionen()
kunden = {r["id"]: r for r in lese_csv("kunden.csv")}
lieferstellen = lese_csv("lieferstellen.csv")


def periode(p):
    return "2027T" if p["jahr"] == 2027 else str(p["jahr"])


# Zellen: Zeitraum x Segment x Land x Vertriebsweg x Anwendung (ohne Muster)
zellen = defaultdict(lambda: {"l": 0.0, "ff": 0.0, "fh": 0.0, "u": 0.0, "n": 0})
for p in pos:
    if not absatz(p):
        continue
    k = (periode(p), p["segment"], p["land"], p["vertriebsweg"], p["anwendung"])
    z = zellen[k]
    z["l"] += p["liter"]
    if p["linie"] == "fluorfrei":
        z["ff"] += p["liter"]
    elif p["linie"] == "fluorhaltig":
        z["fh"] += p["liter"]
    z["u"] += p["umsatz_eur"]
    z["n"] += 1

zellen_liste = []
for k, z in sorted(zellen.items()):
    zellen_liste.append({"j": k[0], "seg": k[1], "land": k[2], "weg": k[3], "anw": k[4],
                         "l": round(z["l"], 2), "ff": round(z["ff"], 2), "fh": round(z["fh"], 2),
                         "u": round(z["u"], 2), "n": z["n"]})

# Kunden: aktiv nach Definition (Lieferung ab 01.03.2025); Vertriebswege dieser Lieferungen
wege = defaultdict(set)
for p in pos:
    if p["art"] == "Lieferung" and p["datum"] >= "2025-03-01":
        wege[p["kunde_id"]].add(p["vertriebsweg"])
anw_kunde = defaultdict(set)
for r in lieferstellen:
    anw_kunde[r["kunde_id"]].add(r["anwendung"])
kunden_liste = []
for kid in sorted(wege):
    k = kunden[kid]
    kunden_liste.append({"id": kid, "seg": k["segment"], "land": k["land"],
                         "wege": sorted(wege[kid]), "anw": sorted(anw_kunde[kid])})

# Lieferstellen (Stamm); Vertriebswege = Wege aller bisherigen Lieferungen an die Lieferstelle
ls_wege = defaultdict(set)
for p in pos:
    if p["art"] == "Lieferung":
        ls_wege[p["lieferstelle_id"]].add(p["vertriebsweg"])
ls_liste = []
for r in lieferstellen:
    k = kunden[r["kunde_id"]]
    ls_liste.append({"seg": k["segment"], "land": k["land"], "anw": r["anwendung"],
                     "wege": sorted(ls_wege[r["lieferstelle_id"]])})

daten = {
    "stichtag": "28.02.2027",
    "ziel": 60,
    "zellen": zellen_liste,
    "kunden": kunden_liste,
    "lieferstellen": ls_liste,
    "segmente": sorted(set(k["segment"] for k in kunden.values())),
    "laender": sorted(set(k["land"] for k in kunden.values())),
    "wege": ["direkt", "Händler", "Rahmenvertrag", "Notfallservice"],
    "anwendungen": sorted(set(r["anwendung"] for r in lieferstellen)),
    "statistik": stat,
}

ziel = os.path.join(BASIS, "meine-ergebnisse", "dashboard-daten")
os.makedirs(ziel, exist_ok=True)
with open(os.path.join(ziel, "ueberblick.js"), "w", encoding="utf-8") as f:
    f.write("const UEBERBLICK = " + json.dumps(daten, ensure_ascii=False) + ";\n")
print("Zellen:", len(zellen_liste), "Kunden:", len(kunden_liste), "Lieferstellen:", len(ls_liste))
print("Segmente:", daten["segmente"])
print("Länder:", daten["laender"])
