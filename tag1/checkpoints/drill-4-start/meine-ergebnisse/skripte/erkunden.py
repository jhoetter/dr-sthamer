# -*- coding: utf-8 -*-
"""Erkundung der Auftragsdaten für Drill 1 (nur Lesen, gibt Zahlen im Chat aus)."""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemeinsam as g

pos, stat = g.positionen()
print("Statistik:", stat)
print("Positionen bereinigt:", len(pos))
art = defaultdict(int)
for p in pos:
    art[(p["art"], p["art_auftrag"])] += 1
for k in sorted(art):
    print(k, art[k])

# Vorzeichen
neg = [p for p in pos if p["art"] in ("Gutschrift", "Retoure")]
print("Gutschrift/Retoure:", len(neg), "alle Liter<0:", all(p["liter"] <= 0 for p in neg), "alle EUR<=0:", all(p["eur"] <= 0 for p in neg))
# Muster
m = [p for p in pos if p["muster"]]
print("Muster:", len(m), "EUR:", sum(p["eur"] for p in m), "Liter:", sum(p["liter"] for p in m))
# Konsistenz menge_l zu menge*Gebinde
abw = [p for p in pos if abs(p["liter"] - p["menge"] * g.GEBINDE[p["einheit"]]) > 0.01]
print("menge_l weicht von Menge x Gebinde ab:", len(abw))
for p in abw[:5]:
    print(p["auftrag_id"], p["position"], p["einheit"], p["menge"], p["liter"])
# Absatz je Jahr
jahr_l = defaultdict(float)
jahr_e = defaultdict(float)
jahr_n = defaultdict(int)
for p in pos:
    if p["muster"]:
        continue
    jahr_l[p["jahr"]] += p["liter"]
    jahr_e[p["jahr"]] += p["eur"]
    jahr_n[p["jahr"]] += 1
for j in sorted(jahr_l):
    print(j, round(jahr_l[j], 1), round(jahr_e[j], 2), jahr_n[j])
# Lieferstellen: Anwendung im Auftrag = Anwendung in Tabelle?
ls = g.lieferstellen()
kd = g.kunden()
diff = [p for p in pos if p["ls"] in ls and ls[p["ls"]]["anwendung"] != p["anwendung"]]
print("Anwendung weicht ab:", len(diff))
unbek = set(p["ls"] for p in pos if p["ls"] not in ls)
print("Lieferstellen im Auftrag ohne Stamm:", unbek)
unbek_k = set(p["kunde"] for p in pos if p["kunde"] not in kd)
print("Kunden ohne Stamm:", unbek_k)
ls_kunde_abw = [p for p in pos if p["ls"] in ls and ls[p["ls"]]["kunde_id"] != p["kunde"]]
print("Lieferstelle gehört anderem Kunden:", len(ls_kunde_abw))
# Lieferstellen mit Lieferung in 24 Monaten
akt = set(p["ls"] for p in pos if p["art"] == "Lieferung" and p["ld"] >= g.FENSTER_24M_AB)
print("Lieferstellen im Stamm:", len(ls), "mit Lieferung in 24 Monaten:", len(akt))
akt_k = set(p["kunde"] for p in pos if p["art"] == "Lieferung" and p["ld"] >= g.FENSTER_24M_AB)
print("aktive Kunden 24M:", len(akt_k))
vw = defaultdict(int)
for p in pos:
    vw[p["vw"]] += 1
print("Vertriebswege:", dict(vw))
# Vertriebsweg Muster?
print("Muster-Vertriebswege:", sorted(set(p["vw"] for p in pos if p["muster"])))
# Erstbefüllung Vertriebsweg
print("Erstbefüllung Vertriebswege:", sorted(set((p["vw"], p["kunde"] in [k for k, v in kd.items() if v["ist_haendler"] == "ja"]) for p in pos if p["art_auftrag"] == "Erstbefüllung")))
# Notfall groß
nf = sorted([p for p in pos if p["art_auftrag"] == "Notfall" and p["jahr"] >= 2025], key=lambda p: -p["liter"])[:6]
for p in nf:
    print("Notfall", p["auftrag_id"], p["position"], p["ld"], p["kunde"], p["liter"], round(p["eur"], 2), p["art"])
print("Segmente:", sorted(set(v["segment"] for v in kd.values())))
print("Länder:", sorted(set(v["land"] for v in kd.values())))
print("Anwendungen:", sorted(set(v["anwendung"] for v in ls.values())))
print("Währungen:", sorted(set(p["waehrung"] for p in pos)))
