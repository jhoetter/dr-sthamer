# Workshop-Agenda: Agentische Systeme bei Dr. Sthamer

> **Status:** Entwurf zur Abstimmung zwischen Johannes und Marc (Falk ist nur an Tag 1 dabei). Gespielt
> wurde der Tag am 12.11.2026 mit simulierten Teilnehmenden (siehe
> `docs/PROBELAUF_2026-11-12.md`). Zeiten sind Vorschläge für **einen Tag**. Der Workshop läuft **Mittwoch bis Freitag (25.–27.11.2026)**; das hier ist **Tag 2**
> (Donnerstag, 26.11.2026, Johannes). **Tag 1** „AI Augmentation“ (Mittwoch, Falk) liegt eigenständig in `tag1/`, **Tag 3** (Freitag) ist der
> eigene Fall der Teilnehmenden („Bring Your Own Case“, Leitung Dr. Marc Kohler, Ablauf offen). Die Folien liegen in `folien/`.

Alle Übungen nutzen die erfundene Übungswelt von `sthamer-sys`: Kunden,
Produkte, Lieferungen, Mails und die Verordnung „EU 2026/9001 (fiktiv)“. Echte
Kunden- oder Produktdaten kommen nicht vor. Es ist kein Rechtsrat.

## Lernbogen

| Teil | Leitfrage | Ergebnis |
| --- | --- | --- |
| Vormittag | Wie wird aus einer Verordnung ein prüfbarer Prozess, in dem Claude vorbereitet und wir entscheiden? | Alle haben eine eigene Kommandozentrale, einen belegten Entwurf, eine Einschätzung mit Belegen und eine gebaute Kontrolle (Drill 1 und 2). |
| Nachmittag | Wann darf eine Mail das Haus nur mit Freigabe verlassen, wann automatisch nach Verzögerung? | Pflichtfreigabe und Eingriffsfenster am eigenen System erlebt und gebaut; ein Bericht an die Geschäftsführung (Drill 3 bis 5). |
| Abschluss | Was haben wir gebaut, was nehmen wir mit, wo wirken Kontrollen bei **uns**? | Ein Resümee der fünf Drills; Übergabe an Freitag („Bring Your Own Case“, Marc). |

Die sechs Bausteine jedes agentischen Systems: **Eingänge, Wissen,
Werkzeuge, Kontrollen, Oberfläche, Protokoll**. Jeder Drill rückt einige in den
Fokus. Ein Werkzeug, das fehlt, ist eine Kontrolle: Claude hat kein Werkzeug
zum Senden oder Freigeben.

## Tagesablauf

