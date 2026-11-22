# Drill 1 · Überblicks-Dashboard: Wo wachsen wir, wo verlieren wir?

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 75 Minuten: 10 Einführung · 55 Übung · 10 Auswertung.

> **Du startest mit** der Notiz zur Kundenzahl aus Drill 0 (`meine-ergebnisse/notiz-kundenzahl.md`). Die Zählweise,
> die du dort empfohlen hast, wird die Definition der Kunden-Kachel. Fehlt die Notiz, legst du die Zählweise in
> Etappe 2 selbst fest.

## Deine Rolle

Du bist Dr. Henrike Vossberg, Leiterin Unternehmensentwicklung bei Dr. Sthamer. Die Geschäftsführerin hat dir
aufgetragen, dem Beirat am 09.03.2027 das Geschäftsjahr 2026 zu zeigen und Prioritäten für 2027 vorzuschlagen.
Ihre Frage zieht sich durch den ganzen Tag: „Wo wachsen wir, wo verlieren wir – und was heißt das für 2027?“
Heute legst du den ersten Teil: Wie haben sich Absatz und Umsatz entwickelt, nach Segment, Land und Vertriebsweg,
und was davon ist laufendes Nachfüllgeschäft, was einmaliges Projektgeschäft?

## Lernziel

Du lässt Claude eine unübersichtliche Datenlage erkunden und daraus ein Dashboard im Circle Design bauen, das du
im Browser bedienst: erst den Überblick, dann die Analyse. Du lenkst Auswertungen in Geschäftssprache („nur
Händler“, „ohne den Notfall“), verlangst zu jeder Zahl die Definition und rechnest mindestens eine Zahl nach. Du
hakst nach, bis du die Ursache eines Befunds kennst, und entscheidest, welche drei Aussagen vor den Beirat kommen.

## Mission

Verschaff dir zuerst einen Überblick: Baue dein Dashboard im Circle Design mit dem Reiter „Überblick“ –
Kennzahl-Kacheln, der Bestand nach Segment, Land, Vertriebsweg und Anwendung, eine Filterleiste und der Absatz
2021 bis 2026 als Zeitreihe. Dann analysierst du im zweiten Reiter „Wachstum“, wo wir 2026 gegenüber 2025 wachsen
und wo wir verlieren: Nachfüll- gegen Projektgeschäft, Händler gegen direkt, die große Notfalllieferung, eine
Wachstumsampel. Zum Schluss schreibst du eine Management-Summary mit drei Kernaussagen. Sie ist die Grundlage für
die Finanzanalyse in Drill 2 und für deine Präsentation am Ende des Tages.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Vorführung von Etappe 1: Claude erkundet die Tabellen und schlägt Kennzahlen mit Definitionen vor; Plan-Modus; das Circle Design |
| Übung | 55 Min. | Etappen 2 bis 4, allein oder mit deinem Peer. Richtwert: 22 · 20 · 13 Minuten. Etappe 1 selbst stellen und die Rückfrage-Runde sind Zusatzaufgaben (unter „Für Schnelle“) |
| Auswertung | 10 Min. | Welche Definition, welche Ursache, welche Kernaussagen, welche Zahl habt ihr nachgerechnet? |

## Vorher kurz einstellen

Claude-App, Reiter **Code**, Modell **Sonnet**, Ordner **`tag1`**. Am besten eine neue Sitzung beginnen. Liegt
deine Notiz aus Drill 0 in `meine-ergebnisse/`, liest Claude sie in Etappe 2 mit.

Das Aussehen deines Dashboards gibt **Circle Design** vor, das Design-Framework von Falk Uebernickel für
Dashboards. Es liegt im Ordner `design/circle/`: Stilfibel `CIRCLE.md`, Farben und Schriften, Bausteine und ein
Gerüst. Öffne `design/circle/beispiel-dashboard.html` per Doppelklick: So wird dein Dashboard aussehen, nur mit
echten Zahlen. Die Reiter in Drill 2 und 3 kommen in dasselbe Dashboard und sehen genauso aus.

## Neu in Claude Code: Plan-Modus, eigene Skripte, Aufgabenliste

