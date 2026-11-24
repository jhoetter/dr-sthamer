# Einstieg für Teilnehmende – Tag 1 „AI Augmentation“

Willkommen bei Dr. Sthamer, einer Übungsfirma, an der du heute das Arbeiten mit KI-Unterstützung übst. Alles hier ist erfunden: Personen, Kunden, Produkte, Aufträge, Zahlen. Du kannst nichts kaputt machen.

## In der Claude-App (so arbeiten wir im Kurs)

Du arbeitest nur in der Claude-App, im Reiter „Code“. Ein Terminal brauchst du nicht, ein GitHub-Konto auch nicht.

1. **App einstellen:** Claude-App öffnen, Reiter „Code“, Modell Sonnet.
2. **Arbeitsstand holen:** im Reiter „Code“ eine neue Sitzung in deinem Benutzerordner beginnen (Windows: `C:\Users\<dein Name>`, nicht OneDrive, nicht Desktop) und schreiben: „Klone https://github.com/jhoetter/dr-sthamer in den Ordner dr-sthamer in meinem Benutzerordner und öffne den Ordner tag1.“ Claude holt das Repository mit Git; Vertrauensfrage und Erlaubnis für den Git-Befehl bestätigen. Ein Repository ist ein Projektordner mit allen Dateien, GitHub die Website, auf der er liegt; Git bedient Claude für dich.
3. **Ordner öffnen:** neue Sitzung im Reiter „Code“ und genau den Ordner `tag1` wählen, nicht `dr-sthamer` darüber. Fragt die App, ob du dem Ordner vertraust: Ja.
4. **Claude kennt den Ordner:** Claude liest die Datei `CLAUDE.md` und weiß damit, wo welche Unterlage liegt. Braucht Claude für eine Auswertung Python, prüft es selbst, was auf deinem Rechner da ist; du installierst nichts.
5. **Erste Frage stellen**, zum Beispiel: „Erkläre mir in fünf Sätzen, was in diesem Ordner steckt.“
6. **Mit einem Drill beginnen:** „Ich möchte mit Drill 0 weitermachen.“ Claude zeigt dir Rolle, Ziel und den ersten Schritt.

## Die Geschichte in einem Absatz

Dr. Sthamer stellt Schaumlöschmittel für Feuerwehren, Industrie, Häfen und Schiffe her. Das Geschäft hat drei Teile: das laufende Nachfüllgeschäft, einmalige Erstbefüllungen neuer Anlagen und einen Notfallservice. Verkauft wird direkt, über Händler und über Rahmenverträge. Seit Juli 2024 läuft ein neues ERP-System, die alten Aufträge stammen aus dem Vorgänger; zum 01.01.2026 stiegen die Listenpreise um 4 %. Die Daten reichen bis Sonntag, 28.02.2027; heute ist Montag, 01.03.2027. Im März berichtet die Geschäftsführung dem Beirat: Wo wachsen wir, wo verlieren wir – und was heißt das für 2027?

## Die Drills des Tages

| Drill | Thema | Du bist | Dein Ergebnis |
|---|---|---|---|
| 0 | Arbeitsumgebung: Was ist ein Kunde? | Lina Osterkamp, Trainee Vertriebsinnendienst | Notiz zur Kundenzahl |
| 1 | Überblicks-Dashboard: Wo wachsen wir, wo verlieren wir? | Dr. Henrike Vossberg, Leiterin Unternehmensentwicklung | Dashboard mit den Reitern „Überblick“ und „Wachstum“, Management-Summary |
| 2 | Finanzanalyse: Wo verdienen wir Geld? | Jasper Dierksmeyer, Leiter Controlling | Reiter „Finanzen“, Finanzkommentar für die Geschäftsführerin |
| 3 | Angebote mit Assistenz | Mathis Grevenbroich, Leiter Angebotsmanagement | Entscheidungsvorlagen, Reiter „Angebote“, eigener Skill |
| 4 | Personalgespräche vorbereiten | Birte Lohmeyer, Teamleiterin Anwendungstechnik & Kundendienst | Gesprächsvorbereitungen im Notizbuch |
| 5 | Präsentation an den Beirat: Geschäftsjahr 2026 und Prioritäten 2027 | Dr. Henrike Vossberg | Präsentation im Exhibit-Stil als HTML und PDF |

Die Anleitungen stehen in `drills/`. Du musst sie nicht öffnen: Sag Claude „Zeig mir den Prompt für Etappe 1“ oder „Was ist mein nächster Schritt? Nur den ersten Hinweis.“ Kommst du zu spät oder hängst du fest: „Ich möchte mit Drill 3 weitermachen.“ Claude lädt dann einen Zwischenstand.

## Wo was liegt

| Ordner | Inhalt |
|---|---|
| `daten/` | Die Tabellen der Übungsfirma: Kunden, Produkte, Lieferstellen, Aufträge, Preise, Kosten, Budget, Kurse; dazu Unternehmensprofil und Datenkatalog |
| `angebotseingang/` | Vier offene Angebotsvorgänge für den Tender Desk |
| `regelwerke/` | Angebots- und Freigaberichtlinie, Kompetenzordnung |
| `notizbuch/` | Das Notizbuch einer Teamleiterin als Obsidian-Vault (geht auch ohne Obsidian) |
| `praesentation/` | Auftrag der Geschäftsführerin, Vorlage im Exhibit-Stil und Stilfibel |
| `design/circle/` | Circle Design: Stilfibel und Gerüste für dein Dashboard und jede andere HTML-Seite, die gut aussehen soll |
| `folien-skills/` | Drei fertige Skills zum Installieren in Drill 5: Folien im Exhibit-Stil, Aktionstitel, Circle Design |
| `folien/` | Die Folien des Tages zum Nachlesen |
| `meine-ergebnisse/` | Deine eigenen Ergebnisse; Claude legt den Ordner beim ersten Ergebnis an |

Lösungen und Dozentenmaterial liegen nicht in diesem Ordner.

## Ein paar Fragen zum Warmwerden

- Wie viele Kunden haben wir in Deutschland, wie viele im Ausland?
- Welche Vertriebswege gibt es, und welcher ist der größte?
- Was steht in der Angebotsrichtlinie über Rabatte?
- Was hat Birte Lohmeyer in ihrem letzten Jour fixe notiert?

## Notizbuch ohne Obsidian

Ist Obsidian nicht installiert, sag Claude: „Zeig mir das Notizbuch im Browser.“ Claude erzeugt dann eine Seite, auf der du durch die Notizen klicken kannst.

## Hinweis

Dr. Sthamer ist hier eine Übungsfirma mit frei erfundenen Daten. Personen, Kunden, Produkte, Zahlen und Ereignisse beschreiben kein reales Unternehmen. Aussagen zu Regeln sind vereinfacht und ersetzen keine Rechtsberatung.
