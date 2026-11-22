# Drill 5 · Management-Präsentation im Exhibit-Stil

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 50 Minuten: 10 Einführung · 30 Übung · 10 Auswertung.

> **Du startest mit** allem, was du heute gebaut hast: Management-Summary (Drill 1), Finanzkommentar (Drill 2),
> Entscheidungsvorlagen (Drill 3) und, falls vorhanden, Birtes Beitrag zum Beiratsbericht im Notizbuch (Drill 4).
> Daraus wird jetzt die Antwort auf die Frage des Tages: „Wo wachsen wir, wo verlieren wir – und was heißt das
> für 2027?“

## Deine Rolle

Du bist wieder Dr. Henrike Vossberg, Leiterin Unternehmensentwicklung. Die Geschäftsführerin hat dir am
15.02.2027 den Auftrag geschickt: Am 09.03.2027 präsentierst du dem Beirat „Geschäftsjahr 2026 und Prioritäten
2027“, vier bis fünf Folien, 15 Minuten, im Exhibit-Stil der Beiratsunterlagen. Der Vorsitzende wird fragen, ob wir
Kunden verlieren und wie abhängig wir von unseren größten Kunden sind. Das externe Mitglied war lange Finanzchef in
der Industrie und prüft, ob eine Zahl oder Marge schöngerechnet ist.

## Lernziel

Du installierst fertige Skills von außen und arbeitest mit ihnen: In Drill 3 hast du selbst einen Skill gebaut,
hier holst du dir drei fertige ins Projekt (Exhibit-Stil, Aktionstitel, Circle Design) und siehst, wann Claude sie
lädt. Du schreibst die Storyline selbst: Titel als Aussagesätze mit der Zahl, die sie belegt. Claude prüft nach dem
Skill, schreibt aber nicht um. Du baust eine HTML-Präsentation mit Diagrammen aus echten Daten, Sprechernotizen und
PDF. Du gibst Claude ein Bild deiner eigenen Folie zur Prüfung und lässt es den Browser im Hintergrund steuern.

## Mission

Installiere die Folien-Skills, lies den Auftrag der Geschäftsführerin, schreib deine Storyline, lass sie nach dem
Skill prüfen und bau daraus die Präsentation als Kopie der Vorlage in deinen Ergebnissen, mit Sprechernotizen und
PDF für den Versand.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 10 Min. | Fertige Skills von außen: was in einem Skill steht und wann Claude ihn lädt; was einen Aktionstitel ausmacht; die Vorlage im Exhibit-Stil und ihr Prüfkasten; Vorführung: ein Screenshot geht an Claude |
| Übung | 30 Min. | Etappen 1 bis 5, allein oder mit deinem Peer. Richtwert: 3 · 3 · 9 · 10 · 5 Minuten |
| Auswertung | 10 Min. | Zwei, drei Präsentationen am Beamer: Erzählen die Titel allein die Geschichte? Was würde das externe Beiratsmitglied angreifen? |

## Vorher kurz einstellen

Claude-App, Reiter **Code**, Modell **Sonnet**, Ordner **`tag1`**. Neue Sitzung beginnen. Fehlen dir Ergebnisse
früherer Drills, lade zuerst den Zwischenstand (unten unter „Checkpoint“). Edge oder Chrome sollte installiert sein;
das ist auf den meisten Rechnern der Fall.

## Neu in Claude Code: Skills installieren und nutzen

