# Etappe 4: Zahlen für die Management-Summary und Vorrechnung stationäre Anlagen 2026
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lese_csv, lade_positionen, absatz, GEBINDE

pos, stat = lade_positionen()

# Tabelle Gesamt und stationäre Anlagen 2021–2026
print("Jahr | Gesamt Z / N / Pos | Anteil | stationär Z / N / Pos | Anteil")
for j in range(2021, 2027):
    for lab, f in (("Gesamt", lambda p: True), ("stationär", lambda p: p["anwendung"] == "stationaere_anlage")):
        sel = [p for p in pos if p["jahr"] == j and absatz(p) and f(p)]
        z = sum(p["liter"] for p in sel if p["linie"] == "fluorfrei")
        n = sum(p["liter"] for p in sel)
        print(j, lab, z, n, len(sel), "%.1f %%" % (100 * z / n) if len(sel) >= 20 else "Lücke")

# Vorrechnung stationäre Anlagen 2026
print("\n== Vorrechnung stationäre Anlagen 2026")
alle = lese_csv("auftraege.csv")
roh = [r for r in alle if r["lieferdatum"][:4] == "2026" and r["anwendung"] == "stationaere_anlage"]
print("Rohzeilen 2026 stationär:", len(roh))
seen = set(); dup = 0
for r in roh:
    k = (r["auftrag_id"], r["position"])
    if k in seen:
        dup += 1
    seen.add(k)
print("davon Doppelimporte (wegfallend):", dup)
sel = [p for p in pos if p["jahr"] == 2026 and p["anwendung"] == "stationaere_anlage"]
print("Positionen nach Bereinigung:", len(sel))
for art in ("Lieferung", "Gutschrift", "Retoure", "Muster"):
    print(" ", art, len([p for p in sel if p["art"] == art]), sum(p["liter"] for p in sel if p["art"] == art))
for lin in ("fluorfrei", "fluorhaltig", "offen"):
    print("  Linie", lin, sum(p["liter"] for p in sel if p["art"] != "Muster" and p["linie"] == lin))
print("Positionen mit Literumrechnung aus Gebinde (menge_l leer):", len([r for r in roh if r["menge_l"].strip() == ""]))
print("Zähler:", sum(p["liter"] for p in sel if p["art"] != "Muster" and p["linie"] == "fluorfrei"),
      "Nenner:", sum(p["liter"] for p in sel if p["art"] != "Muster"))
print("Zähler-Positionen:", [(p["auftrag_id"], p["liter"], p["produkt_id"]) for p in sel if p["linie"] == "fluorfrei"])

# Datenaufnahme
ls = [r for r in lese_csv("lieferstellen.csv") if r["anwendung"] == "stationaere_anlage"]
print("\nStationäre Anlagen im Stamm:", len(ls), "mit Datenaufnahme:", len([r for r in ls if r["datenaufnahme_am"]]))
# stationäre Anlagen mit Lieferung 2026
ls26 = set(p["lieferstelle_id"] for p in sel)
print("stationäre Lieferstellen mit Lieferung 2026:", len(ls26))
for r in ls:
    if r["lieferstelle_id"] in ls26 and r["datenaufnahme_am"]:
        pass
print("davon mit Datenaufnahme:", len([r for r in ls if r["lieferstelle_id"] in ls26 and r["datenaufnahme_am"]]))
# zumischrate abweichend
ab = [(r["lieferstelle_id"], r["zumischrate_anlage"], r["zumischrate_crm"]) for r in ls if r["datenaufnahme_am"] and r["zumischrate_anlage"] != r["zumischrate_crm"]]
print("Datenaufnahme mit abweichender Zumischrate zum CRM:", len(ab), ab)
# Nachfolgeprodukt vorhanden?
prod = {r["id"]: r for r in lese_csv("produkte.csv")}
print("aktuelle Produkte stationär:", sorted(set((r["aktuelles_produkt_id"], prod[r["aktuelles_produkt_id"]]["produktlinie"]) for r in ls)))
