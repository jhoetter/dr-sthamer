# -*- coding: utf-8 -*-
"""Baut meine-ergebnisse/praesentation.html aus praesentation/vorlage.html (Exhibit-Stil, Beirat 09.03.2027).

Aufruf: python meine-ergebnisse/skripte/praesentation_bauen.py            (ohne Sprechernotizen, Etappe 4)
        python meine-ergebnisse/skripte/praesentation_bauen.py notizen    (mit Sprechernotizen, Etappe 5)

Stil, Raster und Skripte der Vorlage bleiben unverändert; ersetzt werden nur die Folien im main-Block,
der Datenblock DIAGRAMM-DATEN und das Attribut data-fuss. Zahlen kommen aus
meine-ergebnisse/skripte/d5/praesentation_zahlen.json (erzeugt von praesentation_zahlen.py) und
meine-ergebnisse/skripte/bruecke_ergebnis.json (Brücke aus Drill 2).
"""
import json
import os
import sys

BASIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MIT_NOTIZEN = len(sys.argv) > 1 and sys.argv[1] == "notizen"
NBSP = "&nbsp;"
MINUS = "−"

with open(os.path.join(BASIS, "meine-ergebnisse", "skripte", "d5", "praesentation_zahlen.json"), encoding="utf-8") as f:
    Z = json.load(f)
with open(os.path.join(BASIS, "meine-ergebnisse", "skripte", "bruecke_ergebnis.json"), encoding="utf-8") as f:
    B = json.load(f)
with open(os.path.join(BASIS, "praesentation", "vorlage.html"), encoding="utf-8") as f:
    html = f.read()


def de(x, n=0):
    s = "{:,.{n}f}".format(abs(x), n=n).replace(",", "X").replace(".", ",").replace("X", ".")
    return (MINUS + s) if x < 0 and round(abs(x), n) != 0 else s


def pct(x, n=1, vorz=False):
    s = de(x, n)
    if vorz and x > 0:
        s = "+" + s
    return s + NBSP + "%"


def eur(x, n=0, vorz=False):
    s = de(x, n)
    if vorz and x > 0:
        s = "+" + s
    return ("EUR" + NBSP + s) if not s.startswith(MINUS) else (MINUS + "EUR" + NBSP + s[1:])


ZR = Z["zeitreihe"]
a, b = ZR["2025"], ZR["2026"]
wachstum = (b["gesamt_l"] / a["gesamt_l"] - 1) * 100
wachstum_ohne = (b["ohne_notfall_l"] / a["ohne_notfall_l"] - 1) * 100
nachf_wachstum = (b["nachfuell_l"] / a["nachfuell_l"] - 1) * 100
nachf_anteil = b["nachfuell_l"] / b["gesamt_l"] * 100
T = Z["top5"]
t25, t26, t26o = T["2025 mit Notfall"], T["2026 mit Notfall"], T["2026 ohne Notfall"]
for t in (t25, t26, t26o):
    t["anteil"] = t["zaehler"] / t["nenner"] * 100   # aus Zähler und Nenner neu, nicht aus dem gerundeten Wert
E = B["effekte"]
db_ohne = B["DBp"] + E["menge"] + E["mix"] + E["preis"] + E["kosten"] + E["fx"]
abw_ohne = db_ohne - B["DBp"]
abw_ohne_pct = abw_ohne / B["DBp"] * 100
KS = Z["kundenstatus"]

# Prüfungen: Titelzahlen gegen gerechnete Werte
assert de(wachstum, 1) == "0,6" and de(wachstum_ohne, 1) == MINUS + "10,1", (wachstum, wachstum_ohne)
assert de(abw_ohne_pct, 1) == MINUS + "14,6", abw_ohne_pct
assert de(t26["anteil"], 1) == "63,5" and de(t25["anteil"], 1) == "50,8" and de(t26o["anteil"], 1) == "55,8"
assert abs(B["summe"] - B["gesamtabw"]) < 0.01

