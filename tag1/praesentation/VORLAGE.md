# Vorlage im Exhibit-Stil für Management-Präsentationen

`vorlage.html` ist ein Foliensatz im **Exhibit-Stil**: Folien im Format 16:9 (1280 × 720 Pixel), ein Aktionstitel je
Folie, ein einziger blauer Akzent, graue Karten mit blauem Oberbalken, eine navyblaue Fazitbox nur auf Kernfolien und
eine Quellenzeile auf jeder Folie mit Zahlen. Die Vorlage enthält je einen Baustein jeder Folienart mit Platzhaltern in
eckigen Klammern.

Für eine Präsentation die Vorlage nach `meine-ergebnisse/praesentation.html` kopieren und dort arbeiten; die Vorlage
selbst bleibt unverändert.

Die Datei läuft **ohne Internet** direkt aus dem Ordner. Die Diagramm-Bibliothek D3 7.9.0 ist am Ende der Datei
eingebettet; diesen Block nicht ändern und nichts aus dem Netz nachladen. Schriften sind Systemschriften: Georgia für
Titel, Arial für Text. Es gibt kein Logo.

**Firmenbezeichnung:** Dr. Sthamer (Attribut `data-firma` an `<main class="buehne">`, erscheint in der Fußzeile).

## Regeln für den Inhalt

1. **Eine Botschaft je Folie.** Der Titel ist diese Botschaft als ganzer Satz mit Verb (Aktionstitel):
   „[Gruppe] wächst schneller als der Rest, weil [Grund]“, nicht „Umsatz nach [Gruppe]“. Höchstens zwei Zeilen. Wer nur die Titel
   liest, kennt die Geschichte. Ausnahme: Titelfolie und Anhang.
2. **Die Meta-Zeile unter dem Titel** nennt Kennzahl, Zeitraum und Zählweise in Kürze, Fakten mit « · » getrennt,
   das erste fett.
3. **Der Inhalt belegt den Titel** und nichts anderes. Höchstens drei Punkte in einer Karte, höchstens drei Beschlüsse
   auf der Entscheidungsfolie, je ein Satz.
4. **Jede Zahl mit Quelle und Definition** in der Quellenzeile unten: Tabelle oder Unterlage in Worten, Stichtag, was
   gezählt wird (etwa „Umsatz im Kalenderjahr nach Lieferdatum, netto nach Gutschriften und Retouren, ohne Muster, in EUR
   zum Konzernkurs des Jahres“), Währung und Kurs. Keine Dateipfade, keine Spaltennamen.
   Einschränkungen (Übungsausschnitt, Teiljahr, Zahl für das ganze Unternehmen, kleine Basis) stehen dort, nicht nur in
   den Notizen. Ist, Budget und Ziel immer als solche bezeichnen.
5. **Zahlen** aus den eigenen Ergebnissen oder frisch aus den Tabellen, nie geschätzt. Deutsches Format: 1.513.301 ·
   34,6 % · EUR 1.240; Fremdwährungen getrennt oder umgerechnet mit genanntem Kurs; Datum TT.MM.JJJJ. Zwischen Zahl und
   Einheit ein geschütztes Leerzeichen (`34,6&nbsp;%`, `EUR&nbsp;1.240`). Große Beträge runden (`EUR 1,24 Mio.`).
   Unterschiede von Anteilen in Prozentpunkten („+7 Prozentpunkte“), nicht in Prozent.
6. **Schrift:** Fließtext mindestens 18 px, Beschriftungen, Achsen und Quellen mindestens 13 px. Passt ein Text nicht,
   kürzen, nicht verkleinern.
7. **Navyblaue Fazitbox** nur auf Kernfolien, höchstens zwei im Satz (meist nur auf der Entscheidungsfolie). Keine
   Leseanleitungen auf Folien („Lesebeispiel“, „Achtung“); was der Sprecher sagt, gehört in die Notizen.
