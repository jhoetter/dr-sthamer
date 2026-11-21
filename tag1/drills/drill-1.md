# Drill 1 · Das Überblicks-Dashboard

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 75 Minuten: 10 Einführung · 55 Übung · 10 Auswertung.

> **Du startest mit** der Notiz zur Kundenzahl aus Drill 0 (`meine-ergebnisse/notiz-kundenzahl.md`). Die Zählweise,
> die du dort empfohlen hast, wird die Definition der Kunden-Kachel. Fehlt die Notiz, legst du die Zählweise in
> Etappe 1 selbst fest.

## Deine Rolle

Du bist Dr. Henrike Vossberg, Programmleiterin Fluorfrei-Umstellung bei Dr. Sthamer. Die Geschäftsführerin hat
dir aufgetragen, dem Beirat am 09.03.2027 zu zeigen, wo das Umstellungsprogramm FreeFoam nach einem Jahr steht.
Ihre Frage für den Beirat zieht sich durch den ganzen Tag: „Wo steht die Umstellung, rechnet sie sich, und was
entscheiden wir?“ Heute legst du den ersten Teil: Wie weit sind wir mit den fluorfreien Produkten, gemessen am
Ziel von 60 % für 2026, und wo hängen wir?

## Lernziel

Du lässt Claude eine unübersichtliche Datenlage erkunden und daraus ein Dashboard im Circle Design bauen, das du
im Browser bedienst: erst den Überblick, dann die Analyse. Du lenkst Auswertungen in Geschäftssprache („nur stationäre Anlagen“, „getrennt nach Segment“),
verlangst zu jeder Zahl die Definition und rechnest mindestens eine Zahl nach. Du hakst nach, bis du die Ursache
eines Befunds kennst, und entscheidest, welche drei Aussagen vor den Beirat kommen.

## Mission

Verschaff dir zuerst einen Überblick: Baue dein Dashboard im Circle Design mit dem Reiter „Überblick“ –
Kennzahl-Kacheln, der Bestand nach Segment, Land, Vertriebsweg und Anwendung, eine Filterleiste und Absatz und
Fluorfrei-Anteil 2021 bis 2026 als Zeitreihe. Dann analysierst du im zweiten Reiter „Umstellung“, woran der
Rückstand liegt: Fluorfrei-Anteil nach Anwendung und Segment, die große Einzellieferung, eine Ampel je Segment
und Land. Zum Schluss schreibst du eine Management-Summary mit drei Kernaussagen. Sie ist die Grundlage für die
Finanzanalyse in Drill 2 und für deine Präsentation am Ende des Tages.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Vorführung: vom Plan zum Dashboard im Browser, im Circle Design; erst Überblick, dann Analyse; was eine Definition ist und warum „fluorfrei“ mehrdeutig ist |
| Übung | 55 Min. | Etappen 1 bis 4, allein oder mit deinem Peer. Richtwert: 10 · 17 · 16 · 12 Minuten. Die Rückfrage-Runde ist eine Zusatzaufgabe (unter „Für Schnelle“) |
| Auswertung | 10 Min. | Welche Definition, welche Ursache, welche Kernaussagen, welche Zahl habt ihr nachgerechnet? |

## Vorher kurz einstellen