TITEL = [
    "Der Absatz wächst nur dank einer Notfalllieferung; 2027 trägt die Nachfüllung",
    "Der Absatz wächst um 0,6" + NBSP + "% – ohne die Notfalllieferung sinkt er um 10,1" + NBSP + "%",
    "Ohne den Notfallservice liegt der Deckungsbeitrag 2026 um 14,6" + NBSP + "% unter dem Budget",
    "Die fünf größten Kunden tragen 2026 63,5" + NBSP + "% des Umsatzes, 2025 waren es 50,8" + NBSP + "%",
    "Der Beirat soll 2027 aufs Nachfüllgeschäft setzen und den Notfall getrennt führen",
]

NOTIZEN = {
    1: """Kernsatz: Der Absatz 2026 wächst nur wegen einer einzigen Notfalllieferung; tragen muss 2027 das Nachfüllgeschäft.
Zur Zahl: –
Einschränkung: Alle Zahlen stammen aus dem Übungsausschnitt (32 Kunden), Stand 28.02.2027, nicht aus dem ganzen Unternehmen.
Überleitung: Zuerst zur Frage, wo wir wachsen und wo wir verlieren.
Zeit: 1 Minute""",
    2: """Kernsatz: Der Absatz wächst um 0,6 %, aber nur wegen einer Notfalllieferung; ohne sie sinkt er um 10,1 %.
Zur Zahl: Absatz = Liter im Kalenderjahr nach Lieferdatum, netto nach Gutschriften und Retouren, ohne Muster: 225.660 Liter 2026 gegen 224.420 Liter 2025; ohne die Notfalllieferung vom 22.09.2026 (24.000 Liter) 201.660 Liter.
Einschränkung: Notfalllieferungen gab es auch 2022 und 2024, sie sind nicht planbar. Die Erstbefüllungen sind eine kleine Basis: 1 Position 2026 gegen 8 Positionen 2025.
Überleitung: Wachstum ist das eine; die Frage ist, ob wir daran auch verdienen.
Zeit: 3 Minuten""",
    3: """Kernsatz: Ohne den Notfallservice liegt der Deckungsbeitrag 14,6 % unter dem Budget; die Lücke ist eine Mengenlücke.
Zur Zahl: Deckungsbeitrag = Nettoumsatz minus Herstellkosten minus Fracht. Ist ohne Notfallservice EUR 297.939 gegen Budget EUR 348.764, also minus EUR 50.825. Mit der Notfalllieferung liegt der Ist-Deckungsbeitrag bei EUR 391.186, plus EUR 42.422.
Einschränkung: Das Budget ist zu Plankursen gerechnet, das Ist zu Ist-Monatskursen; der Währungseffekt ist mit plus EUR 1.395 getrennt ausgewiesen. Die Reihenfolge der Effekte bestimmt die Einzelwerte, die Summe ist fest. Falls das externe Mitglied fragt, ob etwas geschönt ist: Ohne Notfallservice liegt die DB-Marge mit 39,3 % genau auf Budgetniveau (39,3 %); die Notfalllieferung hat 57,9 % Marge (EUR 93.247 von EUR 160.963 Umsatz) und steht deshalb als eigener Balken, nicht im Durchschnitt versteckt. Die Marge ist nach Herstellkosten und Fracht, nicht nach Gemeinkosten.
Überleitung: Eine zweite Frage hinter dem Wachstum ist, wie abhängig wir von den größten Kunden sind.
Zeit: 4 Minuten""",
    4: """Kernsatz: Die fünf größten Kunden tragen 2026 63,5 % des Umsatzes, 2025 waren es 50,8 %; ohne die Notfalllieferung sind es 55,8 %.
Zur Zahl: Anteil = Nettoumsatz der fünf umsatzstärksten Kunden geteilt durch den gesamten Nettoumsatz des Jahres; ein Händler zählt als ein Kunde. Zu Kunden, die wir verlieren: Nach unserer Definition (letzte Lieferung) sind am 28.02.2027 von 32 Kunden 29 aktiv, 3 ruhend und keiner verloren.
Einschränkung: Übungsausschnitt mit 32 Kunden, nicht alle Kunden des Unternehmens; eine andere Zählweise von Kunden ergäbe andere Zahlen.
Überleitung: Daraus folgen drei Punkte, über die wir heute entscheiden möchten.
Zeit: 3 Minuten""",
    5: """Kernsatz: Wir bitten den Beirat, 2027 auf das Nachfüllgeschäft zu setzen, den Notfallservice getrennt zu führen und die Abhängigkeit von den größten Kunden zu beobachten.
Zur Zahl: 88,6 % = Nachfüllung 199.860 Liter von 225.660 Litern Gesamtabsatz 2026; EUR 93.247 = Deckungsbeitrag der einen Notfalllieferung; 55,8 % = Anteil der fünf größten Kunden 2026 ohne diese Lieferung.
Einschränkung: Offen bleiben die Ursachen der Margen je Vertriebsweg und der Rückgang der Erstbefüllungen; dafür belegen die Tabellen keine Gründe.
Überleitung: Welche der drei Punkte sollen wir heute beschließen, und welche brauchen mehr Zeit?
Zeit: 4 Minuten""",
}


