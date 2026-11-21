# Drill 0 · Arbeitsumgebung: Was ist ein Kunde?

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 30 Minuten: 10 Einführung · 15 Übung · 5 Auswertung.

> **Du startest mit** dem frischen Ordner `tag1`, den du von der Kursleitung bekommst. Aus früheren Drills brauchst du nichts.

## Deine Rolle

Du bist Lina Osterkamp, Trainee im Vertriebsinnendienst von Dr. Sthamer, Werk Nord. Dr. Sthamer stellt
Schaumlöschmittel her und stellt seine Kunden seit 2023 im Programm „FreeFoam“ von fluorhaltigen auf
fluorfreie Produkte um. Heute ist dein erster Tag mit dem neuen Datenauszug. Dr. Henrike Vossberg,
Programmleiterin Fluorfrei-Umstellung, bereitet für den Beirat eine Übersicht vor und fragt dich als Erstes:
„Wie viele Kunden haben wir in Deutschland, wie viele im Ausland, und wie ist gezählt?“ Deine Antwort legst du
ihr als kurze Notiz ab. Ab Drill 1 bist du Dr. Vossberg selbst und findest deine Notiz vor.

## Lernziel

Du kennst die drei Arbeitsweisen der Claude-App (Chat, Cowork, Code) und weißt, wann du welche nimmst. Du hast
im Reiter „Code“ den Ordner `tag1` geöffnet und Claude die ersten Fragen dazu gestellt. Du hast gesehen, dass
Claude Dateien liest, selbst nachrechnet und wann es um Erlaubnis fragt, und du hast einmal nachgehakt, wie Claude
auf eine Zahl gekommen ist.

## Mission

Öffne den Ordner `tag1` im Reiter „Code“. Lass dir erklären, was darin steckt. Stell die Frage nach der
Kundenzahl, vergleiche die Zählweisen und entscheide, welche du Dr. Vossberg empfiehlst. Schau dir dann einen
Kunden in allen Quellen an.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Rundgang durch Chat, Cowork und Code; Vorführung des ersten Gesprächs im Ordner `tag1`, dabei stellst du die App gleich mit ein (Etappe 1); Etappe 2 siehst du in der Vorführung |
| Übung | 15 Min. | Etappen 3 und 4 (Etappe 1, falls sie in der Einführung nicht geklappt hat), allein oder mit deinem Peer. Richtwert: 9 · 6 Minuten |
| Auswertung | 5 Min. | Was hat Claude getan, woher wusste es das, wo musstest du nachhaken? |

## Vorher kurz einstellen

Das machst du während der Vorführung mit. Claude-App öffnen, Reiter **Code**, Modell **Sonnet**. Als Ordner den
Ordner **`tag1`** wählen, den du von der Kursleitung bekommen hast (entpackt, nicht in einem Cloud-Ordner wie
OneDrive). Wichtig: genau `tag1`, nicht einen Ordner darüber. Fragt die App, ob du dem Ordner vertraust: Ja.
Ein GitHub-Konto brauchst du nicht.

Öffne dieses Blatt digital, kopiere die Eingaben aus der Tabelle unten und füge sie ein, statt sie abzutippen.

## Neu in Claude Code: Arbeitsordner, Projektgedächtnis, Erlaubnis

