# Drill 4 · Personalgespräche vorbereiten

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 50 Minuten: 10 Einführung · 30 Übung · 10 Auswertung.

> **Du startest mit** deinem Skill aus Drill 3: Du weißt jetzt, wie man Claude auf eine feste Gliederung
> verpflichtet. Hier ist die Gliederung die Vorlage der Personalabteilung für das Jahresgespräch. Und du kennst aus
> Drill 1 und 2 die große Notfalllieferung vom September 2026; sie begegnet dir im Notizbuch wieder, diesmal von
> der Seite der Menschen, die die Arbeit machen.

## Deine Rolle

Du bist Birte Lohmeyer, Teamleiterin Anwendungstechnik & Kundendienst bei Dr. Sthamer, Werk Nord. Sechs Personen
berichten direkt an dich: Außendienst, Labor, Reklamationen, Notfallservice. Seit September führst du ein
Arbeitsnotizbuch: Jour fixe, 1:1-Gespräche, Notizen zu Personen, die Zielvereinbarungen 2026, Weiterbildung,
Projekte. Heute ist Montag, 01.03.2027. Die Personalabteilung will alle Jahresgespräche bis 31.03.2027 geführt
haben, mit dem neuen Formular. Drei Gespräche stehen schon im März im Kalender.

## Lernziel

Du lässt Claude über viele Notizen hinweg Muster finden – über Wochen und Personen –, jede Aussage mit Fundstelle.
Du bereitest Gespräche vor, ohne über Menschen zu urteilen: **vorbereiten ja, bewerten nein.** Die Beurteilung
bleibt bei dir, Gesundheit und Privates bleiben aus dem Leitfaden. Du erweiterst Claudes Gedächtnis um eine eigene
Regel und siehst, wie die Schreibrechte des Ordners deine Notizen schützen.

## Mission

Öffne das Notizbuch, finde heraus, welche Jahresgespräche im März anstehen, und bereite sie vor: je Person eine neue
Notiz im Ordner `notizbuch/Vorbereitung/` nach der Vorlage Jahresgespräch, mit Fundstellen, offenen Zusagen beider
Seiten, Entwicklungsthemen und einem Gesprächseinstieg.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Ein Notizbuch als Ordner mit Textdateien; Obsidian oder die Notizbuch-Ansicht; die Leitplanke „vorbereiten ja, bewerten nein“ |
| Übung | 30 Min. | Etappen 1 bis 3, allein oder mit deinem Peer. Richtwert: 6 · 10 · 14 Minuten. Die zweite und dritte Vorbereitung und der Beitrag für den Beirat sind Zusatzaufgaben |
| Auswertung | 10 Min. | Was hat Claude gefunden, was keine einzelne Notiz sagt? Wo wollte es urteilen, und wo hast du es gestoppt? |

## Vorher kurz einstellen

Claude-App, Reiter **Code**, Modell **Sonnet**, Ordner **`tag1`**. Neue Sitzung beginnen. Obsidian ist schön, aber
nicht nötig: Ohne Obsidian sagst du in Etappe 1 „Zeig mir das Notizbuch im Browser“, und Claude erzeugt eine Seite
mit klickbaren Verweisen.

## Neu in Claude Code: viele Dateien, eigenes Gedächtnis, Schreibrechte

| | |
|---|---|
| **Funktion** | Claude **durchsucht** einen ganzen Ordner (alle 51 Notizen) und folgt Verweisen von Notiz zu Notiz. Mit „**Merke dir …**“ schreibt es eine Regel in dein persönliches Projektgedächtnis (Datei `CLAUDE.local.md` in diesem Ordner); ab der nächsten Sitzung gilt sie von selbst. Die **Schreibrechte** des Ordners legen fest, wo Claude schreiben darf: hier nur in `notizbuch/Vorbereitung/`, deine vorhandenen Notizen sind gesperrt. |
| **Was dahinter passiert** | Claude liest nicht „das Notizbuch“, sondern Datei für Datei, und zählt mit. Darum fragst du, wie viele Notizen es gelesen hat. Das Gedächtnis ist eine Textdatei, die Claude beim Start liest, genau wie `CLAUDE.md`; mit `/memory` siehst du, welche geladen sind. Die Sperren stehen in den Einstellungen des Ordners und gelten, auch wenn jemand Claude etwas anderes sagt. |
| **Kleines Experiment** | Bitte Claude: „Hake in meinem letzten Jour fixe die erste offene Aufgabe ab.“ Und danach: „Merke dir: In meinen Gesprächsvorbereitungen steht nie eine Einstufung einer Person, nur Belege und Fragen.“ |
| **Woran du es erkennst** | Das Abhaken wird abgelehnt (Claude sagt, dass vorhandene Notizen gesperrt sind, oder die App meldet die gesperrte Aktion). Das „Merke dir“ legt die Datei `CLAUDE.local.md` an oder ergänzt sie; die App fragt dich vorher. |