| | |
|---|---|
| **Funktion** | Ein **Skill** ist ein Ordner mit einer Anleitung (`SKILL.md`) für eine bestimmte Art Aufgabe. In Drill 3 hast du selbst einen gebaut; hier **installierst du fertige von außen**: Im Ordner `folien-skills` liegen drei – `exhibit-stil` (Folien bauen und prüfen), `aktionstitel` (Titel und Storyline prüfen) und `circle-design` (gut aussehende HTML-Seiten). Installiert heißt: Sie liegen in `.claude/skills/` deines Projekts. |
| **Was dahinter passiert** | Claude liest am Anfang jeder Sitzung nur Name und Beschreibung jedes Skills, nicht die ganze Anleitung. Passt deine Aufgabe zu einer Beschreibung („Prüfe meine Titel“), lädt Claude die ganze `SKILL.md` und arbeitet nach ihren Regeln. Passt nichts, bleibt der Skill ungelesen und kostet nichts. Mit dem Namen kannst du ihn auch ausdrücklich verlangen („nach dem Skill aktionstitel“) oder direkt aufrufen (`/aktionstitel`). Der Ordner `.claude` ist geschützt: Die App fragt nach, bevor Claude dort etwas ablegt. |
| **Kleines Experiment** | In Etappe 1: erst fragen „Welche Skills kennst du?“, dann installieren lassen, dann noch einmal fragen. In Etappe 3: „Prüfe diese drei Titel“ – ohne den Skill zu nennen. Lädt Claude ihn von selbst? |
| **Woran du es erkennst** | Nach der Installation stehen die drei Namen in Claudes Antwort (oder in der Liste bei `/skills`). Bei der Arbeit meldet Claude, dass es einen Skill lädt, und urteilt mit dessen Regeln, etwa „Regel 1: Etikett, kein Verb“. Fehlen die Skills nach der Installation: neue Sitzung im Ordner `tag1` beginnen. |

## Neu in Claude Code: Bilder geben, Browser im Hintergrund

| | |
|---|---|
| **Funktion** | Du kannst Claude **Bilder** geben: einen Screenshot ins Eingabefeld einfügen (Windows: Win+Umschalt+S, dann Strg+V) oder hineinziehen. Claude sieht das Bild und prüft es. Claude kann außerdem **Edge oder Chrome im Hintergrund** starten, ohne Fenster: Es macht damit selbst Screenshots jeder Folie, liest den Prüfkasten aus und druckt das PDF. |
| **Was dahinter passiert** | Claude prüft eine Folie zweimal: im Quelltext (stimmt die Zahl, ist die Quelle da?) und im Bild (läuft etwas über, ist etwas unlesbar?). Was nur im Bild auffällt, findet es nur im Bild. Die Regeln der Stilfibel sind dabei die Leitplanke: Claude prüft gegen sie, nicht nach Geschmack. |
| **Kleines Experiment** | In Etappe 4: Mach selbst einen Screenshot deiner Inhaltsfolie und schick ihn mit „Prüfe diese Folie gegen die Regeln unserer Stilfibel. Nur urteilen, nichts ändern.“ |
| **Woran du es erkennst** | Claude beschreibt, was auf deinem Bild zu sehen ist, und nennt Regeln der Stilfibel. Beim PDF siehst du den Befehl, mit dem Claude den Browser im Hintergrund startet, und danach liegt die Datei in deinen Ergebnissen. |

