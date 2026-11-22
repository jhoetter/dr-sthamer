# Exhibit-Stil – Bausteine, Diagrammdaten, Befehle

Nachschlagen beim Bauen. Die Regeln stehen in `SKILL.md`.

## Bausteine der Vorlage

Jede Folie ist eine `<section class="folie" data-baustein="…">` in `<main class="buehne" data-firma="…" data-fuss="…">`.

| `data-baustein` | Wichtige Teile |
|---|---|
| `titel` | `.eyebrow`, `.t-titel`, `.t-unter`, `.t-meta` (Sitzung, Vorgelegt von, Datenstand); `data-quelle="keine"` |
| `zusammenfassung` | `.zeile` mit `.num`, `.frage` (Kurzform + Folienverweis), `.antwort`, `.beleg`, Zahl rechts |
| `diagramm` | `.diagrammfeld` mit `.diagrammkopf[data-kopf=NAME]` und `<svg class="diagramm" data-daten="NAME">`, rechts `.karte` (Etikett, große Zahl, Erklärung, bis drei Punkte) |
| `tabelle` | `.einheitzeile`, `table.tabelle`; Zahlenspalten `class="z"`, hervorgehoben `tr.betont`, Summe `tr.summe`; höchstens rund sechs Zeilen |
| `entscheidung` | bis drei `.beschluss` (Nummer, `.stichwort`, `.satz`, Zahl rechts), darunter `.fazit` mit „Nächster Schritt“ |
| `anhang` | Tabelle Kennzahl · Definition · Quelle · Stand |

Gemeinsam auf Inhaltsfolien: `.eyebrow`, `<h2>` (Aktionstitel), `.meta` (Fakten mit `<span class="dot">·</span>`
getrennt, das erste in `<b>`), `.quelle` mit `<span class="qk">Quelle</span>`, `<aside class="notizen">`.
Die Kommentare in der Vorlage sagen, was wo steht.

## Diagrammdaten (Block «DIAGRAMM-DATEN»)

Ein `<svg class="diagramm" data-daten="NAME">` zeichnet den Eintrag `NAME` aus `const DIAGRAMME = { … }`.

Gemeinsame Felder: `art` (`"linie"` | `"balken"` | `"wasserfall"`), `titel` (Kennzahl, fett im Kopf), `zusatz`
(Gliederung und Zeitraum), `einheit` (einmal im Kopf), `stellen` (0 oder 1 Nachkommastelle).

```js
umsatz: {
  art: "linie", titel: "Nettoumsatz", zusatz: "nach Geschäftsteil, 2022–2026", einheit: "in Mio. EUR", stellen: 1,
  x: ["2022", "2023", "2024", "2025", "2026"],
  ziel: { wert: 14, text: "Budget 2026" },          // optional, gestrichelte Linie
  teiljahr: false,                                   // true setzt den letzten Wert gestrichelt ab
  reihen: [
    { name: "Nachfüllung", betont: true, werte: [8.1, 8.6, 9.0, 9.4, { wert: 9.9, zaehler: 9.9, nenner: 1 }] },
    { name: "Projekt",                   werte: [3.0, 2.7, null, 2.5, 2.2] },   // null = Lücke, nie 0
    { name: "Gesamt", grau: true,        werte: [11.1, 11.3, 11.6, 11.9, 12.1] }
  ]
},
rangfolge: {
  art: "balken", titel: "Anteil am Umsatz", zusatz: "nach Vertriebsweg, 2026", einheit: "in %", stellen: 1,
  balken: [ { name: "Direkt", wert: 46.0, betont: true }, { name: "Händler", wert: 31.5 }, { name: "Rahmenvertrag", wert: 22.5 } ]
},
bruecke: {
  art: "wasserfall", titel: "Deckungsbeitrag", zusatz: "Budget → Ist 2026", einheit: "in Tsd. EUR", stellen: 0,
  basis: 0,                                          // > 0 nur, wenn Schritte sonst unlesbar; dann in der Quelle sagen
  schritte: [ { name: "Budget", wert: 5200, summe: true }, { name: "Menge", wert: -310 }, { name: "Preis", wert: 140 },
              { name: "Währung", wert: -30 }, { name: "Ist", wert: 5000, summe: true } ]
}
```

(Die Zahlen oben sind nur ein Formatbeispiel.) Regeln: eine Reihe oder ein Balken `betont` (navy), die anderen blau,
Vergleich `grau`. Namen kurz (rund 15 Zeichen). Wasserfall: Anfang + Schritte = Ende, sonst meldet es der Prüfkasten.
Ein Linienwert darf `{ wert, zaehler, nenner }` sein – der Tooltip zeigt dann Zähler und Nenner.

## Befehle für Edge oder Chrome im Hintergrund

Browserpfad – Windows Edge: `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"`, Windows Chrome:
`"C:\Program Files\Google\Chrome\Application\chrome.exe"`, Mac: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.
Adresse der Datei als `file:///` mit Vorwärts-Schrägstrichen, etwa `file:///C:/Users/<Name>/projekt/meine-ergebnisse/praesentation.html`.

```text
Prüfkasten lesen (im Ergebnis den letzten Wert von data-pruefung suchen; "ok" = alles gut):
  <Browser> --headless --virtual-time-budget=3000 --dump-dom "<Adresse>"

Screenshot einer Folie (#/0 = erste Folie, #/1 = zweite …):
  <Browser> --headless --hide-scrollbars --window-size=1280,720 --virtual-time-budget=3000 --screenshot="<Ordner>\folie-1.png" "<Adresse>#/0"

PDF, eine Folie je Seite:
  <Browser> --headless --no-pdf-header-footer --virtual-time-budget=3000 --print-to-pdf="<Ordner>\praesentation.pdf" "<Adresse>"

PDF mit Notizseite nach jeder Folie: dieselbe Zeile mit der Adresse "<Adresse>?druck-notizen".
```

Screenshots in einen Unterordner (etwa `meine-ergebnisse/screenshots/`) legen und danach ansehen. Startet der
Browser nicht, den Weg von Hand erklären: Datei per Doppelklick öffnen, Taste P, Als PDF speichern, Ränder keine,
Hintergrundgrafiken an.