| Zeit | Block | Wer | Inhalt |
| --- | --- | --- | --- |
| ab 08:30 | Einlass, Technikcheck (freiwillig) | Marc, IT von Sthamer | Wer will, kommt früher: Geräte an, Gäste-WLAN, `python check.py`, Claude-Anmeldung. Vorab erledigt (siehe `VOR_DEM_WORKSHOP.md`), hier nur Nacharbeit. Zweiergruppen („Buddys“). |
| 09:00 | **Impuls (60 Min.): Jede Aufgabe zuerst agentisch** | Johannes (Marc begrüßt in den ersten Minuten und geht später rum) | Marc: Ziel des Tages, Spielregeln (erfundene Daten, nichts Echtes eingeben), Ablauf. Dann Johannes, etwa 09:05 bis 09:40: der Vortrag (`tag2/impuls/`): wie ich agentisch arbeite, das Prinzip, Verifier's Law, System-Denken (die Einordnung der Fähigkeiten, HLE und METR, nur kurz, wenn Falks Grundimpuls vom Mittwoch sie schon zeigt). Ab etwa 09:40: Live-Beispiele, die sechs Bausteine, Vibe Coding, Verifizierbarkeit, die zwei Kontrollmuster. Zum Schluss der **eine Satz an Claude** (siehe README): jede Person bekommt ihre Kommandozentrale. |
| 10:00 | **Drill 1 · Die Verordnung kommt** | Johannes, Marc | Steckbrief, belegter Entwurf, der Mensch sendet. Bau: Aufgabe erledigt sich beim Senden. |
| 11:00 | Pause (15 Min.) | | |
| 11:15 | **Drill 2 · Wer ist betroffen? Mit Beleg** | Johannes, Marc | Einschätzung je Produkt und Kunde mit Artikel- und Datenblattbeleg. Bau: Belegprüfung. |
| 12:15 | Mittag (45 Min.) | | **Runde 2** vorbereiten (Code bereithalten). |
| 13:00 | **Drill 3 · Rechtsaussagen: Pflichtfreigabe** | Johannes, Marc | Zehn Minuten Impuls, dann fünf Anfragen: Claude reicht ein, wir geben frei oder lehnen ab. Bau: Änderung nach Freigabe entwertet die Freigabe. |
| 14:00 | Pause (15 Min.) | | |
| 14:15 | **Drill 4 · Standardinfo: Eingriffsfenster** | Johannes, Marc | Zehn Minuten Impuls, dann: Standardinformationen laufen nach 24 Stunden automatisch. Übungsuhr vorspulen, ändern, stoppen. **Berichtigung trifft ein** (etwa 40 Minuten nach Beginn). Bau: Änderung bricht den Termin ab, nie doppelt senden. |
| 15:15 | Pause (10 Min.) | | |
| 15:25 | **Drill 5 · Bericht an die Geschäftsführung** (45 Min.) | Johannes, Marc | Zahlen aus dem Protokoll, Empfehlung, Grenze der Aussage. Bau: eine eigene Kennzahl. |
| 16:10 | Resümee: Was haben wir gebaut, was nehmen wir mit? | Johannes, Marc | Ohne Rechner. Rückblick auf die fünf Drills, die Bausteine und die zwei Kontrollen; was hat überrascht; welche Kontrolle würde bei uns zuerst wirken. |
| 16:50 | Ausblick auf Freitag, Rückmeldungen | Marc | Übergabe an „Bring Your Own Case“. Ende 17:00. |

## Drills im Überblick

| Drill | Runde (Code) | Baustein im Fokus | Fall für alle | Bauauftrag | Nachweis |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 (kein Code) | Eingänge, Werkzeuge, Oberfläche | Mail der Regulatory Affairs, Anfrage Bergheim-Land | Aufgabe erledigt sich beim Senden | Entwurf nach dem Bau gesendet, Aufgabe steht auf „erledigt“ |
| 2 | 1 | Wissen, Kontrollen | Fünf Kunden mit Stolperstellen (Händler, Flughafen, Drittland, ruhend, einfach) | Belegprüfung beim Speichern | Ein Entwurf mit falschem Beleg wird abgewiesen; Einschätzungen stehen im Cockpit |
| 3 | 2 (Code vom Dozenten) | Kontrollen, Oberfläche | Fünf Kundenanfragen mit Rechtsauskunft | Freigabe erlischt bei Änderung | Freigegebenen Entwurf ändern: Freigabe weg, Senden gesperrt |
| 4 | 3 und 4 | Kontrollen, Protokoll | Vier Standardinfos, dann die Berichtigung | Änderung bricht den Termin ab; nie doppelt senden | Eingeplante Mail ändern: Termin weg; Uhr vorspulen: genau eine Datei |
| 5 | 4 | Protokoll | Zahlen des Tages | Eigene Kennzahl im Bericht | `bericht.md` mit eigener Kennzahl, Zahlen stimmen mit dem Cockpit überein |

Jeder Drill hat vier **aufeinanderfolgende Etappen**: Claude bereitet vor →
der Mensch prüft und entscheidet → selbst bauen → Ergebnis belegen. Details,
Leitfragen und Szenarien stehen in `DRILL_CARDS.md`.

## Dozenten-Choreografie