def notizen(nr):
    if not MIT_NOTIZEN:
        return ""
    return '    <aside class="notizen">\n' + NOTIZEN[nr] + "\n    </aside>\n"


def folie_titel():
    return """  <section class="folie" data-baustein="titel" data-quelle="keine">
    <div class="titel-band"></div>
    <div class="titel-innen">
      <div class="eyebrow">Beirat · Geschäftsjahr 2026 und Prioritäten 2027</div>
      <div class="t-titel">%s</div>
      <div class="t-unter">Wo wir wachsen, wo wir verlieren, wo wir Geld verdienen – und was der Beirat für 2027 beschließen soll</div>
      <div class="t-meta">
        <div><div class="lab">Sitzung</div><div>Beirat, 09.03.2027</div></div>
        <div><div class="lab">Vorgelegt von</div><div>Dr. Henrike Vossberg, Leiterin Unternehmensentwicklung</div></div>
        <div><div class="lab">Datenstand</div><div>28.02.2027 · Übungsausschnitt</div></div>
      </div>
    </div>
%s  </section>
""" % (TITEL[0], notizen(1))


def folie_absatz():
    return """  <section class="folie" data-baustein="diagramm">
    <div class="eyebrow">Geschäftsjahr 2026 · Frage 1: Wachsen und verlieren</div>
    <h2>%s</h2>
    <div class="meta"><b>Absatz in Litern</b><span class="dot">·</span>2021–2026<span class="dot">·</span>netto nach Gutschriften und Retouren, ohne Muster</div>
    <div class="inhalt zwei">
      <div class="diagrammfeld">
        <div class="diagrammkopf" data-kopf="verlauf"></div>
        <svg class="diagramm" data-daten="verlauf" width="790" height="390"></svg>
      </div>
      <div class="karte">
        <div class="labb">Einordnung</div>
        <div class="gross tnum">%s</div>
        <div class="erl">Absatz 2026 gegen 2025 ohne die Notfalllieferung (24.000%sl)</div>
        <ul>
          <li>Nachfüllung wächst um %s auf %s%sl.</li>
          <li>Erstbefüllungen fallen von %s%sl auf %s%sl.</li>
        </ul>
      </div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Auftragstabelle, Übungsausschnitt (32 Kunden), Stichtag 28.02.2027. Absatz = Liter im Kalenderjahr nach Lieferdatum, netto nach Gutschriften und Retouren, ohne Muster, Doppelimporte einmal; nur ganze Jahre. Erstbefüllungen: %d Position 2026 gegen %d 2025, kleine Basis.</div>
%s  </section>
""" % (TITEL[1], pct(wachstum_ohne, 1), NBSP, pct(nachf_wachstum, 1), de(b["nachfuell_l"]), NBSP,
       de(a["erst_l"]), NBSP, de(b["erst_l"]), NBSP, b["erst_pos"], a["erst_pos"], notizen(2))


