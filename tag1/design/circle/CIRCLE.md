# Circle Design – Stilfibel für Dashboards

Circle Design ist das Design-Framework von Falk Uebernickel. Alle Dashboards dieses Tages (Drill 1 bis 3) sehen damit gleich aus: ruhig, warm, gut lesbar, hell und dunkel. Diese Fibel gilt für Teilnehmende und für Claude.

**Drei Dateien, sonst nichts:**

| Datei | Wozu |
|---|---|
| `circle.css` | Tokens: alle Farben, Schriften, Abstände, Radien, Schatten. Die **einzige** Stelle mit Farbwerten. Nicht ändern. |
| `komponenten.css` | Bausteine (Seite, Kopfzeile, Reiter, Filterleiste, Kachel, Karte, Diagramm, Tabelle, Zustands-Pille, Hinweis, Quelle). Nutzt nur Tokens. Nicht ändern. |
| `beispiel-dashboard.html` | Gerüst mit allen Bausteinen und Platzhaltern in eckigen Klammern. Zum Anschauen und Abschreiben. |

Schriften (Inter, Instrument Serif, Lizenz OFL) liegen in `fonts/`; alles läuft offline aus der Datei, ohne Internet.

## 1 Einbinden

Aus `meine-ergebnisse/dashboard.html` (Pfade relativ, nie absolut):

```html
<link rel="stylesheet" href="../design/circle/circle.css">
<link rel="stylesheet" href="../design/circle/komponenten.css">
```

Eigene Regeln im `<style>` der Seite nur für die Anordnung (Raster, Breiten), und dann nur mit Tokens: `var(--space-4)`, `var(--color-text)`, `var(--chart-series)`. **Keine eigenen Farbwerte** (kein `#…`, kein `rgb(…)`, keine Farbnamen).

## 2 Grundsätze

1. **Papier und Karten.** Die Seite hat einen warmen Papierton mit weichen Verläufen; Inhalte liegen auf weißen Karten mit sanftem Schatten (`--shadow-card`). Keine Rahmen um alles, keine harten Kästen.
2. **Zwei Schriften, klare Rollen.** Instrument Serif nur für kurze Überschriften (h1–h3, Kernaussage). Inter für alles andere: Text, Zahlen, Tabellen, Achsen. Ein Wort in der Überschrift darf mit `<em>` blau-kursiv betont werden – eines, nicht mehr.
3. **Blau heißt „unsere Zahl“ oder „hier klicken“.** Blau ist die Primärserie im Diagramm und die Farbe für Interaktion (aktiver Reiter, Knopf). Blau ist **nie** ein Zustand.
4. **Zustände immer mit Form und Wort.** Grün, Orange, Koralle tragen nie allein eine Bedeutung. Jede Zustands-Pille hat eine Form (Kreis, Dreieck, Raute, gestrichelter Ring) und ein Wort.
5. **Eine Botschaft zuerst.** Oben die Kacheln mit den wichtigsten Zahlen, dann die Diagramme, dann die Tabelle. Filterleiste und Kacheln passen zusammen in den ersten Bildschirm.
6. **Jede Zahl mit Herkunft.** Unter jeder Karte eine Quellenzeile (`.quelle`): Tabelle in Worten, Stichtag, Definition, Einschränkung.

## 3 Farben und Tokens

Nur über Tokens ansprechen. Die wichtigsten:

| Zweck | Token |
|---|---|
| Seite, Karte, ruhige Fläche | `--color-bg`, `--color-surface`, `--color-surface-muted` |
| Text: Haupt, zweitrangig, leise | `--color-text`, `--color-text-secondary`, `--color-text-muted` |
| Linien | `--color-border`, `--color-border-strong` |
| Interaktion, Link, Fokus | `--color-accent`, `--color-link`, `--color-focus` |
| Hinweis (blau), Warnung, Beispiel | `--color-accent-soft`, `--color-warning-bg`, `--color-demo-bg` |
| Zustände | `--state-ok`, `--state-warn`, `--state-crit`, `--state-off` (dazu je `-bg` und `-text`) |
| Kernaussage, Einordnung | `--color-ai-bg`, `--color-ai-border` |
| Abstände | `--space-1` (4 px) bis `--space-7` (48 px) |
| Radien, Schatten | `--radius-md`, `--radius-pill`, `--shadow-card` |

