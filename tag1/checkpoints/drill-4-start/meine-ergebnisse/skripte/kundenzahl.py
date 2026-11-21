import csv
import datetime
from collections import defaultdict, Counter


def lies(pfad):
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


kunden = lies("daten/kunden.csv")
ls = lies("daten/lieferstellen.csv")
auf = lies("daten/auftraege.csv")

stichtag = datetime.date(2027, 2, 28)
# 24 Monate vor dem Stichtag: ab 01.03.2025 (Variante: ab 28.02.2025)
grenze = datetime.date(2025, 3, 1)
grenze_alt = datetime.date(2025, 2, 28)


def de(code):
    return "Deutschland" if code == "DE" else "Ausland"


def zaehle(ids):
    c = Counter()
    for k in kunden:
        if k["id"] in ids:
            c[de(k["land"])] += 1
    return c


alle = set(k["id"] for k in kunden)
print("Kundenstamm", len(alle), zaehle(alle))

aktiv_status = set(k["id"] for k in kunden if k["status"] == "aktiv")
print("Status aktiv", len(aktiv_status), zaehle(aktiv_status))
print("ruhend:", [(k["id"], k["name"]) for k in kunden if k["status"] != "aktiv"])

# Doppelimporte entfernen
gesehen = set()
pos = []
dopp = 0
for r in auf:
    key = (r["auftrag_id"], r["position"])
    if key in gesehen:
        dopp += 1
        continue
    gesehen.add(key)
    pos.append(r)
print("Positionen", len(auf), "Doppelimporte", dopp, "bereinigt", len(pos))

letzte = {}
for r in pos:
    if r["art"] != "Lieferung":
        continue
    d = datetime.date.fromisoformat(r["lieferdatum"])
    if d > stichtag:
        continue
    if r["kunde_id"] not in letzte or d > letzte[r["kunde_id"]]:
        letzte[r["kunde_id"]] = d

akt24 = set(k for k, d in letzte.items() if d >= grenze)
akt24_alt = set(k for k, d in letzte.items() if d >= grenze_alt)
print("Aktiv nach 24 Monaten (ab 01.03.2025)", len(akt24), zaehle(akt24))
print("Variante ab 28.02.2025", len(akt24_alt), zaehle(akt24_alt))
print("Nicht aktiv nach Definition:")
for k in kunden:
    if k["id"] not in akt24:
        print("  ", k["id"], k["name"], k["land"], k["status"], k["ist_haendler"],
              "letzte Lieferung", letzte.get(k["id"]))

# Aktiv nach Definition, aber Status ruhend / umgekehrt
print("Status aktiv, aber ohne Lieferung in 24 Mon.:", sorted(aktiv_status - akt24))
print("Status ruhend, aber mit Lieferung in 24 Mon.:", sorted(akt24 - aktiv_status))

# ohne Haendler
haendler = set(k["id"] for k in kunden if k["ist_haendler"] == "ja")
print("Haendler", sorted(haendler))
ohne_h = alle - haendler
print("Kundenstamm ohne Haendler", len(ohne_h), zaehle(ohne_h))
print("Aktiv 24 Mon. ohne Haendler", len(akt24 - haendler), zaehle(akt24 - haendler))

# Endkunden ueber Haendler
end = set()
for k in kunden:
    if k["beliefert_endkunden"]:
        for e in k["beliefert_endkunden"].split(";"):
            end.add(e)
print("Endkunden ueber Haendler", sorted(end))
land = dict((k["id"], k["land"]) for k in kunden)
direkt_gelief = set(r["kunde_id"] for r in pos if r["art"] == "Lieferung" and r["vertriebsweg"] != "Händler")
print("Vertriebswege je Kunde (direkt beliefert, nicht Haendlerweg):", len(direkt_gelief))
for e in sorted(end):
    print("  ", e, land[e], "direkt beliefert:", e in direkt_gelief,
          "Haendlerweg:", any(r["kunde_id"] == e and r["vertriebsweg"] == "Händler" for r in pos))
print("Vertriebsweg Haendler in Auftraegen, Kunden:",
      sorted(set(r["kunde_id"] for r in pos if r["vertriebsweg"] == "Händler")))

# Lieferstellen
lsz = Counter()
ls_je_kunde = Counter()
for r in ls:
    lsz[de(land[r["kunde_id"]])] += 1
    ls_je_kunde[r["kunde_id"]] += 1
print("Lieferstellen", len(ls), lsz)
ls_ids = set(r["kunde_id"] for r in ls)
print("Kunden ohne Lieferstelle:", sorted(alle - ls_ids))
print("Lieferstellen je Kunde:", dict(sorted(ls_je_kunde.items())))

# Lieferstellen mit Lieferung in 24 Monaten
lsl = Counter()
for r in ls:
    if r["letzte_lieferung"] and datetime.date.fromisoformat(r["letzte_lieferung"]) >= grenze:
        lsl[de(land[r["kunde_id"]])] += 1
print("Lieferstellen mit letzter Lieferung ab 01.03.2025", sum(lsl.values()), lsl)

# Lieferungen an Lieferstellen von Kunden: Kunde der Lieferstelle == Kunde des Auftrags?
lsk = dict((r["lieferstelle_id"], r["kunde_id"]) for r in ls)
abw = [(r["auftrag_id"], r["position"], r["kunde_id"], r["lieferstelle_id"]) for r in pos
       if r["lieferstelle_id"] in lsk and lsk[r["lieferstelle_id"]] != r["kunde_id"]]
print("Auftraege, bei denen Lieferstelle zu anderem Kunden gehoert:", len(abw), abw[:5])
