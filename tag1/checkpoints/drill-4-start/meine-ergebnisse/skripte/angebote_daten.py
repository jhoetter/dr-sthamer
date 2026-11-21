# Etappe 1/2 Drill 3: Stammdaten zu den Angebotsvorgaengen pruefen (nur lesen)
import csv
import os

BASIS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def lies(name):
    with open(os.path.join(BASIS, "daten", name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


auf = lies("auftraege.csv")
print("Spalten Auftraege:", list(auf[0].keys()))
for kid in ("K-1018", "K-1019", "K-1020"):
    zeilen = [z for z in auf if z.get("kunde_id") == kid]
    liefer = [z for z in zeilen if z.get("art") == "Lieferung"]
    print("\n", kid, "Zeilen", len(zeilen), "Lieferungen", len(liefer))
    daten = sorted(z["lieferdatum"] for z in liefer)
    if daten:
        print("  erste/letzte Lieferung:", daten[0], daten[-1])
    for z in sorted(zeilen, key=lambda r: r["lieferdatum"])[-6:]:
        print("  ", z["lieferdatum"], z["art"], z["produkt_id"], z.get("gebinde"), z.get("menge"), z.get("menge_l"), z.get("nettobetrag"), z.get("waehrung"))

hk = lies("herstellkosten.csv")
print("\nHerstellkosten")
for z in hk:
    if z["produkt_id"] in ("P-201", "P-202", "P-204") and z["jahr"] in ("2025", "2026"):
        print(" ", z)

fr = lies("fracht.csv")
print("\nFracht-Spalten", list(fr[0].keys()))

ls = lies("lieferstellen.csv")
for z in ls:
    if z["kunde_id"] in ("K-1018", "K-1019", "K-1020"):
        print(z["lieferstelle_id"], z["anlage"], z["anwendung"], z["datenaufnahme_am"] or "-", z["zumischrate_anlage"] or "-", z["zumischrate_crm"] or "-")