Claude-App, Reiter **Code**, Modell **Sonnet**, Ordner **`tag1`**. Am besten eine neue Sitzung beginnen. Liegt
deine Notiz aus Drill 0 in `meine-ergebnisse/`, liest Claude sie in Etappe 1 mit.

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
| **1 · Überblick** | „Ich bin Programmleiterin Fluorfrei-Umstellung und soll dem Beirat zeigen, wo das Programm FreeFoam steht. Liegt in meinen Ergebnissen eine Notiz von Lina Osterkamp zur Kundenzahl, lies sie zuerst und sag mir in einem Satz, welche Zählweise sie empfiehlt und warum. Verschaff dir einen Überblick über alle Datentabellen mit Zeilenzahl und je einem Satz, wozu sie dient. Schlag mir dann fünf Kennzahlen zur Umstellung am Stichtag vor, je mit Wert und Definition, darunter den Fluorfrei-Anteil 2026 nach unserer verbindlichen Definition. Noch keine Webseite.“ | Prüfen: Stammen die Zahlen aus dem Übungsausschnitt (32 Kunden) und nicht aus dem Unternehmensprofil? Hat jede Kennzahl eine Definition? Zählt „fluorfrei“ nach der Produktlinie, nicht nach der Deklaration, und sind Gutschriften, Retouren, Muster und doppelt importierte Positionen richtig behandelt? Dann **entscheiden**, ob du Linas Empfehlung folgst, und Claude sagen, wie gezählt wird, zum Beispiel: „Fürs Dashboard gilt: Kunden zählen nach Linas Empfehlung. Umsatz heißt Nettoumsatz in EUR, Fremdwährung zum Konzernkurs des Jahres.“ |
| **2 · Überblick im Dashboard** (zuerst im Plan-Modus) | „Lege mein Dashboard an, im Circle Design aus dem Ordner design/circle: Lies zuerst die Stilfibel und nimm das Beispiel-Dashboard als Gerüst. Der erste Reiter heißt ‚Überblick‘: oben Kacheln mit den Kennzahlen, die wir eben festgelegt haben – Kunden, Lieferstellen, Absatz 2026 in Litern, Nettoumsatz 2026 in EUR und Fluorfrei-Anteil 2026 gegen das Ziel –, jede mit ihrer Definition; darunter unser Bestand nach Segment, Land, Vertriebsweg und Anwendung, je mit Kunden, Lieferstellen und Litern 2026; dazu Absatz und Fluorfrei-Anteil insgesamt von 2021 bis 2026 als Zeitreihe, Januar und Februar 2027 sichtbar als Teiljahr abgesetzt. Eine Filterleiste für Segment, Land und Vertriebsweg soll auf alle Zahlen wirken. Öffne das Dashboard im Browser.“ | Zuerst den Plan lesen: Stehen die Definitionen aus Etappe 1 drin, rechnet Claude mit einem Skript, und bindet es Circle Design ein, ohne eigene Farben? Einen Punkt ändern oder freigeben. Dann im Browser: Sieht das Dashboard aus wie das Beispiel (Papierton, weiße Karten, ruhige Schrift)? Selbst klicken: Segment auf „Industrie“ stellen. Ändern sich Kacheln, Bestand und Zeitreihe? Eine Kachel mit Etappe 1 vergleichen. Siehst du Filter und alle Kacheln, ohne zu scrollen? Dann eine Verbesserung verlangen, die **du** willst, zum Beispiel: „Zeig neben dem Fluorfrei-Anteil den Abstand zum Ziel in Prozentpunkten.“ |
| **3 · Wo hängen wir?** | „Berechne den Fluorfrei-Anteil für jedes Jahr von 2021 bis 2026 und für Januar bis Februar 2027 getrennt, insgesamt, nach Segment und nach Anwendung (zum Beispiel stationäre Anlage, Feuerwehrfahrzeug, Lager, Übung). Nenne zuerst deine Definition. Zeig es mir als Tabelle mit Zähler und Nenner, noch nichts ins Dashboard.“ | Definition prüfen: Was steht im Zähler, was im Nenner? Ist das Teiljahr 2027 abgesetzt? Sind Gruppen mit weniger als 20 Positionen eine Lücke statt einer Zahl? **Nachhaken:** „Liegt der Rückstand am Segment Industrie oder an den stationären Anlagen? Vergleiche in der Industrie die stationären Anlagen mit allen anderen Anwendungen, dazu die stationären Anlagen außerhalb der Industrie und alle stationären Anlagen zusammen, je mit der Zahl der Positionen.“ Ist eine Teilgruppe zu klein und damit eine Lücke, welche größere Gruppe trägt die Aussage trotzdem? Dann: „Gibt es 2026 einzelne sehr große Lieferungen, die eine Gruppe verzerren? Wie sieht der Anteil ohne sie aus?“ und „Wie viele unserer stationären Anlagen haben schon eine Datenaufnahme vor Ort?“ Halte in einem Satz fest, woran es liegt. Erst wenn du den Zahlen traust, freigeben: „Übernimm das in einen zweiten Reiter ‚Umstellung‘ hinter dem Überblick: den Fluorfrei-Anteil als Liniendiagramm mit Prozentachse, je einer Linie für das Gesamt und für die Anwendungen, dem Ziel 60 % als waagrechte Linie und dem Teiljahr 2027 sichtbar abgesetzt; einen Hinweis zur großen Einzellieferung mit dem Anteil mit und ohne sie; dazu eine Ampel je Segment und Land für 2026 nach unserer Ampelregel, mit den Zustandsfarben aus Circle Design als Pille mit Form und Wort, die Regel sichtbar darüber. Die Filter sollen auch hier wirken. Der Reiter ‚Überblick‘ bleibt unverändert.“ Erschrick nicht: Für 2026 sind die meisten Kombinationen aus Segment und Land kleiner als 20 Positionen und bleiben Lücken; nur wenige Zellen bekommen eine Farbe. Danach „Industrie“ wählen: Ändern sich Linie und Ampel, behält jede Linie ihre Farbe? Kannst du jede Zahl lesen? Funktioniert der Reiter „Überblick“ noch? |
| **4 · Drei Kernaussagen** | „Schreib mir eine Management-Summary für den Beirat mit genau drei Kernaussagen zur Umstellung. Jede Kernaussage als ganzer Satz, der sagt, worauf der Beirat achten oder reagieren sollte, belegt mit einer Zahl samt Definition und Quelle in Worten. Hänge den Fluorfrei-Anteil 2021 bis 2026 insgesamt und für die stationären Anlagen als kleine Tabelle mit Zähler und Nenner an. Leg sie in meinen Ergebnissen ab und zeig sie mir hier.“ | Eine Zahl nachrechnen lassen: „Rechne mir den Fluorfrei-Anteil 2026 der stationären Anlagen vor: welche Liter im Zähler, welche im Nenner, was nicht mitzählt, je mit Menge.“ Dann **entscheiden**: Welche Aussage würdest du vor dem Beirat vertreten, welche nicht? Mindestens eine Kernaussage selbst umformulieren oder ersetzen lassen, zum Beispiel: „Ersetze die schwächste Aussage durch eine zur Datenaufnahme der stationären Anlagen.“ Danach prüfen lassen: „Belegt jede Zahl genau das, was ihr Satz behauptet, und zeigen die drei Aussagen drei verschiedene Dinge? Sag mir zuerst je Aussage, was hält und was nicht, dann korrigiere.“ |