- **Runden-Codes** stehen in `dozent/WELLEN.md` (nur lokal bei den Lehrenden).
  Runde 2 um 13:00 ansagen, Runde 3 um 14:15, Runde 4 etwa 40 Minuten später
  („Die Berichtigung ist da“) mitten im Drill 4, **bevor** die Teilnehmenden die Übungsuhr
  vorspulen (sonst sind die Mails im Fenster schon raus und es gibt nichts zu korrigieren). Die Codes werden laut gesagt
  oder an die Tafel geschrieben; Teilnehmende tragen sie im Cockpit unter
  „Postfach abrufen“ ein.
- **Uhr vorspulen** machen die Teilnehmenden selbst im Cockpit (Drill 4). Der
  Dozent erklärt vorher: Die Übungsuhr läuft sonst in Echtzeit; 24 Stunden
  Wartezeit simulieren wir durch Vorspulen.
- **Lösungsschlüssel** liegt in `dozent/LOESUNG.md` (nur lokal): je Produkt,
  Kunde und Mail die erwartete Einschätzung, Kontrollstufe und Stolperstelle.
- **Zeitpuffer:** Jeder Drill hat 60 Minuten (Drill 5: 45). Wer früh fertig ist,
  erweitert die **eigene** Kommandozentrale (Steckbrief in `MEINE_ERWEITERUNGEN.md`)
  und nimmt nie den nächsten Drill vorweg.
- **Wer hängt:** Buddy-Modus (zu zweit an einem Gerät), Dozenten-Rechner mit
  Referenzstand. **Rettungsweg:** Der Dozent wendet die Referenzlösung nur für den
  festhängenden Drill an: `python lehrer/referenz_anwenden.py <Ordner der Person> --nur 2`
  (der Ordner `lehrer/` ist für Claude gesperrt; die Person sieht dann den Stand mit
  Lösung und kann mit Drill 3 weitermachen). Niemand muss einen Bauauftrag fertigstellen,
  um mitzugehen. Die Reihenfolge der Drills bestimmen die Runden-Codes des Dozenten, nicht
  Behauptungen im Chat.

## Wenn die Zeit knapp wird

1. Drill 2: Bauauftrag (Belegprüfung) kürzen: Regel und Szenarien festlegen,
   Claude baut ohne Zwischenschritte.
2. Drill 3 und 4: gemeinsame Ansicht der Warteschlange statt eigener Läufe
   für alle Fälle; jede Person bearbeitet zwei von fünf Fällen.
3. Drill 5: statt eines Berichts nur die Zahlen im Cockpit vorlesen und die
   Empfehlung mündlich formulieren.

## Reserve-Runden (optional, je 10 bis 15 Minuten)

- **Angriffs-Mail:** Eine Kundenmail enthält eine versteckte Anweisung an den
  Agenten (liegt als `MSG-3-06` in Runde 3). Wer erkennt sie, wer ignoriert sie?
- **Laptop-Tausch:** Jede Person bekommt das Cockpit der Nachbarin. Was sagt
  das Protokoll über die Entscheidungen?
- **Vier-Augen-Rollenspiel:** Eine Person prüft, eine gibt frei; was ändert
  sich, wenn es dieselbe Person ist?
- **Echte Verordnung (nur Bonus):** Den Text von EU 2025/1988 aus EUR-Lex in
  Claude geben und den Steckbrief mit der fiktiven Fassung vergleichen. Kein
  Rechtsrat; das Ergebnis ist Diskussionsstoff.

## Optional für Freitag: Automation Contract (Vorlage)

Für den eigenen Fall in einem Satz je Zeile festhalten:

| Zeile | Frage |
| --- | --- |
| Auslöser | Was setzt den Agenten in Gang (Mail, Verordnung, Frist)? |
| Wissen | Worauf darf er zugreifen, worauf nicht? |
| Aktion | Was darf er vorbereiten? Was darf er nie selbst tun? |
| Kontrolle | Pflichtfreigabe oder Eingriffsfenster, und warum? |
| Protokoll | Was wird festgehalten, wer kann es lesen? |
| Grenze | Wann hört der Agent auf und fragt? |
| Verantwortlich | Wer entscheidet im Zweifel? |