8. **Sprechernotizen** zu jeder Folie, fünf Zeilen: „Kernsatz:“, „Zur Zahl:“ (Definition in Alltagssprache),
   „Einschränkung:“, „Überleitung:“ (letzte Folie: Frage in die Runde), „Zeit: n Minuten“. Die Zeiten ergeben die
   Redezeit aus dem Auftrag.
9. Im fertigen Satz keine eckigen Klammern, kein Hinweis „Beispieldaten“, keine leeren Bausteine.

## Farben

| Name | Wert | Wofür |
|---|---|---|
| Navy | `#051C2C` | Titel, Fazitbox, Summenbalken, die eine Botschafts-Reihe im Diagramm |
| Blau | `#2251FF` | der einzige Akzent: Rubrik, Oberbalken, Nummern, normale Balken und Linien |
| Hellblau | `#E6EEFF` | hervorgehobene Tabellenzeile |
| Mittelblau | `#9DB0FF` | Rückgänge im Wasserfall |
| Kartengrau / Linie | `#F0F0F0` / `#D0D0D0` | Karten / Trennlinien |
| Kontextgrau | `#A6A6A6` | Vergleichsreihe (etwa Gesamt) |
| Text / Meta / Quelle | `#333333` / `#4D4D4D` / `#6B6B6B` | Fließtext / Meta-Zeile / Quellen, Achsen, Fußzeile |

Keine weiteren Farben, **keine Ampelfarben** (rot, gelb, grün). Rot (`#C0392B`) nur für den Prüfkasten der Vorlage,
nie auf einer Folie.

## Aufbau einer Folie

Rand links und rechts 56 px. Von oben: Rubrik (blau, Großbuchstaben, etwa „Geschäftsjahr 2026 · Frage 1“) →
Aktionstitel (Georgia 30 px, höchstens zwei Zeilen) → Meta-Zeile → Inhaltsfläche → optional Fazitbox → Quellenzeile →
Fußzeile. Fußzeile und Foliennummer setzt die Vorlage selbst; den Text der Fußzeile ändert man einmal im Attribut
`data-fuss` (etwa „Beirat · 09.03.2027“).

## Bausteine

| Baustein (`data-baustein`) | Aufbau | Wofür |
|---|---|---|
| `titel` | Rubrik, Titel, Untertitel, Sitzung, vorgelegt von, Datenstand | immer die erste Folie |
| `zusammenfassung` | zwei bis drei Zeilen: Nummer, Frage in Kurzform mit Folienverweis, Antwort, Beleg, Zahl rechts | Agenda und Antwort zugleich, gleich nach dem Titel |
| `diagramm` | Diagramm links (Daten im Block «DIAGRAMM-DATEN»), graue Karte rechts mit großer Zahl oder Treibern | die wichtigsten Aussagen |
| `tabelle` | Einheit über der Tabelle, Zahlen rechtsbündig, eine Zeile hervorgehoben, Summenzeile | genaue Werte zum Nachschlagen |
| `entscheidung` | bis drei Beschlüsse: Nummer, Stichwort, ein Satz, Zahl rechts; darunter die Fazitbox mit „Nächster Schritt“ | immer die letzte Inhaltsfolie |
| `anhang` | Tabelle Kennzahl · Definition · Quelle · Stand | Quellen und Definitionen, nach der letzten Inhaltsfolie |

Neue Folie: die passende `<section class="folie" …>` ganz kopieren und Texte ersetzen. Die Kommentare in
`vorlage.html` sagen, was wo steht.

## Diagramme

Ein Diagramm auf einer Folie ist ein `<svg class="diagramm" data-daten="NAME">`; seine Werte stehen im Block
**«DIAGRAMM-DATEN»** unter dem Eintrag `NAME`. Nur diesen Block ändern. Den Diagrammkopf (Kennzahl fett, Zusatz,
Einheit einmal) schreibt die Vorlage aus `titel`, `zusatz` und `einheit`.