## 4 Typografie

| Element | Schrift | Größe |
|---|---|---|
| Titel der Seite (h1) | Instrument Serif | 34 px |
| Kartentitel (h3) | Instrument Serif | 19 px |
| Kernaussage | Instrument Serif | 21 px |
| Fließtext, Tabelle | Inter | 13–13,5 px |
| Kachelwert | Inter 650, Ziffern gleich breit | 26 px |
| Etikett (`.etikett`), Tabellenkopf | Inter, Großbuchstaben, gesperrt | 10,5 px |
| Achsen, Quellen | Inter | 12 px |

Zahlen immer deutsch: 1.234,5 · 34,6 % · EUR 1.240,00 · 28.02.2027. Zwischen Zahl und Einheit kein Umbruch (`.zahl` oder `&nbsp;`).

## 5 Bausteine

**Seite und Kopfzeile**

```html
<div class="seite">
  <header class="kopf">
    <div class="kopf__titel">
      <span class="etikett">Dr. Sthamer · Übungsausschnitt</span>
      <h1>Umstellung auf <em>fluorfrei</em></h1>
    </div>
    <div class="kopf__meta"><span>Stichtag <span class="zahl">28.02.2027</span></span></div>
  </header>
  …
</div>
```

**Reiter** (der aktive hat `aria-selected="true"`, der Inhalt ist eine `section.reiterinhalt`, die anderen `hidden`)

```html
<nav class="reiter" role="tablist">
  <button class="reiter__knopf" role="tab" data-reiter="ueberblick" aria-selected="true">Überblick</button>
  <button class="reiter__knopf" role="tab" data-reiter="umstellung" aria-selected="false">Umstellung</button>
</nav>
<section class="reiterinhalt" id="reiter-ueberblick">…</section>
<section class="reiterinhalt" id="reiter-umstellung" hidden>…</section>
```

Die Abschnitte heißen `reiter-…`, nicht wie der Reiter selbst: Sonst springt der Browser beim Öffnen mit `#umstellung`
zum Abschnitt, und Kopfzeile und Reiter sind aus dem Bild. Beim Reiterwechsel nach oben scrollen.

**Filterleiste** und **Umschalter**

```html
<div class="filter">
  <label class="filter__feld">Jahr <select>…</select></label>
  <span class="filter__ende umschalter">
    <button aria-pressed="true">Liter</button><button aria-pressed="false">Umsatz</button>
  </span>
</div>
```

**Kennzahl-Kachel** (Wert einzeilig, Definition kurz darunter, vollständig in `data-tip`)

```html
<div class="kacheln">
  <div class="kachel" data-tip="Volle Definition mit Zähler und Nenner">
    <span class="kachel__name">Fluorfrei-Anteil</span>
    <span class="kachel__wert">[n]<small>%</small></span>
    <span class="kachel__def">2026, Liter netto</span>
    <span class="kachel__delta kachel__delta--auf">▲ [n] Prozentpunkte zum Vorjahr</span>
  </div>
</div>
```

**Karte und Diagrammkarte**

```html
<article class="karte">
  <div class="karte__kopf"><h3>Aussage als Satz</h3><span class="karte__unter">Einheit</span></div>
  <div class="diagramm" id="d-linie"></div>
  <div class="legende">…</div>
  <p class="quelle">Quelle: Auftragstabelle, Lieferdatum; Stichtag 28.02.2027. Definition: …</p>
</article>
```

`karte--flach` für ruhige Nebeninhalte, `kernaussage` mit `kernaussage__satz` für den einen Satz, der zählt.

**Tabelle** (Zahlenspalten rechtsbündig mit `class="zahl"`, Summe im `tfoot`; in einer Karte mit `.tabelle-rahmen` umschließen)

```html
<div class="tabelle-rahmen"><table class="tabelle">
  <thead><tr><th>Segment</th><th class="zahl">Liter</th><th>Ampel</th></tr></thead>
  <tbody><tr><td>[Segment]</td><td class="zahl">[n]</td><td><span class="zustand zustand--ok">grün</span></td></tr></tbody>
</table></div>
```

**Zustands-Pille** (Form kommt automatisch aus der Klasse)

