# Drill 3, Etappe 2: Preisrechnung nach RL-ANG-2026 (nur Standardbibliothek, Python 3.9)
# Liest daten/*.csv, schreibt nichts ausser der Konsole und meine-ergebnisse/_sim/angebote_rechnung.json
import csv
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
BASIS = os.path.dirname(os.path.dirname(HIER))


def D(x):
    return Decimal(str(x))


def cent(x):
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def lies(name):
    with open(os.path.join(BASIS, "daten", name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


PREIS = {}
for jahr, datei in (("2025", "preisliste_2025.csv"), ("2026", "preisliste_2026.csv")):
    for r in lies(datei):
        PREIS[(jahr, r["produkt_id"], r["gebinde"])] = D(r["preis_netto_eur"])
with open(os.path.join(BASIS, "daten", "kennzahlen.json"), encoding="utf-8") as f:
    KZ = json.load(f)
NOK = D(KZ["konzernkurse"]["kurse"]["2027"]["NOK"])
LITER = {"IBC": 1000, "Fass": 200, "Kanister": 20}


def position(liste, produkt, anzahl, satz):
    """anzahl = {'IBC': n, 'Fass': n, 'Kanister': n}; satz = Summe der Rabattsaetze (Dezimal)."""
    zeilen = []
    liter = 0
    listenwert = D(0)
    netto = D(0)
    for g in ("IBC", "Fass", "Kanister"):
        n = anzahl.get(g, 0)
        if not n:
            continue
        lp = PREIS[(liste, produkt, g)]
        lw = lp * n
        nt = cent(lw * (1 - D(satz)))
        zeilen.append({"gebinde": g, "anzahl": n, "listenpreis": str(lp), "listenwert": str(cent(lw)), "netto": str(nt)})
        liter += n * LITER[g]
        listenwert += lw
        netto += nt
    return {"zeilen": zeilen, "liter": liter, "listenwert": cent(listenwert), "netto": cent(netto), "satz": D(satz)}


def zeige(name, p):
    print("  ", name, "Liter", p["liter"], "Liste", p["listenwert"], "Satz", p["satz"], "Netto", p["netto"])
    for z in p["zeilen"]:
        print("      ", z)


erg = {}

print("== A-01: Assistent damals (Preisliste 2025, 13 % auf alle) ==")
a_alt = position("2025", "P-204", {"IBC": 1, "Fass": 6}, "0.13")
zeige("alt gesamt", a_alt)

print("== A-01: richtig nach RL-ANG-2026 zum Angebotsdatum 14.07.2026 (Liste 2026) ==")
p1 = position("2026", "P-204", {"IBC": 1, "Fass": 3}, "0.08")  # Erstbefuellung 1.600 l: Mengen 3 % + Projekt 5 %
p2 = position("2026", "P-204", {"Fass": 3}, "0.03")  # Reserve 600 l: nur Mengenrabatt 3 %
zeige("Pos 1 Erstbefuellung", p1)
zeige("Pos 2 Reserve", p2)
a_neu_summe = cent(p1["netto"] + p2["netto"])
a_neu_liste = cent(p1["listenwert"] + p2["listenwert"])
print("   Summe Liste", a_neu_liste, "Summe netto", a_neu_summe)
print("   Differenz zum Assistenten (richtig - alt):", cent(a_neu_summe - a_alt["netto"]))
nur_liste = position("2026", "P-204", {"IBC": 1, "Fass": 6}, "0.13")
print("   nur falsche Liste (2026 mit 13 %):", nur_liste["netto"], " -> Effekt Liste:", cent(nur_liste["netto"] - a_alt["netto"]))
print("   Effekt Rabatt (2026 richtig vs 2026 mit 13 %):", cent(a_neu_summe - nur_liste["netto"]))
print("   alter Preis entspricht Rabatt auf Liste 2026:", cent((1 - a_alt["netto"] / a_neu_liste) * 100), "%")
erg["a01"] = {"alt_netto": str(a_alt["netto"]), "alt_liste": str(a_alt["listenwert"]), "neu_netto": str(a_neu_summe),
              "neu_liste": str(a_neu_liste), "pos1": str(p1["netto"]), "pos2": str(p2["netto"])}

print("\n== A-02: Rahmenvertrag P-201, 24.000 l je Jahr, Liste 2026 ==")
jahr_ibc = 18
jahr_kan = 300
herst_l = D("2.421") + D("0.555")
for name, satz in (("Rahmenrabatt 8 %", "0.08"), ("Mengenrabatt 10 %", "0.10"), ("Entwurf Assistent 18 %", "0.18"), ("ohne Rabatt", "0")):
    p = position("2026", "P-201", {"IBC": jahr_ibc, "Kanister": jahr_kan}, satz)
    gesamt = cent(p["netto"] * 3)
    herst = herst_l * p["liter"]
    marge_vor_fracht = (p["netto"] - herst) / p["netto"]
    print("  ", name, "Jahr Liste", p["listenwert"], "Jahr netto", p["netto"], " 3 Jahre", gesamt,
          " HK/Jahr", cent(herst), " Marge vor Fracht", cent(marge_vor_fracht * 100), "%",
          " DB vor Fracht/Jahr", cent(p["netto"] - herst))
    erg["a02_" + satz] = {"jahr_netto": str(p["netto"]), "gesamt": str(gesamt), "marge_vor_fracht_pct": str(cent(marge_vor_fracht * 100)),
                          "jahr_liste": str(p["listenwert"]), "hk_jahr": str(cent(herst))}
liste_jahr = position("2026", "P-201", {"IBC": jahr_ibc, "Kanister": jahr_kan}, "0")["listenwert"]
hk_jahr = herst_l * 24000
for m in ("0.23", "0.0"):
    r = 1 - hk_jahr / (liste_jahr * (1 - D(m)))
    print("   Rabatt, bei dem die Marge vor Fracht", m, "erreicht:", cent(r * 100), "%")
print("   Listenpreis je Liter IBC", PREIS[("2026", "P-201", "IBC")] / 1000, " Kanister", PREIS[("2026", "P-201", "Kanister")] / 20)
print("   Herstellkosten P-201 2026 je Liter:", herst_l)

print("\n== A-03: P-204, 6 IBC, Liste 2026 ==")
b1 = position("2026", "P-204", {"IBC": 4}, "0.11")  # Mengen 6 % + Projekt 5 %
b2 = position("2026", "P-204", {"IBC": 2}, "0.06")
zeige("Pos 1 Erstbefuellung Nord-3", b1)
zeige("Pos 2 Reserve", b2)
b_liste = cent(b1["listenwert"] + b2["listenwert"])
b_netto = cent(b1["netto"] + b2["netto"])
print("   Liste", b_liste, "netto", b_netto, "in NOK", cent(b_netto / NOK), "Kurs", NOK)
print("   Budget NOK 650.000 in EUR:", cent(D(650000) * NOK), " (Budget enthaelt Fracht)")
erg["a03"] = {"liste": str(b_liste), "netto": str(b_netto), "nok": str(cent(b_netto / NOK)), "pos1": str(b1["netto"]), "pos2": str(b2["netto"]),
              "budget_eur": str(cent(D(650000) * NOK)), "kurs": str(NOK)}

print("\n== A-04: P-202, 6 IBC + 2 Fass, Liste 2026 ==")
c = position("2026", "P-202", {"IBC": 6, "Fass": 2}, "0.06")
zeige("Nachbestellung", c)
print("   Auftragswert", c["netto"], "Abstand zu 25.000:", cent(D(25000) - c["netto"]))
print("   mit Expresszuschlag 450 (falsch gezaehlt):", cent(c["netto"] + 450))
erg["a04"] = {"liste": str(c["listenwert"]), "netto": str(c["netto"]), "abstand": str(cent(D(25000) - c["netto"]))}

print("\n== Marge fluorfrei aus den Daten (Einordnung) ==")
from fin_kern import lade_fin, summiere
pos, stat = lade_fin()
g = summiere(pos, lambda p: (p["linie"], p["jahr"]), lambda p: p["jahr"] in (2025, 2026))
for k in sorted(g):
    z = g[k]
    if k[0] == "fluorfrei":
        print("  ", k, "Pos", z["n"], "Umsatz", round(z["umsatz"], 2), "HK", round(z["herst"], 2), "Fracht", round(z["fracht"], 2),
              "DB", round(z["db"], 2), "Marge", round(100 * z["marge"], 2), "% Fracht/Umsatz", round(100 * z["fracht"] / z["umsatz"], 2), "%")
        erg["ff_" + str(k[1])] = {"n": z["n"], "umsatz": round(z["umsatz"], 2), "herst": round(z["herst"], 2), "fracht": round(z["fracht"], 2),
                                  "marge": round(100 * z["marge"], 2)}
g2 = summiere(pos, lambda p: (p["produkt_id"], p["jahr"]), lambda p: p["produkt_id"] == "P-201" and p["jahr"] == 2026)
for k, z in g2.items():
    print("   P-201 2026: Pos", z["n"], "Umsatz", round(z["umsatz"], 2), "Marge", None if z["marge"] is None else round(100 * z["marge"], 2))
g3 = summiere(pos, lambda p: p["segment"], lambda p: p["jahr"] == 2026 and p["linie"] == "fluorfrei")
for k, z in sorted(g3.items()):
    print("   2026 fluorfrei", k, "Pos", z["n"], "Umsatz", round(z["umsatz"], 2), "Marge", None if z["marge"] is None else round(100 * z["marge"], 2),
          "Fracht/Umsatz", round(100 * z["fracht"] / z["umsatz"], 2) if z["umsatz"] else None)

fr = lies("fracht.csv")
vers = {}
for r in fr:
    vers.setdefault(r["versandart"], []).append((float(r["frachtkosten_eur"]), float(r["liter"])))
for k, v in vers.items():
    print("   Fracht", k, "Sendungen", len(v), "EUR je Liter", round(sum(a for a, b in v) / sum(b for a, b in v), 3))

out = os.path.join(BASIS, "meine-ergebnisse", "skripte", "angebote_rechnung.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(erg, f, ensure_ascii=False, indent=1)
print("\ngeschrieben:", out)
