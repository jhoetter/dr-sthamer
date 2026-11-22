# Drill 5 · Management-Präsentation im Exhibit-Stil

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 50 Minuten: 10 Einführung · 30 Übung · 10 Auswertung.

> **Du startest mit** deiner Management-Summary (Drill 1) und deinem Finanzkommentar (Drill 2); aus ihnen kommen
> die Zahlen der Pflichtfolien. Deine Erfahrung mit dem eigenen Skill (Drill 3) brauchst du gleich zu Beginn.
> Daraus wird jetzt die Antwort auf die Frage des Tages: „Wo wachsen wir, wo verlieren wir – und was heißt das
> für 2027?“

## Deine Rolle

Du bist wieder Dr. Henrike Vossberg, Leiterin Unternehmensentwicklung. Die Geschäftsführerin hat dir am
15.02.2027 den Auftrag geschickt: Am 09.03.2027 präsentierst du dem Beirat „Geschäftsjahr 2026 und Prioritäten
2027“, drei Folien (eine vierte mit dem Entscheidungsbedarf, wenn möglich), 10 Minuten, im Exhibit-Stil der
Beiratsunterlagen. Der Vorsitzende wird fragen, ob wir Kunden verlieren und wie abhängig wir von unseren größten
Kunden sind. Das externe Mitglied war früher Finanzchef eines Industrieunternehmens und prüft, ob eine Zahl oder
Marge schöngerechnet ist.

## Lernziel

Du installierst fertige Skills von außen und arbeitest mit ihnen: In Drill 3 hast du selbst einen Skill gebaut,
hier holst du dir drei fertige ins Projekt (Exhibit-Stil, Aktionstitel, Circle Design) und siehst, wann Claude sie
lädt. Du schreibst die Storyline selbst: Titel als Aussagesätze mit der Zahl, die sie belegt; Claude prüft sie nach
dem Skill `aktionstitel`, schreibt aber nicht um. Claude baut die Folien nach dem Skill `exhibit-stil` mit
Diagrammen aus echten Daten. Du gibst Claude ein Bild deiner eigenen Folie zur Prüfung.

## Mission

Installiere die Folien-Skills, lies den Auftrag der Geschäftsführerin, schreib drei Titel (Titelfolie und zwei
Inhaltsfolien mit den Zahlen aus Drill 1 und 2), lass sie nach dem Skill prüfen und bau daraus die Präsentation als
Kopie der Vorlage in deinen Ergebnissen. Sprechernotizen, PDF, eine weitere Folie und die Begleitseite im Circle
Design stehen unter „Für Schnelle“.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Fertige Skills von außen: was in einem Skill steht, wie man ihn installiert und wann Claude ihn lädt (Bezug zu deinem Skill aus Drill 3); was einen Aktionstitel ausmacht; die Vorlage im Exhibit-Stil und ihr Prüfkasten; Vorführung: ein Screenshot geht an Claude |
| Übung | 30 Min. | Etappen 1 bis 4, allein oder mit deinem Peer. Richtwert: 4 · 5 · 9 · 12 Minuten |
| Auswertung | 10 Min. | Zwei, drei Präsentationen am Beamer: Erzählen die Titel allein die Geschichte? Hat Claude die Skills von selbst geladen? Was würde das externe Beiratsmitglied angreifen? |

## Vorher kurz einstellen

Claude-App, Reiter **Code**, Modell **Sonnet**, Ordner **`tag1`**. Neue Sitzung beginnen. Fehlen dir Ergebnisse
früherer Drills, lade zuerst den Zwischenstand (unten unter „Checkpoint“). Edge oder Chrome sollte installiert sein;
das ist auf den meisten Rechnern der Fall.

## Neu in Claude Code: Skills installieren und nutzen

