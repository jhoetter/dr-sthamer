# Drill 2 · Finanzanalyse: Rechnet sich die Umstellung?

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 60 Minuten: 10 Einführung · 40 Übung · 10 Auswertung.

> **Du startest mit** deinem Dashboard (`meine-ergebnisse/dashboard.html`, Reiter „Überblick“ und „Umstellung“)
> und deiner Management-Summary aus Drill 1. Beide liest Claude in Etappe 1 mit.

## Deine Rolle

Du bist Jasper Dierksmeyer, Leiter Controlling von Dr. Sthamer, Werk Nord. Dr. Henrike Vossberg hat dir ihr Dashboard und ihre Summary geschickt:
„Wo die Umstellung steht, wissen wir jetzt. Der Beirat fragt aber auch, ob sie sich rechnet, und unser externes
Mitglied wird nach dem Budget fragen.“ Die Geschäftsführerin will von dir eine Seite: Was verdienen wir an den
fluorfreien Nachfolgern im Vergleich zu den alten Produkten, wie lief 2026 gegen das Budget, und welche Rolle
spielen Währungen und die Preiserhöhung 2026?

## Lernziel

Du lässt Claude Deckungsbeitrag, Marge und eine Plan-Ist-Brücke nach verbindlichen Definitionen rechnen und
verlangst zu jedem Effekt die Methode. Du prüfst ein Ergebnis auf einem zweiten, unabhängigen Weg, siehst dir
Änderungen am Dashboard als Vorher-nachher an und machst eine Änderung wieder rückgängig. Du entscheidest, welche
drei Aussagen die Geschäftsführerin bekommt.

## Mission

Ergänze dein Dashboard um den Reiter „Finanzen“, im selben Circle Design wie die anderen Reiter: Kacheln zu Nettoumsatz, Deckungsbeitrag und Marge 2026, die
Brücke vom Budget zum Ist als Wasserfall, die Marge je Produktlinie und den Vergleich von Listenpreis und
realisiertem Preis je Vertriebsweg. Schreibe dazu einen Finanzkommentar von einer Seite für die Geschäftsführerin.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Was ein Deckungsbeitrag ist und wie eine Plan-Ist-Brücke liest; Vorführung: ein Subagent rechnet nach |
| Übung | 40 Min. | Etappen 1 bis 4, allein oder mit deinem Peer. Richtwert: 10 · 12 · 10 · 8 Minuten. Die Rückfrage-Runde ist eine Zusatzaufgabe |
| Auswertung | 10 Min. | Liegt der Deckungsbeitrag über Plan, und warum? Welche Methode hat eure Brücke, und hat der zweite Weg dasselbe ergeben? |

## Vorher kurz einstellen

Claude-App, Reiter **Code**, Modell **Sonnet**, Ordner **`tag1`**. Neue Sitzung beginnen. Fehlen dir Dashboard
oder Summary aus Drill 1, lade zuerst den Zwischenstand (unten unter „Checkpoint“). Den **Plan-Modus** kennst du
aus Drill 1: Nutze ihn für Etappe 1 und 2, bevor Claude rechnet.

## Neu in Claude Code: zweiter Weg, Vorher-nachher, Zurückspulen

| | |
|---|---|
| **Funktion** | Ein **Subagent** ist eine zweite Claude-Instanz mit frischem Kontext. Sie bekommt nur die Frage und die Definition, nicht Claudes bisheriges Ergebnis, und rechnet unabhängig nach. Jede Änderung an einer Datei siehst du als **Diff** (grün neu, rot entfernt). Mit **Zurückspulen** (Befehl `/rewind` oder zweimal Esc) setzt du Gespräch und Dateien auf einen früheren Stand zurück. |
| **Was dahinter passiert** | Wer sein eigenes Ergebnis prüft, findet seine eigenen Fehler selten. Der Subagent kennt Claudes Rechenweg nicht und muss die Tabellen selbst lesen; stimmen beide Wege überein, ist das ein echter Beleg. Claude merkt sich vor jeder Dateiänderung einen Stand, zu dem du zurückkehren kannst. |
| **Kleines Experiment** | Bitte Claude: „Zeig im Reiter ‚Finanzen‘ alle Beträge in Tausend EUR statt in EUR.“ Sieh dir die Änderung als Diff an. Dann `/rewind` und den Stand vor dieser Bitte wählen. |
| **Woran du es erkennst** | Claude meldet, dass es eine Aufgabe an einen Subagenten gibt, und berichtet danach dessen Ergebnis getrennt. Nach dem Zurückspulen stehen die Beträge wieder in vollen Euro. |

