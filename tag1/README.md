# Tag 1 „AI Augmentation“ – Arbeitsstand für Teilnehmende

Material für Tag 1 eines zweitägigen AI-Bootcamps an der Übungsfirma Dr. Sthamer (fiktive Daten). Tag 2 („Agentische Systeme“) arbeitet im übergeordneten Repository; dieser Ordner ist davon unabhängig.

**Einstieg für Teilnehmende:** [START.md](START.md). Claude liest zusätzlich die Datei [CLAUDE.md](CLAUDE.md).

## So öffnen

- Die Claude-App (Reiter „Code“) **im Ordner `tag1` selbst** öffnen, nicht im Repository darüber. Nur dann gelten `tag1/CLAUDE.md` und `tag1/.claude/settings.json`.
- Laden (Drill 0, Etappe 1): Standard ist, dass Claude in einer Sitzung im Benutzerordner das Repository nach `%USERPROFILE%\dr-sthamer` klont („Klone https://github.com/jhoetter/dr-sthamer in den Ordner dr-sthamer in meinem Benutzerordner und öffne den Ordner tag1“); Rückfall ohne Git: „Code → Download ZIP“ und nach `%USERPROFILE%\dr-sthamer` entpacken (nicht OneDrive, nicht Desktop). Danach eine neue Sitzung im Unterordner `tag1`. Das Repository ist öffentlich: `https://github.com/jhoetter/dr-sthamer` (Ordner `tag1` im Hauptzweig `main`); ein GitHub-Konto ist nicht nötig. Tag 2 nutzt dasselbe Repository im selben Zielordner `dr-sthamer`.
- Voraussetzungen wie an Tag 2: Python ab 3.9 (nur Standardbibliothek), Edge oder Chrome für PDF, optional Obsidian. Kein pip, kein Node, kein Internet nötig.

## Aufbau

| Ordner/Datei | Inhalt |
|---|---|
| `CLAUDE.md` | Tutor-Leitfaden für Claude (gilt in diesem Ordner allein) |
| `START.md` | Einstieg in Geschäftssprache |
| `.claude/settings.json` | Modell, Rechte und Sperren für diesen Ordner |
| `.claude/skills/` | leer; Ziel des eigenen Skills aus Drill 3 |
| `drills/` | Anleitungen Drill 0–5 |
| `daten/`, `angebotseingang/`, `regelwerke/`, `notizbuch/`, `praesentation/` | Übungsmaterial |
| `design/circle/` | Circle Design (Stilfibel, Tokens, Bausteine, Gerüst) für das Dashboard |
| `checkpoints/` | Zwischenstände zum Einsteigen nach einem Drill |
| `folien/` | Folien des Tages ohne Sprechernotizen |
| `werkzeuge/` | Herstellung des Arbeitsstands (`erzeuge_daten.py`, `pruefe_daten.py`) und Notizbuch-Ansicht ohne Obsidian (`notizbuch_ansicht.py`) |
| `meine-ergebnisse/` | entsteht beim Arbeiten, wird nicht versioniert |

## Hinweise für Betreuung und IT

- Pfade in diesem Ordner sind relativ; der Ordner kann als Ganzes in ein anderes Repository umziehen.
- Damit ein übergeordneter Leitfaden nicht mitgeladen wird, schließt `.claude/settings.json` mit `claudeMdExcludes` jede `CLAUDE.md` aus, deren Ordner nicht `tag1` heißt. **Wird der Inhalt von `tag1/` an die Wurzel eines eigenen Repositorys verschoben (Ordner heißt dann nicht mehr `tag1`), diesen Eintrag entfernen oder anpassen**, sonst schließt er die eigene `CLAUDE.md` aus.
- `werkzeuge/erzeuge_daten.py` und `pruefe_daten.py` lesen Daten aus dem übergeordneten Repository und sind nur für die Herstellung gedacht, nicht für Teilnehmende.
- Ergebnisse (`meine-ergebnisse/`), neue Notizen (`notizbuch/Vorbereitung/`) und eigene Skills werden von `.gitignore` ausgeschlossen.

Alle Personen, Firmen, Adressen, Kennzahlen und Ereignisse sind erfunden. Ähnlichkeiten mit realen Personen oder Unternehmen sind unbeabsichtigt. Aussagen zu Regeln sind vereinfacht und ersetzen keine Rechtsberatung.
