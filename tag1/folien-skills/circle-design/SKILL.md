---
name: circle-design
description: Gestaltet gut aussehende HTML-Seiten im Circle Design – warmer Papierton, weiße Karten, Instrument Serif für Überschriften, Inter für Text, hell und dunkel, läuft offline aus der Datei. Verwenden für jede HTML-Seite, die keine Präsentation ist – Dashboard, Übersichtsseite, Bericht oder Handout als Webseite, Begleitseite, Formular, Checkliste im Browser („HTML-Seite“, „Webseite“, „Übersicht“, „Dashboard“, „Bericht im Browser“, „Handout“, „Formular“, „schöne Seite“). Nicht für Folien und Präsentationen; die kommen in den Exhibit-Stil (Skill exhibit-stil).
---

# Circle Design: gut aussehende HTML-Seiten

Circle Design besteht aus zwei Stylesheets und zwei Schriften. Die Seite selbst schreibt man mit den fertigen
Bausteinen; Farben, Schriften, Abstände und Dark Mode kommen aus den Stylesheets.

Dateien in `assets/` dieses Skill-Ordners: `circle.css` (Tokens: die **einzige** Stelle mit Farbwerten),
`komponenten.css` (Bausteine), `fonts/` (Inter und Instrument Serif mit Lizenztexten OFL), `beispiel-seite.html`
(Gerüst einer Seite mit allen Bausteinen).

## 1 Einbinden

1. **Hat das Projekt schon ein Circle-Kit** (ein Ordner mit `circle.css`, `komponenten.css` und `fonts/`, etwa
   `design/circle/`), dieses relativ zur neuen Seite einbinden. Aus `meine-ergebnisse/seite.html` heißt das:
   ```html
   <link rel="stylesheet" href="../design/circle/circle.css">
   <link rel="stylesheet" href="../design/circle/komponenten.css">
   ```
   Eine Stilfibel des Projekts (etwa `design/circle/CIRCLE.md`) geht diesem Skill vor; dort liegt oft auch ein
   Gerüst für Dashboards.
2. **Sonst** den Ordner `assets/` dieses Skills als Unterordner `circle/` neben die neue Seite kopieren (Ordner ganz
   kopieren, die Schriften sind Binärdateien) und `circle/circle.css`, dann `circle/komponenten.css` einbinden.
   `fonts/` muss neben `circle.css` liegen.
3. Pfade immer relativ, nie absolut; nichts aus dem Internet laden (keine Schriften, keine Bibliotheken).
4. `circle.css` und `komponenten.css` nie ändern. Eigene Regeln im `<style>` der Seite nur für die Anordnung (Raster,
   Breiten, Abstände) und nur mit Tokens: `var(--space-4)`, `var(--color-text)`, `var(--chart-series)`.

## 2 Gerüst

- **Seite zum Lesen** (Übersicht, Bericht, Handout, Begleitseite): `beispiel-seite.html` aus `assets/` (oder aus dem
  Kit des Projekts) als Gerüst kopieren, die `<link>`-Pfade anpassen, Platzhalter in `[eckigen Klammern]` ersetzen,
  nicht gebrauchte Abschnitte löschen und den gelben Hinweis «Gerüst» entfernen.
- **Dashboard** (Kacheln, Reiter, Filter, Diagramme): das Dashboard-Gerüst des Projekts nehmen, wenn es eines gibt;
  sonst `beispiel-seite.html` mit den Bausteinen Reiter und Filterleiste aus Abschnitt 4 erweitern.

## 3 Regeln

1. **Papier und Karten:** Inhalte liegen auf weißen Karten mit sanftem Schatten. Keine Rahmen um alles.
2. **Zwei Schriften:** Instrument Serif nur für kurze Überschriften (h1–h3, Kernaussage, Zitat); Inter für alles
   andere, auch Zahlen und Tabellen. Ein Wort im Titel darf mit `<em>` blau-kursiv betont sein, nur eines.
3. **Blau heißt „unsere Zahl“ oder „hier klicken“:** Primärserie im Diagramm, aktiver Reiter, Knopf, Link. Blau ist
   **nie** ein Zustand.
4. **Zustände immer mit Form und Wort:** Grün, Orange, Koralle tragen nie allein eine Bedeutung; die Zustands-Pille
   bringt die Form (Kreis, Dreieck, Raute, gestrichelter Ring) selbst mit, das Wort schreibst du dazu. Die Regel
   (Schwellen) steht sichtbar über der Tabelle.
5. **Keine eigenen Farbwerte:** kein `#…`, kein `rgb(…)`, keine Farbnamen – nur Tokens. Dann funktioniert Dark Mode
   von selbst.