| | |
|---|---|
| **Funktion** | Claude arbeitet in einem Ordner auf deinem Rechner. Beim Start liest es die Datei `CLAUDE.md` in diesem Ordner: Das ist sein Projektgedächtnis (wo was liegt, welche Regeln gelten). Bevor Claude einen Befehl ausführt oder eine Datei schreibt, fragt es dich, außer die Einstellungen des Ordners erlauben die Aktion schon (hier: eigene Skripte und Dateien in deinem Ergebnisordner). Mit `@` sprichst du eine Datei direkt an. |
| **Was dahinter passiert** | Claude ist kein Chat über Dateien, sondern liest sie wirklich: Es öffnet Tabellen, schreibt kleine Programme und führt sie aus. Welche Aktionen ohne Rückfrage erlaubt sind und welche gesperrt, steht in den Einstellungen des Ordners. „Immer erlauben“ merkt sich die App für diese Aktion. |
| **Kleines Experiment** | Tipp `@daten/` und wähle `kennzahlen.json` aus der Liste: „Was steht in @daten/kennzahlen.json zum aktiven Kunden? Ein Satz.“ |
| **Woran du es erkennst** | Beim ersten Öffnen fragt die App, ob du dem Ordner vertraust. Danach zeigt Claude jede Datei, die es liest, und jeden Befehl, den es ausführt; bei allem, was die Einstellungen nicht freigeben, wartet es auf dein „Erlauben“. |

## Dialog in vier Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Ordner öffnen** | „Erkläre mir in drei Sätzen, was in diesem Ordner liegt und woher du das weißt.“ | Nennt Claude die Ordner (Daten, Angebotseingang, Regelwerke, Notizbuch, Präsentation) und sagt es, dass es das aus seinem Leitfaden `CLAUDE.md` weiß? Wenn Claude nichts kennt, ist der falsche Ordner gewählt (Hinweis 1). |
| **2 · Orientieren** (Vorführung in der Einführung; selbst stellen ist eine Zusatzaufgabe) | „Lies das Einstiegsblatt für Teilnehmende und das Unternehmensprofil. Erkläre mir dann in fünf Sätzen und ohne Fachjargon: Wer ist Dr. Sthamer – echt oder erfunden – und was verkauft das Unternehmen an wen, worum geht es im Programm FreeFoam, was ist der Stichtag, wie groß ist unser Übungsausschnitt, und was ist an ihm besonders?“ | In der Vorführung mitprüfen: Nennt Claude die Größe des **Übungsausschnitts** (32 Kunden) oder die Zahlen aus dem Unternehmensprofil („rund 1.400 Kunden in über 50 Ländern“)? Die Firmenzahlen gelten für das ganze Unternehmen und lassen sich in den Tabellen nicht nachzählen. |
| **3 · Was ist ein Kunde?** | „Wie viele unserer Kunden sitzen in Deutschland, wie viele im Ausland? Sag mir dazu, wen du als Kunden gezählt hast und aus welcher Quelle die Zahl stammt.“ | Zuschauen, was Claude tut: Es liest, rechnet und zeigt jeden Schritt an (und fragt, wo die Einstellungen es verlangen). Meist nennt Claude schon mehrere Zählweisen. Nennt es nur eine Zahl, nachhaken: „Und wenn nur zählt, wer in den letzten 24 Monaten etwas bestellt hat? Und wenn wir Lieferstellen zählen oder die Endkunden, die wir über Händler beliefern?“ Vergleiche: Kundenstamm, Status aktiv, Auftrag in 24 Monaten, Lieferstellen. Ergeben zwei Zählweisen dieselbe Zahl, ist das kein Fehler: Frag, warum. Wer ist ruhend, wer ist ein Händler? **Dann entscheidest du:** Welche Zählweise empfiehlst du Dr. Vossberg für ihr Dashboard und den Beirat? Schreib Claude deine Empfehlung mit einem Satz Begründung, zum Beispiel: „Ich empfehle Dr. Vossberg …, weil … Leg die Zahlen mit allen Zählweisen und meiner Empfehlung als Notiz für sie in meinen Ergebnissen ab.“ Entscheiden wird Dr. Vossberg. In Drill 1 bist du sie. |
| **4 · Ein Kunde, mehrere Quellen** | „Zeig mir die Raffinerie Küstenmark, Kundennummer K-1003, in allen Tabellen: im Kundenstamm, ihre Lieferstellen mit Anwendung und aktuellem Produkt, ihre Aufträge je Jahr in Litern, ihre Reklamationen und die Kontakte mit ihr. Je Quelle zwei Zeilen, und sag mir bei der Verladestation, was über die Anlage bekannt ist und was fehlt.“ | Nachhaken: „Woher weißt du, dass das überall derselbe Kunde ist?“ Schau bei der Verladestation genau hin: Welche Zumischrate steht im System, und gibt es eine Datenaufnahme vor Ort? Was dir auffällt, sagst du deinem Peer oder bringst es in die Auswertung mit. Die Datenaufnahme der Anlagen begegnet dir in Drill 1 wieder. |

