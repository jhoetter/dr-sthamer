import csv
from collections import defaultdict

KID = "K-1003"
GEB = {"IBC": 1000, "Fass": 200, "Kanister": 20, "l": 1}


def lies(pfad):
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


produkte = dict((p["id"], p) for p in lies("daten/produkte.csv"))
for k in lies("daten/kunden.csv"):
    if k["id"] == KID:
        print("KUNDE", k)

print("LIEFERSTELLEN")
for r in lies("daten/lieferstellen.csv"):
    if r["kunde_id"] == KID:
        p = produkte[r["aktuelles_produkt_id"]]
        print(" ", r["lieferstelle_id"], r["anlage"], r["anwendung"], r["aktuelles_produkt_id"], p["name"],
              p["produktlinie"], "deklariert:", p["fluorfrei_deklariert"], "Fuell", r["fuellmenge_l"],
              "letzte", r["letzte_lieferung"], "Datenaufnahme", r["datenaufnahme_am"] or "-",
              "Rate Anlage", r["zumischrate_anlage"] or "-", "Rate CRM", r["zumischrate_crm"],
              "Rate Produkt", p["zumischrate_prozent"])

gesehen = set()
je_jahr = defaultdict(lambda: defaultdict(float))
dopp = 0
for r in lies("daten/auftraege.csv"):
    key = (r["auftrag_id"], r["position"])
    if key in gesehen:
        if r["kunde_id"] == KID:
            dopp += 1
        continue
    gesehen.add(key)
    if r["kunde_id"] != KID:
        continue
    ml = r["menge_l"]
    liter = float(ml) if ml else float(r["menge"]) * GEB[r["einheit"]]
    jahr = r["lieferdatum"][:4]
    p = produkte[r["produkt_id"]]
    if r["art"] == "Muster":
        je_jahr[jahr]["muster"] += liter
    else:
        je_jahr[jahr][p["produktlinie"]] += liter
        je_jahr[jahr]["netto_gesamt"] += liter
        if r["art"] != "Lieferung":
            je_jahr[jahr]["abzug_" + r["art"]] += liter
print("AUFTRAEGE je Jahr (Liter netto, ohne Doppelimporte, ohne Muster; Doppelimporte K-1003:", dopp, ")")
for j in sorted(je_jahr):
    print(" ", j, dict((k, round(v, 1)) for k, v in je_jahr[j].items()))

print("REKLAMATIONEN")
for r in lies("daten/reklamationen.csv"):
    if r["kunde_id"] == KID:
        print(" ", r)

print("KONTAKTE")
n = 0
for r in lies("daten/kontakte.csv"):
    if r["kunde_id"] == KID:
        n += 1
        print(" ", r["datum"], r["kanal"], r["richtung"], r["bearbeitung"], "|", r["betreff"], "|", r["dokument"])
print("Kontakte gesamt:", n)
