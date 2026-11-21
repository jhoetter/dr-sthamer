# Drill 3 · Angebote mit Assistenz

Tag 1 „AI Augmentation“, Mittwoch, 25.11.2026. Zeitbox 60 Minuten: 15 Einführung · 35 Übung · 10 Auswertung.

> **Du startest mit** deinem Dashboard (Reiter „Überblick“, „Umstellung“ und „Finanzen“) und dem Finanzkommentar aus Drill 2.
> Die DB-Marge der fluorfreien Produkte brauchst du in Etappe 2 für die Ausschreibung.

## Deine Rolle

Du bist Mathis Grevenbroich, Leiter Angebotsmanagement (Tender Desk) im Vertriebsbüro Süd von Dr. Sthamer. Seit
einem Jahr rechnet ein Angebotsassistent im ERP Rabatte und Angebotsklassen vor. Auf deinem Tisch liegen vier
Vorgänge: ein Angebot vom Juli 2026, zu dem der Kunde fragt, ob „ein System“ seinen Rabatt berechnet hat; eine
Ausschreibung für einen Rahmenvertrag über drei Jahre; eine Anfrage aus Norwegen auf Englisch, mit Garantie und
einer Bestätigung, die du nicht geben darfst; und eine Nachbestellung, wie sie jeden Tag kommt. Die Geschäftsführung
will für den Beirat wissen, ob wir bei Angeboten preisdiszipliniert sind.

## Lernziel

Du lässt Claude eine Richtlinie lesen und Anfragen danach prüfen, mit fester Gliederung und einem Paragrafen für
jede Bewertung. Du erkennst, wo die Richtlinie eine Spanne lässt oder ein Mensch entscheiden muss, und triffst
selbst eine Wahl. Du hältst dein Vorgehen als eigenen Skill fest, der in einer neuen Sitzung von selbst greift.

## Mission

Erstelle für drei Vorgänge eine Entscheidungsvorlage nach unserer Angebots- und Freigaberichtlinie und ergänze
dein Dashboard um den Reiter „Angebote“ mit dem Regelpfad jedes Vorgangs. Baue dann den Skill „angebotsvorlage“
und teste ihn in einer neuen Sitzung mit einem Satz am vierten Vorgang.

## Zeitbox

| Teil | Dauer | Was passiert |
|---|---|---|
| Einführung | 15 Min. | Die Richtlinie in drei Minuten; was ein Skill ist und wann Claude ihn lädt; Vorführung: ein Skill greift in einer neuen Sitzung |
| Übung | 35 Min. | Etappen 1 bis 3, allein oder mit deinem Peer. Richtwert: 8 · 17 · 10 Minuten. Der Kundenbrief ist eine Zusatzaufgabe |
| Auswertung | 10 Min. | Welcher Fall war der heikelste? Wo hat der Angebotsassistent falsch gerechnet? Wo entscheidet ein Mensch, und hat euer Skill gegriffen? |

## Vorher kurz einstellen

Claude-App, Reiter **Code**, Modell **Sonnet**, Ordner **`tag1`**. Neue Sitzung beginnen. Fehlen dir die
Ergebnisse aus Drill 2, lade zuerst den Zwischenstand (unten unter „Checkpoint“). Für Etappe 3 brauchst du eine
zweite, neue Sitzung im selben Ordner.

## Neu in Claude Code: Skills

| | |
|---|---|
| **Funktion** | Ein **Skill** ist eine Arbeitsanleitung, die du Claude einmal gibst: eine Datei `SKILL.md` in einem eigenen Ordner unter `.claude/skills/`. Oben steht eine Beschreibung, wann der Skill gilt, darunter die Schritte. Du kannst ihn auch direkt aufrufen, mit `/angebotsvorlage`. |
| **Was dahinter passiert** | Claude liest beim Start nur die Beschreibungen aller Skills. Passt deine Bitte zu einer Beschreibung, lädt es den ganzen Skill und arbeitet danach. Darum entscheidet die Beschreibung, ob der Skill von selbst greift. Anders als das Projektgedächtnis `CLAUDE.md` gilt ein Skill nur für seine Aufgabe. |
| **Kleines Experiment** | In der neuen Sitzung zuerst „Welche Skills kennst du in diesem Ordner?“ fragen, dann den Test aus Etappe 3. |
| **Woran du es erkennst** | Claude zeigt an, dass es den Skill „angebotsvorlage“ benutzt, und die neue Vorlage hat dieselbe Gliederung wie deine drei ersten. |

