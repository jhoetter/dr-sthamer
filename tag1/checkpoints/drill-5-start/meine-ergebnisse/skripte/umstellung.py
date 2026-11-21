# Reiter „Umstellung“: erzeugt dashboard-daten/umstellung.js
# Fluorfrei-Anteil nach Anwendung und Segment, große Einzellieferung, Ampel Segment x Land
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lese_csv, lade_positionen, absatz, BASIS

pos, stat = lade_positionen()
pos = [p for p in pos if absatz(p)]
kunden = {r["id"]: r for r in lese_csv("kunden.csv")}

# Große Einzellieferung 2026 = größte einzelne Position 2026
p26 = [p for p in pos if p["jahr"] == 2026]
gross = max(p26, key=lambda p: p["liter"])
median = sorted(p["liter"] for p in p26)[len(p26) // 2]
print("Größte Position 2026:", gross["auftrag_id"], gross["position"], gross["datum"], gross["kunde_id"],
      gross["segment"], gross["anwendung"], gross["vertriebsweg"], gross["linie"], gross["liter"], "Median:", median)


def ist_gross(p):
    return p["auftrag_id"] == gross["auftrag_id"] and p["position"] == gross["position"]


zellen = defaultdict(lambda: {"l": 0.0, "ff": 0.0, "fh": 0.0, "n": 0})
for p in pos:
    j = "2027T" if p["jahr"] == 2027 else str(p["jahr"])
    k = (j, p["segment"], p["land"], p["vertriebsweg"], p["anwendung"], 1 if ist_gross(p) else 0)
    z = zellen[k]
    z["l"] += p["liter"]
    if p["linie"] == "fluorfrei":
        z["ff"] += p["liter"]
    elif p["linie"] == "fluorhaltig":
        z["fh"] += p["liter"]
    z["n"] += 1

liste = [{"j": k[0], "seg": k[1], "land": k[2], "weg": k[3], "anw": k[4], "g": k[5],
          "l": round(z["l"], 2), "ff": round(z["ff"], 2), "fh": round(z["fh"], 2), "n": z["n"]}
         for k, z in sorted(zellen.items())]

# Stationäre Anlagen: Datenaufnahme vor Ort
st = []
for r in lese_csv("lieferstellen.csv"):
    if r["anwendung"] == "stationaere_anlage":
        k = kunden[r["kunde_id"]]
        st.append({"seg": k["segment"], "land": k["land"], "da": 1 if r["datenaufnahme_am"] else 0})

daten = {
    "ziel": 60,
    "zellen": liste,
    "stationaer": st,
    "ausreisser": {"auftrag": gross["auftrag_id"], "datum": gross["datum"], "kunde": gross["kunde_id"],
                   "segment": gross["segment"], "anwendung": gross["anwendung"], "weg": gross["vertriebsweg"],
                   "linie": gross["linie"], "liter": gross["liter"], "median": median},
    "segmente": sorted(set(k["segment"] for k in kunden.values())),
    "laender": sorted(set(k["land"] for k in kunden.values())),
}
ziel = os.path.join(BASIS, "meine-ergebnisse", "dashboard-daten")
os.makedirs(ziel, exist_ok=True)
with open(os.path.join(ziel, "umstellung.js"), "w", encoding="utf-8") as f:
    f.write("const UMSTELLUNG = " + json.dumps(daten, ensure_ascii=False) + ";\n")
print("Zellen:", len(liste), "stationäre Anlagen:", len(st), "mit Datenaufnahme:", sum(s["da"] for s in st))