| Klasse | Form | Wort (Beispiel) |
|---|---|---|
| `zustand--ok` | Kreis, grün | grün, im Ziel |
| `zustand--warn` | Dreieck, orange | gelb, beobachten |
| `zustand--crit` | Raute, koralle | rot, Hier entscheidet ein Mensch |
| `zustand--off` | gestrichelter Ring | Lücke (zu kleine Basis) |
| `zustand--neutral` | Quadrat, grau | offen |

Die Regel der Ampel steht sichtbar über der Tabelle (`.regel` mit den Pillen und den Schwellen).

**Hinweis und Quelle:** `.hinweis` (blau, Information), `.hinweis--warnung`, `.hinweis--beispiel` (gelb, für Gerüste und Beispielwerte), `.quelle` unter jeder Karte.

## 6 Diagramme

- **Inline-SVG**, selbst gezeichnet, keine Bibliothek, kein Internet. Werte kommen aus einem markierten Datenblock (im Dashboard `dashboard-daten/<reiter>.js`, erzeugt von einem Skript), nie von Hand in die Grafik getippt.
- Farben nur über die Klassen in `komponenten.css`, die auf `--chart-*`-Tokens zeigen:

| Klasse | Token | Wofür |
|---|---|---|
| `d-linie`, `d-balken`, `d-punkt` | `--chart-series` | Primärserie (unsere Zahl) |
| `d-linie--2`, `d-balken--2` | `--chart-series-2` | zweite, blassere Serie |
| `d-linie--vergleich` | `--chart-benchmark` | Vergleich, Vorjahr |
| `d-ziel` | `--chart-marker` | Ziellinie, gestrichelt |
| `d-linie--teil` | (gestrichelt) | Teiljahr, abgesetzt |
| `d-flaeche` | `--chart-area` | Fläche unter der Linie |
| `d-spur` | `--chart-track` | Hintergrundspur eines Balkens |
| `d-raster`, Achsentext | `--chart-grid`, `--chart-axis-text` | Gitter, Achsen |
| `d-wert`, `d-name` | `--chart-label`, `--chart-sub` | Wert am Ende, Name |
| Abweichung ▲ / ▼ | `--chart-delta-up`, `--chart-delta-down` | nur für Veränderung |

- Weitere Gruppen (Segmente, Produktlinien) als Abstufungen der Primärserie (`--chart-series`, `--chart-series-2`, `--chart-benchmark`, `--chart-peer`), jede Gruppe in allen Ansichten mit derselben Farbe. Zustandsfarben nie als Serienfarbe.
- Prozentachsen in runden Schritten (0, 25, 50, 75, 100 %); Wert am letzten Punkt; Zähler und Nenner beim Überfahren (`data-tip`); Lücken ohne Punkt; Teiljahr gestrichelt; keine Beschriftung überdeckt eine andere.
- Das SVG in der echten Pixelbreite der Karte zeichnen (`clientWidth`) und beim Reiterwechsel neu, damit Schrift überall 12 px bleibt (so im Gerüst).

## 7 Dark Mode

Läuft automatisch nach der Systemeinstellung. Übersteuern mit `<html data-theme="dark">` oder `"light"`; das Gerüst hat dafür den Umschalter System/Hell/Dunkel (und `?thema=dark` in der Adresse). Wer nur Tokens benutzt, muss für Dark Mode nichts tun. Prüfen: einmal hell, einmal dunkel als Screenshot ansehen.

## 8 Was man nicht tut

- Keine eigenen Farbwerte, keine Farbnamen, kein Ändern von `circle.css` oder `komponenten.css`.
- Kein Zustand nur über Farbe; kein Blau als Zustand; keine Ampelfarbe als Diagrammserie.
- Keine Serifenschrift für Fließtext, Zahlen oder Tabellen.
- Keine Bibliotheken oder Schriften aus dem Internet, keine absoluten Pfade.
- Kein Logo, keine Namen von Veranstaltern; die Firma heißt „Dr. Sthamer“.
- Keine 3D-Diagramme, Tortendiagramme mit vielen Stücken oder Doppelachsen.
- Nicht mehrere Kernaussagen auf einer Karte; nicht mehr als eine Kernaussage je Reiter.
- Keine Zahl ohne Quellenzeile.