## Dialog in fünf Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Folien-Skills installieren** | Zuerst: „Welche Skills kennst du?“ Dann: „Installiere die drei Folien-Skills aus dem Ordner folien-skills für dieses Projekt und zeig mir, dass du sie kennst.“ | Fragt die App, ob Claude in den geschützten Ordner `.claude` schreiben darf: Ja. Nennt Claude jetzt `exhibit-stil`, `aktionstitel` und `circle-design`, je mit einem Satz, wofür? Fehlen sie, neue Sitzung im Ordner `tag1` beginnen und noch einmal fragen. Öffne eine `SKILL.md` per Doppelklick und lies die Beschreibung oben: Bei welchen Wörtern greift der Skill? Die Skills selbst änderst du nicht. |
| **2 · Vorlage und Auftrag** | „Wir haben eine Vorlage im Exhibit-Stil für Präsentationen an den Beirat. Öffne sie im Browser und erklär mir nach dem Skill exhibit-stil in wenigen Sätzen: welche Folienarten es gibt, welche Regeln gelten, wie ich eine Folie dazunehme, wie der Prüfkasten arbeitet und wie daraus ein PDF wird. Ändere noch nichts.“ | Im Browser mit den Pfeiltasten blättern. Taste **S** drücken: Erscheinen die Sprechernotizen unter der Folie? Oben rechts steht ein roter Prüfkasten (anklicken klappt die Hinweise auf): Was meldet er bei der leeren Vorlage (Platzhalter, Beispieldaten)? Dann den Auftrag selbst lesen: „Zeig mir den Auftrag der Geschäftsführerin im Wortlaut, ohne Kommentar.“ Welche drei Fragen soll der Beirat beantwortet bekommen, und was darf **nicht** auf die Folien? |
| **3 · Deine Storyline** | Zuerst liest **du**, Claude schreibt hier nichts vor: deine Management-Summary, deinen Finanzkommentar, deine Entscheidungsvorlagen und, falls vorhanden, Birtes Beitrag zum Beiratsbericht. Öffnen per Doppelklick oder mit „Zeig mir meinen Finanzkommentar im Wortlaut.“ Dann schreibst **du** vier oder fünf Titel, je als ganzen Satz mit der Zahl, die ihn belegt, höchstens etwa 80 Zeichen, auf der Titelfolie etwa 70 (sonst bricht er in eine dritte Zeile um; ein Anhang mit Quellen zählt nicht mit): Titelfolie mit deiner Kernaussage, zwei bis drei Inhaltsfolien zu „Wo wachsen wir, wo verlieren wir?“ und „Wo verdienen wir Geld?“, eine Entscheidungsfolie mit höchstens drei Beschlüssen zu den Prioritäten 2027. Was die Beschlüsse trägt, darf aus allen Drills kommen: Nachfüll- und Projektgeschäft, Händlernetz, Abhängigkeit von großen Kunden und Einzelaufträgen, Preisdisziplin bei Angeboten, Kapazität von Anwendungstechnik und Notfallservice (ohne Personen). Dann schickst du: „Hier ist meine Storyline für den Beirat. Folie 1: … Folie 2: … · Zahl: … Folie 3: … · Zahl: … Folie 4: … · Beschlüsse: 1. … 2. … 3. … Diagramme (höchstens zwei) kommen auf Folie … Prüfe meine Titel nach dem Skill aktionstitel. Lass einen Subagenten unabhängig prüfen, ob jede Zahl in meinen Ergebnissen steht und mit den Tabellen übereinstimmt. Prüf selbst, ob meine Folien die drei Fragen der Geschäftsführerin beantworten. Sag mir je Folie ‚stimmt‘ oder was nicht stimmt und warum. Formuliere keinen Titel um und schlag keine eigene Storyline vor.“ | Hat Claude den Skill geladen und nennt es je Titel die Regel? Claudes Befund je Folie lesen; den Subagenten kennst du aus Drill 2. Selbst prüfen: Trägt jeder Titel eine Aussage mit Verb, nicht ein Etikett wie „Absatz 2026“? Spricht die Zahl über dieselbe Gruppe wie der Titel? Steht bei Finanzzahlen Ist oder Budget, und ist der Notfallservice ehrlich behandelt? Bei jedem Beschluss: Kann ein Beirat das beschließen (Auftrag, Freigabe, Berichtspflicht)? Was nicht stimmt, **korrigierst du selbst** und schickst nur die geänderten Zeilen. Zum Schluss die Titel laut lesen: Erzählen sie allein die Geschichte? |
| **4 · Die Folien** | „Bau die Präsentation jetzt nach dem Skill exhibit-stil und meiner geprüften Storyline als Kopie der Vorlage in meinen Ergebnissen. Meine Titel und Beschlüsse übernimmst du wörtlich; musst du einen ändern, weil er gegen eine Regel der Stilfibel verstößt, nenn mir danach jede Änderung. Die Diagramme zeichnest du auf den Folien, die ich gewählt habe, mit den echten Werten, bei Anteilen samt Zähler und Nenner. Jede Zahl bekommt ihre Quellenzeile, Quellen und Definitionen dürfen zusätzlich in einen Anhang. Mach danach mit Edge oder Chrome im Hintergrund einen Screenshot jeder Folie, sieh sie dir an, lies den Prüfkasten aus und behebe, was er meldet; nur den Hinweis auf fehlende Sprechernotizen lässt du bis Etappe 5 stehen. Öffne die Präsentation dann im Browser. Sprechernotizen und PDF machen wir danach.“ | Durchblättern. Stehen deine Titel so da, wie du sie geschrieben hast? Meldet der Prüfkasten noch etwas? Fahr mit der Maus über einen Punkt, der ein Anteil ist: Siehst du Zähler und Nenner? Dann das **Experiment** aus dem Kasten oben: Screenshot einer Folie an Claude, „Prüfe diese Folie gegen die Regeln unserer Stilfibel. Nur urteilen, nichts ändern.“ Dann die Rolle des externen Beiratsmitglieds einnehmen: „Unser externes Mitglied war lange Finanzchef in der Industrie. Welche Zahl würde er als schöngerechnet angreifen, und hält sie? Was antworte ich ihm, mit Zahl, und gehört ein Satz dazu auf die Folie? Ändere noch nichts, ich entscheide.“ |
| **5 · Notizen und PDF** | „Der Satz für das externe Mitglied kommt auf Folie … (oder: nur in die Notizen). Schreib dann zu jeder Folie Sprechernotizen für 15 Minuten Vortrag: Kernsatz, was ich zur Zahl sage, die Einschränkung, bevor jemand fragt, die Überleitung und die Zeit. Zeig mir die Zeiten je Folie und ihre Summe. Erstelle dann mit Edge oder Chrome im Hintergrund ein PDF mit einer Folie je Seite in meinen Ergebnissen, prüf es – so viele Seiten wie Folien, Diagramm sichtbar – und öffne es.“ | Taste **S** und eine Folie laut vortragen, eine Minute, nur mit den Notizen. Klingt das nach dir? Nur wenn nicht: „Kürze die Notizen zu Folie 2 auf vier Sätze, ich spreche frei.“ Das PDF öffnen: richtige Seitenzahl, Diagramm sichtbar, nichts abgeschnitten? Klappt das PDF nicht: in Edge oder Chrome **Drucken → Als PDF speichern**, Ränder „Keine“, Hintergrundgrafiken an. Zum Schluss **entscheiden**: Würdest du diesen Entwurf so an die Geschäftsführerin schicken? |