| | |
|---|---|
| **Funktion** | Im **Plan-Modus** plant Claude nur: Es liest, schlägt Vorgehen, Quellen, Definitionen und Dateien vor und ändert nichts, bis du den Plan freigibst. Danach schreibt Claude **eigene Auswertungsskripte** (unter `meine-ergebnisse/skripte/`), führt sie aus und führt bei längeren Aufgaben eine **Aufgabenliste**, die es abhakt. |
| **Was dahinter passiert** | Claude rechnet nicht „im Kopf“: Jede Zahl im Dashboard stammt aus einem Skript, das die Tabellen liest. Darum kannst du jederzeit fragen „Wie hast du gerechnet?“ und das Skript zeigen lassen. Der Plan ist dein Moment, falsche Annahmen abzufangen, bevor gebaut wird. |
| **Kleines Experiment** | Stell den Modus am Eingabefeld auf **Plan** (im Terminal: Umschalt+Tab), bevor du Etappe 2 schickst. Lies den Plan, ändere einen Punkt („Die Kunden-Kachel zählt nach meiner Notiz“) und gib ihn dann frei. |
| **Woran du es erkennst** | Im Plan-Modus kommt ein Plan statt einer Datei; nach der Freigabe siehst du die Aufgabenliste, die Befehle, mit denen Claude seine Skripte ausführt, und zum Schluss öffnet sich das Dashboard im Browser. |

