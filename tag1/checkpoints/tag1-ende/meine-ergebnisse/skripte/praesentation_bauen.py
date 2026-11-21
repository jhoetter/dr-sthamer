# Baut meine-ergebnisse/praesentation.html aus praesentation/vorlage.html (Stil, Raster, Skripte, D3 bleiben unverändert).
# Ersetzt nur den Folienblock (<main class="buehne"> ... </main>) und den Block DIAGRAMM-DATEN.
# Zahlen kommen aus meine-ergebnisse/praesentation-daten.json (erzeugt von praesentation_zahlen.py aus den Tabellen).
# Titel und Beschlüsse stammen wörtlich aus der Storyline von Dr. Henrike Vossberg.
import json
import os

HIER = os.path.dirname(os.path.abspath(__file__))
ERG = os.path.join(HIER, "..")
VORLAGE = os.path.join(ERG, "..", "praesentation", "vorlage.html")
ZIEL = os.path.join(ERG, "praesentation.html")
ZAHLEN = os.path.join(ERG, "praesentation-daten.json")
NOTIZEN_DATEI = os.path.join(HIER, "praesentation_notizen.json")

Z = json.load(open(ZAHLEN, encoding="utf-8"))
NB = "&nbsp;"


def de(v, nd=0):
    s = f"{abs(v):,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + s


def pz(v, nd=1):
    return de(v, nd) + NB + "%"


def eur(v):
    return ("−" if v < 0 else "") + "EUR" + NB + de(abs(v))


def notiz(nr):
    try:
        n = json.load(open(NOTIZEN_DATEI, encoding="utf-8"))
    except OSError:
        return ""
    return n.get(str(nr), "")


def aside(nr):
    return '<aside class="notizen">\n' + notiz(nr) + "\n    </aside>"


g = Z["fluorfrei_gesamt"]
s = Z["fluorfrei_stationaer"]
m = Z["marge"]
b = Z["bruecke_db"]
da = Z["datenaufnahme"]
ohne = Z["db_ohne_notfall"]
st26 = s["2026"]
ue26 = Z["uebrige_2026"]
sn = Z["stationaer_2026_ohne_notfall"]

# ------------------------------------------------------------------ Folien
f1 = f"""
  <section class="folie" data-baustein="titel" data-quelle="keine">
    <div class="titel-band"></div>
    <div class="titel-innen">
      <div class="eyebrow">Beirat · Ein Jahr Umstellungsprogramm FreeFoam</div>
      <div class="t-titel">{pz(g['2026']['anteil'])} fluorfrei 2026: Wir verfehlen das Ziel von 60{NB}%</div>
      <div class="t-unter">Ein Jahr FreeFoam: Wo die Umstellung steht, ob sie sich rechnet und was der Beirat entscheiden soll</div>
      <div class="t-meta">
        <div><div class="lab">Sitzung</div><div>Beirat, 09.03.2027</div></div>
        <div><div class="lab">Vorgelegt von</div><div>Dr. Henrike Vossberg, Programmleiterin Fluorfrei-Umstellung</div></div>
        <div><div class="lab">Datenstand</div><div>28.02.2027, Übungsausschnitt</div></div>
      </div>
    </div>
    {aside(1)}
  </section>
"""

f2 = f"""
  <section class="folie" data-baustein="diagramm">
    <div class="eyebrow">Umstellungsprogramm · Frage 1: Wo steht die Umstellung?</div>
    <h2>Stationäre Anlagen bremsen die Umstellung: Nur {pz(st26['anteil'])} ihrer Liter sind 2026 fluorfrei, in allen übrigen Anwendungen {pz(ue26['anteil'])}</h2>
    <div class="meta"><b>Fluorfrei-Anteil</b><span class="dot">·</span>2021 bis 2026, Ist<span class="dot">·</span>Liter netto, ohne Muster</div>
    <div class="inhalt zwei">
      <div class="diagrammfeld">
        <div class="diagrammkopf" data-kopf="verlauf"></div>
        <svg class="diagramm" data-daten="verlauf" width="790" height="390"></svg>
      </div>
      <div class="karte">
        <div class="labb">Einordnung</div>
        <div class="gross tnum">{pz(st26['anteil'])}<small>fluorfrei 2026</small></div>
        <div class="erl">Stationäre Anlagen: {de(st26['zaehler'])} von {de(st26['nenner'])}{NB}Litern, {st26['positionen']} Positionen</div>
        <ul>
          <li>Gesamt {pz(g['2025']['anteil'])} auf {pz(g['2026']['anteil'])}: fluorfreie Liter {de(100 * (g['2026']['zaehler'] / g['2025']['zaehler'] - 1), 1)}{NB}%, alle Liter {de(100 * (g['2026']['nenner'] / g['2025']['nenner'] - 1), 1)}{NB}%; der Anteil steigt, weil fluorhaltig stärker sinkt.</li>
          <li>Ohne die Notfalllieferung vom 22.09.2026 (24.000{NB}Liter fluorhaltig) sind es {pz(sn['anteil'])}.</li>
          <li>Nur {da['mit_datenaufnahme']} von {da['anlagen']} stationären Anlagen haben eine Datenaufnahme vor Ort.</li>
        </ul>
      </div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Auftrags-, Produkt- und Lieferstellentabelle, Stichtag 28.02.2027, Übungsausschnitt (32 Kunden). Fluorfrei-Anteil = Liter der fluorfreien Produktlinie ÷ alle gelieferten Liter im Kalenderjahr, netto nach Gutschriften und Retouren, ohne Muster; Ist, ohne Jan.–Feb. 2027 (Teiljahr).</div>
    {aside(2)}
  </section>
"""

