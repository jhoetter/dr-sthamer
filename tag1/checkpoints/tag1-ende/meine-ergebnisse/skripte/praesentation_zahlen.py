# Zahlen für die Beiratspräsentation (Drill 5): frisch aus den Tabellen, nur Standardbibliothek.
# Ausgabe: meine-ergebnisse/praesentation-daten.json und Text im Terminal.
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lade_positionen, lese_csv, absatz as absatz_k
from fin_kern import lade_fin, summiere
from bruecke import bruecke

HIER = os.path.dirname(os.path.abspath(__file__))
AUS = os.path.join(HIER, "..", "praesentation-daten.json")

pos, stat = lade_positionen()
ergebnis = {}

# 1) Fluorfrei-Anteil je Jahr: gesamt und stationäre Anlagen (Liter netto, ohne Muster)
def anteil(jahr, filt):
    z = n = 0.0
    k = 0
    for p in pos:
        if p["jahr"] != jahr or not absatz_k(p) or not filt(p):
            continue
        n += p["liter"]
        k += 1
        if p["linie"] == "fluorfrei":
            z += p["liter"]
    return z, n, k

reihe_gesamt, reihe_stat = {}, {}
for j in range(2021, 2027):
    z, n, k = anteil(j, lambda p: True)
    reihe_gesamt[j] = {"zaehler": z, "nenner": n, "positionen": k, "anteil": round(100 * z / n, 1)}
    z, n, k = anteil(j, lambda p: p["anwendung"] == "stationaere_anlage")
    reihe_stat[j] = {"zaehler": z, "nenner": n, "positionen": k,
                     "anteil": round(100 * z / n, 1) if k >= 20 else None}
ergebnis["fluorfrei_gesamt"] = reihe_gesamt
ergebnis["fluorfrei_stationaer"] = reihe_stat
z, n, k = anteil(2026, lambda p: p["anwendung"] == "stationaere_anlage" and p["vertriebsweg"] != "Notfallservice")
ergebnis["stationaer_2026_ohne_notfall"] = {"zaehler": z, "nenner": n, "positionen": k, "anteil": round(100 * z / n, 1)}
z, n, k = anteil(2026, lambda p: p["anwendung"] != "stationaere_anlage")
ergebnis["uebrige_2026"] = {"zaehler": z, "nenner": n, "positionen": k, "anteil": round(100 * z / n, 1)}

# 2) Datenaufnahme stationäre Anlagen
ls = [r for r in lese_csv("lieferstellen.csv") if r["anwendung"] == "stationaere_anlage"]
mit = [r for r in ls if r["datenaufnahme_am"].strip()]
liefer26 = set(p["lieferstelle_id"] for p in pos if p["jahr"] == 2026 and p["anwendung"] == "stationaere_anlage" and absatz_k(p))
ergebnis["datenaufnahme"] = {
    "anlagen": len(ls), "mit_datenaufnahme": len(mit), "ohne": len(ls) - len(mit),
    "mit_lieferung_2026": len([r for r in ls if r["lieferstelle_id"] in liefer26]),
    "davon_mit_datenaufnahme": len([r for r in mit if r["lieferstelle_id"] in liefer26]),
}

# 3) Marge je Produktlinie 2026 und 2025 (nach Herstellkosten und Fracht)
fpos, fstat = lade_fin()
def marge(jahr, linie, notfall):
    s = summiere(fpos, lambda p: p["linie"],
                 lambda p: p["jahr"] == jahr and (notfall is None or (p["vertriebsweg"] == "Notfallservice") == notfall))
    z = s[linie]
    return {"positionen": z["n"], "umsatz": round(z["umsatz"], 2), "db": round(z["db"], 2),
            "marge": round(100 * z["db"] / z["umsatz"], 1)}
ergebnis["marge"] = {
    "fluorfrei_2026": marge(2026, "fluorfrei", None),
    "fluorhaltig_2026_ohne_notfall": marge(2026, "fluorhaltig", False),
    "fluorhaltig_2026_mit_notfall": marge(2026, "fluorhaltig", None),
    "fluorfrei_2025": marge(2025, "fluorfrei", None),
    "fluorhaltig_2025": marge(2025, "fluorhaltig", None),
}

# 4) DB-Brücke Budget -> Ist 2026 (Methode wie Finanzkommentar)
b = bruecke(fpos, "db")
ergebnis["bruecke_db"] = {k: round(v, 2) for k, v in b.items()}
ist_ohne_nf = b["ist"] - b["notfall"]
ergebnis["db_ohne_notfall"] = {"ist": round(ist_ohne_nf, 2), "abw_eur": round(ist_ohne_nf - b["plan"], 2),
                               "abw_prozent": round(100 * (ist_ohne_nf - b["plan"]) / b["plan"], 1),
                               "abw_mit_notfall_eur": round(b["ist"] - b["plan"], 2),
                               "abw_mit_notfall_prozent": round(100 * (b["ist"] - b["plan"]) / b["plan"], 1)}

with open(AUS, "w", encoding="utf-8") as f:
    json.dump(ergebnis, f, ensure_ascii=False, indent=1)
print(json.dumps(ergebnis, ensure_ascii=False, indent=1))