## Fertig, wenn

- deine Sitzung im Ordner `tag1` läuft und Claude weiß, wo was liegt,
- du weißt, wer Dr. Sthamer ist, worum es in FreeFoam geht und welcher Stichtag gilt,
- du eine Zahl zu Kunden in Deutschland und im Ausland hast, **weißt, wie sie gezählt ist**, und deine Notiz für
  Dr. Vossberg in deinen Ergebnissen liegt (`meine-ergebnisse/notiz-kundenzahl.md`),
- du die Raffinerie Küstenmark in mehreren Quellen gesehen hast.

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

1. **Claude kennt die Daten nicht oder fragt nach Dateien?** Schau oben in der App, welcher Ordner gewählt ist.
   Es muss `tag1` sein, nicht ein Ordner darüber oder darunter. Neue Sitzung, richtigen Ordner wählen, Frage
   wiederholen.
2. **Claude fragt dauernd um Erlaubnis?** Das ist Absicht: Lies, was Claude tun will. Lesen und kleine
   Auswertungen in deinem Ergebnisordner darfst du mit „Immer erlauben“ freigeben. Befehle, die etwas außerhalb
   des Ordners tun wollen, lehnst du ab.
3. **Die Zahlen wirken seltsam oder widersprechen sich?** Frag: „Zeig mir, wie du gezählt hast: welche Tabelle,
   welcher Filter, welcher Stichtag.“ Zahlen aus dem Unternehmensprofil gelten für das ganze Unternehmen; der
   Übungsausschnitt hat 32 Kunden.

## Für Schnelle

Hast du Etappe 2 in der Vorführung verpasst, stell sie jetzt selbst. Dann wähle **eines** von beiden.

- **Vertiefen:** „Welche fluorfreien Produkte ersetzen welche fluorhaltigen? Zeig mir die Nachfolger als Tabelle,
  und sag mir, bei welchen Produkten Produktlinie und Deklaration nicht zusammenpassen.“ Was „fluorfrei“ heißt,
  wird in Drill 1 wichtig.
- **Vorausbauen (Drill 1):** „Dr. Vossberg baut diese Woche ein Dashboard zur Umstellung für den Beirat. Welche
  fünf Kennzahlen sollte es zeigen? Gib mir dazu eine Liste der Tabellen mit Zeilenzahl und Zweck, noch keine
  Webseite.“ Das Dashboard baust du in Drill 1.

## Drei Arbeitsweisen

| Weg | Wenn du … | So bittest du Claude |
|---|---|---|
| Geführt | zum ersten Mal mit Claude arbeitest | „Erkläre mir jeden Schritt, bevor du ihn machst, und warte auf mein Okay.“ |
| Bauend | die Etappen zügig schaffst | Eigene Fragen an die Daten stellen; bei jeder Zahl fragen, wie gezählt wurde. |
| Vorausbauend | vor der Zeit fertig bist | Eine Aufgabe aus „Für Schnelle“; das Ergebnis ist ein Vorsprung, kein Muss. |

## Checkpoint

Drill 0 braucht keinen Zwischenstand. Fehlt dir am Ende die Notiz, ist das kein Problem: In Drill 1 legst du die
Zählweise selbst fest.

> **Das brauchst du in Drill 1:** Deine Notiz zur Kundenzahl. Die Zählweise, die du empfiehlst, wird die
> Definition der Kunden-Kachel im Dashboard.

Alle Personen, Firmen und Zahlen bei Dr. Sthamer sind erfunden. Verwende keine echten Kundendaten.
