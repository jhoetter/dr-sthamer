# -*- coding: utf-8 -*-
"""Etappe 2: Plan-Ist-Brücke 2026 für den Deckungsbeitrag nach kennzahlen.json (plan_ist_bruecke).

Aufruf: python meine-ergebnisse/skripte/bruecke.py

Methode (Reihenfolge Menge, Mix, Preis, Kosten, Fremdwährung, Notfallservice; DB-Brücke):
- Zellen = Segment x Vertriebsweg (direkt, Händler, Rahmenvertrag), Kalenderjahr 2026.
- Plan je Zelle aus budget_2026.csv (12 Monate summiert): Liter, Umsatz, DB. Plan-Durchschnitt je Liter = Plan-DB / Plan-Liter gesamt.
- Ist je Zelle: Liter netto ohne Muster; Umsatz zum Plankurs; Kosten = Herstellkosten + Fracht (Muster tragen Kosten).
- Menge  = (Ist-Liter - Plan-Liter) x Plan-DB je Liter (Durchschnitt über alle Zellen)
- Mix    = Summe je Zelle (Ist-Liter x Plan-DB je Liter der Zelle) - Ist-Liter gesamt x Plan-Durchschnitt
- Preis  = Summe je Zelle (Ist-Umsatz zum Plankurs - Ist-Liter x Plan-Preis je Liter der Zelle)
- Kosten = Summe je Zelle (Ist-Liter x Plan-Kosten je Liter - Ist-Kosten); Plan-Kosten je Liter = Plan-Preis - Plan-DB je Liter
- Fremdwährung = Summe Ist-Betrag in Fremdwährung x (Ist-Monatskurs - Plankurs), ohne Notfallservice
- Notfallservice = DB der Notfallservice-Positionen (Ist-Monatskurs), nicht budgetiert
Abgleich: Summe der Effekte = Ist-DB gesamt - Budget-DB.
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finanz_basis as fb
import gemeinsam as g

WEGE_PLAN = ["direkt", "Händler", "Rahmenvertrag"]


def rechne():
    pos, kd, prod, pruef = fb.lade()
    plan = defaultdict(lambda: {"l": 0.0, "u": 0.0, "db": 0.0, "zeilen": 0})
    for z in g.lies("budget_2026.csv"):
        c = (z["segment"], z["vertriebsweg"])
        plan[c]["l"] += float(z["menge_l"])
        plan[c]["u"] += float(z["umsatz_eur"])
        plan[c]["db"] += float(z["db_eur"])
        plan[c]["zeilen"] += 1
    ist = defaultdict(lambda: {"l": 0.0, "u_plan": 0.0, "u_monat": 0.0, "kosten": 0.0, "hk": 0.0, "fracht": 0.0, "fx": 0.0, "n": 0})
    notfall = {"l": 0.0, "u_monat": 0.0, "kosten": 0.0, "hk": 0.0, "fracht": 0.0, "n": 0, "fx": 0.0}
    for p in pos:
        if p["jahr"] != 2026:
            continue
        if p["vw"] == "Notfallservice":
            w = notfall
        else:
            w = ist[(p["segment"], p["vw"])]
            w["u_plan"] += p["eur_plan"]
            w["fx"] += p["fx_effekt"]
        w["u_monat"] += p["eur_monat"]
        w["hk"] += p["hk"]
        w["fracht"] += p["fracht"]
        w["kosten"] += p["hk"] + p["fracht"]
        if not p["muster"]:
            w["l"] += p["liter"]
            if "n" in w:
                w["n"] += 1
        # Notfall: Zähler
    zellen = sorted(set(plan) | set(ist))
    ohne_plan = [c for c in zellen if c in ist and plan[c]["l"] == 0 and (ist[c]["l"] or ist[c]["kosten"])]
    ohne_ist = [c for c in zellen if c in plan and c not in ist]

    Qp = sum(plan[c]["l"] for c in plan)
    DBp = sum(plan[c]["db"] for c in plan)
    Up = sum(plan[c]["u"] for c in plan)
    Qi = sum(ist[c]["l"] for c in ist)
    avg = DBp / Qp

    def pw(c, feld):
        return plan[c][feld] / plan[c]["l"] if plan[c]["l"] else None

    menge = (Qi - Qp) * avg
    mix_summe = 0.0
    preis = 0.0
    kosten = 0.0
    fx = 0.0
    sonder = []   # Zellen ohne Plan
    for c in ist:
        w = ist[c]
        if plan[c]["l"] == 0:
            # Zelle ohne Plan: Plan-Wert je Liter = Plan-Durchschnitt (Preis) -> hier explizit melden
            sonder.append(c)
            continue
        pdb = pw(c, "db")
        ppreis = pw(c, "u")
        pkost = ppreis - pdb
        mix_summe += w["l"] * pdb
        preis += w["u_plan"] - w["l"] * ppreis
        kosten += w["l"] * pkost - w["kosten"]
        fx += w["fx"]
    mix = mix_summe - Qi * avg

    # Zellen ohne Plan (falls vorhanden): komplette Ist-Werte, gesonderter Posten, damit die Brücke aufgeht
    ohne_plan_db = 0.0
    for c in sonder:
        w = ist[c]
        ohne_plan_db += w["u_plan"] - w["kosten"]
        fx += w["fx"]
        # Menge-Anteil dieser Zellen steckt im Mengeneffekt (Qi enthält ihre Liter) -> Korrektur unten
    # Korrekturterm: Liter ohne Plan-Zelle sind in Qi (Mengeneffekt zum Durchschnitt) enthalten, ihr DB je Liter fehlt in Mix
    korr_menge_sonder = sum(ist[c]["l"] for c in sonder) * avg
    # Ist-DB aller Zellen (Plankurs) + FX = Monatskurs
    ist_db_zellen = sum(ist[c]["u_plan"] + ist[c]["fx"] - ist[c]["kosten"] for c in ist)
    nf_db = notfall["u_monat"] - notfall["kosten"]
    ist_db_gesamt = ist_db_zellen + nf_db
    effekte = {"menge": menge, "mix": mix, "preis": preis, "kosten": kosten, "fx": fx, "notfall": nf_db}
    # Sonderposten nur wenn nötig
    if sonder:
        # Rest so zuordnen, dass die Brücke aufgeht, und offen ausweisen
        effekte["zellen_ohne_plan"] = ohne_plan_db - korr_menge_sonder
    summe = sum(effekte.values())
    gesamtabw = ist_db_gesamt - DBp
    return {
        "plan": {c: plan[c] for c in plan}, "ist": {c: ist[c] for c in ist}, "notfall": notfall,
        "Qp": Qp, "Qi": Qi, "DBp": DBp, "Up": Up, "avg": avg, "effekte": effekte, "summe": summe,
        "ist_db_gesamt": ist_db_gesamt, "ist_db_zellen": ist_db_zellen, "nf_db": nf_db, "gesamtabw": gesamtabw,
        "sonder": sonder, "ohne_ist": ohne_ist, "pos": pos,
        "ist_u_monat": sum(ist[c]["u_monat"] for c in ist) + notfall["u_monat"],
        "ist_u_plan_zellen": sum(ist[c]["u_plan"] for c in ist),
    }


if __name__ == "__main__":
    r = rechne()
    print("Budget 2026 (Plankurs): Liter {} · Umsatz EUR {} · DB EUR {} · Marge {:.2f} %".format(
        g.de(r["Qp"]), g.de(r["Up"], 2), g.de(r["DBp"], 2), r["DBp"] / r["Up"] * 100))
    k = g.kennzahlen()["ziele"]["2026"]
    print("Ziel laut kennzahlen.json: Liter {} · Umsatz {} · DB {} · Marge {}".format(g.de(k["absatz_l"]), g.de(k["nettoumsatz_eur"], 2), g.de(k["deckungsbeitrag_eur"], 2), k["db_marge"]))
    print("Plan-Durchschnitt DB je Liter: {:.4f}".format(r["avg"]))
    print("Zellen Plan:", len(r["plan"]), "| Zellen Ist (ohne Notfall):", len(r["ist"]), "| Ist-Zellen ohne Plan:", r["sonder"], "| Plan-Zellen ohne Ist:", r["ohne_ist"])
    print("\nIst 2026 (Ist-Monatskurse): DB aller Zellen ohne Notfall EUR {}; Notfallservice EUR {}; gesamt EUR {}".format(
        g.de(r["ist_db_zellen"], 2), g.de(r["nf_db"], 2), g.de(r["ist_db_gesamt"], 2)))
    print("Ist-Liter ohne Notfall {} (Plan {}), Notfall {} l".format(g.de(r["Qi"]), g.de(r["Qp"]), g.de(r["notfall"]["l"])))
    print("Ist-Umsatz Zellen: Plankurs EUR {} | Monatskurse EUR {}".format(g.de(r["ist_u_plan_zellen"], 2),
          g.de(sum(w["u_monat"] for w in r["ist"].values()), 2)))
    print("\nBrücke Budget-DB -> Ist-DB (EUR):")
    print("  Budget-DB 2026                     {:>14}".format(g.de(r["DBp"], 2)))
    namen = {"menge": "Mengeneffekt", "mix": "Mixeffekt", "preis": "Preiseffekt", "kosten": "Kosteneffekt",
             "fx": "Fremdwährungseffekt", "notfall": "Notfallservice (eigener Balken)", "zellen_ohne_plan": "Zellen ohne Plan"}
    for kk, v in r["effekte"].items():
        print("  {:<34}{:>14}".format(namen[kk], g.de(v, 2)))
    print("  Ist-DB 2026 (aus Effekten)         {:>14}".format(g.de(r["DBp"] + r["summe"], 2)))
    print("  Ist-DB 2026 (direkt gerechnet)     {:>14}".format(g.de(r["ist_db_gesamt"], 2)))
    print("  Summe der Effekte {:>14} | Gesamtabweichung {:>14} | Differenz {:.6f}".format(
        g.de(r["summe"], 2), g.de(r["gesamtabw"], 2), r["summe"] - r["gesamtabw"]))
    ohne_nf = r["ist_db_zellen"] - r["DBp"]
    print("\nOhne Notfallservice: Ist-DB {} gegen Budget {} = {} ({:+.1f} %)".format(
        g.de(r["ist_db_zellen"], 2), g.de(r["DBp"], 2), g.de(ohne_nf, 2), ohne_nf / r["DBp"] * 100))
    print("Fremdwährungseffekt je Währung (Ist-Betrag x (Ist-Monatskurs - Plankurs), ohne Notfall):")
    je = defaultdict(float)
    for p in r["pos"]:
        if p["jahr"] == 2026 and p["vw"] != "Notfallservice" and p["waehrung"] != "EUR":
            je[p["waehrung"]] += p["fx_effekt"]
    for w, v in sorted(je.items()):
        print("  ", w, g.de(v, 2))
    print("\nIst-Zellen ohne Notfall, Liter Ist/Plan je Vertriebsweg:")
    for weg in WEGE_PLAN:
        li = sum(w["l"] for c, w in r["ist"].items() if c[1] == weg)
        lp = sum(w["l"] for c, w in r["plan"].items() if c[1] == weg)
        dbi = sum(w["u_plan"] + w["fx"] - w["kosten"] for c, w in r["ist"].items() if c[1] == weg)
        dbp = sum(w["db"] for c, w in r["plan"].items() if c[1] == weg)
        print("  {:<14} Liter Ist {:>8} Plan {:>8} ({:+.1f} %) | DB Ist {:>10} Plan {:>10} ({})".format(
            weg, g.de(li), g.de(lp), (li / lp - 1) * 100, g.de(dbi), g.de(dbp), g.de(dbi - dbp)))
    # Nachhaken: Mengeneffekt je Auftragsart (nur Liter, Nachfüllung/Erstbefüllung) – Beobachtung
    print("\nIst-Liter 2026 ohne Notfall je Auftragsart (Beobachtung zum Mengeneffekt):")
    la = defaultdict(float)
    la25 = defaultdict(float)
    for p in r["pos"]:
        if p["vw"] == "Notfallservice" or p["muster"]:
            continue
        if p["jahr"] == 2026:
            la[p["art_auftrag"]] += p["liter"]
        if p["jahr"] == 2025:
            la25[p["art_auftrag"]] += p["liter"]
    for a in sorted(set(la) | set(la25)):
        print("  ", a, "2025:", g.de(la25[a]), "2026:", g.de(la[a]))
    # Budget-Liter 2026 vs. Ist-Liter 2025 ohne Notfall
    print("  Ist-Liter 2025 gesamt (ohne Muster):", g.de(sum(la25.values())), "; Plan 2026:", g.de(r["Qp"]), "; Ist 2026 ohne Notfall:", g.de(r["Qi"]))
    with open(os.path.join(g.BASIS, "meine-ergebnisse", "skripte", "bruecke_ergebnis.json"), "w", encoding="utf-8") as f:
        json.dump({"effekte": r["effekte"], "summe": r["summe"], "gesamtabw": r["gesamtabw"], "DBp": r["DBp"], "ist_db": r["ist_db_gesamt"]}, f, ensure_ascii=False, indent=1)