## Dialog in vier Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Überblick** (Vorführung in der Einführung; selbst stellen ist eine Zusatzaufgabe) | „Ich leite die Unternehmensentwicklung und soll dem Beirat zeigen, wo wir wachsen und wo wir verlieren. Verschaff dir einen Überblick über alle Datentabellen mit Zeilenzahl und je einem Satz, wozu sie dient. Schlag mir dann fünf Kennzahlen für 2026 vor, je mit Wert und Definition, darunter Absatz und Nettoumsatz mit der Veränderung zum Vorjahr nach unseren verbindlichen Definitionen. Noch keine Webseite.“ | In der Vorführung mitprüfen: Stammen die Zahlen aus dem Übungsausschnitt (32 Kunden) und nicht aus dem Unternehmensprofil? Hat jede Kennzahl eine Definition? Sind Gutschriften, Retouren, Muster und doppelt importierte Positionen richtig behandelt, und ist die Fremdwährung umgerechnet? |
| **2 · Überblick im Dashboard** (zuerst im Plan-Modus) | „Ich leite die Unternehmensentwicklung. Liegt in meinen Ergebnissen eine Notiz von Lina Osterkamp zur Kundenzahl, lies sie zuerst und nimm ihre Empfehlung als Zählweise für die Kunden. Lege dann mein Dashboard an, im Circle Design aus dem Ordner design/circle: Lies zuerst die Stilfibel und nimm das Beispiel-Dashboard als Gerüst. Der erste Reiter heißt ‚Überblick‘: oben Kacheln für Kunden, Lieferstellen, Absatz 2026 in Litern und Nettoumsatz 2026 in EUR, Absatz und Umsatz mit der Veränderung zum Vorjahr, jede Kachel mit ihrer Definition nach unseren Kennzahlen; darunter unser Bestand nach Segment, Land, Vertriebsweg und Anwendung, je mit Kunden, Lieferstellen und Litern 2026; dazu der Absatz von 2021 bis 2026 als Zeitreihe, Januar und Februar 2027 sichtbar als Teiljahr abgesetzt. Eine Filterleiste für Segment, Land und Vertriebsweg soll auf alle Zahlen wirken. Öffne das Dashboard im Browser.“ | Zuerst den Plan lesen: Steht die Zählweise aus Linas Notiz drin, sind Absatz und Umsatz so definiert wie in unseren Kennzahlen (netto, ohne Muster, Fremdwährung zum Konzernkurs), rechnet Claude mit einem Skript, und bindet es Circle Design ein, ohne eigene Farben? Einen Punkt ändern oder freigeben. **Entscheiden:** Folgst du Linas Empfehlung? Dann im Browser: Sieht das Dashboard aus wie das Beispiel (Papierton, weiße Karten, ruhige Schrift)? Selbst klicken: Vertriebsweg auf „Händler“ stellen. Ändern sich Kacheln, Bestand und Zeitreihe? Siehst du Filter und alle Kacheln, ohne zu scrollen? Dann eine Verbesserung verlangen, die **du** willst, zum Beispiel: „Zeig in der Zeitreihe den Wert am letzten vollen Jahr als Zahl.“ |
| **3 · Wo wachsen wir, wo verlieren wir?** | „Vergleiche Absatz in Litern und Nettoumsatz 2026 mit 2025, insgesamt und getrennt nach Auftragsart (Nachfüllung, Erstbefüllung, Notfall) und nach Vertriebsweg. Nenne zuerst deine Definitionen. Zeig es mir als Tabelle mit beiden Jahren, der Veränderung und der Zahl der Positionen, noch nichts ins Dashboard.“ | Definition prüfen: Wie sind Gutschriften und Retouren der Auftragsart zugeordnet? Zählen Muster mit? **Nachhaken:** „Woher kommt der Rückgang der Liter? Vergleiche Nachfüllung und Erstbefüllung, und zeig mir die Erstbefüllungen 2025 und 2026 einzeln mit Kunde, Anlage und Litern.“ Dann: „Gibt es 2026 einzelne sehr große Lieferungen? Wie sehen Umsatz und Veränderung je Segment ohne sie aus?“ Halte in einem Satz fest, wo wir wachsen und wo wir verlieren. Erst wenn du den Zahlen traust, freigeben: „Übernimm das in einen zweiten Reiter ‚Wachstum‘ hinter dem Überblick: Absatz 2025 und 2026 nach Auftragsart und nach Vertriebsweg; Nachfüllung und Erstbefüllung 2021 bis 2026 als Zeitreihe in Litern; einen Hinweis zur großen Notfalllieferung mit den Werten mit und ohne sie; eine Kachel mit dem Anteil der fünf größten Kunden am Umsatz 2026; dazu eine Wachstumsampel je Segment und je Vertriebsweg nach unserer Regel, mit den Zustandsfarben aus Circle Design als Pille mit Form und Wort, die Regel sichtbar darüber. Die Filter sollen auch hier wirken. Der Reiter ‚Überblick‘ bleibt unverändert.“ | Erschrick nicht: Einige Gruppen haben weniger als 20 Positionen und bleiben in der Ampel eine Lücke, auch wenn dort viel passiert. Schau dir an, was die Ampel für das Segment Industrie sagt, und vergleiche mit deiner Rechnung ohne die Notfalllieferung: Hält die Farbe? Danach „Händler“ wählen: Ändern sich Kacheln und Zeitreihe, behält jede Linie ihre Farbe? Kannst du jede Zahl lesen? Funktioniert der Reiter „Überblick“ noch? |
| **4 · Drei Kernaussagen** | „Schreib mir eine Management-Summary für den Beirat mit genau drei Kernaussagen zur Frage ‚Wo wachsen wir, wo verlieren wir?‘. Jede Kernaussage als ganzer Satz, der sagt, worauf der Beirat achten oder reagieren sollte, belegt mit einer Zahl samt Definition und Quelle in Worten. Hänge den Absatz 2025 und 2026 nach Auftragsart und Vertriebsweg als kleine Tabelle an. Leg sie in meinen Ergebnissen ab und zeig sie mir hier.“ | Eine Zahl nachrechnen lassen: „Rechne mir den Absatz 2026 im Nachfüllgeschäft vor: welche Positionen zählen, welche nicht, Gutschriften und Retouren je mit Menge.“ Dann **entscheiden**: Welche Aussage würdest du vor dem Beirat vertreten, welche nicht? Mindestens eine Kernaussage selbst umformulieren oder ersetzen lassen, zum Beispiel: „Ersetze die schwächste Aussage durch eine zur Notfalllieferung: Was bedeutet sie für den Vergleich mit 2025?“ Danach prüfen lassen: „Belegt jede Zahl genau das, was ihr Satz behauptet, und zeigen die drei Aussagen drei verschiedene Dinge? Sag mir zuerst je Aussage, was hält und was nicht, dann korrigiere.“ |

## Fertig, wenn

- dein Dashboard im Circle Design im Browser öffnet, mit zwei Reitern: „Überblick“ mit Kacheln, Bestand,
  Filterleiste und Zeitreihe, „Wachstum“ mit Auftragsarten, Vertriebswegen, Notfall-Hinweis und Wachstumsampel,
- der Filter „Händler“ Kacheln **und** Zeitreihen verändert,
- du in eigenen Worten erklären kannst, wo wir 2026 wachsen, wo wir verlieren und welche Rolle die Notfalllieferung
  spielt,
