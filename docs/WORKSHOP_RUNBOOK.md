# Runbook für die Lehrenden

Das ist die operative Quelle für Johannes am Workshop-Tag (Donnerstag). Lernbogen und Zeiten stehen in
[WORKSHOP_AGENDA.md](WORKSHOP_AGENDA.md), die Etappen und Szenarien je Drill in [DRILL_CARDS.md](DRILL_CARDS.md),
die Installation für Teilnehmende in [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) und [INSTALL_MAC.md](INSTALL_MAC.md),
das, was die IT von Sthamer vorbereiten muss, in [IT_VORAB.md](IT_VORAB.md).

## Was nur bei den Lehrenden liegt (nie im Repo, nie bei Claude)

| Datei | Inhalt |
| --- | --- |
| `dozent/WELLEN.md` | Codes für Runde 2 bis 4 (Taktgeber, kein Geheimnis: die Codes sind kurze Wörter) |
| `dozent/LOESUNG.md`, `dozent/loesung.json` | Lösungsschlüssel: je Produkt, Kunde und Mail die erwartete Einschätzung, Kontrollstufe und Stolperstelle |
| `lehrer/` (liegt im Repo, ist für Claude gesperrt) | Referenzlösungen, Simulation von Cockpit-Klicks, Absicherungstest |

`dozent/` ist Git-ignoriert und entsteht mit `python scripts/make_data.py --loesung` neu. Codes ändern: Hash in `data/wellen.json`
(SHA-256 des Codes in Kleinbuchstaben) und `dozent/WELLEN.md` anpassen.

## Vor dem Tag

1. **Generalprobe** auf einem echten Sthamer-Gastgerät (Windows und der eine Mac): Installation nach Anleitung, `python check.py`,
   Claude-Anmeldung, Erststart, ein Durchlauf von Drill 1. Offene Punkte: [PLAN.md](PLAN.md), Abschnitt 8a.
2. **Repo erreichbar machen:** Teilnehmende haben kein GitHub-Konto. Das Repo öffentlich stellen (spätestens am Vortag, vorher
   Logo und Zeichen von Sthamer freigeben lassen) oder die ZIP-Datei verteilen ([OFFLINE_PAKET.md](OFFLINE_PAKET.md)).
3. **Claude-Konten:** Alle haben Claude Pro, haben sich einmal angemeldet und die Rückfragen „Ordner vertrauen“ und „Werkzeug
   sthamer erlauben“ gesehen ([VOR_DEM_WORKSHOP.md](VOR_DEM_WORKSHOP.md)).
4. Tests laufen lassen: `python -m unittest discover -s tests` und `python -m unittest discover -s lehrer` (beides muss grün sein).
5. Das ITMP-SG-Logo als `web/logo-itmp.svg` ablegen (erscheint dann links unten im Cockpit).

## Am Tag

- **Runden abrufen:** Die Teilnehmenden tragen den Code im Cockpit ein („Postfach abrufen“). Runde 2 zu Drill 3, Runde 3 zu Drill 4.
  **Runde 4 (Berichtigung) in Drill 4, nachdem die Teilnehmenden Mails im Fenster geändert und gestoppt haben, aber bevor sie
  die Übungsuhr vorspulen.** Sonst sind die Mails schon raus und es gibt nichts zu korrigieren.
- **Wer festhängt:** Buddy-Modus. **Rettungsweg:** die Referenzlösung nur für den hängenden Drill auf die Kopie der Person anwenden:

  ```
  python lehrer/referenz_anwenden.py <Ordner der Person> --nur 2
  ```

  Danach läuft das System in der Kopie mit dem Bau dieses Drills; die Person macht mit Drill 3 weiter. Das lädt sich selbst nach,
  es muss nichts neu gestartet werden.
- **Bauauftrag prüfen:** `python scripts/akzeptanz.py <1-5>` im Ordner der Person (meldet BESTANDEN oder NICHT BESTANDEN je Szenario).
- **Eine Person braucht zurück auf Anfang:** `python sthamer.py reset --yes` löscht nur Fälle, Entwürfe und Postausgang (nicht den Code).
- **Claude hat keine Tokens mehr:** Drill-Karte, Browser und Buddy-Modus; nie Konten teilen.
- **Die Übungsuhr** spulen die Teilnehmenden selbst im Cockpit vor (Chip oben rechts, ab Runde 3).

## Was Claude darf und was nicht (zum Erklären am Whiteboard)

| Claude kann | Der Mensch im Cockpit | Technisch gesperrt für Claude |
| --- | --- | --- |
| lesen (Eingang, Verordnung, Produkte, Kunden), Fälle anlegen, Entwürfe schreiben und überarbeiten, Einschätzungen festhalten, **einreichen**, geplante Mails **stoppen**, Berichtsdaten lesen | **senden, freigeben, ablehnen**, Übungsuhr vorspulen, weitere Runden abrufen, eingereichte Entwürfe zurückholen | Menschen-Aktionen laufen nur im Cockpit-Prozess; Python-Skripte aus der Kommandozentrale, Datenbank, Prozesse beenden und Dateien in `data/`, `lehrer/` sind gesperrt; eingereichte Entwürfe ändert das Werkzeug nicht |

Die Sperren sind für den Workshop gebaut (sie verhindern den versehentlichen Abkürzer und machen jeden Umweg sichtbar), keine
Sicherheitsgrenze gegen jemanden, der den Code absichtlich ändert. Siehe [PROBELAUF_2026-11-12.md](PROBELAUF_2026-11-12.md).

## Wenn etwas hakt

| Symptom | Ursache und Abhilfe |
| --- | --- |
| Claude hat keine Werkzeuge | Beim ersten Start fehlen sie (Verbindung wird erst eingerichtet): neue Sitzung im selben Ordner, „weiter mit Drill N“; die Rückfragen mit Ja beantworten |
| Cockpit zeigt Änderung nicht | Änderungen laden sich selbst nach; Seite im Browser neu laden. Meldet der Status `code_fehler`, hat der neue Code einen Tippfehler (der alte bleibt aktiv) |
| Port 3005 belegt | `serve` sucht selbst einen freien Port (3006 …) und schreibt ihn in die Konsole |
| `python3` öffnet den Microsoft Store (Windows) | `python` oder `py -3` nehmen ([INSTALL_WINDOWS.md](INSTALL_WINDOWS.md), Fehlerbehebung) |
| GitHub nicht erreichbar | ZIP-Weg ([OFFLINE_PAKET.md](OFFLINE_PAKET.md)) |