| | |
|---|---|
| **Funktion** | Ein **Skill** ist ein Ordner mit einer Anleitung (`SKILL.md`) für eine bestimmte Art Aufgabe. In Drill 3 hast du selbst einen gebaut; hier **installierst du fertige von außen**: Im Ordner `folien-skills` liegen drei – `exhibit-stil` (Folien bauen und prüfen), `aktionstitel` (Titel und Storyline prüfen) und `circle-design` (gut aussehende HTML-Seiten). Installiert heißt: Sie liegen in `.claude/skills/` deines Projekts, genau wie dein Skill `angebotsvorlage`. |
| **Was dahinter passiert** | Claude liest am Anfang jeder Sitzung nur Name und Beschreibung jedes Skills, nicht die ganze Anleitung. Passt deine Aufgabe zu einer Beschreibung („Prüfe meine Titel“), lädt Claude die ganze `SKILL.md` und arbeitet nach ihren Regeln. Passt nichts, bleibt der Skill ungelesen und kostet nichts. Mit dem Namen kannst du ihn auch ausdrücklich verlangen („nach dem Skill aktionstitel“) oder direkt aufrufen (`/aktionstitel`). Der Ordner `.claude` ist geschützt: Die App fragt nach, bevor Claude dort etwas ablegt. |
| **Kleines Experiment** | In Etappe 1: erst fragen „Welche Skills kennst du?“, dann installieren lassen, dann noch einmal fragen. In Etappe 3: „Prüfe diese drei Titel“ – ohne den Skill zu nennen. Lädt Claude ihn von selbst? |
| **Woran du es erkennst** | Nach der Installation stehen die drei Namen in Claudes Antwort (oder in der Liste bei `/skills`). Bei der Arbeit meldet Claude, dass es einen Skill lädt, und urteilt mit dessen Regeln, etwa „Regel 1: Etikett, kein Verb“. Fehlen die Skills nach der Installation: neue Sitzung im Ordner `tag1` beginnen. |

## Neu in Claude Code: Bilder geben, Browser im Hintergrund

| | |
|---|---|
| **Funktion** | Du kannst Claude **Bilder** geben: einen Screenshot ins Eingabefeld einfügen (Windows: Win+Umschalt+S, dann Strg+V) oder hineinziehen. Claude sieht das Bild und prüft es. Claude kann außerdem **Edge oder Chrome im Hintergrund** starten, ohne Fenster: Es macht damit selbst Screenshots jeder Folie und liest den Prüfkasten aus. |
| **Was dahinter passiert** | Claude prüft eine Folie zweimal: im Quelltext (stimmt die Zahl, ist die Quelle da?) und im Bild (läuft etwas über, ist etwas unlesbar?). Was nur im Bild auffällt, findet es nur im Bild. Die Regeln der Stilfibel sind dabei die Leitplanke: Claude prüft gegen sie, nicht nach Geschmack. |
| **Kleines Experiment** | In Etappe 4: Mach selbst einen Screenshot deiner Inhaltsfolie und schick ihn mit „Prüfe diese Folie gegen die Regeln unserer Stilfibel. Nur urteilen, nichts ändern.“ |
| **Woran du es erkennst** | Claude beschreibt, was auf deinem Bild zu sehen ist, und nennt Regeln der Stilfibel. |

