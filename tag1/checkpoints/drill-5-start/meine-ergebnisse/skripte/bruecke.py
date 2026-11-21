# Plan-Ist-Brücke 2026 nach kennzahlen.json -> definitionen.plan_ist_bruecke
# Zellen: Produktlinie x Segment. Reihenfolge: Menge -> Mix -> Preis -> (Kosten) -> Fremdwährung -> Notfallservice.
# Umsatzbrücke: Wert je Liter = Umsatz je Liter. DB-Brücke: Wert je Liter = DB je Liter.
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fin_kern import lade_fin, absatz
from kern import lese_csv


def plan_zellen():
    plan = defaultdict(lambda: {"l": 0.0, "u": 0.0, "db": 0.0})
    for r in lese_csv("budget_2026.csv"):
        z = plan[(r["produktlinie"], r["segment"])]
        z["l"] += float(r["menge_l"])
        z["u"] += float(r["umsatz_eur"])
        z["db"] += float(r["db_eur"])
    return plan


def ist_zellen(pos, notfall):
    """Ist 2026 je Zelle: Liter (ohne Muster), Umsatz zum Plankurs und zum Ist-Monatskurs, Kosten (Herst. + Fracht)."""
    ist = defaultdict(lambda: {"l": 0.0, "u_plan": 0.0, "u_ist": 0.0, "kosten": 0.0, "herst": 0.0, "fracht": 0.0})
    for p in pos:
        if p["jahr"] != 2026:
            continue
        if (p["vertriebsweg"] == "Notfallservice") != notfall:
            continue
        z = ist[(p["linie"], p["segment"])]
        if absatz(p):
            z["l"] += p["liter"]
        z["u_plan"] += p["umsatz_plan"]
        z["u_ist"] += p["umsatz_ist_m"]
        z["herst"] += p["herst"]
        z["fracht"] += p["fracht"]
        z["kosten"] += p["herst"] + p["fracht"]
    return ist


def bruecke(pos, wert):
    """wert = 'u' (Umsatzbrücke) oder 'db' (DB-Brücke). Gibt Dict mit Effekten und Abgleich zurück."""
    plan = plan_zellen()
    ist = ist_zellen(pos, notfall=False)
    nf = ist_zellen(pos, notfall=True)
    L_plan = sum(z["l"] for z in plan.values())
    P_plan = sum(z[wert] for z in plan.values())
    avg_plan = P_plan / L_plan
    L_ist = sum(z["l"] for z in ist.values())
    wj = {k: plan[k][wert] / plan[k]["l"] for k in plan}  # Plan-Wert je Liter je Zelle
    pj = {k: plan[k]["u"] / plan[k]["l"] for k in plan}   # Plan-Preis je Liter
    menge = (L_ist - L_plan) * avg_plan
    mix = sum(ist[k]["l"] * wj[k] for k in ist) - L_ist * avg_plan
    preis = sum(ist[k]["u_plan"] - ist[k]["l"] * pj[k] for k in ist)
    kosten = 0.0
    if wert == "db":
        # Plan-Kosten je Liter = Plan-Preis - Plan-DB je Liter
        kosten = sum(ist[k]["l"] * (pj[k] - wj[k]) - ist[k]["kosten"] for k in ist)
    fx = sum(ist[k]["u_ist"] - ist[k]["u_plan"] for k in ist)
    # Ist ohne Notfallservice (Ist-Monatskurs) und Notfallservice
    umsatz_ist_zellen = sum(z["u_ist"] for z in ist.values())
    kosten_ist_zellen = sum(z["kosten"] for z in ist.values())
    ist_zellen_wert = umsatz_ist_zellen if wert == "u" else umsatz_ist_zellen - kosten_ist_zellen
    umsatz_nf = sum(z["u_ist"] for z in nf.values())
    kosten_nf = sum(z["kosten"] for z in nf.values())
    notfall = umsatz_nf if wert == "u" else umsatz_nf - kosten_nf
    ist_gesamt = ist_zellen_wert + notfall
    summe_effekte = menge + mix + preis + kosten + fx + notfall
    return {
        "plan": P_plan, "L_plan": L_plan, "L_ist": L_ist, "avg_plan": avg_plan,
        "menge": menge, "mix": mix, "preis": preis, "kosten": kosten, "fx": fx, "notfall": notfall,
        "ist": ist_gesamt, "ist_zellen": ist_zellen_wert,
        "gesamtabweichung": ist_gesamt - P_plan, "summe_effekte": summe_effekte,
        "differenz": (ist_gesamt - P_plan) - summe_effekte,
    }


def fx_je_waehrung(pos):
    """Fremdwährungseffekt 2026 je Währung (ohne Notfallservice): Ist-Betrag in FW x (Ist-Monatskurs - Plankurs)."""
    g = defaultdict(lambda: {"n": 0, "betrag_fw": 0.0, "effekt": 0.0})
    for p in pos:
        if p["jahr"] != 2026 or p["vertriebsweg"] == "Notfallservice" or p["waehrung"] == "EUR":
            continue
        z = g[p["waehrung"]]
        z["n"] += 1
        z["betrag_fw"] += p["betrag_fw"]
        z["effekt"] += p["umsatz_ist_m"] - p["umsatz_plan"]
    return g
