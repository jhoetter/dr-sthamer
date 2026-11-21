# Tag 1 „AI Augmentation“ – Arbeitsstand für Teilnehmende

Material für Tag 1 eines zweitägigen AI-Bootcamps an der Übungsfirma Dr. Sthamer (fiktive Daten). Tag 2 („Agentische Systeme“) arbeitet im übergeordneten Repository; dieser Ordner ist davon unabhängig.

**Einstieg für Teilnehmende:** [START.md](START.md). Claude liest zusätzlich die Datei [CLAUDE.md](CLAUDE.md).

## So öffnen

- Die Claude-App (Reiter „Code“) **im Ordner `tag1` selbst** öffnen, nicht im Repository darüber. Nur dann gelten `tag1/CLAUDE.md` und `tag1/.claude/settings.json`.
- Laden ohne GitHub-Konto: Branch `tag1-augmentation` als ZIP herunterladen und nur den Ordner `tag1` entpacken, oder `git clone --depth 1 -b tag1-augmentation <Repository-URL>` und dann den Unterordner `tag1` öffnen.
- Voraussetzungen wie an Tag 2: Python ab 3.9 (nur Standardbibliothek), Edge oder Chrome für PDF, optional Obsidian. Kein pip, kein Node, kein Internet nötig.

## Aufbau

| Ordner/Datei | Inhalt |
|---|---|
| `CLAUDE.md` | Tutor-Leitfaden für Claude (gilt in diesem Ordner allein) |
| `START.md` | Einstieg in Geschäftssprache |
| `.claude/settings.json` | Modell, Rechte und Sperren für diesen Ordner |
| `.claude/skills/` | leer; Ziel des eigenen Skills aus Drill 3 |
| `drills/` | Anleitungen Drill 0–5 |
| `daten/`, `angebotseingang/`, `regelwerke/`, `notizbuch/`, `praesentation/`, `akten/` | Übungsmaterial |
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