## Dialog in vier Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Was verdienen wir?** (zuerst im Plan-Modus) | „Ich leite das Controlling. Lies zuerst die Management-Summary von Dr. Vossberg in meinen Ergebnissen und dann unsere verbindlichen Definitionen für Deckungsbeitrag, Fremdwährung, Rabattquote und Plan-Ist-Brücke. Berechne Nettoumsatz, Herstellkosten, Fracht, Deckungsbeitrag und DB-Marge für 2025 und 2026, je Produktlinie fluorhaltig und fluorfrei. Sag mir vorher in drei Sätzen, wie du Gutschriften, Retouren, Muster, doppelt importierte Positionen und die Fracht behandelst. Zeig mir das Ergebnis als Tabelle, noch nichts ins Dashboard.“ | Im Plan prüfen: Steht die Fracht als eigene Zeile, nicht in den Herstellkosten? Haben Muster Kosten, aber keinen Umsatz? Mindern Gutschriften die Herstellkosten (sie sollten es nicht)? Dann die Tabelle lesen: Sind die Margen aus Summen gerechnet, nicht gemittelt? **Nachhaken:** „Wie sieht die Marge fluorhaltig 2026 ohne den Notfallservice aus? Das ist die große Einzellieferung aus dem Dashboard.“ **Entscheiden:** Zeigst du der Geschäftsführerin die Marge mit oder ohne Notfallservice, und wie kennzeichnest du das? |
| **2 · Plan gegen Ist** | „Wie lief 2026 gegen das Budget? Baue eine Brücke vom Budget zum Ist, einmal für den Nettoumsatz und einmal für den Deckungsbeitrag, mit den Effekten Menge, Mix, Preis, beim Deckungsbeitrag zusätzlich Kosten, dazu Fremdwährung und den Notfallservice als eigenen Balken, genau nach unserer Definition. Nenne die Methode in einem Satz: Reihenfolge der Effekte und womit jeder bewertet ist. Zeig mir den Abgleich, dass die Summe der Effekte die Gesamtabweichung genau ergibt.“ | Geht die Brücke auf, auf den Euro? Ist der Fremdwährungseffekt aus Ist-Monatskurs und Plankurs gerechnet? Dann den **zweiten Weg** verlangen: „Lass einen Subagenten unabhängig nachrechnen, nur mit der Definition aus unseren Kennzahlen und den Tabellen, ohne dein Ergebnis zu kennen: Budget-Deckungsbeitrag 2026, Ist-Deckungsbeitrag 2026 und Notfallservice. Vergleiche dann beide Wege Zeile für Zeile.“ Stimmen beide überein? **Nachhaken:** „Liegt der Deckungsbeitrag nur wegen des Notfallservice über Plan? Und warum ist der Mix-Effekt im Umsatz negativ, im Deckungsbeitrag aber positiv?“ Mit den Litern und dem Fluorfrei-Anteil aus deinem Dashboard erklären lassen. Nicht wundern: Der Ist-Umsatz der Brücke (Monatskurse) weicht um wenige Euro vom Umsatz im Dashboard (Konzernkurs) ab; Claude soll beide Kurse benennen. |
| **3 · Preise, Währung und Reiter** | „Wie viel von der Preiserhöhung 2026 ist bei den Kunden angekommen? Vergleiche die Rabattquote 2025 und 2026 nach unserer Definition, getrennt nach Vertriebsweg. Übernimm danach alles in einen neuen Reiter ‚Finanzen‘ in meinem Dashboard, im Circle Design wie die anderen Reiter: Kacheln mit Nettoumsatz, Deckungsbeitrag und Marge 2026 und der Abweichung zum Budget, je als Ist oder Budget bezeichnet; die Deckungsbeitrags-Brücke als Wasserfall mit der Methode in einem Satz darunter und dem Abgleich; die Marge je Produktlinie; Listenpreis gegen realisierten Preis je Vertriebsweg. Die Reiter ‚Überblick‘ und ‚Umstellung‘ bleiben unverändert. Öffne das Dashboard.“ | Prüfen: Nennt jede Kachel Ist oder Budget und den Kurs? Ist der Notfallservice ein eigener Balken? Steht unter dem Wasserfall, welche Methode gilt? Wo bleibt die Preiserhöhung hängen, bei welchem Vertriebsweg? Dann das **Experiment** aus dem Kasten oben: eine Änderung als Diff ansehen und mit `/rewind` zurückspulen. Klick zum Schluss auf „Überblick“ und „Umstellung“: Funktionieren beide noch? |
| **4 · Finanzkommentar** | „Schreib mir einen Finanzkommentar von einer Seite für die Geschäftsführerin: drei Kernaussagen, je ein ganzer Satz mit Folgerung und Beleg-Zahl samt Definition; dann die Deckungsbeitrags-Brücke als kleine Tabelle mit Methode und Abgleich; dann die Einschränkungen (Übungsausschnitt, Kurse, Ausreißer, Teiljahr). Keine Ursachen, die keine Tabelle belegt. Leg ihn in meinen Ergebnissen ab und zeig ihn mir hier.“ | **Entscheiden:** Welche drei Aussagen soll die Geschäftsführerin lesen? Mindestens eine selbst umformulieren, zum Beispiel: „Die erste Aussage soll sagen, was der Notfallservice für den Vergleich mit dem Budget bedeutet.“ Dann prüfen lassen: „Belegt jede Zahl genau ihren Satz, und steht bei jeder Zahl Ist oder Budget und der Kurs? Sag mir zuerst je Aussage, was hält und was nicht, dann korrigiere.“ |

