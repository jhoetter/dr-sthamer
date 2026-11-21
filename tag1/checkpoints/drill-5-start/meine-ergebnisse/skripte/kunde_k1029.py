import csv
import datetime


def lies(pfad):
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


auf = lies("daten/auftraege.csv")
letzte = {}
for r in auf:
    if r["art"] != "Lieferung":
        continue
    d = datetime.date.fromisoformat(r["lieferdatum"])
    if r["kunde_id"] not in letzte or d > letzte[r["kunde_id"]]:
        letzte[r["kunde_id"]] = d
print("Aelteste 'letzte Lieferung' je Kunde (5 aelteste):")
for k, d in sorted(letzte.items(), key=lambda x: x[1])[:5]:
    print("  ", k, d)

print("K-1029, Lieferungen ab 2025:")
for r in auf:
    if r["kunde_id"] == "K-1029" and r["lieferdatum"] >= "2025-01-01":
        print("  ", r["auftrag_id"], r["position"], r["lieferdatum"], r["art"], r["produkt_id"],
              r["menge_l"], r["nettobetrag"], r["waehrung"], r["vertriebsweg"])
print("K-1029 Zeilen insgesamt:", sum(1 for r in auf if r["kunde_id"] == "K-1029"))