## Dialog in drei Etappen

Schreib nicht alle Fragen auf einmal. Nach jeder Antwort prüfst oder entscheidest **du** etwas, bevor es
weitergeht.

| Etappe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **1 · Regeln und Anfragen** | „Ich leite das Angebotsmanagement. Lies unsere Angebots- und Freigaberichtlinie und die Kompetenzordnung vollständig. Erkläre mir in höchstens zehn Sätzen, jeder mit Paragraf, wie ein Angebot geprüft wird: welcher Prüfumfang bei welchem Auftragswert, wie Rabatte zusammenkommen, wann eine Datenaufnahme der Anlage nötig ist, wie aus Punkten eine Angebotsklasse wird und wer entscheidet, ein System oder ein Mensch. Stell mir dann die vier Vorgänge aus dem Angebotseingang in einer Tabelle nebeneinander: Kunde, worum es geht, Datum, Produkt und Menge, Währung und was beiliegt. Noch keine Bewertung und keine Webseite.“ | Prüfen: Kommen Rabattstaffel, Prüfumfang, Angebotsklasse und Kompetenz vor, je mit Paragraf? Selbst nachlesen: „Zeig mir die Punktetabelle für die Angebotsklasse im Wortlaut.“ Steht bei jedem Vorgang, was **wirklich** beiliegt und was nur erwähnt ist? **Entscheiden:** Welcher Vorgang ist für dich der heikelste, und worauf willst du bei ihm achten? |
| **2 · Vorlagen und Reiter** | „Erstelle für A-01, A-02 und A-03 je eine Entscheidungsvorlage nach unserer Richtlinie, jede als eigene Datei in meinen Ergebnissen, mit genau diesen Abschnitten: Vorgang in Kürze; Stand-Datum und welche Preisliste und Richtlinie gelten; vorliegende und nur erwähnte Unterlagen; Preisrechnung Schritt für Schritt (Listenpreis, jeder Rabatt mit Paragraf, Auftragswert in EUR); Prüfumfang und Datenaufnahme; Angebotsklasse mit Punkten; wer entscheidet, System oder Mensch; Empfehlung; offene Rückfragen; was nicht in die Entscheidung einfließen darf. Lässt die Richtlinie eine Spanne oder muss ein Mensch wählen, nenne die Möglichkeiten, schlag eine vor, begründe sie und markiere die Wahl als offen, bis ich entscheide. Prüfe bei A-01, was der Angebotsassistent damals gerechnet hat, gegen die Richtlinie zum Angebotsdatum. Bei A-02: Trägt die DB-Marge der fluorfreien Produkte aus meinem Finanzkommentar den verlangten Rabatt? Rechne die Marge des Angebots mit den Herstellkosten des Produkts, vor und nach Fracht, und sag, was dabei fehlt. Noch kein Dashboard.“ **Sobald die Vorlagen da sind, als zweite Nachricht:** „Ergänze mein Dashboard um den Reiter ‚Angebote‘, im Circle Design wie die anderen Reiter: links die Vorgänge mit Auftragswert, Klasse und Empfehlung; ein Klick zeigt rechts den Regelpfad vom Prüfumfang bis zur Kompetenz, jeder Schritt mit Paragraf und Ergebnis, der Schritt, an dem ein Mensch entscheiden muss, rot markiert als Zustands-Pille mit Form und dem Wort ‚Hier entscheidet ein Mensch‘, darunter die ganze Vorlage. Die anderen Reiter bleiben unverändert. Öffne das Dashboard zum Schluss.“ | Claude braucht für die Vorlagen rund zehn Minuten und führt dabei eine Aufgabenliste, an der du den Fortschritt siehst. Lies die Vorlage zu A-01 ganz; bei A-02 und A-03 genügen Angebotsklasse, wer entscheidet und Empfehlung. Mit Peer: Teilt euch die Vorgänge. Schick den Reiter erst, wenn du den Vorlagen traust. Einen Rabatt selbst nachrechnen: Passt er zur Staffel, gilt die richtige Preisliste? Nachhaken, wo es hakt, etwa: „Darf der Projektrabatt bei A-01 zweimal gewährt werden?“ oder „Spielt bei A-03 eine Rolle, dass der Kunde aus Norwegen kommt?“ Im Browser alle drei Vorgänge anklicken: Ist bei jedem die rote Markierung „Hier entscheidet ein Mensch“ da? **Entscheiden** (eine Frage genügt): Hältst du bei A-01 den alten Preis, oder machst du ein neues Angebot? Oder: Gibst du A-02 an die Geschäftsführung mit dem verlangten Rabatt oder mit einem anderen? Sag es Claude: „Übernimm meine Entscheidung … in Vorlage und Reiter, mit Vermerk ‚entschieden durch mich‘ an genau dieser Wahl. Bleibt die Freigabe nach der Kompetenzordnung bei einer anderen Stelle, steht sie weiter unter ‚wer entscheidet‘. Lösche jeden Satz, der ihr jetzt widerspricht, ganz und zeig mir die Stelle.“ |
| **3 · Dein Skill** | „Halte fest, wie bei uns eine gute Entscheidungsvorlage für ein Angebot entsteht, als Skill ‚angebotsvorlage‘ in diesem Projekt, den du künftig von selbst benutzt, sobald jemand eine Entscheidungsvorlage, eine Angebotsprüfung oder ein Kundenschreiben zu einer Anfrage verlangt. Hinein gehören: welche Quellen du liest; die Prüfschritte in fester Reihenfolge mit Paragrafen; welche Preisliste nach welchem Datum gilt; wie Rabatte zusammenkommen und was nicht zusammenkommt; wann eine Datenaufnahme Pflicht ist; wer entscheiden darf; was nie in eine Entscheidung einfließt; was nie in ein Kundenschreiben gehört; die Gliederung der Vorlage und wo sie abgelegt wird; dass jeder neue Vorgang im Reiter ‚Angebote‘ dazukommt. Nimm auf, was ich heute entschieden und korrigiert habe, aber als allgemeine Regel für jede künftige Anfrage, ohne Namen, Beträge oder Ergebnisse unserer drei Vorgänge. Erkläre mir den Skill danach in einfachen Worten.“ | Den Skill überfliegen, vor allem die Rabattregeln und wer entscheidet: Fehlt eine Regel, die dir wichtig ist? Eine selbst ergänzen lassen, zum Beispiel: „Jede Vorlage endet mit der Zeile ‚Entscheid durch: …, Datum: …‘. Dort steht nur dann ein Name, wenn ein Mensch selbst entschieden hat, sonst ‚offen‘.“ Dann eine **neue Sitzung** im Ordner `tag1` beginnen und nur einen Satz schreiben: „Entscheidungsvorlage für die Nachbestellung A-04.“ Prüfen: Zeigt Claude an, dass es den Skill benutzt? Hat die Vorlage dieselbe Gliederung? Steht A-04 im Reiter? Liegt der Auftragswert unter oder über einer Grenze der Richtlinie, und was zählt zum Auftragswert? **Entscheiden:** Darf ein Vorgang wie dieser künftig automatisch rausgehen? |