## Dialog in vier Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Folien-Skills installieren** | Zuerst: „Welche Skills kennst du?“ Dann: „Installiere die drei Folien-Skills aus dem Ordner folien-skills für dieses Projekt und zeig mir, dass du sie kennst.“ | Fragt die App, ob Claude in den geschützten Ordner `.claude` schreiben darf: Ja. Nennt Claude jetzt `exhibit-stil`, `aktionstitel` und `circle-design`, je mit einem Satz, wofür, und daneben deinen Skill `angebotsvorlage` aus Drill 3? Fehlen sie, neue Sitzung im Ordner `tag1` beginnen und noch einmal fragen. Die Skills selbst änderst du nicht. |
| **2 · Vorlage und Auftrag** | „Wir haben eine Vorlage im Exhibit-Stil für Präsentationen an den Beirat. Öffne sie im Browser und erklär mir nach dem Skill exhibit-stil in höchstens fünf Sätzen, welche Folienarten es gibt, welche Regeln gelten und wie der Prüfkasten arbeitet. Zeig mir danach den Auftrag der Geschäftsführerin im Wortlaut, ohne Kommentar. Ändere noch nichts.“ | Im Browser mit den Pfeiltasten blättern. Oben rechts steht ein roter Prüfkasten (anklicken klappt die Hinweise auf): Was meldet er bei der leeren Vorlage? Im Auftrag: Welche drei Fragen soll der Beirat beantwortet bekommen, und was darf **nicht** auf die Folien? |
| **3 · Deine Storyline** | Zuerst liest **du**, Claude schreibt hier nichts vor: deine Management-Summary (Drill 1) und deinen Finanzkommentar (Drill 2), per Doppelklick oder mit „Zeig mir meinen Finanzkommentar im Wortlaut.“ Dann schreibst **du** drei Titel, je als ganzen Satz mit Verb, höchstens etwa 80 Zeichen, auf der Titelfolie etwa 70: Titelfolie mit deiner Kernaussage, eine Inhaltsfolie zu „Wo wachsen wir, wo verlieren wir?“ mit einer Zahl aus der Summary, eine zu „Wo verdienen wir Geld?“ mit einer Zahl aus dem Finanzkommentar. Dann schickst du: „Hier ist meine Storyline für den Beirat. Folie 1: … Folie 2: … · Zahl: … Folie 3: … · Zahl: … Ein Diagramm kommt auf Folie … Prüfe meine Titel. Prüf auch, ob jede Zahl so in meinen Ergebnissen steht. Sag mir je Folie ‚stimmt‘ oder was nicht stimmt und warum. Formuliere keinen Titel um und schlag keine eigene Storyline vor.“ | Hat Claude den Skill `aktionstitel` von selbst geladen (du hast ihn nicht genannt), und nennt es je Titel die Regel? Selbst prüfen: Trägt jeder Titel eine Aussage mit Verb, nicht ein Etikett wie „Absatz 2026“? Spricht die Zahl über dieselbe Gruppe wie der Titel? Steht bei Finanzzahlen Ist oder Budget, und ist der Notfallservice ehrlich behandelt? Was nicht stimmt, **korrigierst du selbst** und schickst nur die geänderten Zeilen. Zum Schluss die drei Titel laut lesen: Erzählen sie allein die Geschichte? |
| **4 · Die Folien** | „Bau die Präsentation jetzt nach dem Skill exhibit-stil und meiner geprüften Storyline als Kopie der Vorlage in meinen Ergebnissen, genau drei Folien. Meine Titel übernimmst du wörtlich; musst du einen ändern, weil er gegen eine Regel der Stilfibel verstößt, nenn mir danach jede Änderung. Das Diagramm zeichnest du auf der Folie, die ich gewählt habe, mit den echten Werten, bei Anteilen samt Zähler und Nenner. Jede Zahl bekommt ihre Quellenzeile. Mach danach mit Edge oder Chrome im Hintergrund einen Screenshot jeder Folie, sieh sie dir an, lies den Prüfkasten aus und behebe, was er meldet; nur den Hinweis auf fehlende Sprechernotizen lässt du stehen. Öffne die Präsentation dann im Browser.“ | Durchblättern. Stehen deine Titel so da, wie du sie geschrieben hast? Meldet der Prüfkasten noch etwas außer fehlenden Notizen? Hat jede Folie mit Zahl eine Quellenzeile? Dann das **Experiment** aus dem Kasten oben: Screenshot einer Inhaltsfolie an Claude, „Prüfe diese Folie gegen die Regeln unserer Stilfibel. Nur urteilen, nichts ändern.“ Zum Schluss **entscheiden**: Würdest du diesen Entwurf so an die Geschäftsführerin schicken? |

## Fertig, wenn

- die drei Folien-Skills im Projekt installiert sind und Claude beim Prüfen der Titel nach `aktionstitel` und beim
  Bauen nach `exhibit-stil` gearbeitet hat,
- deine Präsentation in deinen Ergebnissen liegt (`praesentation.html`), drei Folien mit deinen Titeln, einem
  Diagramm aus echten Daten und einer Quellenzeile auf jeder Folie mit Zahl,
- der Prüfkasten nichts mehr meldet außer fehlenden Sprechernotizen,
- du Claude einmal einen Screenshot deiner Folie zur Prüfung gegeben hast.

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

0. **Claude kennt die Skills nicht, oder es lädt sie nicht?** Neue Sitzung im Ordner `tag1` beginnen und fragen
   „Welche Skills kennst du?“. Fehlen sie dann noch: „Liegen die drei Ordner aus folien-skills in .claude/skills?
   Zeig mir die Liste.“ Lädt Claude einen Skill nicht von selbst, nenn ihn: „… nach dem Skill aktionstitel“.
1. **Dir fällt kein Titel ein, oder Claude schreibt deine Titel um?** Nimm die Kernaussagen aus Summary und
   Finanzkommentar und frag dich: Was soll der Beirat nach dieser Folie wissen? Ein Titel hat ein Verb und
   höchstens zwei Zeilen. Schlägt Claude eigene Titel vor: „Bitte nur prüfen, meine Titel bleiben.“
2. **Der Prüfkasten meldet Hinweise, oder ein Text ist rot gestrichelt?** Frag: „Lies die Prüfung der Vorlage und
   behebe jeden Hinweis außer den fehlenden Notizen. Kürze zu lange Texte, verkleinere nie die Schrift, und lass
   Stil und Raster unverändert.“ Weichen Zahlen von deiner Summary ab: „Rechne mir die Zahl auf Folie 2 vor:
   Zähler, Nenner, was nicht mitzählt.“