## Fertig, wenn

- dein Dashboard im Circle Design im Browser öffnet, mit zwei Reitern: „Überblick“ mit Kacheln, Bestand,
  Filterleiste und Zeitreihe, „Umstellung“ mit Fluorfrei-Anteil nach Anwendung, Ziellinie und Ampel,
- der Filter „Industrie“ Kacheln **und** Zeitreihen verändert,
- du die Definition des Fluorfrei-Anteils in eigenen Worten erklären kannst und weißt, woran der Rückstand liegt,
- du eine Zahl selbst nachgerechnet oder dir hast vorrechnen lassen, mit Zähler und Nenner,
- die Management-Summary mit drei Kernaussagen in deinen Ergebnissen liegt und mindestens eine Aussage deine
  eigene Entscheidung trägt.

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

1. **Das Dashboard öffnet nicht, zeigt keine Diagramme oder sieht nicht aus wie das Beispiel?** Frag: „Öffne mein
   Dashboard im Browser.“ Bleiben die Diagramme leer: „Zeichne die Diagramme ohne externe Bibliotheken, damit das
   Dashboard auch ohne Internet läuft.“ Sieht es anders aus als `design/circle/beispiel-dashboard.html`: „Binde
   circle.css und komponenten.css aus design/circle relativ ein und nimm nur deren Bausteine und Farben.“