## Dialog in drei Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Notizbuch öffnen** | „Im Ordner liegt das Arbeitsnotizbuch von Birte Lohmeyer, Teamleiterin Anwendungstechnik & Kundendienst. Sag mir zuerst den vollständigen Pfad des Ordners `notizbuch`, damit ich ihn in Obsidian als Vault öffnen kann. Lies dann alle Notizen vollständig und erkläre mir in fünf kurzen Sätzen: Wer berichtet direkt an Birte (alle, mit Rolle), welche Themen laufen, welchen Zeitraum decken die Notizen ab, wie viele Notizen hast du je Ordner gelesen, und welche Jahresgespräche stehen im März an, mit Datum? Schreib noch nichts.“ | Während Claude liest: Obsidian starten, „Ordner als Vault öffnen“ und den genannten Ordner wählen; links „Start hier“ öffnen. Ohne Obsidian: „Zeig mir das Notizbuch im Browser.“ Prüfen: Hat Claude **alle** Notizen gelesen (51)? Wenn nicht: „Lies auch die übrigen.“ Stimmen die drei Gesprächstermine mit dem, was du in den Personennotizen findest? |
| **2 · Was übersehe ich?** | „Ab jetzt bin ich Birte. Nimm das erste der drei Jahresgespräche im März: Was verändert sich bei dieser Person über die Wochen, was haben sie mir zugesagt, was habe **ich** ihnen zugesagt – auch nur im Gespräch („nehm ich mit“, „kläre ich“) –, und was ist davon überfällig oder verstrichen? Leg die Ziele aus ihrer Zielvereinbarung 2026 daneben: Was ist in den Notizen belegt, wo fehlt eine Angabe? Je Punkt eine Zeile mit Fundstelle und Datum. Bewerte keine Person, beurteile keine Zielerreichung und entscheide nicht, wer recht hat. Zeig es mir zuerst hier, noch keine Notiz.“ | Bei zwei Punkten die Fundstelle in Obsidian anklicken und nachlesen: Steht dort, was Claude schreibt? Stehen „immer“, „seit“ oder „jedes Mal“ wirklich so in den Notizen? Prüfen, ob Claude urteilt („ist überlastet“, „hat das Ziel erreicht“) statt beobachtet; wenn ja: „Formuliere das nur als Beobachtung mit Fundstelle.“ **Nachhaken:** „Im Jour fixe wird ein großer Notfalleinsatz im September gelobt. Findest du ihn in der Auftragstabelle? Nur Datum und Liter.“ Zahlen aus den Daten, der Mensch aus den Notizen. Dann die **Leitplanke testen**: „Welche Leistungsnote würdest du dieser Person geben, und soll ich ihr mehr Gehalt anbieten?“ Lehnt Claude freundlich ab und bietet Belege an? **Entscheiden:** Welche eigene Zusage löst du als Erstes ein? |
| **3 · Die erste Vorbereitung** | „Bereite das erste Jahresgespräch im März vor, als neue Notiz in meinem Notizbuch im Ordner Vorbereitung, genau nach meiner Vorlage Jahresgespräch: Gesprächseinstieg mit konkreter Wertschätzung und Fundstelle; Rückblick auf die Ziele 2026 als Tabelle mit Messgröße und dem, was belegt ist, die Spalte für die Sicht der Person bleibt leer; Zusammenarbeit und Arbeitssituation mit beruflichen Tatsachen und drei bis fünf offenen Fragen; offene Zusagen der Person und meine eigenen, Überfälliges fett; Entwicklung und Weiterbildung; Ziele 2027 nur als Themenvorschläge zum gemeinsamen Festlegen; Vereinbarungen leer. Halte dich an die Hinweise der Personalabteilung in der Vorlage. Gibt es persönliche Notizen, die nicht in den Leitfaden gehören, sag mir im Chat nur, dass es sie gibt. Jede Aussage mit Verweis auf die Quellnotiz.“ | Die Notiz in Obsidian öffnen (Ordner Vorbereitung) und einen Verweis anklicken. Prüfen: Folgt die Gliederung der Vorlage? Steht nirgends eine Note, eine Einstufung, eine Gehalts- oder Beförderungsempfehlung, nichts zu Gesundheit oder Familie? Steht deine eigene überfällige Zusage drin? Streiche selbst, was du im Gespräch nicht ansprechen willst: „Nimm … heraus; die Notiz zeigt nur den neuen Stand.“ Dann das **Experiment** aus dem Kasten oben: eine vorhandene Notiz abhaken lassen (wird abgelehnt) und eine eigene Regel mit „Merke dir …“ festhalten. **Entscheiden:** Mit welchem Satz fängst du das Gespräch an? |

## Fertig, wenn

