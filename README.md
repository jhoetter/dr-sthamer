# dr-sthamer – Die Regulatorik-Werkstatt (sthamer-sys)

Eine kleine, **fiktive** Software für den Workshop *Agentische Systeme* mit
Dr. Sthamer (Veranstalter: ITMP SG). Die EU erlässt eine neue Verordnung zu
Schaumlöschmitteln. Sie wird zum Fall, Claude Code bereitet über Werkzeuge
(MCP) vor, wer betroffen ist und was den Kunden gesagt werden muss, und **ihr
baut selbst die Kontrollen**, die entscheiden, wann eine Mail das Haus
verlassen darf: **Pflichtfreigabe** bei Rechtsaussagen, **Eingriffsfenster**
bei Standardinformationen.

> Alle Kunden, Produkte, Messwerte, Lieferungen, Mails und die Verordnung sind
> **erfunden**. Nichts hier ist Rechtsrat. Nie echte Kundendaten verwenden.
> Es werden **keine echten Mails** versendet: „Senden“ legt nur eine Datei im
> Postausgang ab.

## Schnellstart in einem Satz

Auf jedem Gerät mit **Python 3**, **Git** und Claude Code genügt in einer neuen Sitzung (in einem beliebigen Ordner, am besten im Benutzerordner):

> Clone das Repo jhoetter/dr-sthamer und starte die Anwendung.

Claude klont nach `dr-sthamer`, findet den passenden Python-Befehl und führt **einen** Befehl im Hintergrund aus:

```
python sthamer.py start
```