2. **Die Filter wirken nicht auf den Fluorfrei-Anteil, oder der Anteil springt seltsam?** Frag: „Die Filter sollen
   den Anteil neu berechnen: fluorfreie Liter und alle Liter getrennt zusammenzählen und erst dann teilen, nicht
   Anteile mitteln.“
3. **Deine Zahlen weichen von denen deines Peers ab, oder der Reiter ist kaputt?** Frag: „Zeig mir deine Definition
   und rechne mir 2026 vor.“ Unterschiede kommen fast immer aus Gutschriften, Mustern, Doppelimporten, Gebinden ohne
   Literangabe oder der Währung. Ist ein Reiter kaputt: „Baue den Reiter ‚Umstellung‘ neu, lass den Überblick
   unverändert.“

## Für Schnelle

**Zusatzaufgabe zuerst: die Rückfrage-Runde.** Stell Claude zwei oder drei Fragen, die der Beirat zu deiner
Summary stellen würde, zum Beispiel: „Der Vorsitzende fragt, ob wir mit der Umstellung Kunden verlieren. Was
sagen die Daten, nach meiner Zählweise der Kunden?“ Prüfe, ob jede Antwort mit einer Zahl aus unseren Tabellen
belegt ist. Die Antworten bleiben im Chat; die Summary änderst du nur, wenn eine Aussage dadurch nicht mehr hält.

Danach, wenn noch Zeit bleibt, **eines** von diesen:

- **Vertiefen:** „Welche Lieferstellen haben schon ein fluorfreies Produkt bekommen und danach wieder ein
  fluorhaltiges? Zeig sie mir mit Datum, ohne Wertung.“
- **Vorausbauen (Drill 2):** „Was verdienen wir an einem Liter fluorfrei im Vergleich zu fluorhaltig? Lies dazu nur
  die Definition des Deckungsbeitrags und sag mir, welche Tabellen du dafür brauchst. Noch nichts rechnen.“

## Drei Arbeitsweisen

| Weg | Wenn du … | So bittest du Claude |
|---|---|---|
| Geführt | lieber Schritt für Schritt vorgehst | „Erkläre mir jeden Schritt, bevor du ihn machst, und warte auf mein Okay.“ |
| Bauend | die Etappen zügig schaffst | Eigene Kacheln, Diagramme und Fragen verlangen; jede Zahl mit Definition und Quelle. |
| Vorausbauend | vor der Zeit fertig bist | Eine Aufgabe aus „Für Schnelle“; das Ergebnis ist ein Vorsprung, kein Muss. |

## Checkpoint

Kommst du später dazu oder fehlt dir die Notiz aus Drill 0? Sag „Ich möchte mit Drill 1 weitermachen“. Claude
bietet dir dann einen Zwischenstand mit einer Notiz zur Kundenzahl an.

> **Das brauchst du in Drill 2:** dein Dashboard mit „Überblick“ und „Umstellung“ und deine Summary. Der Reiter
> „Finanzen“ kommt in dasselbe Dashboard, im selben Circle Design. Die Liter und der Fluorfrei-Anteil erklären dort Menge und Mix gegen das Budget, und die große
> Einzellieferung, die du in Etappe 3 gefunden hast, spielt im Deckungsbeitrag eine Hauptrolle.

Alle Personen, Firmen und Zahlen bei Dr. Sthamer sind erfunden. Verwende keine echten Kundendaten.
