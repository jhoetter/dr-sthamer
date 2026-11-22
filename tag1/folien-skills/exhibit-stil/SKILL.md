---
name: exhibit-stil
description: Baut und prüft Folien und Präsentationen im Exhibit-Stil (Navy, ein blauer Akzent, Aktionstitel in Georgia, graue Karten mit blauem Oberbalken, Fazitbox nur auf Kernfolien, Quellenzeile auf jeder Folie mit Zahl) als HTML-Foliensatz aus einer Vorlage, mit Diagrammen, Sprechernotizen, eingebautem Prüfkasten und PDF über Edge oder Chrome. Verwenden, wenn jemand eine Folie, eine Präsentation, eine Management-Präsentation, eine Unterlage für Beirat, Vorstand oder Geschäftsführung, ein Exhibit oder ein Diagramm für Folien bauen, ändern, prüfen oder als PDF ausgeben will („Folie“, „Foliensatz“, „Präsentation“, „Beirat“, „Exhibit“, „Folien als PDF“). Titel und Storyline zusätzlich nach dem Skill aktionstitel; HTML-Seiten, die keine Folien sind, nach circle-design.
---

# Exhibit-Stil: Folien als HTML-Foliensatz

Ein Foliensatz im Exhibit-Stil ist **eine HTML-Datei**: Folien 1280 × 720 px (16:9), läuft offline aus dem Ordner,
blättert im Browser, druckt als PDF und prüft sich beim Öffnen selbst. Bausteine, Datenformat der Diagramme und
Befehle stehen in `bausteine.md` in diesem Ordner.

## 1 Welche Vorlage

1. Hat das Projekt eine eigene Vorlage im Exhibit-Stil (etwa `praesentation/vorlage.html` mit einer Stilfibel wie
   `VORLAGE.md`), **diese** nehmen. Die Stilfibel des Projekts geht diesem Skill vor.
2. Sonst `vorlage.html` aus diesem Skill-Ordner nehmen.
3. Die Vorlage nie selbst ändern: in den Ergebnisordner kopieren (etwa `meine-ergebnisse/praesentation.html`) und
   dort arbeiten. Den Block `<style>`, die Skripte und die eingebettete Bibliothek D3 (letzter Block, eine sehr lange
   Zeile) nicht lesen und nicht ändern. Nichts aus dem Internet nachladen, nichts installieren.

## 2 Ablauf

1. **Storyline zuerst** (Skill aktionstitel): je Folie ein Aktionstitel und die Zahl, die ihn belegt. Bringt die
   Person ihre Titel mit, gehören sie ihr: wörtlich übernehmen. Verstößt ein Titel gegen eine Regel, ihn trotzdem
   setzen und danach jede Abweichung mit Gegenvorschlag nennen.
2. **Zahlen** aus den eigenen Ergebnissen oder frisch aus den Tabellen, vor dem Einsetzen gegen die Quelle prüfen,
   nie schätzen. Umschreibungen („jeder dritte“, „verdoppelt“) nachrechnen.
3. **Folien bauen:** die passende `<section class="folie" data-baustein="…">` ganz kopieren, Platzhalter in
   `[eckigen Klammern]` ersetzen, nicht gebrauchte Bausteine löschen.
4. **Diagramme** nur über den Block «DIAGRAMM-DATEN» füllen (Format in `bausteine.md`), danach den Hinweis
   «Beispieldaten» auf der Folie löschen.
5. **Sprechernotizen** in jede Folie, **prüfen** (Abschnitt 6), **PDF** erzeugen, Präsentation im Browser öffnen.

## 3 Aufbau jeder Inhaltsfolie

Von oben: **Rubrik** (Eyebrow, blau, Großbuchstaben) → **Aktionstitel** (Georgia 30 px, ganzer Satz mit Verb,
höchstens zwei Zeilen) → **Meta-Zeile** (Kennzahl · Zeitraum · Zählweise, das erste fett, keine zweite Aussage) →
**Inhalt** (Diagramm, Karten, Tabelle) → optional **Fazitbox** → **Quellenzeile** → Fußzeile mit Foliennummer
(setzt die Vorlage selbst; Text einmal im Attribut `data-fuss` an `<main class="buehne">`).

## 4 Welcher Baustein, welches Diagramm

| Aussage | Form | Baustein / Art |
|---|---|---|
| Worum es geht, wer vorlegt, Datenstand | Titelfolie | `titel` (immer zuerst) |
| Die Antwort in zwei, drei Zeilen vorweg | Zusammenfassung mit Zahl je Zeile | `zusammenfassung` |
| Verlauf über die Jahre, Abstand zum Ziel | Linie, eine Reihe navy | `diagramm` + `linie` |
| Rangfolge, Vergleich von Gruppen | waagrechte Balken, ein Balken navy | `diagramm` + `balken` |
| Von A nach B, zerlegt in Treiber (Budget → Ist, Vorjahr → Jahr) | Wasserfall | `diagramm` + `wasserfall` |
| Eine einzige Schlüsselzahl | große Zahl in der grauen Karte rechts | Karte im `diagramm` |
| Genaue Werte zum Nachschlagen | Tabelle, eine Zeile hervorgehoben, Summenzeile | `tabelle` |
| Was beschlossen werden soll | bis drei Beschlüsse + Fazitbox „Nächster Schritt“ | `entscheidung` (letzte Inhaltsfolie) |
| Definitionen und Quellen | Tabelle Kennzahl · Definition · Quelle · Stand | `anhang` (nach dem Schluss) |