zeilen = [
    ("2026 fluorfrei", m["fluorfrei_2026"], True),
    ("2026 fluorhaltig, ohne Notfallservice", m["fluorhaltig_2026_ohne_notfall"], False),
    ("2026 fluorhaltig, mit Notfallservice", m["fluorhaltig_2026_mit_notfall"], False),
    ("2025 fluorfrei", m["fluorfrei_2025"], False),
    ("2025 fluorhaltig", m["fluorhaltig_2025"], False),
]
tr = ""
for name, d, betont in zeilen:
    klasse = ' class="betont"' if betont else ""
    tr += ('            <tr' + klasse + '><td>' + name + '</td><td class="z">' + de(d["umsatz"] / 1000, 1) + '</td>'
           '<td class="z">' + de(d["db"] / 1000, 1) + '</td><td class="z">' + pz(d["marge"]) + '</td><td class="z">'
           + str(d["positionen"]) + '</td></tr>\n')

f3 = f"""
  <section class="folie" data-baustein="tabelle">
    <div class="eyebrow">Umstellungsprogramm · Frage 2: Rechnet sie sich?</div>
    <h2>Fluorfreie Produkte erzielen 2026 weniger als die Hälfte der Marge fluorhaltiger: {pz(m['fluorfrei_2026']['marge'])} gegen {pz(m['fluorhaltig_2026_ohne_notfall']['marge'])}</h2>
    <div class="meta"><b>DB-Marge</b><span class="dot">·</span>2025 und 2026, Ist<span class="dot">·</span>nach Herstellkosten und Fracht, Konzernkurs des Lieferjahres</div>
    <div class="inhalt">
      <div>
        <div class="einheitzeile">Tsd. EUR, netto; DB-Marge in % des Nettoumsatzes</div>
        <table class="tabelle">
          <thead><tr><th>Produktlinie und Jahr</th><th class="z">Nettoumsatz</th><th class="z">Deckungsbeitrag</th><th class="z">DB-Marge</th><th class="z">Positionen</th></tr></thead>
          <tbody>
{tr}          </tbody>
        </table>
      </div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Auftrags-, Herstellkosten- und Frachttabelle, Stichtag 28.02.2027, Übungsausschnitt. DB-Marge = (Nettoumsatz − Herstellkosten − Fracht) ÷ Nettoumsatz, aus Summen gerechnet; Ist, netto, ohne Muster im Umsatz. Notfallservice = eine Lieferung am 22.09.2026 (24.000{NB}Liter). Eine Ursache belegt keine Tabelle.</div>
    {aside(3)}
  </section>
"""