## Fertig, wenn

- drei Entscheidungsvorlagen in deinen Ergebnissen liegen, jede mit Paragrafen, Auftragswert, Klasse, Kompetenz
  und Empfehlung, und du bei mindestens einer selbst entschieden hast (Vermerk „entschieden durch mich“),
- der Reiter „Angebote“ im Browser öffnet, ein Klick den Regelpfad mit der roten Markierung „Hier entscheidet ein
  Mensch“ zeigt und die anderen drei Reiter weiter funktionieren,
- du weißt, ob die Marge der fluorfreien Produkte den Rabatt der Ausschreibung trägt,
- dein Skill „angebotsvorlage“ angelegt ist und in einer neuen Sitzung aus einem Satz die Vorlage für A-04
  entstanden ist.

## Hinweise, nacheinander

Nimm den nächsten Hinweis erst, wenn du ihn brauchst.

1. **Claude findet die Vorgänge nicht oder vermischt sie?** Sag: „Die vier Vorgänge liegen im Angebotseingang, die
   Übersicht steht in dessen README.“ **Fehlen Klasse oder Kompetenz?** Frag: „Lies die Paragrafen zur
   Angebotsklasse und zur Kompetenz noch einmal ganz und zeig mir, wo sie bei unseren drei Vorgängen greifen.“
