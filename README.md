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
(<http://127.0.0.1:3005>). Wenn gefragt wird, ob das Werkzeug **sthamer-sys**
verwendet werden darf: **Ja**.

**Wenn du nicht weiterweißt, frag Claude.** Es ist hier dein Tutor und gibt dir
Hinweise in kleinen Schritten. Klappt etwas bei der Einrichtung nicht, hilft
dir die Fehlerbehebung in der Installationsanleitung, oder du setzt dich zu
jemandem dazu („Buddy-Modus“).

> **Für Claude Code – Einrichtung:** Lies `CLAUDE.md` und folge dem Abschnitt
> „Erststart“. Kurz: passenden Python-Befehl finden (`python`, `python3` oder
> `py -3`), `check.py` ausführen, `sthamer.py setup`, dann
> `sthamer.py serve --open` im Hintergrund. Die Person bedient kein Terminal und
> hört keinen Fachjargon.

## Was in diesem Repo liegt

| Ordner / Datei | Inhalt |
| --- | --- |
| `check.py` | Systemcheck für Teilnehmende (Python, Git, Rechte, Umlaute, Internet) |
| `sthamer.py`, `sthamer_sys/` | die Anwendung: Kommandozentrale im Browser, Werkzeuge für Claude (MCP), Kommandozeile |
| `web/` | die Oberfläche der Kommandozentrale |
| `data/` | erfundene Stammdaten: Produkte, Kunden, Lieferungen, Verordnung, Nachrichten |
| `tests/` | Prüfszenarien (`python -m unittest discover -s tests`) |
| `docs/` | Anleitungen, Plan und Datenmodell: [PLAN](docs/PLAN.md), [DATENMODELL](docs/DATENMODELL.md), [IT-Vorbereitung](docs/IT_VORAB.md), [Offline-Paket](docs/OFFLINE_PAKET.md) |
| `CLAUDE.md` | Leitfaden für Claude als Tutor |

Es wird **nichts installiert**: keine Pakete, kein `pip`, kein Node. Die
Anwendung nutzt nur die Standardbibliothek von Python (ab Version 3.9).

## Hinweise

- Die Kommandozentrale läuft nur auf deinem Gerät (`127.0.0.1`) und ist aus dem
  Netz nicht erreichbar.
- Es gibt kein Werkzeug zum Senden oder Freigeben für Claude. Das ist die
  wichtigste Kontrolle des Tages: **Claude bereitet vor, du entscheidest.**
- Die Software zeigt, wie man einen **prüfbaren Prozess** baut, nicht, was
  rechtlich gilt.