6. **Eine Botschaft zuerst:** oben Titel und Einleitung oder die wichtigsten Kennzahlen, dann Abschnitte, dann
   Tabellen. Höchstens eine Kernaussage je Seite oder Reiter.
7. **Jede Zahl mit Herkunft:** unter jeder Karte mit Zahlen eine Quellenzeile (`.quelle`) – Quelle in Worten,
   Stichtag, Definition, Einschränkung.
8. **Zahlen deutsch:** 1.234,5 · 34,6 % · EUR 1.240,00 · 28.02.2027; zwischen Zahl und Einheit `&nbsp;` oder `.zahl`.
9. Kein Logo, keine Tortendiagramme mit vielen Stücken, kein 3D, keine Doppelachsen.

## 4 Bausteine (aus `komponenten.css`)

| Baustein | Klassen |
|---|---|
| Seite, Raster | `.seite`, `.raster` (zwei Spalten), `.raster--3`, `.stapel` |
| Kopfzeile | `header.kopf` mit `.kopf__titel` (`.etikett` + `h1`) und `.kopf__meta` |
| Reiter | `nav.reiter` mit `button.reiter__knopf[aria-selected]`, Inhalt in `section.reiterinhalt` (Abschnitte heißen `reiter-…`) |
| Filterleiste, Umschalter, Knopf | `.filter`, `.filter__feld`, `.umschalter` mit `button[aria-pressed]`, `.knopf`, `.knopf--primaer` |
| Kennzahl-Kachel | `.kacheln` > `.kachel` mit `.kachel__name`, `.kachel__wert` (`<small>` Einheit), `.kachel__def`, `.kachel__delta--auf`/`--ab`; volle Definition in `data-tip` |
| Karte | `article.karte` (`.karte--flach` für Nebeninhalte), `.karte__kopf` mit `h3` und `.karte__unter` |
| Tabelle | `.tabelle-rahmen` > `table.tabelle`; Zahlenspalten `class="zahl"`, Summe im `tfoot` |
| Zustands-Pille | `.zustand--ok` (Kreis), `--warn` (Dreieck), `--crit` (Raute), `--off` (gestrichelter Ring = Lücke), `--neutral` (Quadrat) |
| Hinweis, Kernaussage, Quelle | `.hinweis`, `.hinweis--warnung`, `.hinweis--beispiel` (gelb, nur für Gerüste); `.kernaussage` > `.kernaussage__satz`; `.quelle` |
| Etikett, leise, Zahl | `.etikett` (Großbuchstaben), `.leise`, `.zahl` (Ziffern gleich breit, kein Umbruch) |

## 5 Diagramme

- Inline-SVG, selbst gezeichnet, ohne Bibliothek und ohne Internet, in einem `<div class="diagramm">`. Werte aus einem
  markierten Datenblock oder einer Datendatei, nie von Hand in die Grafik getippt.
- Farben nur über die Klassen: `d-linie`, `d-balken`, `d-punkt` (Primärserie), `d-linie--2`, `d-balken--2` (zweite
  Serie), `d-linie--vergleich` (Vorjahr, Vergleich), `d-ziel` (Ziellinie), `d-linie--teil` (Teiljahr gestrichelt),
  `d-flaeche`, `d-spur`, `d-raster`, `d-wert`, `d-name`. Zustandsfarben nie als Serienfarbe.
- Wert am letzten Punkt, Achsen in runden Schritten, Zähler und Nenner beim Überfahren, keine Beschriftung überdeckt
  eine andere. SVG in der echten Breite der Karte zeichnen, damit die Schrift 12 px bleibt.

## 6 Hell, dunkel und prüfen

- Dark Mode folgt der Systemeinstellung; übersteuern mit `<html data-theme="dark">` oder `"light"`. Das Gerüst hat
  einen Umschalter System/Hell/Dunkel und versteht `?thema=dark` in der Adresse.
- Nach dem Bauen die Seite im Browser öffnen und **zwei Screenshots ansehen**: hell und mit `?thema=dark`. Mit Edge
  oder Chrome im Hintergrund, etwa
  `<Browser> --headless --hide-scrollbars --window-size=1280,1800 --virtual-time-budget=3000 --screenshot="<Ordner>\seite-dunkel.png" "file:///<Pfad>/seite.html?thema=dark"`
  (Browserpfade: Windows Edge `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`, Chrome
  `C:\Program Files\Google\Chrome\Application\chrome.exe`).
- Prüfen: Schriften geladen (Überschriften in schmaler Serifenschrift, nicht Times)? Nichts läuft über? Jede Zahl mit
  Quelle? Keine Platzhalter mehr? In beiden Modi lesbar?