def folie_bruecke():
    return """  <section class="folie" data-baustein="diagramm">
    <div class="eyebrow">Geschäftsjahr 2026 · Frage 2: Wo wir Geld verdienen</div>
    <h2>%s</h2>
    <div class="meta"><b>Deckungsbeitrag nach Herstellkosten und Fracht</b><span class="dot">·</span>Ist 2026 gegen Budget 2026<span class="dot">·</span>EUR, Ist-Monatskurse, Budget zum Plankurs</div>
    <div class="inhalt zwei">
      <div class="diagrammfeld">
        <div class="diagrammkopf" data-kopf="bruecke"></div>
        <svg class="diagramm" data-daten="bruecke" width="790" height="390"></svg>
      </div>
      <div class="karte">
        <div class="labb">Treiber</div>
        <ul>
          <li><b>Ohne Notfallservice:</b> Ist %s gegen Budget %s, also %s (%s).</li>
          <li><b>Menge:</b> größter Abzug,%s bei 35.010%sl weniger Absatz als im Budget.</li>
          <li><b>Notfallservice:</b> %s aus einer Lieferung, nicht budgetiert.</li>
        </ul>
      </div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Finanzkommentar 2026 aus Auftrags-, Herstellkosten-, Fracht- und Budgettabelle, Übungsausschnitt, Stichtag 28.02.2027. Ist zum Ist-Monatskurs, Budget zum Plankurs (CHF 1,04 · GBP 1,19 · NOK 0,09). Reihenfolge Menge, Mix, Preis, Kosten, Währung, Notfallservice; Summe der Effekte = Abweichung %s.</div>
%s  </section>
""" % (TITEL[2], eur(db_ohne), eur(B["DBp"]), eur(abw_ohne, 0, True), pct(abw_ohne_pct, 1, True),
       eur(E["menge"]), NBSP, eur(E["notfall"], 0, True), eur(B["gesamtabw"], 0, True), notizen(3))


def folie_top5():
    def zeile(name, t, abstand, betont=False):
        return '            <tr%s><td>%s</td><td class="z">%s</td><td class="z">%s</td><td class="z">%s</td><td class="z">%s</td></tr>\n' % (
            ' class="betont"' if betont else "", name, de(t["zaehler"]), de(t["nenner"]), pct(t["anteil"], 1), abstand)
    return """  <section class="folie" data-baustein="tabelle">
    <div class="eyebrow">Geschäftsjahr 2026 · Frage 1: Abhängigkeit von großen Kunden</div>
    <h2>%s</h2>
    <div class="meta"><b>Anteil der fünf größten Kunden am Nettoumsatz</b><span class="dot">·</span>2025 und 2026<span class="dot">·</span>Händler zählt als ein Kunde</div>
    <div class="inhalt">
      <div>
        <div class="einheitzeile">Nettoumsatz in EUR zum Konzernkurs des Lieferjahres</div>
        <table class="tabelle">
          <thead><tr><th>Jahr</th><th class="z">Fünf größte Kunden</th><th class="z">Gesamtumsatz</th><th class="z">Anteil</th><th class="z">Gegen 2025</th></tr></thead>
          <tbody>
%s%s%s          </tbody>
        </table>
      </div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Auftragstabelle und Kundenstamm, Übungsausschnitt (32 Kunden), Stichtag 28.02.2027. Nettoumsatz netto nach Gutschriften und Retouren, ohne Muster, in EUR zum Konzernkurs des Lieferjahres (2026: CHF 1,071 · GBP 1,168 · NOK 0,0849). Kunde nach Kundennummer; Anteil aus Summen gerechnet.</div>
%s  </section>
""" % (TITEL[3],
       zeile("2025 (keine Notfalllieferung)", t25, "–"),
       zeile("2026 mit Notfalllieferung", t26, "+" + de(t26["anteil"] - t25["anteil"], 1) + NBSP + "Prozentpunkte", True),
       zeile("2026 ohne Notfalllieferung", t26o, "+" + de(t26o["anteil"] - t25["anteil"], 1) + NBSP + "Prozentpunkte"),
       notizen(4))