## Fertig, wenn

- deine Präsentation in deinen Ergebnissen liegt (`praesentation.html`), vier oder fünf Folien mit deinen Titeln,
  höchstens zwei Diagrammen aus echten Daten und einer Quellenzeile auf jeder Folie mit Zahl,
- der Prüfkasten nichts mehr meldet,
- jede Folie Sprechernotizen hat und die Zeiten 15 Minuten ergeben,
- das PDF in deinen Ergebnissen liegt, eine Folie je Seite,
- die drei Folien-Skills im Projekt installiert sind und Claude beim Prüfen und Bauen nach ihnen gearbeitet hat,
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
   behebe jeden Hinweis. Kürze zu lange Texte, verkleinere nie die Schrift, und lass Stil und Raster unverändert.“
3. **Kein PDF, oder das PDF hat leere oder zu viele Seiten?** Frag: „Erzeuge das PDF mit Edge oder Chrome im
   Hintergrund, wie es in der Stilfibel beschrieben ist, ohne etwas zu installieren.“ Klappt es nicht: selbst
   drucken (siehe Etappe 5). Weichen Zahlen von deiner Summary ab: „Rechne mir die Zahl auf Folie 2 vor: Zähler,
   Nenner, was nicht mitzählt.“

## Für Schnelle

Wähle **eines** davon.

- **Vertiefen: die Fragen des Vorsitzenden.** „Der Vorsitzende fragt, ob wir Kunden verlieren und wie abhängig wir
  von unseren größten Kunden sind. Beantworte beides mit unseren Tabellen: Kundenstatus aktiv, ruhend, verloren nach
  unserer Definition und Anteil der fünf größten Kunden am Umsatz 2025 und 2026, mit und ohne die Notfalllieferung.
  Gehört die Antwort auf eine Folie, in den Anhang oder nur in die Notizen?“ Du entscheidest.
- **Vorausbauen:** „Halte fest, wie wir heute vorgegangen sind – Auftrag lesen, meine Storyline gegen die Belege
  prüfen lassen, Vorlage füllen, Screenshots prüfen, Notizen, PDF –, als Skill ‚management-praesentation‘, damit ich
  die nächste Beiratsunterlage mit einem Satz beginnen kann. Ohne Zahlen und Titel von heute.“
- **Begleitseite im Circle Design:** „Mach aus meiner Präsentation eine Begleitseite für den Beirat als HTML-Seite
  in meinen Ergebnissen, nach dem Skill circle-design: Kernaussage, je Folie Titel und Beleg-Zahl mit Quelle, die
  Beschlüsse. Keine neuen Aussagen. Zeig sie mir hell und dunkel.“ Die Präsentation bleibt im Exhibit-Stil, die
  Begleitseite ist eine Webseite.

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