2. **Rabatt oder Auftragswert wirken falsch?** Frag: „Rechne noch einmal vor: Preisliste nach Angebotsdatum, nur
   der höchste Mengenrabatt, Projektrabatt einmal je Angebot, Fracht und Zuschläge nicht im Auftragswert,
   Fremdwährung zum Kurs aus unseren Kennzahlen.“ **Ein Klick im Reiter zeigt nichts?** Frag: „Nimm Regelpfad und
   Volltext der Vorlagen in die Daten des Reiters auf, damit das Dashboard ohne Server läuft.“
3. **Der Skill greift in der neuen Sitzung nicht?** Schreib `/angebotsvorlage A-04` oder frag: „Welche Skills
   kennst du hier, und warum hast du meinen nicht benutzt?“ Meist ist die Beschreibung zu eng; lass sie in der
   ersten Sitzung erweitern. Ist ein Reiter kaputt: „Baue den Reiter ‚Angebote‘ neu, lass die anderen unverändert.“

## Für Schnelle

**Zusatzaufgabe zuerst: Antwort an die Reederei.** Mach sie, wenn dein Skill steht.

| Zusatzaufgabe | Du schreibst Claude | Dann prüfst du |
|---|---|---|
| **Zusatz · Brief zu A-01** | „Der Kunde in A-01 fragt, ob ein System seinen Rabatt berechnet hat. Entwirf die Antwort als Brief, wie sie heute rausgehen sollte: seine Fragen der Reihe nach beantwortet; ehrlich, wie das Angebot entstanden ist und von wem; was jetzt gilt. Halte die Regel zur Kundenkommunikation unserer Richtlinie ein: keine Angebotsklasse, keine Marge, keine Bonität, keine Rechtsauskunft. Höchstens eine Seite. Prüfe den Entwurf dann Satz für Satz gegen diese Regel und zeig mir die Prüfung als Tabelle.“ | Den Brief lesen, als wärst du der Kunde: Ist die Frage nach dem System klar beantwortet? Steht irgendwo eine Klasse, Marge oder Bonität? Mindestens einen Satz selbst ändern lassen. **Entscheiden:** Wer unterschreibt? |

Danach, wenn noch Zeit bleibt, **eines** von beiden:

- **Vertiefen:** Frag deinen Skill in einer neuen Sitzung nach einem Fall, der ihn fordert: „Entscheidungsvorlage
  für A-03, diesmal mit doppelter Menge.“ Ändert sich die Klasse, ändert sich, wer entscheidet?
- **Vorausbauen (Drill 4):** Lade Obsidian von **obsidian.md** herunter und installiere es, falls du darfst. Frag
  dann: „Im Ordner liegt das Notizbuch von Birte Lohmeyer. Sag mir den vollständigen Ordnerpfad, damit ich es in
  Obsidian öffnen kann, und wie viele Notizen es hat. Noch keine neue Notiz.“

## Drei Arbeitsweisen

| Weg | Wenn du … | So bittest du Claude |
|---|---|---|
| Geführt | lieber Schritt für Schritt vorgehst | „Erkläre mir jeden Prüfschritt, bevor du ihn machst, und warte auf mein Okay.“ Für Etappe 2: „Mach erst nur die Vorlage zu A-01 und zeig sie mir.“ |
| Bauend | die Etappen zügig schaffst | Eigene Regeln in den Skill aufnehmen; jede Bewertung mit Paragraf. |
| Vorausbauend | vor der Zeit fertig bist | Eine Aufgabe aus „Für Schnelle“; das Ergebnis ist ein Vorsprung, kein Muss. |

## Checkpoint

Fehlen dir die Ergebnisse aus Drill 2? Sag „Ich möchte mit Drill 3 weitermachen“. Claude lädt dann den
Zwischenstand mit den Ergebnissen von Drill 0 bis 2 (Dashboard mit „Überblick“, „Umstellung“ und „Finanzen“,
Summary, Finanzkommentar).

> **Das brauchst du in Drill 4:** die Erfahrung mit deinem Skill. In Drill 4 nutzt du die Vorlage für das
> Jahresgespräch genauso verbindlich wie die Gliederung deiner Entscheidungsvorlagen, auf Wunsch wieder als Skill.
> Deine Zahlen zur Preisdisziplin brauchst du in Drill 5 für den Beirat.

Alle Personen, Firmen und Zahlen bei Dr. Sthamer sind erfunden. Verwende keine echten Kundendaten.