def folie_entscheidung():
    return """  <section class="folie" data-baustein="entscheidung">
    <div class="eyebrow">Geschäftsjahr 2026 · Entscheidungsbedarf</div>
    <h2>%s</h2>
    <div class="meta"><b>3 Beschlüsse</b><span class="dot">·</span>Grundlage: Folien 2 bis 4</div>
    <div class="inhalt">
      <div>
        <div class="beschluss">
          <span class="num navy">1</span>
          <div class="stichwort">Planungskern</div>
          <div class="satz">Der Beirat bestätigt das Nachfüllgeschäft als Kern der Planung 2027.</div>
          <div class="zahl tnum">%s<small>Anteil Nachfüllung am Absatz 2026</small></div>
        </div>
        <div class="beschluss">
          <span class="num navy">2</span>
          <div class="stichwort">Notfallservice</div>
          <div class="satz">Der Beirat verlangt den Notfallservice als eigene Zeile in Budget und Bericht.</div>
          <div class="zahl tnum">%s<small>Deckungsbeitrag 2026, eine Lieferung</small></div>
        </div>
        <div class="beschluss">
          <span class="num navy">3</span>
          <div class="stichwort">Großkunden</div>
          <div class="satz">Der Beirat verlangt einen Quartalsbericht zum Anteil der fünf größten Kunden.</div>
          <div class="zahl tnum">%s<small>Anteil 2026 ohne Notfalllieferung</small></div>
        </div>
      </div>
    </div>
    <div class="fazit">
      <div><div class="k">Fazit</div><div class="h">Der Beirat setzt 2027 auf das, was verlässlich wächst, und trennt, was sich nicht planen lässt.</div></div>
      <div class="rechts"><div class="k">Nächster Schritt</div><div class="h">Controlling legt das Budget 2027 mit Notfallzeile vor</div></div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Management-Summary und Finanzkommentar 2026, Übungsausschnitt, Stichtag 28.02.2027. Nachfüllung %s von %s%sl Gesamtabsatz 2026; Deckungsbeitrag der Notfalllieferung vom 22.09.2026 zu Ist-Monatskursen; Top-5-Anteil am Nettoumsatz 2026 ohne diese Lieferung.</div>
%s  </section>
""" % (TITEL[4], pct(nachf_anteil, 1), eur(E["notfall"]), pct(t26o["anteil"], 1),
       de(b["nachfuell_l"]) + NBSP + "l", de(b["gesamt_l"]), NBSP, notizen(5))


def folie_anhang():
    return """  <section class="folie" data-baustein="anhang">
    <div class="eyebrow">Anhang</div>
    <h2>Quellen und Definitionen</h2>
    <div class="meta"><b>Datenstand 28.02.2027</b><span class="dot">·</span>Zahlen des Übungsausschnitts (32 Kunden), nicht des Gesamtunternehmens</div>
    <div class="inhalt">
      <table class="tabelle klein">
        <thead><tr><th style="width:20%%">Kennzahl</th><th style="width:44%%">Definition</th><th style="width:24%%">Quelle</th><th style="width:12%%">Stand</th></tr></thead>
        <tbody>
          <tr><td>Absatz</td><td>Liter im Kalenderjahr nach Lieferdatum, netto nach Gutschriften und Retouren, ohne Muster, Doppelimporte einmal; Gebinde IBC 1.000, Fass 200, Kanister 20 Liter</td><td>Auftragstabelle</td><td>28.02.2027</td></tr>
          <tr><td>Nettoumsatz, Top-5-Anteil</td><td>Summe der Nettobeträge in EUR zum Konzernkurs des Lieferjahres; Anteil der fünf umsatzstärksten Kunden am Gesamtumsatz, Händler als ein Kunde</td><td>Auftragstabelle, Kundenstamm</td><td>28.02.2027</td></tr>
          <tr><td>Deckungsbeitrag (Ist, Budget)</td><td>Nettoumsatz minus Herstellkosten minus Fracht; Ist zu Ist-Monatskursen, Budget zu Plankursen; Notfallservice nicht budgetiert</td><td>Finanzkommentar 2026</td><td>28.02.2027</td></tr>
          <tr><td>Kundenstatus</td><td>nach letzter Lieferung am Stichtag: aktiv bis 12 Monate, ruhend 12 bis 24 Monate, verloren darüber; %d aktiv, %d ruhend, %d verloren von 32</td><td>Auftragstabelle, Kundenstamm</td><td>28.02.2027</td></tr>
        </tbody>
      </table>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>siehe Tabelle; Jan.–Feb. 2027 ist Teiljahr und nirgends mit ganzen Jahren verglichen.</div>
%s  </section>
""" % (KS["aktiv"], KS["ruhend"], KS["verloren"],
       ('    <aside class="notizen">\nKernsatz: Anhang, nur bei Rückfragen zeigen.\nZur Zahl: –\nEinschränkung: –\nÜberleitung: –\nZeit: 0 Minuten\n    </aside>\n' if MIT_NOTIZEN else ""))


