# Drill 0 · Arbeitsumgebung: Was ist ein Kunde?

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 30 Minuten: 10 Einführung · 15 Übung · 5 Auswertung.

> **Du startest mit** einem leeren Rechner: Den Arbeitsstand holst du in Etappe 1 selbst von GitHub. Aus
> früheren Drills brauchst du nichts.

## Deine Rolle

Du bist Lina Osterkamp, Trainee im Vertriebsinnendienst von Dr. Sthamer, Werk Nord. Dr. Sthamer stellt
Schaumlöschmittel her und verkauft sie direkt, über Händler, über Rahmenverträge und über einen Notfallservice.
Heute ist dein erster Tag mit dem neuen Datenauszug. Dr. Henrike Vossberg, Leiterin Unternehmensentwicklung,
bereitet für den Beirat eine Übersicht zur Geschäftsentwicklung vor und fragt dich als Erstes: „Wie viele Kunden
haben wir in Deutschland, wie viele im Ausland, und wie ist gezählt?“ Deine Antwort legst du ihr als kurze Notiz
ab. Ab Drill 1 bist du Dr. Vossberg selbst und findest deine Notiz vor.

## Lernziel

Du kennst die drei Arbeitsweisen der Claude-App (Chat, Cowork, Code) und weißt, wann du welche nimmst. Du hast
den Arbeitsstand mit Claude von GitHub geholt, im Reiter „Code“ den Ordner `tag1` geöffnet und Claude die ersten
Fragen dazu gestellt. Du hast gesehen, dass Claude Dateien liest, selbst nachrechnet und wann es um Erlaubnis
fragt, und du hast einmal nachgehakt, wie Claude auf eine Zahl gekommen ist.

## Mission

Hol den Arbeitsstand auf deinen Rechner und öffne den Ordner `tag1` im Reiter „Code“. Lass dir erklären, was
darin steckt. Stell die Frage nach der Kundenzahl, vergleiche die Zählweisen und entscheide, welche du
Dr. Vossberg empfiehlst. Schau dir dann einen Kunden in allen Quellen an.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Rundgang durch Chat, Cowork und Code; du holst den Arbeitsstand und öffnest den Ordner gleich mit (Etappen 1 und 2); Etappe 3 siehst du in der Vorführung |
| Übung | 15 Min. | Etappen 4 und 5 (Etappe 1 oder 2, falls sie in der Einführung nicht geklappt hat), allein oder mit deinem Peer. Richtwert: 9 · 6 Minuten |
| Auswertung | 5 Min. | Was hat Claude getan, woher wusste es das, wo musstest du nachhaken? |

## Vorher kurz einstellen

Das machst du während der Einführung mit. Claude-App öffnen, Reiter **Code**, Modell **Sonnet**. Ein
GitHub-Konto brauchst du nicht. Öffne dieses Blatt digital, kopiere die Eingaben aus der Tabelle unten und füge
sie ein, statt sie abzutippen.

**Was ist GitHub?** Ein Repository ist ein Ordner mit allen Dateien eines Projekts und ihrer Geschichte. GitHub
ist eine Website, auf der solche Ordner liegen. Mit dem Programm Git holt man eine Kopie davon auf den eigenen
Rechner („klonen“). Du musst Git nicht bedienen können: Das macht Claude für dich.

## Neu in Claude Code: Claude bedient Git, Arbeitsordner, Projektgedächtnis, Erlaubnis

| | |
|---|---|
| **Funktion** | Claude führt Befehle auf deinem Rechner aus, zum Beispiel Git: Es holt ein Repository von GitHub, wenn du es in einem Satz darum bittest. Danach arbeitet Claude in einem Ordner. Beim Start liest es die Datei `CLAUDE.md` in diesem Ordner: Das ist sein Projektgedächtnis (wo was liegt, welche Regeln gelten). Bevor Claude einen Befehl ausführt oder eine Datei schreibt, fragt es dich, außer die Einstellungen des Ordners erlauben die Aktion schon (hier: eigene Skripte und Dateien in deinem Ergebnisordner). Mit `@` sprichst du eine Datei direkt an. |
| **Was dahinter passiert** | Claude ist kein Chat über Dateien, sondern liest sie wirklich: Es öffnet Tabellen, schreibt kleine Programme und führt sie aus. Welche Aktionen ohne Rückfrage erlaubt sind und welche gesperrt, steht in den Einstellungen des Ordners. „Immer erlauben“ merkt sich die App für diese Aktion. |
| **Kleines Experiment** | Tipp `@daten/` und wähle `kennzahlen.json` aus der Liste: „Was steht in @daten/kennzahlen.json zum aktiven Kunden? Ein Satz.“ |
| **Woran du es erkennst** | Beim Klonen siehst du den Git-Befehl und bestätigst ihn. Beim ersten Öffnen eines Ordners fragt die App, ob du ihm vertraust. Danach zeigt Claude jede Datei, die es liest, und jeden Befehl, den es ausführt; bei allem, was die Einstellungen nicht freigeben, wartet es auf dein „Erlauben“. |