Die Form folgt der Aussage, nicht der Gewohnheit. Höchstens ein Diagramm je Folie. Keine Torten, kein 3D, keine
Doppelachsen, keine Legendenkästen: Werte stehen an Balken und Linienenden.

## 5 Inhaltsregeln

1. **Eine Botschaft je Folie.** Der Titel sagt sie, der Inhalt belegt sie und nichts anderes. Wer nur die Titel
   liest, kennt die Geschichte.
2. **Wenig Text:** höchstens drei Punkte in einer Karte, höchstens drei Beschlüsse, je ein Satz. Kartentitel ein bis
   drei Wörter. Nicht überall drei Spalten oder drei Punkte – so viele, wie der Inhalt hat.
3. **Farben:** Navy `#051C2C` für Titel, Fazitbox und die eine Botschafts-Reihe; Blau `#2251FF` als einziger Akzent;
   Grau für Vergleich und Karten. **Keine Ampelfarben** (rot, gelb, grün), keine weiteren Farben.
4. **Fazitbox** (navy) nur auf Kernfolien, höchstens zwei im Satz, meist nur auf der Entscheidungsfolie. Sie sagt die
   Folgerung, nicht noch einmal den Titel.
5. **Quelle Pflicht:** jede Folie mit Zahl hat eine Quellenzeile – Quelle in Worten, Stichtag, was gezählt wird,
   Währung und Kurs, Einschränkungen (Teiljahr, kleine Basis, Ausschnitt). Ist, Budget und Ziel immer als solche
   benennen. Keine Dateipfade, keine Spaltennamen.
6. **Zahlenformat deutsch:** 1.513.301 · 34,6 % · EUR 1,24 Mio. · 28.02.2027; zwischen Zahl und Einheit `&nbsp;`;
   Unterschiede von Anteilen in Prozentpunkten.
7. **Schrift:** Fließtext mindestens 18 px, Beschriftungen und Quellen mindestens 13 px. Passt etwas nicht: kürzen,
   nie die Schrift verkleinern.
8. **Keine Leseanleitungen** auf Folien („Achtung“, „Lesebeispiel“, „sortiert nach …“). Was der Sprecher sagt,
   gehört in die Notizen.
9. **Sprechernotizen** (`<aside class="notizen">`) zu jeder Folie, fünf Zeilen: „Kernsatz:“, „Zur Zahl:“,
   „Einschränkung:“, „Überleitung:“ (letzte Folie: Frage in die Runde), „Zeit: n Minuten“. Die Zeiten ergeben die
   geplante Redezeit.
10. Kein Logo, keine echten Kunden- oder Personendaten, die nicht in den Unterlagen stehen.

## 6 Prüfen und PDF

1. **Prüfkasten:** Die Vorlage prüft sich beim Öffnen (Titel über zwei Zeilen, Überlauf, zu kleine Schrift, fehlende
   Quelle, Platzhalter, «Beispieldaten», fehlende Notizen, zu viele Punkte, Wasserfall geht nicht auf, zu viele
   Fazitboxen). Ergebnis: roter Kasten oben rechts und Attribut `data-pruefung` am `<body>` (`ok` = alles gut). Ohne
   Fenster mit Edge oder Chrome im Hintergrund lesen (`--dump-dom`, Befehl in `bausteine.md`); maßgeblich ist der
   letzte Wert von `data-pruefung`. Beheben, bis `ok` steht.
2. **Folien zählen:** genau die geplanten Folien, nicht gebrauchte Bausteine gelöscht.
3. **Jede Folie ansehen:** Screenshot je Folie (Adresse mit `#/0`, `#/1` …, Befehl in `bausteine.md`) und das Bild
   anschauen: läuft etwas über, ist etwas unlesbar, steht der Titel so da wie geplant?
4. **PDF:** mit Edge oder Chrome im Hintergrund (`--print-to-pdf`, Befehl in `bausteine.md`), eine Folie je Seite.
   Danach prüfen: Seitenzahl = Zahl der Folien, Diagramme sichtbar, nichts abgeschnitten. Klappt es nicht, den Weg von
   Hand erklären: im Browser Drucken (Taste P) → Als PDF speichern, Ränder keine, Hintergrundgrafiken an.
5. **Zeigen:** Datei im Browser öffnen. Pfeiltasten blättern, **S** Sprechernotizen, **F** Vollbild, **P** Drucken.

## 7 Fertig, wenn

- jede Folie einen Aktionstitel mit höchstens zwei Zeilen hat und die Titel allein die Geschichte erzählen,
- jede Zahl stimmt und eine Quellenzeile hat,
- der Prüfkasten `ok` meldet und jede Folie als Bild angesehen wurde,
- jede Folie Sprechernotizen hat und das PDF eine Seite je Folie hat,
- jede Änderung an Titeln der Person genannt wurde.