def daten():
    x = ["2021", "2022", "2023", "2024", "2025", "2026"]
    # in Tausend Liter mit einer Nachkommastelle: kürzere Endwerte, damit die Beschriftung im Diagramm Platz hat
    gesamt = [round(ZR[j]["gesamt_l"] / 1000, 1) for j in x]
    ohne = [round(ZR[j]["ohne_notfall_l"] / 1000, 1) for j in x]
    schritte = [
        {"name": "Budget", "wert": round(B["DBp"] / 1000, 3), "summe": True},
        {"name": "Menge", "wert": round(E["menge"] / 1000, 3)},
        {"name": "Mix", "wert": round(E["mix"] / 1000, 3)},
        {"name": "Preis", "wert": round(E["preis"] / 1000, 3)},
        {"name": "Kosten", "wert": round(E["kosten"] / 1000, 3)},
        {"name": "Währung", "wert": round(E["fx"] / 1000, 3)},
        {"name": "Ist ohne Notfall", "wert": round((B["ist_db"] - E["notfall"]) / 1000, 3), "summe": True},
        {"name": "Notfall", "wert": round(E["notfall"] / 1000, 3)},
        {"name": "Ist", "wert": round(B["ist_db"] / 1000, 3), "summe": True},
    ]
    d = {
        "verlauf": {"art": "linie", "titel": "Absatz", "zusatz": "Gesamt und ohne Notfalllieferung, 2021–2026", "einheit": "in Tsd. Litern",
                    "stellen": 1, "x": x, "teiljahr": False,
                    "reihen": [{"name": "Gesamt", "betont": True, "werte": gesamt}, {"name": "o. Notfall", "werte": ohne}]},
        "bruecke": {"art": "wasserfall", "titel": "Deckungsbeitrag", "zusatz": "Budget → Ist 2026", "einheit": "in Tsd. EUR",
                    "stellen": 1, "schritte": schritte},
    }
    return '<script id="diagramm-daten">\nconst DIAGRAMME = ' + json.dumps(d, ensure_ascii=False, indent=1) + ";\n</script>"


# ---- Vorlage zerlegen und neu zusammensetzen ----
i0 = html.index('<main class="buehne"')
i0_ende = html.index(">", i0) + 1
i1 = html.index("</main>")
oeffnung = html[i0:i0_ende].replace('data-fuss="[Gremium] · [TT.MM.JJJJ]"', 'data-fuss="Beirat · 09.03.2027"')
folien = "\n" + "\n".join([folie_titel(), folie_absatz(), folie_bruecke(), folie_top5(), folie_entscheidung(), folie_anhang()]) + "\n"
html = html[:i0] + oeffnung + folien + html[i1:]
j0 = html.index('<script id="diagramm-daten">')
j1 = html.index("</script>", j0) + len("</script>")
html = html[:j0] + daten() + html[j1:]

ziel = os.path.join(BASIS, "meine-ergebnisse", "praesentation.html")
with open(ziel, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)
print("geschrieben:", ziel, "| Notizen:", MIT_NOTIZEN, "| Folien im Satz:", html.count('<section class="folie"'))
print("Kontrolle: Gesamt 2026 %s / 2025 %s = %s; ohne Notfall %s = %s" % (de(b["gesamt_l"]), de(a["gesamt_l"]), pct(wachstum, 2, True), de(b["ohne_notfall_l"]), pct(wachstum_ohne, 2, True)))
print("Kontrolle: DB ohne Notfall %s, Budget %s, Abweichung %s = %s" % (de(db_ohne, 2), de(B["DBp"], 2), de(abw_ohne, 2), pct(abw_ohne_pct, 2, True)))