- du eine Zahl selbst nachgerechnet oder dir hast vorrechnen lassen,
- die Management-Summary mit drei Kernaussagen in deinen Ergebnissen liegt und mindestens eine Aussage deine
  eigene Entscheidung trägt.

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

1. **Das Dashboard öffnet nicht, zeigt keine Diagramme oder sieht nicht aus wie das Beispiel?** Frag: „Öffne mein
   Dashboard im Browser.“ Bleiben die Diagramme leer: „Zeichne die Diagramme ohne externe Bibliotheken, damit das
   Dashboard auch ohne Internet läuft.“ Sieht es anders aus als `design/circle/beispiel-dashboard.html`: „Binde
   circle.css und komponenten.css aus design/circle relativ ein und nimm nur deren Bausteine und Farben.“
2. **Die Filter wirken nicht, oder Veränderungen springen seltsam?** Frag: „Die Filter sollen alle Zahlen neu
   berechnen: Werte je Jahr erst zusammenzählen und dann vergleichen, nicht Prozentwerte mitteln.“
3. **Deine Zahlen weichen von denen deines Peers ab, oder der Reiter ist kaputt?** Frag: „Zeig mir deine Definition
   und rechne mir 2026 vor.“ Unterschiede kommen fast immer aus Gutschriften, Mustern, Doppelimporten, Gebinden ohne
   Literangabe oder der Währung. Ist ein Reiter kaputt: „Baue den Reiter ‚Wachstum‘ neu, lass den Überblick
   unverändert.“

## Für Schnelle

**Zusatzaufgabe zuerst: die Rückfrage-Runde.** Stell Claude zwei oder drei Fragen, die der Beirat zu deiner
Summary stellen würde, zum Beispiel: „Der Vorsitzende fragt, ob wir Kunden verlieren. Was sagen die Daten, nach
unserer Definition aktiv, ruhend und verloren?“ Prüfe, ob jede Antwort mit einer Zahl aus unseren Tabellen belegt
ist. Die Antworten bleiben im Chat; die Summary änderst du nur, wenn eine Aussage dadurch nicht mehr hält.

Danach, wenn noch Zeit bleibt, **eines** von diesen:

- **Etappe 1 selbst stellen:** Schick den Prompt aus Etappe 1 und vergleiche die vorgeschlagenen Kennzahlen mit
  deinen Kacheln.
- **Vertiefen:** „Wie abhängig sind wir von unseren größten Kunden? Zeig mir den Anteil der fünf größten Kunden am
  Nettoumsatz 2025 und 2026, einmal mit und einmal ohne die Notfalllieferung.“
- **Vorausbauen (Drill 2):** „Wo verdienen wir mehr, im Händlergeschäft oder direkt? Lies dazu nur die Definition
  des Deckungsbeitrags und sag mir, welche Tabellen du dafür brauchst. Noch nichts rechnen.“

## Drei Arbeitsweisen

| Weg | Wenn du … | So bittest du Claude |
|---|---|---|
| Geführt | lieber Schritt für Schritt vorgehst | „Erkläre mir jeden Schritt, bevor du ihn machst, und warte auf mein Okay.“ |
| Bauend | die Etappen zügig schaffst | Eigene Kacheln, Diagramme und Fragen verlangen; jede Zahl mit Definition und Quelle. |
| Vorausbauend | vor der Zeit fertig bist | Eine Aufgabe aus „Für Schnelle“; das Ergebnis ist ein Vorsprung, kein Muss. |

## Checkpoint

Kommst du später dazu oder fehlt dir die Notiz aus Drill 0? Sag „Ich möchte mit Drill 1 weitermachen“. Claude
bietet dir dann einen Zwischenstand mit einer Notiz zur Kundenzahl an.

> **Das brauchst du in Drill 2:** dein Dashboard mit „Überblick“ und „Wachstum“ und deine Summary. Der Reiter
> „Finanzen“ kommt in dasselbe Dashboard, im selben Circle Design. Die fehlenden Liter aus dem Projektgeschäft
> erklären dort den Mengeneffekt gegen das Budget, und die große Notfalllieferung, die du in Etappe 3 gefunden
> hast, spielt im Deckungsbeitrag eine Hauptrolle.

Alle Personen, Firmen und Zahlen bei Dr. Sthamer sind erfunden. Verwende keine echten Kundendaten.