uebrige = b["mix"] + b["preis"] + b["kosten"] + b["fx"]
f4 = f"""
  <section class="folie" data-baustein="diagramm">
    <div class="eyebrow">Umstellungsprogramm · Frage 2: Rechnet sie sich?</div>
    <h2>Der Ist-Deckungsbeitrag 2026 liegt nur dank einer einzigen Notfalllieferung über dem Budget; ohne sie fehlen {eur(abs(ohne['abw_eur']))}</h2>
    <div class="meta"><b>Deckungsbeitrag</b><span class="dot">·</span>Ist 2026 gegen Budget 2026<span class="dot">·</span>EUR, Ist-Monatskurse, Budget zum Plankurs</div>
    <div class="inhalt zwei">
      <div class="diagrammfeld">
        <div class="diagrammkopf" data-kopf="bruecke"></div>
        <svg class="diagramm" data-daten="bruecke" width="790" height="390"></svg>
      </div>
      <div class="karte">
        <div class="labb">Treiber</div>
        <ul>
          <li><b>Menge:</b> {eur(b['menge'])}, {de(b['L_ist'])}{NB}Liter gegen {de(b['L_plan'])}{NB}Liter im Budget (ohne Notfallservice).</li>
          <li><b>Notfallservice:</b> +{eur(b['notfall'])} aus einer nicht budgetierten Lieferung.</li>
          <li><b>Mix, Preis, Kosten, Währung:</b> zusammen +{eur(uebrige)}.</li>
        </ul>
      </div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Auftrags-, Budget-, Herstellkosten-, Fracht- und Kurstabelle, Stichtag 28.02.2027, Übungsausschnitt. Ist {eur(b['ist'])} gegen Budget {eur(b['plan'])} = +{eur(b['gesamtabweichung'])}; ohne Notfallservice {eur(ohne['ist'])} ({de(ohne['abw_prozent'], 1)}{NB}%). Reihenfolge Menge → Mix → Preis → Kosten → Währung → Notfall, je Zelle Produktlinie × Segment; Summe der Effekte = Abweichung; Einzelwerte gerundet.</div>
    {aside(4)}
  </section>
"""

f5 = f"""
  <section class="folie" data-baustein="entscheidung">
    <div class="eyebrow">Umstellungsprogramm · Entscheidungsbedarf</div>
    <h2>Der Beirat soll drei Beschlüsse fassen, damit die stationären Anlagen 2027 aufholen</h2>
    <div class="meta"><b>3 Beschlüsse</b><span class="dot">·</span>Grundlage: Zahlen per 28.02.2027, Übungsausschnitt</div>
    <div class="inhalt">
      <div>
        <div class="beschluss">
          <span class="num navy">1</span>
          <div class="stichwort">Datenaufnahme</div>
          <div class="satz">Die Geschäftsführung legt bis zur nächsten Sitzung einen Plan mit der Kapazität der Anwendungstechnik vor, um bei den übrigen stationären Anlagen die Daten vor Ort aufzunehmen.</div>
          <div class="zahl tnum">{da['ohne']} von {da['anlagen']}<small>Anlagen ohne Datenaufnahme</small></div>
        </div>
        <div class="beschluss">
          <span class="num navy">2</span>
          <div class="stichwort">Ziel 2027</div>
          <div class="satz">Der Beirat bewertet das Ziel von 80{NB}% für 2027 in der nächsten Sitzung neu.</div>
          <div class="zahl tnum">{pz(g['2026']['anteil'])}<small>Ist 2026, Ziel 60{NB}%</small></div>
        </div>
        <div class="beschluss">
          <span class="num navy">3</span>
          <div class="stichwort">Berichtspflicht</div>
          <div class="satz">Die Geschäftsführung berichtet quartalsweise den Ist-Deckungsbeitrag gegen das Budget, mit und ohne Notfallservice.</div>
          <div class="zahl tnum">{eur(ohne['abw_eur'])}<small>Ist 2026 ohne Notfallservice</small></div>
        </div>
      </div>
    </div>
    <div class="fazit">
      <div><div class="k">Fazit</div><div class="h">Mit diesen Beschlüssen hat der Beirat Plan, Maßstab und Zahlen für 2027 in der Hand.</div></div>
      <div class="rechts"><div class="k">Nächster Schritt</div><div class="h">Geschäftsführung: Plan zur Datenaufnahme, bis zur nächsten Sitzung</div></div>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>Lieferstellen- und Auftragstabelle, Stichtag 28.02.2027, Übungsausschnitt: Anlagen ohne Datenaufnahme, Fluorfrei-Anteil 2026 (Ist), Ist-Deckungsbeitrag 2026 gegen Budget ohne Notfallservice (Definitionen im Anhang).</div>
    {aside(5)}
  </section>
"""