## Fertig, wenn

- der Reiter „Finanzen“ im Browser öffnet, mit Kacheln, Wasserfall samt Methode und Abgleich, Marge je Produktlinie
  und Preisvergleich, und die Reiter „Überblick“ und „Umstellung“ weiter funktionieren,
- du die Brücke in eigenen Worten erklären kannst: welcher Effekt wie groß ist und welche Rolle der Notfallservice
  spielt,
- ein Subagent den Deckungsbeitrag unabhängig nachgerechnet hat und du weißt, ob beide Wege übereinstimmen,
- du eine Änderung als Diff gesehen und einmal zurückgespult hast,
- der Finanzkommentar in deinen Ergebnissen liegt und mindestens eine Aussage deine Entscheidung trägt.

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

1. **Die Margen wirken zu hoch, oder fluorhaltig und fluorfrei liegen kaum auseinander?** Frag: „Ist die Fracht
   abgezogen, nach Litern auf die Positionen verteilt? Haben Muster ihre Herstellkosten? Zeig mir die Rechnung für
   fluorfrei 2026 Zeile für Zeile.“
2. **Die Brücke geht nicht auf?** Frag: „Rechne Mengen-, Mix-, Preis-, Kosten- und Fremdwährungseffekt genau nach
   der Definition in unseren Kennzahlen, in dieser Reihenfolge, den Notfallservice getrennt. Zeig mir die Differenz
   zwischen Summe der Effekte und Gesamtabweichung.“
3. **Subagent und Claude kommen auf verschiedene Zahlen?** Gut, dass du es gemerkt hast. Frag: „Wo genau weichen
   die beiden Wege ab? Vergleiche Nettoumsatz, Herstellkosten und Fracht getrennt und sag mir, welche Definition
   der Unterschied verletzt.“ Ist der Reiter kaputt: „Baue den Reiter ‚Finanzen‘ neu, lass die anderen Reiter unverändert.“

## Für Schnelle

**Zusatzaufgabe zuerst: die Rückfrage-Runde.** Unser externes Beiratsmitglied war Finanzchef in der Chemie. Frag
Claude: „Welche drei Fragen würde ein früherer Finanzchef zu meinem Kommentar stellen, um zu prüfen, ob die Marge
schöngerechnet ist? Beantworte jede mit einer Zahl aus unseren Tabellen.“ Den Kommentar änderst du nur, wenn eine
Aussage dadurch nicht mehr hält.

Danach, wenn noch Zeit bleibt, **eines** von diesen:

- **Breiter:** „Zeig mir die DB-Marge 2025 und 2026 zusätzlich je Segment und den Fremdwährungseffekt 2026 je
  Währung. Gruppen mit weniger als 20 Positionen als Lücke.“

- **Vertiefen:** „Welche fünf Kunden haben 2026 den größten Deckungsbeitrag gebracht, und wie hoch ist ihr
  Fluorfrei-Anteil? Zeig es ohne Wertung.“
- **Vorausbauen (Drill 3):** „Im Angebotseingang liegt eine Ausschreibung mit einem Rabatt auf ein fluorfreies
  Produkt. Was sagt die Angebotsrichtlinie dazu, ab welchem Auftragswert der Deckungsbeitrag geprüft werden muss?
  Nur der Paragraf, noch keine Bewertung.“

## Drei Arbeitsweisen

| Weg | Wenn du … | So bittest du Claude |
|---|---|---|
| Geführt | lieber Schritt für Schritt vorgehst | „Erkläre mir jeden Effekt der Brücke, bevor du ihn rechnest, und warte auf mein Okay.“ |
| Bauend | die Etappen zügig schaffst | Eigene Sichten im Reiter verlangen, etwa die Marge je Kunde; jede Zahl mit Ist, Budget oder Ziel. |
| Vorausbauend | vor der Zeit fertig bist | Eine Aufgabe aus „Für Schnelle“; das Ergebnis ist ein Vorsprung, kein Muss. |

## Checkpoint

Fehlen dir Dashboard oder Summary aus Drill 1? Sag „Ich möchte mit Drill 2 weitermachen“. Claude lädt dann den
Zwischenstand mit den Ergebnissen von Drill 0 und 1 und sagt dir, welche Reiter und Dateien jetzt da sind.

> **Das brauchst du in Drill 3:** die DB-Marge der fluorfreien Produkte aus deinem Finanzkommentar. In der
> Angebotsprüfung fragst du damit, ob ein Rabatt auf ein fluorfreies Produkt die Marge noch trägt. Der Reiter
> „Angebote“ kommt in dasselbe Dashboard.

Alle Personen, Firmen und Zahlen bei Dr. Sthamer sind erfunden. Verwende keine echten Kundendaten.