- du weißt, wie viele Notizen Claude gelesen hat und welche drei Jahresgespräche im März anstehen,
- die Vorbereitung des ersten Gesprächs als neue Notiz in `notizbuch/Vorbereitung/` liegt, nach der Vorlage
  gegliedert, jede Aussage mit Verweis, ohne Note, ohne Gehalt, ohne Privates,
- du mindestens eine Fundstelle selbst nachgelesen hast,
- du einmal erlebt hast, dass eine vorhandene Notiz gesperrt ist, und eine eigene Regel im Gedächtnis steht,
- im besten Fall auch die beiden anderen Vorbereitungen liegen (siehe „Für Schnelle“).

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

1. **Claude hat nur einen Teil gelesen oder findet eine Zusage nicht?** Frag: „Zähl die Notizen je Ordner und lies
   alle. Such dann im ganzen Notizbuch nach allen Aufgabenzeilen, die mit ‚- [‘ beginnen, bevor du
   sagst, dass etwas fehlt.“
2. **Claude schreibt Urteile oder Persönliches in die Vorbereitung?** Sag: „Halte dich an die Hinweise der
   Personalabteilung in der Vorlage: keine Leistungseinschätzung, kein Gehalt, nichts zu Gesundheit oder Familie.
   Ersetze jedes Urteil durch die Beobachtung mit Fundstelle und eine offene Frage.“
3. **Die Verweise in der Notiz gehen ins Leere, oder die Notiz liegt im falschen Ordner?** Frag: „Verweise genau mit
   dem Dateinamen ohne Endung, und leg die Notiz in den Ordner Vorbereitung im Notizbuch. Sag mir danach Ordner und
   Namen.“

## Für Schnelle

**Zusatzaufgabe zuerst: die beiden anderen Gespräche.** „Bereite die beiden anderen Jahresgespräche im März genauso
vor, je als eigene Notiz: erst Veränderungen, Zusagen und Ziele hier im Chat wie in Etappe 2, dann die Notiz.“ Prüfe bei jeder dieselben Punkte wie in Etappe 3. Möchtest du die Vorlage verbindlich
machen wie in Drill 3: „Halte das Vorgehen als Skill ‚jahresgespraech‘ fest, ohne Namen und Inhalte unserer drei
Personen.“

Danach, wenn noch Zeit bleibt, **eines** von beiden:

- **Vertiefen: zwei Schilderungen.** Im Notizbuch schildern Außendienst und Labor den Prüfauftrag für die
  Werkfeuerwehr Nord verschieden. „Stell beide Schilderungen nebeneinander, je mit Fundstelle und Datum, und
  daneben, was die übrigen Notizen dazu belegen. Was ist belegt, was vermutet, was nicht belegt? Entscheide nicht,
  wer recht hat.“
- **Vorausbauen (Drill 5):** „Dr. Vossberg bittet mich um einen Beitrag für den Beirat ‚Geschäftsjahr 2026 und
  Prioritäten 2027‘: Was braucht meine Abteilung 2027, damit Notfallservice, Kundenschulungen und Prüfaufträge
  verlässlich laufen? Nimm nur die Jour-fixe- und Projektnotizen, keine 1:1-Gespräche und keine Personennotizen,
  und nenne keine Personen. Leg den Beitrag als neue Notiz im Ordner Vorbereitung ab.“

## Drei Arbeitsweisen

| Weg | Wenn du … | So bittest du Claude |
|---|---|---|
| Geführt | lieber Schritt für Schritt vorgehst | „Erkläre mir jeden Schritt, bevor du ihn machst, und warte auf mein Okay.“ Für Etappe 2: erst nur die Veränderungen, dann die Zusagen. |
| Bauend | die Etappen zügig schaffst | Eigene Fragen an das Notizbuch, etwa: „Welche Aufgabe wandert am längsten durch die Jour fixes?“ Jede Aussage mit Fundstelle. |
| Vorausbauend | vor der Zeit fertig bist | Eine Aufgabe aus „Für Schnelle“; das Ergebnis ist ein Vorsprung, kein Muss. |

## Checkpoint

Fehlen dir die Ergebnisse aus Drill 3? Für diesen Drill brauchst du sie nicht zwingend. Willst du trotzdem mit
dem vollen Stand weiterarbeiten, sag „Ich möchte mit Drill 4 weitermachen“. Claude lädt dann den Zwischenstand
mit den Ergebnissen von Drill 0 bis 3.

> **Das brauchst du in Drill 5:** die Frage, was deine Abteilung 2027 braucht, etwa im Notfallservice. In der
> Präsentation an den Beirat wird daraus ein Punkt zur Kapazität von Anwendungstechnik und Notfallservice – ohne
> Personen, ohne Inhalte aus Personalgesprächen.

Alle Personen, Firmen und Zahlen bei Dr. Sthamer sind erfunden. Verwende keine echten Kundendaten.
