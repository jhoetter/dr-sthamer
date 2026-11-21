# Gemeinsame Rechenfunktionen fuer Angebote (Drill 3), nur Standardbibliothek, Python 3.9
# Regeln: regelwerke/RL-ANG-2026.md (§ 3 Rabatte, § 6 Preisliste, § 7 Fremdwaehrung)
import csv
import json
import os
from decimal import Decimal, ROUND_HALF_UP

HIER = os.path.dirname(os.path.abspath(__file__))
BASIS = os.path.dirname(os.path.dirname(HIER))
LITER = {"IBC": 1000, "Fass": 200, "Kanister": 20}


def D(x):
    return Decimal(str(x))


def cent(x):
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def lies(name):
    with open(os.path.join(BASIS, "daten", name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def de(x, n=2):
    """Deutsche Zahl: 1.234,56"""
    q = Decimal(1).scaleb(-n)
    s = "{:,.{n}f}".format(D(x).quantize(q, rounding=ROUND_HALF_UP), n=n)
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def eur(x, n=2):
    return "EUR " + de(x, n)


def pct(x, n=1):
    """x als Anteil (0,35) -> '35,0 %'"""
    return de(D(x) * 100, n) + " %"


PREIS = {}
for _jahr, _datei in (("2025", "preisliste_2025.csv"), ("2026", "preisliste_2026.csv")):
    for _r in lies(_datei):
        PREIS[(_jahr, _r["produkt_id"], _r["gebinde"])] = D(_r["preis_netto_eur"])

with open(os.path.join(BASIS, "daten", "kennzahlen.json"), encoding="utf-8") as _f:
    KZ = json.load(_f)


def kurs(jahr, waehrung):
    return D(KZ["konzernkurse"]["kurse"][str(jahr)][waehrung])


HK = {}
for _r in lies("herstellkosten.csv"):
    HK[(_r["produkt_id"], _r["jahr"])] = D(_r["rohstoff_eur_l"]) + D(_r["fertigung_eur_l"])


def position(liste, produkt, anzahl, satz):
    """anzahl = {'IBC': n, 'Fass': n, 'Kanister': n}; satz = Summe der Rabattsaetze (Dezimal), § 3 Nr. 5."""
    zeilen = []
    liter = 0
    listenwert = D(0)
    netto = D(0)
    for g in ("IBC", "Fass", "Kanister"):
        n = anzahl.get(g, 0)
        if not n:
            continue
        lp = PREIS[(liste, produkt, g)]
        lw = cent(lp * n)
        nt = cent(lp * n * (1 - D(satz)))
        zeilen.append({"gebinde": g, "anzahl": n, "listenpreis": lp, "listenwert": lw, "netto": nt, "liter": n * LITER[g]})
        liter += n * LITER[g]
        listenwert += lw
        netto += nt
    return {"zeilen": zeilen, "liter": liter, "listenwert": cent(listenwert), "netto": cent(netto), "satz": D(satz)}


def fracht_je_liter():
    """EUR je Liter je Versandart aus der Frachttabelle (Einordnung, nicht fuer ein Angebot belegt)."""
    s = {}
    for r in lies("fracht.csv"):
        a = s.setdefault(r["versandart"], [D(0), D(0)])
        a[0] += D(r["frachtkosten_eur"])
        a[1] += D(r["liter"])
    return {k: v[0] / v[1] for k, v in s.items()}


KLASSE = [(0, "A"), (2, "B"), (4, "C"), (6, "D")]


def klasse_nach_punkten(p):
    if p == 0:
        return "A"
    if p <= 2:
        return "B"
    if p <= 4:
        return "C"
    if p <= 6:
        return "D"
    return "E"


def hoeher(a, b):
    return a if a > b else b


def md_html(md):
    """Kleiner Markdown-Umsetzer fuer die eigenen Vorlagen (Ueberschriften, Tabellen, Listen, Absaetze, **fett**)."""
    import html as h
    import re

    def inline(t):
        t = h.escape(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        return re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<em>\1</em>", t)

    zeilen = md.split("\n")
    out = []
    i = 0
    while i < len(zeilen):
        z = zeilen[i]
        if not z.strip():
            i += 1
            continue
        if z.startswith("# "):
            out.append("<h4>" + inline(z[2:]) + "</h4>")
        elif z.startswith("## "):
            out.append("<h5 class=\"vorlage__abschnitt\">" + inline(z[3:]) + "</h5>")
        elif z.startswith("### "):
            out.append("<h6 class=\"vorlage__unter\">" + inline(z[4:]) + "</h6>")
        elif z.startswith("|"):
            tab = []
            while i < len(zeilen) and zeilen[i].startswith("|"):
                tab.append(zeilen[i])
                i += 1
            kopf = [c.strip() for c in tab[0].strip("|").split("|")]
            rows = [[c.strip() for c in t.strip("|").split("|")] for t in tab[2:]]
            s = "<div class=\"tabelle-rahmen\"><table class=\"tabelle\"><thead><tr>" + "".join("<th>" + inline(c) + "</th>" for c in kopf) + "</tr></thead><tbody>"
            for r in rows:
                s += "<tr>" + "".join("<td>" + inline(c) + "</td>" for c in r) + "</tr>"
            out.append(s + "</tbody></table></div>")
            continue
        elif z.startswith("- "):
            items = []
            while i < len(zeilen) and zeilen[i].startswith("- "):
                items.append("<li>" + inline(zeilen[i][2:]) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r"^\d+\. ", z):
            items = []
            while i < len(zeilen) and re.match(r"^\d+\. ", zeilen[i]):
                items.append("<li>" + inline(re.sub(r"^\d+\. ", "", zeilen[i])) + "</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        else:
            out.append("<p>" + inline(z) + "</p>")
        i += 1
    return "".join(out)