## Dialog in fünf Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Arbeitsstand holen** (in der Einführung) | **Weg A (Standard):** Im Reiter „Code“ eine neue Sitzung in deinem Benutzerordner beginnen (unter Windows `C:\Users\<dein Name>`, nicht OneDrive, nicht Desktop). Dann schreiben: „Klone [Repo-Adresse prüfen] in den Ordner dr-sthamer in meinem Benutzerordner und öffne den Ordner tag1.“ **Weg B (ohne Git):** Auf GitHub die Repository-Seite öffnen, „Code → Download ZIP“, die ZIP-Datei nach `%USERPROFILE%\dr-sthamer` entpacken (nicht OneDrive, nicht Desktop). | Bei Weg A: Fragt die App, ob du dem Ordner vertraust und ob Claude den Git-Befehl ausführen darf? Beide Male bestätigen. Liegt danach in deinem Benutzerordner ein Ordner `dr-sthamer` mit dem Unterordner `tag1`? Meldet Claude, dass Git fehlt, nimm Weg B und lass nichts installieren. **Dann in beiden Fällen:** neue Sitzung, als Ordner genau **`tag1`** wählen (nicht `dr-sthamer` darüber), Vertrauensfrage mit „Ja“ beantworten. |
| **2 · Ordner öffnen** (in der Einführung) | „Erkläre mir in drei Sätzen, was in diesem Ordner liegt und woher du das weißt.“ | Nennt Claude die Ordner (Daten, Angebotseingang, Regelwerke, Notizbuch, Präsentation) und sagt es, dass es das aus seinem Leitfaden `CLAUDE.md` weiß? Wenn Claude nichts kennt, ist der falsche Ordner gewählt (Hinweis 1). |
| **3 · Orientieren** (Vorführung in der Einführung; selbst stellen ist eine Zusatzaufgabe) | „Lies das Einstiegsblatt für Teilnehmende und das Unternehmensprofil. Erkläre mir dann in fünf Sätzen und ohne Fachjargon: Wer ist Dr. Sthamer – echt oder erfunden –, was verkauft das Unternehmen an wen und über welche Vertriebswege, aus welchen Teilen besteht das Geschäft, was ist der Stichtag, wie groß ist unser Übungsausschnitt, und was ist an ihm besonders?“ | In der Vorführung mitprüfen: Nennt Claude die Größe des **Übungsausschnitts** (32 Kunden) oder die Zahlen aus dem Unternehmensprofil („rund 1.400 Kunden in über 50 Ländern“)? Die Firmenzahlen gelten für das ganze Unternehmen und lassen sich in den Tabellen nicht nachzählen. Erklärt Claude den Unterschied zwischen Nachfüllgeschäft, Projektgeschäft und Notfallservice? |
| **4 · Was ist ein Kunde?** | „Wie viele unserer Kunden sitzen in Deutschland, wie viele im Ausland? Sag mir dazu, wen du als Kunden gezählt hast und aus welcher Quelle die Zahl stammt.“ | Zuschauen, was Claude tut: Es liest, rechnet und zeigt jeden Schritt an (und fragt, wo die Einstellungen es verlangen). Meist nennt Claude schon mehrere Zählweisen. Nennt es nur eine Zahl, nachhaken: „Und wenn nur zählt, wer in den letzten 24 Monaten etwas bestellt hat? Und wenn wir Lieferstellen zählen oder die Endkunden, die wir über Händler beliefern?“ Vergleiche: Kundenstamm, Status im Kundenstamm, Auftrag in 24 Monaten, Lieferstellen. Ergeben zwei Zählweisen dieselbe Zahl, ist das kein Fehler: Frag, warum. Wer ist ruhend – laut Feld Status im Kundenstamm oder nach dem Datum der letzten Lieferung (das ergibt verschiedene Kunden)? Wer ist ein Händler, und sind die Endkunden, die er beliefert, zusätzliche Kunden oder stehen sie schon im Kundenstamm? **Dann entscheidest du:** Welche Zählweise empfiehlst du Dr. Vossberg für ihr Dashboard und den Beirat? Schreib Claude deine Empfehlung mit einem Satz Begründung, zum Beispiel: „Ich empfehle Dr. Vossberg …, weil … Leg die Zahlen mit allen Zählweisen und meiner Empfehlung als Notiz für sie in meinen Ergebnissen ab.“ Entscheiden wird Dr. Vossberg. In Drill 1 bist du sie. |
| **5 · Ein Kunde, mehrere Quellen** | „Zeig mir das Stahlwerk Ruhrtal, Kundennummer K-1004, in allen Tabellen: im Kundenstamm, seine Lieferstellen mit Anwendung und aktuellem Produkt, seine Aufträge je Jahr in Litern, getrennt nach Auftragsart, und seine Reklamationen. Je Quelle zwei Zeilen. Sag mir dann, welche Lieferstellen seit 2021 neu dazugekommen sind und woran du das erkennst.“ | Nachhaken: „Woher weißt du, dass das überall derselbe Kunde ist?“ Schau bei den Auftragsarten genau hin: Was ist eine Nachfüllung, was eine Erstbefüllung, und wie unterscheiden sie sich in der Menge? Was dir auffällt, sagst du deinem Peer oder bringst es in die Auswertung mit. Nachfüll- und Projektgeschäft begegnen dir in Drill 1 wieder. |