| Art | Wofür | Daten |
|---|---|---|
| `linie` | Verlauf über die Jahre, Abstand zum Ziel | `x` (Jahre als Text), `reihen` mit `name`, `werte`; eine Reihe `betont: true` (navy), Vergleich `grau: true`; `ziel: { wert, text }`; `teiljahr: true` setzt den letzten Wert gestrichelt ab |
| `balken` | Rangfolge, Vergleich von Gruppen | `balken` mit `name`, `wert`, eine Gruppe `betont: true` |
| `wasserfall` | Brücke von einem Wert zum anderen, etwa Budget → Ist nach Menge, Mix, Preis, Währung | `schritte` mit `name`, `wert`; erster und letzter mit `summe: true`, eine Zwischensumme (etwa „Ist ohne Sondereffekt“) ebenso mit `summe: true`; optional `basis` (Achse beginnt nicht bei 0, Bruchzeichen auf den Summen; dann in der Quellenzeile sagen) |
| Tabelle | genaue Werte | Baustein `tabelle`, kein Datenblock |

- Eine Botschafts-Reihe oder ein Botschafts-Balken in Navy, die anderen blau, Vergleich grau. Werte stehen an den
  Linienenden und Balken; keine Legende, keine Ampelfarben, keine Torten, kein 3D.
- `null` heißt Lücke (kein oder zu kleiner Bestand, etwa weniger als 20 Positionen), nie 0 eintragen.
- `linie` und `balken` zeigen nur Werte ab 0 (Liter, EUR, Anteile). Veränderungen, auch negative, gehören in den Wasserfall, in die Beleg-Zahl unter dem Titel oder in eine Tabelle.
- Ein Wert in einer Linie darf `{ wert, zaehler, nenner }` sein: Zähler und Nenner zeigt der Tooltip beim Überfahren.
- Im Wasserfall müssen Anfang und Schritte genau das Ende ergeben; sonst meldet es der Prüfkasten.
- Reihen- und Schrittnamen kurz (rund 15 Zeichen). Nach dem Eintragen echter Werte den Hinweis «Beispieldaten» auf der
  Folie löschen.

## Prüfen, zeigen und exportieren

- **Prüfkasten:** Beim Öffnen prüft die Vorlage sich selbst und meldet in einem roten Kasten oben rechts: Titel länger als
  zwei Zeilen, Text läuft über oder in die Fußzeile, Schrift kleiner als erlaubt, fehlende oder zu knappe Quelle,
  Platzhalter in eckigen Klammern (auch in Notizen und Daten), Hinweis «Beispieldaten», fehlende Notizen, mehr als drei
  Punkte oder Beschlüsse, Wasserfall geht nicht auf, mehr als zwei Fazitboxen. Betroffene Stellen sind rot gestrichelt.
  Das Ergebnis steht auch im Attribut `data-pruefung` am `<body>` (`ok` = alles in Ordnung); ohne Fenster lesbar mit
  Edge oder Chrome im Hintergrund und `--dump-dom` (Befehl in den Kommentaren der Vorlage).
- **Zeigen:** Im Browser öffnen. Pfeiltasten oder Leertaste blättern, Pos1/Ende springen, **Taste S** blendet die
  Sprechernotizen unter der Folie ein und aus (mit Titel der nächsten Folie), F Vollbild, P Drucken.
- **PDF:** in Edge oder Chrome Drucken (Taste P oder Strg+P) → Als PDF speichern, Ränder keine, Hintergrundgrafiken an;
  eine Folie je Seite im Format 16:9. Mit einer Notizseite nach jeder Folie: die Adresse mit `?druck-notizen` öffnen und
  so drucken. Ohne Klicken geht es mit Edge oder Chrome im Hintergrund (`--headless --print-to-pdf`, Befehl und Pfade in
  den Kommentaren der Vorlage). Danach prüfen: Seitenzahl = Zahl der Folien, Diagramme sichtbar, nichts abgeschnitten.

*Übungsfall mit fiktiven Daten. Kunden, Produkte, Personen und Zahlen sind erfunden.*
