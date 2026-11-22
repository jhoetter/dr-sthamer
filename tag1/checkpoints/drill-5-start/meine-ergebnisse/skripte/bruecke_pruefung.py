import csv
import json
from collections import defaultdict

D = "daten/"


def rd(n):
    with open(D + n, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


kz = json.load(open(D + "kennzahlen.json", encoding="utf-8-sig"))
GEB = kz["definitionen"]["umrechnung_gebinde"]
konzern = kz["konzernkurse"]["kurse"]["2026"]

kurs = {(r["monat"], r["waehrung"]): float(r["ist_kurs_eur"]) for r in rd("kurse.csv")}
hk = {(r["produkt_id"], r["jahr"]): float(r["rohstoff_eur_l"]) + float(r["fertigung_eur_l"])
      for r in rd("herstellkosten.csv")}
fracht = {}
for r in rd("fracht.csv"):
    fracht[r["auftrag_id"]] = fracht.get(r["auftrag_id"], 0) + float(r["frachtkosten_eur"])
fr_rows = len(rd("fracht.csv"))

# Budget
bud_db = bud_um = bud_l = 0.0
for r in rd("budget_2026.csv"):
    bud_db += float(r["db_eur"]); bud_um += float(r["umsatz_eur"]); bud_l += float(r["menge_l"])

# Positionen bereinigen
seen = set()
pos = []
dups = 0
for r in rd("auftraege.csv"):
    k = (r["auftrag_id"], r["position"])
    if k in seen:
        dups += 1
        continue
    seen.add(k)
    if not r["lieferdatum"].startswith("2026"):
        continue
    ml = r["menge_l"].strip()
    r["l"] = float(ml) if ml else float(r["menge"]) * GEB[r["einheit"]]
    pos.append(r)

# Fracht-Verteilung je Auftrag nach Litern (Lieferung/Muster-Positionen, alle Jahre des Auftrags)
# Basis: alle (deduplizierten) Positionen des Auftrags, auch aus anderen Jahren
allpos = defaultdict(list)
seen2 = set()
for r in rd("auftraege.csv"):
    k = (r["auftrag_id"], r["position"])
    if k in seen2:
        continue
    seen2.add(k)
    if r["art"] in ("Lieferung", "Muster"):
        ml = r["menge_l"].strip()
        l = float(ml) if ml else float(r["menge"]) * GEB[r["einheit"]]
        allpos[r["auftrag_id"]].append((r["position"], l))
tot_l = {a: sum(l for _, l in v) for a, v in allpos.items()}
mism = sum(1 for r in rd("fracht.csv") if r["auftrag_id"] in tot_l and abs(tot_l[r["auftrag_id"]] - float(r["liter"])) > 0.5)

res = {"ist": defaultdict(float), "ohne": defaultdict(float), "notfall": defaultdict(float)}
for r in pos:
    art = r["art"]
    l = r["l"]
    m = r["lieferdatum"][:7]
    fx = 1.0 if r["waehrung"] == "EUR" else kurs[(m, r["waehrung"])]
    um = float(r["nettobetrag"]) * fx if art != "Muster" else 0.0
    ab = 0.0 if art == "Muster" else l
    kost = 0.0
    if art in ("Lieferung", "Muster", "Retoure"):
        kost = l * hk[(r["produkt_id"], "2026")]
    fr = 0.0
    if art in ("Lieferung", "Muster") and r["auftrag_id"] in fracht and tot_l.get(r["auftrag_id"]):
        fr = fracht[r["auftrag_id"]] * l / tot_l[r["auftrag_id"]]
    keys = ["ist"] + (["notfall"] if r["vertriebsweg"] == "Notfallservice" else ["ohne"])
    for kk in keys:
        res[kk]["um"] += um; res[kk]["hk"] += kost; res[kk]["fr"] += fr; res[kk]["l"] += ab

print("Doppelimporte entfernt:", dups, "| Fracht-Liter-Abweichungen:", mism)
print("Budget: DB %.2f Umsatz %.2f Liter %.0f" % (bud_db, bud_um, bud_l))
for k, v in res.items():
    print(k, "Umsatz %.2f HK %.2f Fracht %.2f DB %.2f Liter %.1f" % (v["um"], v["hk"], v["fr"], v["um"] - v["hk"] - v["fr"], v["l"]))