(Mac/Linux: `python3 sthamer.py start`, Windows ggf. `py -3 sthamer.py start`.) Der Befehl richtet alles ein (lokale Datenbank, Verbindung zu Claude, Git-Vorbereitung) und öffnet die Kommandozentrale im Browser (<http://127.0.0.1:3005>). Er ist wiederholbar: Läuft sie schon, wird sie nur geöffnet.

**Einmal neu öffnen:** Die Werkzeuge für Claude (MCP) werden beim Start einer Sitzung geladen. Eine Sitzung, die außerhalb des Ordners begonnen hat, kennt sie noch nicht. Danach eine **neue Sitzung im Ordner `dr-sthamer`** öffnen und „weiter mit Drill 1“ schreiben; dort gelten der Leitfaden `CLAUDE.md` und die Freigaben. Fragen zur Vertrauensabfrage („Ordner“, „Werkzeuge von Sthamer“) mit Ja beantworten.

## Drei Tage, zwei Ordner

Der Workshop läuft **Mittwoch bis Freitag (25.–27.11.2026)**. **Dieser Ordner (Wurzel) ist Tag 2, „Agentische Systeme“** (Donnerstag, 26.11.2026, Johannes Hötter). **Tag 1, „AI Augmentation“** (Mittwoch, 25.11.2026, Falk Uebernickel) liegt eigenständig im Ordner [`tag1/`](tag1/README.md) mit eigenen Daten, eigenem Leitfaden und eigenen Einstellungen; er arbeitet mit anderen Beispielfällen (Geschäftsentwicklung statt Verordnung). **Tag 3** (Freitag, 27.11.2026, Dr. Marc Kohler, ITMP SG) ist der eigene Fall der Teilnehmenden („Bring Your Own Case“, Ablauf noch offen). Der Vortrag zu Tag 2 liegt in [`tag2/`](tag2/README.md). Alle Tage nutzen dasselbe Repository und denselben Zielordner `dr-sthamer`; wer Tag 1 schon geklont hat, aktualisiert am Donnerstag mit `git pull` (der Leitfaden macht das selbst). Für Tag 2 liest Claude **nichts** in `tag1/`. Die Folien aller drei Tage (Überblick, Agenda, Tag 2) liegen in [`folien/`](folien/README.md).

## Start für Teilnehmende

Du brauchst nur **Python 3**, **Git** und die **Claude-App** (Claude Pro). Die
Anleitung führt dich Schritt für Schritt, ohne Vorwissen und ohne
Administratorrechte:

- **Windows:** [docs/INSTALL_WINDOWS.md](docs/INSTALL_WINDOWS.md)
- **Mac:** [docs/INSTALL_MAC.md](docs/INSTALL_MAC.md)
- **Eine Woche vorher:** [docs/VOR_DEM_WORKSHOP.md](docs/VOR_DEM_WORKSHOP.md)

Danach prüfst du dein Gerät mit dem **Systemcheck** (im Ordner `dr-sthamer`):

```
python check.py
```

(Mac: `python3 check.py`.) Er zeigt pro Zeile OK, ACHTUNG oder FEHLER, sagt dir,
was zu tun ist, und nennt am Ende einen **Support-Code**, den du uns vorlesen
kannst.

Dann öffne in der Claude-App den Bereich **Code**, starte eine neue Sitzung mit
dem Ordner `dr-sthamer` in deinem Benutzerordner und schreibe:

> Richte alles nach der README ein und starte die Kommandozentrale. Ich bin in Drill 1.

Oder, wenn der Ordner noch nicht da ist:

> Klone https://github.com/jhoetter/dr-sthamer in den Ordner dr-sthamer in meinem Benutzerordner, richte alles nach der README ein und starte die Kommandozentrale. Ich bin in Drill 1.

Claude richtet alles ein und öffnet die Kommandozentrale im Browser
(<http://127.0.0.1:3005>). Beim ersten Öffnen fragt die App, ob du dem **Ordner** vertraust: **Ja**. Wenn gefragt wird, ob das Werkzeug **sthamer-sys**
verwendet werden darf: **Ja**.

**Wenn du nicht weiterweißt, frag Claude.** Es ist hier dein Tutor und gibt dir
Hinweise in kleinen Schritten. Klappt etwas bei der Einrichtung nicht, hilft
dir die Fehlerbehebung in der Installationsanleitung, oder du setzt dich zu
jemandem dazu („Buddy-Modus“).

> **Für Claude Code – Einrichtung:** Lies `CLAUDE.md` und folge dem Abschnitt
> „Erststart“. Kurz: passenden Python-Befehl finden (`python`, `python3` oder
> `py -3`), dann **einen** Befehl im Hintergrund (`run_in_background`, ohne
> Verkettung): `<python> sthamer.py start` (richtet ein und startet die
> Kommandozentrale), danach in einem eigenen Aufruf `<python> sthamer.py status`.
> `check.py` nur bei Problemen. Die Person bedient kein Terminal und
> hört keinen Fachjargon. Die Werkzeuge (MCP) fehlen in dieser ersten Sitzung:
> bitte eine neue Sitzung im Ordner öffnen lassen. Nichts in `tag1/` lesen.

## Was in diesem Repo liegt

| Ordner / Datei | Inhalt |
| --- | --- |
| `check.py` | Systemcheck für Teilnehmende (Python, Git, Rechte, Umlaute, Internet) |
| `sthamer.py`, `sthamer_sys/` | die Anwendung: Kommandozentrale im Browser, Werkzeuge für Claude (MCP), Kommandozeile |
| `web/` | die Oberfläche der Kommandozentrale |
| `data/` | erfundene Stammdaten: Produkte, Kunden, Lieferungen, Verordnung, Nachrichten |
| `tests/` | Prüfszenarien (`python -m unittest discover -s tests`) |
| `scripts/` | `akzeptanz.py` prüft die Bauaufträge der Drills, `make_data.py` erzeugt die Übungsdaten, `postfach_verschluesseln.py` verschlüsselt den E-Mail-Schlüssel (nur Lehrende) |
| `lehrer/` | nur für Lehrende: Referenzlösungen und Absicherungstest (für Claude gesperrt) |
| `docs/` | Anleitungen, Plan und Datenmodell: [PLAN](docs/PLAN.md), [Agenda](docs/WORKSHOP_AGENDA.md), [Drill-Karten](docs/DRILL_CARDS.md), [Runbook](docs/WORKSHOP_RUNBOOK.md), [Probelauf](docs/PROBELAUF_2026-11-12.md), [DATENMODELL](docs/DATENMODELL.md), [IT-Kurzfassung](docs/IT_CHECKLISTE.md), [IT-Details](docs/IT_VORAB.md), [Offline-Paket](docs/OFFLINE_PAKET.md) |
| `tag1/` | Tag 1 „AI Augmentation“ (Falk): eigenständiger Arbeitsstand, siehe [tag1/README.md](tag1/README.md); gehört nicht zu Tag 2 |
| `tag2/` | Material zu Tag 2: Vortrag «Jede Aufgabe zuerst agentisch» (Johannes), siehe [tag2/README.md](tag2/README.md); die Anwendung selbst liegt an der Wurzel |
| `folien/` | Workshop-Folien ITMP × Dr. Sthamer (eine HTML-Datei, läuft offline), siehe [folien/README.md](folien/README.md) |
| `CLAUDE.md` | Leitfaden für Claude als Tutor |

Es wird **nichts installiert**: keine Pakete, kein `pip`, kein Node. Die
Anwendung nutzt nur die Standardbibliothek von Python (ab Version 3.9).

## Hinweise

- Die Kommandozentrale läuft nur auf deinem Gerät (`127.0.0.1`) und ist aus dem
  Netz nicht erreichbar.
- Es gibt kein Werkzeug, mit dem Claude die Übungsmails (Entwürfe an die Kundschaft) sendet oder freigibt. Das ist die
  wichtigste Kontrolle des Tages: **Claude bereitet vor, du entscheidest.** Für den optionalen E-Mail-Bereich (echtes
  Postfach) kann Claude Mails abholen und senden; die App fragt vor jeder Sendung nach.
- Die Software zeigt, wie man einen **prüfbaren Prozess** baut, nicht, was
  rechtlich gilt.
