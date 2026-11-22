# -*- coding: utf-8 -*-
"""Etappe 1: Nettoumsatz, Herstellkosten, Fracht, Deckungsbeitrag, DB-Marge 2025 und 2026
je Vertriebsweg und Schaumart (Konzernkurs des Lieferjahres), nur Ausgabe im Chat."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finanz_basis as fb

pos, kd, prod, pruef = fb.lade()
print("Prüfung: Fracht-Zeilen", pruef["auftraege_mit_fracht"], "| Fracht ohne Auftrag", pruef["fracht_ohne_auftrag"],
      "| Auftrag mit abweichenden Litern in fracht.csv", pruef["fracht_liter_abweichend"],
      "| Positionen ohne Herstellkostensatz", pruef["positionen_ohne_hk"], "| doppelte Fracht-Aufträge", pruef["fracht_doppelt"])
arten = {}
for p in pos:
    arten[p["art"]] = arten.get(p["art"], 0) + 1
print("Positionen nach Art (bereinigt):", arten)


def kopf():
    print("{:<22}{:>6}{:>13}{:>13}{:>11}{:>13}{:>9}".format("Gruppe", "Pos.", "Nettoumsatz", "Herstellk.", "Fracht", "Deckungsb.", "Marge"))


def zeile(name, w):
    m = "{:.1f} %".format(w["marge"] * 100) if w["marge"] is not None else "–"
    print("{:<22}{:>6}{:>13}{:>13}{:>11}{:>13}{:>9}".format(name, w["n"], fb.eur(w["umsatz"]), fb.eur(w["hk"]), fb.eur(w["fracht"]), fb.eur(w["db"]), m))


for jahr in (2025, 2026):
    for titel, schl in (("Vertriebsweg", lambda p: p["vw"]), ("Schaumart", lambda p: p["schaumart"])):
        print("\n=== {} {} (EUR, netto, Konzernkurs {}; DB nach Herstellkosten und Fracht) ===".format(titel, jahr, jahr))
        kopf()
        r = fb.summiere(pos, schl, jahr)
        for k in sorted(r):
            zeile(k, r[k])
        ges = fb.summiere(pos, lambda p: "Gesamt", jahr)["Gesamt"]
        zeile("Gesamt", ges)
        s = sum(w["db"] for w in r.values())
        print("  Abgleich: Summe der Gruppen-DB =", fb.eur(s, 2), " Gesamt-DB =", fb.eur(ges["db"], 2))

print("\n=== Gesamt mit und ohne Notfallservice ===")
for jahr in (2025, 2026):
    mit = fb.summiere(pos, lambda p: "x", jahr)["x"]
    ohne = fb.summiere(pos, lambda p: "x", jahr, filt=lambda p: p["vw"] != "Notfallservice")
    ohne = ohne["x"]
    nur = fb.summiere(pos, lambda p: "x", jahr, filt=lambda p: p["vw"] == "Notfallservice")
    print(jahr, "mit Notfall: Umsatz", fb.eur(mit["umsatz"], 2), "DB", fb.eur(mit["db"], 2), "Marge {:.2f} %".format(mit["marge"] * 100))
    print(jahr, "ohne Notfall: Umsatz", fb.eur(ohne["umsatz"], 2), "DB", fb.eur(ohne["db"], 2), "Marge {:.2f} %".format(ohne["marge"] * 100))
    if nur:
        w = nur["x"]
        print(jahr, "nur Notfall: Umsatz", fb.eur(w["umsatz"], 2), "HK", fb.eur(w["hk"], 2), "Fracht", fb.eur(w["fracht"], 2), "DB", fb.eur(w["db"], 2), "Marge {:.2f} %".format(w["marge"] * 100), "Pos.", w["n"])

print("\n=== Muster 2026 (Kosten ohne Umsatz) ===")
m = fb.summiere(pos, lambda p: "m", 2026, filt=lambda p: p["muster"])
for k, w in m.items():
    print("Positionen", w["n"], "Umsatz", fb.eur(w["umsatz"], 2), "Herstellkosten", fb.eur(w["hk"], 2), "Fracht", fb.eur(w["fracht"], 2))
print("Gutschriften/Retouren 2026:")
for art in ("Gutschrift", "Retoure"):
    w = fb.summiere(pos, lambda p: art, 2026, filt=lambda p: p["art"] == art)
    for k, v in w.items():
        print(" ", art, "Pos.", v["n"], "Umsatz", fb.eur(v["umsatz"], 2), "Herstellkosten", fb.eur(v["hk"], 2))

print("\n=== Händlergeschäft 2026, Zeile für Zeile je Art ===")
for art in ("Lieferung", "Muster", "Gutschrift", "Retoure"):
    w = fb.summiere(pos, lambda p: art, 2026, filt=lambda p: p["vw"] == "Händler" and p["art"] == art)
    for k, v in w.items():
        print(" ", art, "Pos.", v["n"], "Umsatz", fb.eur(v["umsatz"], 2), "HK", fb.eur(v["hk"], 2), "Fracht", fb.eur(v["fracht"], 2), "DB", fb.eur(v["db"], 2))