## Für Schnelle

Nimm sie der Reihe nach, so weit die Zeit reicht.

- **Sprechernotizen und PDF:** „Schreib zu jeder Folie Sprechernotizen für 10 Minuten Vortrag: Kernsatz, was ich zur
  Zahl sage, die Einschränkung, bevor jemand fragt, die Überleitung und die Zeit. Zeig mir die Zeiten je Folie und
  ihre Summe. Erstelle dann mit Edge oder Chrome im Hintergrund ein PDF mit einer Folie je Seite in meinen
  Ergebnissen, prüf es – so viele Seiten wie Folien, Diagramm sichtbar – und öffne es.“ Taste **S** zeigt die
  Notizen unter der Folie. Klappt das PDF nicht: in Edge oder Chrome **Drucken → Als PDF speichern**, Ränder
  „Keine“, Hintergrundgrafiken an.
- **Eine vierte Folie:** eine Entscheidungsfolie mit höchstens drei Beschlüssen zu den Prioritäten 2027 (Nachfüll-
  und Projektgeschäft, Händlernetz, Abhängigkeit von großen Kunden, Preisdisziplin bei Angeboten aus Drill 3,
  Kapazität von Anwendungstechnik und Notfallservice ohne Personen) oder eine dritte Inhaltsfolie. Titel selbst
  schreiben, nach dem Skill aktionstitel prüfen lassen, dann: „Nimm diese Folie nach dem Skill exhibit-stil dazu.“
  Bei jedem Beschluss: Kann ein Beirat das beschließen (Auftrag, Freigabe, Berichtspflicht)?
- **Der Finanzchef greift an:** „Lass einen Subagenten unabhängig prüfen, ob jede Zahl auf meinen Folien in meinen
  Ergebnissen steht und mit den Tabellen übereinstimmt. Unser externes Mitglied war früher Finanzchef eines
  Industrieunternehmens: Welche Zahl würde er als schöngerechnet angreifen, und hält sie? Ändere noch nichts, ich
  entscheide.“ Den Subagenten kennst du aus Drill 2.
- **Begleitseite im Circle Design:** „Mach aus meiner Präsentation eine Begleitseite für den Beirat als HTML-Seite
  in meinen Ergebnissen, nach dem Skill circle-design: Kernaussage, je Folie Titel und Beleg-Zahl mit Quelle. Keine
  neuen Aussagen. Zeig sie mir hell und dunkel.“ Die Präsentation bleibt im Exhibit-Stil, die Begleitseite ist eine
  Webseite.
- **Vorausbauen:** „Halte fest, wie wir heute vorgegangen sind – Auftrag lesen, Storyline prüfen lassen, Vorlage
  füllen, Screenshots prüfen –, als Skill ‚management-praesentation‘, damit ich die nächste Beiratsunterlage mit
  einem Satz beginnen kann. Ohne Zahlen und Titel von heute.“

## Drei Arbeitsweisen

| Weg | Wenn du … | So bittest du Claude |
|---|---|---|
| Geführt | lieber Schritt für Schritt vorgehst | „Erkläre mir jeden Schritt, bevor du ihn machst, und warte auf mein Okay.“ Für Etappe 3: erst nur einen Titel schreiben und nach dem Skill aktionstitel prüfen lassen. Für Etappe 4: „Bau erst nur Folie 2 nach dem Skill exhibit-stil und zeig sie mir.“ |
| Bauend | die Etappen zügig schaffst | Eine andere Diagrammart aus der Stilfibel für eine deiner Fragen; jede Zahl mit Quelle und Definition. |
| Vorausbauend | vor der Zeit fertig bist | Eine Aufgabe aus „Für Schnelle“; das Ergebnis ist ein Vorsprung, kein Muss. |

## Checkpoint

Fehlen dir Ergebnisse früherer Drills? Sag „Ich möchte mit Drill 5 weitermachen“. Claude lädt dann den
Zwischenstand mit den Ergebnissen von Drill 0 bis 4 und sagt dir, welche Dateien jetzt da sind.

> **Und morgen:** Heute hat Claude dich unterstützt; entschieden hast du. An Tag 2 baut ihr Agenten, die selbst
> handeln – mit Kontrollen, die ihr festlegt.

Alle Personen, Firmen und Zahlen bei Dr. Sthamer sind erfunden. Verwende keine echten Kundendaten.