## Fertig, wenn

- der Arbeitsstand auf deinem Rechner liegt, deine Sitzung im Ordner `tag1` läuft und Claude weiß, wo was liegt,
- du weißt, wer Dr. Sthamer ist, aus welchen Teilen das Geschäft besteht und welcher Stichtag gilt,
- du eine Zahl zu Kunden in Deutschland und im Ausland hast, **weißt, wie sie gezählt ist**, und deine Notiz für
  Dr. Vossberg in deinen Ergebnissen liegt (`meine-ergebnisse/notiz-kundenzahl.md`),
- du das Stahlwerk Ruhrtal in mehreren Quellen gesehen hast.

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

1. **Claude kennt die Daten nicht oder fragt nach Dateien?** Schau oben in der App, welcher Ordner gewählt ist.
   Es muss `tag1` sein, nicht `dr-sthamer` darüber oder ein Ordner darunter. Neue Sitzung, richtigen Ordner
   wählen, Frage wiederholen. Liegt der Ordner in OneDrive oder auf dem Desktop, hol ihn neu nach
   `%USERPROFILE%\dr-sthamer`.
2. **Claude fragt dauernd um Erlaubnis?** Das ist Absicht: Lies, was Claude tun will. Lesen und kleine
   Auswertungen in deinem Ergebnisordner darfst du mit „Immer erlauben“ freigeben. Befehle, die etwas außerhalb
   des Ordners tun wollen, lehnst du ab.
3. **Die Zahlen wirken seltsam oder widersprechen sich?** Frag: „Zeig mir, wie du gezählt hast: welche Tabelle,
   welcher Filter, welcher Stichtag.“ Zahlen aus dem Unternehmensprofil gelten für das ganze Unternehmen; der
   Übungsausschnitt hat 32 Kunden.

## Für Schnelle

Hast du Etappe 3 in der Vorführung verpasst, stell sie jetzt selbst. Dann wähle **eines** von beiden.

- **Vertiefen:** „Welche Auftragsarten und welche Vertriebswege gibt es in unserer Auftragstabelle? Zeig mir je
  Kombination die Zahl der Positionen 2026 als kleine Tabelle, ohne Wertung.“ Die Auftragsarten werden in Drill 1
  wichtig.
- **Vorausbauen (Drill 1):** „Dr. Vossberg baut diese Woche ein Dashboard zur Geschäftsentwicklung für den
  Beirat. Welche fünf Kennzahlen sollte es zeigen? Gib mir dazu eine Liste der Tabellen mit Zeilenzahl und Zweck,
  noch keine Webseite.“ Das Dashboard baust du in Drill 1.

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