f6 = f"""
  <section class="folie" data-baustein="anhang">
    <div class="eyebrow">Anhang</div>
    <h2>Quellen und Definitionen</h2>
    <div class="meta"><b>Datenstand 28.02.2027</b><span class="dot">·</span>alle Zahlen aus dem Übungsausschnitt (32 Kunden), keine Zahlen des Gesamtunternehmens</div>
    <div class="inhalt">
      <table class="tabelle klein">
        <thead><tr><th style="width:20%">Kennzahl</th><th style="width:44%">Definition</th><th style="width:24%">Quelle</th><th style="width:12%">Stand</th></tr></thead>
        <tbody>
          <tr><td>Fluorfrei-Anteil</td><td>Liter der fluorfreien Produktlinie ÷ alle gelieferten Liter im Kalenderjahr nach Lieferdatum, netto nach Gutschriften und Retouren, ohne Muster, Doppelimporte einmal; Gebinde in Liter (IBC 1.000, Fass 200, Kanister 20)</td><td>Auftragstabelle, Produkttabelle (Produktlinie)</td><td>28.02.2027</td></tr>
          <tr><td>Datenaufnahme vor Ort</td><td>Stationäre Anlagen mit Datum der Datenaufnahme durch die Anwendungstechnik: {da['mit_datenaufnahme']} von {da['anlagen']}</td><td>Lieferstellentabelle</td><td>28.02.2027</td></tr>
          <tr><td>DB-Marge</td><td>(Nettoumsatz − Herstellkosten − Fracht) ÷ Nettoumsatz, aus Summen; Fracht je Auftrag nach Litern verteilt; Fremdwährung zum Konzernkurs 2026 (CHF 1,071 · GBP 1,168 · NOK 0,0849)</td><td>Auftrags-, Herstellkosten-, Frachttabelle</td><td>28.02.2027</td></tr>
          <tr><td>Brücke Budget → Ist</td><td>Deckungsbeitrag je Zelle Produktlinie × Segment; Ist zum Ist-Monatskurs, Budget zum Plankurs; Notfallservice als eigener Balken, weil nicht budgetiert</td><td>Budget 2026, Kurstabelle, Auftragstabelle</td><td>28.02.2027</td></tr>
        </tbody>
      </table>
    </div>
    <div class="quelle"><span class="qk">Quelle</span>siehe Tabelle</div>
    {aside(6)}
  </section>
"""

main = ('<main class="buehne" data-firma="Dr. Sthamer" data-fuss="Beirat · 09.03.2027">\n' + f1 + f2 + f3 + f4 + f5 + f6 + "\n</main>")

# ------------------------------------------------------------------ Diagrammdaten
reihe_g = []
reihe_s = []
for j in range(2021, 2027):
    e = g[str(j)]
    reihe_g.append({"wert": e["anteil"], "zaehler": e["zaehler"], "nenner": e["nenner"]})
    e = s[str(j)]
    reihe_s.append({"wert": e["anteil"], "zaehler": e["zaehler"], "nenner": e["nenner"]} if e["anteil"] is not None else None)

verlauf = {
    "art": "linie", "titel": "Fluorfrei-Anteil", "zusatz": "gesamt und stationäre Anlagen, 2021 bis 2026", "einheit": "in %",
    "stellen": 1, "x": [str(j) for j in range(2021, 2027)],
    "ziel": {"wert": 60, "text": "Ziel 2026"},
    "reihen": [
        {"name": "Stationär", "betont": True, "werte": reihe_s},
        {"name": "Gesamt", "grau": True, "werte": reihe_g},
    ],
}
bruecke = {
    "art": "wasserfall", "titel": "Deckungsbeitrag", "zusatz": "Budget → Ist, 2026", "einheit": "in EUR", "stellen": 0,
    "schritte": [
        {"name": "Budget", "wert": b["plan"], "summe": True},
        {"name": "Menge", "wert": b["menge"]},
        {"name": "Mix", "wert": b["mix"]},
        {"name": "Preis", "wert": b["preis"]},
        {"name": "Kosten", "wert": b["kosten"]},
        {"name": "Währung", "wert": b["fx"]},
        {"name": "Notfall", "wert": b["notfall"]},
        {"name": "Ist", "wert": b["ist"], "summe": True},
    ],
}
daten = ('<script id="diagramm-daten">\nconst DIAGRAMME = ' + json.dumps({"verlauf": verlauf, "bruecke": bruecke}, ensure_ascii=False, indent=1) + ";\n</script>")

# ------------------------------------------------------------------ Zusammenbau
html = open(VORLAGE, encoding="utf-8").read()
a = html.index('<main class="buehne" data-firma=')  # nicht die Erwähnung im Kommentar am Dateianfang
e = html.index("</main>", a) + len("</main>")
html = html[:a] + main + html[e:]
a = html.index('<script id="diagramm-daten">')
e = html.index("</script>", a) + len("</script>")
html = html[:a] + daten + html[e:]
html = html.replace("<title>Dr. Sthamer · Vorlage Präsentation (Exhibit-Stil)</title>", "<title>Dr. Sthamer · Beirat 09.03.2027 · Ein Jahr Umstellungsprogramm</title>")
with open(ZIEL, "w", encoding="utf-8") as f:
    f.write(html)
print("geschrieben:", ZIEL, "Folien: 6 (5 Inhalt + Anhang)")
