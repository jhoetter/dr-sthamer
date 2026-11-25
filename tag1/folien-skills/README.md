# Folien-Skills für Claude Code

Drei fertige Skills für Präsentationen und HTML-Seiten: **exhibit-stil** (Folien im Exhibit-Stil als HTML mit
Prüfkasten und PDF), **aktionstitel** (Aktionstitel und Storyline nach dem Pyramidenprinzip) und **circle-design**
(gut aussehende HTML-Seiten, hell und dunkel). Sie laufen ohne Internet und ohne Installation von Programmen.

Lizenz: © 2026 Falk Uebernickel, zur eigenen Nutzung durch die Teilnehmenden des Workshops. Schriften in `circle-design/assets/fonts/` unter SIL Open Font License (Lizenztexte liegen
dabei); die Bibliothek D3 in `exhibit-stil/vorlage.html` unter ISC-Lizenz.

## Was ein Skill ist

Ein Skill ist ein Ordner mit einer Datei `SKILL.md`: oben Name und Beschreibung, darunter die Anleitung für Claude.
Claude liest am Anfang nur die Beschreibungen. Passt deine Aufgabe dazu („Prüfe meine Folientitel“), lädt Claude die
ganze Anleitung und arbeitet danach. Ohne passende Aufgabe bleibt der Skill ungelesen.

| Skill | Greift bei | Inhalt |
|---|---|---|
| `exhibit-stil` | Folie, Präsentation, Beirat, Exhibit, PDF der Folien | Vorlage, Bausteine, welches Diagramm wann, Inhaltsregeln, Prüfkasten, Screenshots und PDF mit Edge oder Chrome |
| `aktionstitel` | Aktionstitel, Folientitel prüfen, Storyline, Titeltest, SCQA | sieben Regeln für Titel, Storyline in vier Schritten, Prüfschema als Tabelle |
| `circle-design` | HTML-Seite, Übersicht, Dashboard, Handout, Formular | Einbinden der Stylesheets, Regeln, Bausteine, Gerüst, Dark Mode |

## Installieren

**Weg A – nur für dieses Projekt (im Kurs):** Schreib Claude:

> „Installiere die drei Folien-Skills aus dem Ordner folien-skills für dieses Projekt und zeig mir, dass du sie kennst.“

Claude kopiert `folien-skills/exhibit-stil`, `folien-skills/aktionstitel` und `folien-skills/circle-design` nach
`.claude/skills/`. Der Ordner `.claude` ist geschützt: Die App fragt nach, ob Claude dort schreiben darf – bestätigen.
Die Skills gelten dann für jede Sitzung in diesem Ordner.

**Weg B – für deinen Benutzer (alle Projekte):** dieselben drei Ordner nach `%USERPROFILE%\.claude\skills\` (Windows)
bzw. `~/.claude/skills/` (Mac, Linux) kopieren, von Hand im Explorer oder mit Claude. Danach hat jedes Projekt die
Skills.

Beim Kopieren den ganzen Ordner nehmen: Der Skill `circle-design` enthält Schriftdateien.

## Prüfen, ob die Skills geladen sind

- Neue Sitzung beginnen (neue Skills erkennt Claude spätestens in einer neuen Sitzung) und fragen: „Welche Skills
  kennst du?“ Die drei Namen müssen in der Antwort stehen.
- Wo es den Befehl gibt: `/skills` eintippen; dann erscheint die Liste.
- Beim Arbeiten erkennst du es daran, dass Claude meldet, einen Skill zu laden (etwa „Skill aktionstitel“), und nach
  dessen Regeln urteilt.
- Direkt aufrufen geht auch: `/aktionstitel`, `/exhibit-stil`, `/circle-design`.

## Entfernen

Den Ordner des Skills in `.claude/skills/` (Weg A) bzw. `%USERPROFILE%\.claude\skills\` (Weg B) löschen, dann neue
Sitzung. Die Vorlagen in diesem Ordner `folien-skills/` bleiben unverändert.

## Regeln

- Die Skills nicht verändern. Eigene Wünsche gehören in einen eigenen Skill (wie in Drill 3) oder in deine Notizen
  („Merke dir …“).
- Hat ein Projekt eine eigene Stilfibel (etwa `praesentation/VORLAGE.md` oder `design/circle/CIRCLE.md`), geht sie den
  Skills vor; die Skills nehmen dann die Vorlagen des Projekts.

## Auf GitHub hochladen

Dieser Ordner kann als eigenes Repository hochgeladen werden: README, Lizenz (vorher festlegen) und die drei
Skill-Ordner reichen. Wer ihn herunterlädt, kopiert die Skill-Ordner wie unter Weg B.
