"""Kundenzahl nach verschiedenen Zählweisen (Drill 0). Nur Lesen, nichts in daten/ ändern."""
import csv
import json
from collections import defaultdict, Counter
from datetime import date


def lies(pfad):
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


kunden = lies("daten/kunden.csv")
lst = lies("daten/lieferstellen.csv")
auftr = lies("daten/auftraege.csv")
stichtag = date(2027, 2, 28)
grenze24 = date(2025, 3, 1)
grenze12 = date(2026, 3, 1)


def region(k):
    return "Deutschland" if k["land"] == "DE" else "Ausland"


def zaehle(ids):
    c = Counter(region(k) for k in kunden if k["id"] in ids)
    return c["Deutschland"], c["Ausland"], len(ids)


alle = {k["id"] for k in kunden}
print("A Kundenstamm gesamt:", zaehle(alle))
print("   Länder:", dict(Counter(k["land"] for k in kunden)))

aktiv_status = {k["id"] for k in kunden if k["status"] == "aktiv"}
print("B Status aktiv im Kundenstamm:", zaehle(aktiv_status))
print("   ruhend im Stamm:", [k["id"] for k in kunden if k["status"] == "ruhend"])

# Lieferungen, ohne Doppelimporte
gesehen = set()
letzte = {}
art_je_kunde = defaultdict(Counter)
for r in auftr:
    key = (r["auftrag_id"], r["position"])
    doppel = key in gesehen
    gesehen.add(key)
    if doppel:
        continue
    art_je_kunde[r["kunde_id"]][r["art"]] += 1
    if r["art"] == "Lieferung":
        d = date.fromisoformat(r["lieferdatum"])
        if r["kunde_id"] not in letzte or d > letzte[r["kunde_id"]]:
            letzte[r["kunde_id"]] = d

print("   Doppelimporte (Positionen):", len(auftr) - len(gesehen))

aktiv24 = {k for k, d in letzte.items() if grenze24 <= d <= stichtag}
print("C Auftrag (Lieferung) in 24 Monaten:", zaehle(aktiv24))
status = {}
for k in kunden:
    d = letzte.get(k["id"])
    if d is None or d < grenze24:
        status[k["id"]] = "verloren"
    elif d < grenze12:
        status[k["id"]] = "ruhend"
    else:
        status[k["id"]] = "aktiv"
print("   Kundenstatus nach letzter Lieferung:", Counter(status.values()))
for s in ("aktiv", "ruhend", "verloren"):
    print("   ", s, zaehle({i for i, v in status.items() if v == s}))
for k in kunden:
    if status[k["id"]] != "aktiv" or k["status"] != "aktiv":
        print("   Abweichung:", k["id"], k["name"], k["land"], "Stamm:", k["status"],
              "letzte Lieferung:", letzte.get(k["id"]), "->", status[k["id"]])

# Kunden ohne Händler
haendler = {k["id"] for k in kunden if k["ist_haendler"] == "ja"}
print("   Händler:", sorted(haendler))
print("D Aktive Kunden (24 Mon.) ohne Händler:", zaehle(aktiv24 - haendler))
print("   Händler mit Lieferung in 24 Monaten:", sorted(haendler & aktiv24))

# Endkunden über Händler
end = set()
for k in kunden:
    if k["beliefert_endkunden"]:
        for e in k["beliefert_endkunden"].split(";"):
            end.add(e)
print("E Über Händler belieferte Endkunden:", sorted(end), zaehle(end))
# Kunden, die direkt keine Aufträge haben, nur über Händler?
auftr_ids = set(art_je_kunde.keys())
print("   Kunden ohne eigene Aufträge:", sorted(alle - auftr_ids))
print("   Endkunden mit eigenen Aufträgen:", sorted(end & auftr_ids))
# Aufträge von Endkunden nach Vertriebsweg
vw = defaultdict(Counter)
for r in auftr:
    if r["kunde_id"] in end:
        vw[r["kunde_id"]][r["vertriebsweg"]] += 1
print("   Vertriebswege der Endkunden:", {k: dict(v) for k, v in vw.items()})
# Kunden mit Muster/Notfall nur
for k in kunden:
    c = art_je_kunde.get(k["id"], Counter())
    if c.get("Lieferung", 0) == 0:
        print("   keine Lieferung:", k["id"], dict(c))

# Lieferstellen
lstd = {k["id"]: region(k) for k in kunden}
c = Counter(lstd[r["kunde_id"]] for r in lst)
print("F Lieferstellen gesamt:", dict(c), len(lst))
lst_akt = [r for r in lst if date.fromisoformat(r["letzte_lieferung"]) >= grenze24]
c2 = Counter(lstd[r["kunde_id"]] for r in lst_akt)
print("   Lieferstellen mit Lieferung in 24 Monaten:", dict(c2), len(lst_akt))
print("   Lieferstellen je Kunde (Spanne):",
      min(Counter(r["kunde_id"] for r in lst).values()),
      max(Counter(r["kunde_id"] for r in lst).values()))
print("   Kunden ohne Lieferstelle:", sorted(alle - {r["kunde_id"] for r in lst}))
