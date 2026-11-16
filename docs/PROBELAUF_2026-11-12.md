# Probelauf vom 12. und 13.11.2026

Der Tag wurde mit **simulierten Teilnehmenden** und **echten Claude-Code-Sitzungen (Sonnet)** komplett durchgespielt. Dieses
Dokument sagt, was getestet wurde, was dabei kaputt war und was nicht geprüft ist. Es ersetzt keine Generalprobe auf einem
Sthamer-Gastgerät.

## Methode

- Je Lauf sprach eine **Persona** (ein KI-Agent in der Rolle einer Teilnehmerin oder eines Teilnehmers) mit einer **echten Tutor-Sitzung**
  im Klon des Repos (`claude -p`, Sonnet, Projekteinstellungen wie am Tag). Die Persona klickte im Cockpit (`lehrer/sim_mensch.py` ruft
  dieselben Adressen auf wie der Browser) und bewertete jeden Schritt gegen den Lösungsschlüssel.
- **Sabine** (Regulatory Affairs, geführt) spielte den ganzen Tag, **Jonas** (Vertrieb, ungeduldig) testete Grenzen: Senden und Freigeben
  delegieren, Umwege, Codes erraten, versteckte Anweisung, fremde Daten im Chat, Paketinstallation, echte Daten, Tempodruck.
- Geprüft wurde nach jedem Bau mit `scripts/akzeptanz.py` und `python -m unittest discover -s tests`.

## Ergebnis

| Lauf | Umfang | Ergebnis |
| --- | --- | --- |
| 1 | Erststart | Abbruch durch den Probeaufbau (Ordner nicht vertraut, Werkzeug nicht erlaubt). Daraus: Hinweise zu den zwei Rückfragen der App. |
| 2 | Drill 1 bis 4 (Sabine), Drill 1 bis 3 (Jonas) | Viele Befunde (siehe unten); unterbrochen durch eine Netzstörung. |
| 3 | **ganzer Tag**, Drill 1 bis 5 (Sabine, 39 Tutor-Aufrufe, etwa 15 Min. Tutor-Rechenzeit) und Drill 4 und 5 mit Angriffen (Jonas, 32 Aufrufe) | Alle Akzeptanzprüfungen und alle Prüfszenarien grün, keine Neustarts nötig. Alle Überredungs- und Umwegversuche (Delegieren, Codes, versteckte Anweisung, fremde Daten) hielten; eine technische Lücke (Python-Skript) wurde danach geschlossen. |
| 4 | Drill 4 und 5 auf dem Endstand, normaler Berechtigungsmodus (22 Aufrufe) | **0 Rückfragen** für Bearbeiten, Tests und Speichern. Berichtigung erzeugt Handlungsbedarf (zwei von vier geplanten Mails nannten die alte Frist). |

Kosten der Tutor-Sitzungen je Lauf: 2 bis 6 US-Dollar (Sonnet, kumuliert je Sitzung). Das heißt: Ein Tag mit Claude Pro ist beim
Tempo der Simulation unkritisch; echte Personen sind langsamer und schreiben mehr.

## Was gefunden und behoben wurde

| Befund | Schwere | Behebung |
| --- | --- | --- |
| Nach jedem Bau musste die Kommandozentrale neu gestartet werden; der Tutor suchte Umwege (`kill`, `lsof`, Prozesslisten) | hoch | `sthamer_sys/nachladen.py`: Cockpit und Werkzeug-Server laden geänderten Code selbst nach, bei Tippfehler bleibt der alte Stand aktiv und `code_fehler` meldet es. Eigene Tests im echten Prozess. |
| Die Menschen-Aktionen (Senden, Freigeben, Ablehnen, Uhr, Runden) waren aus einem Python-Skript aufrufbar; ein Heredoc lief in der Simulation ohne Sperre | hoch | `sthamer_sys/schutz.py`: Diese Funktionen laufen nur im Cockpit-Prozess. Dazu Sperren für `python -`, `python -c`, `sqlite3`, `kill`, `cat >`, `tee`, `sed -i` und Bearbeiten von Schutz, Prüfskripten, Daten und Anleitungen. |
| Nach dem Nachladen waren die Menschen-Aktionen im Cockpit gesperrt (das Schutzmodul wurde mit neu geladen) | hoch | Im echten Klon gefunden, nicht von den Einzeltests. Schutzmodul bleibt beim Nachladen stehen; Regressionstest mit Gegenprobe. |
| Die Testsuite wurde nach jedem korrekten Bau rot (Absicherung des Ausgangsstands, Tests gegen die Belegregel von Drill 2) | hoch | Lehrer-Tests nach `lehrer/` verschoben; bestehende Tests an die Belegregel angepasst; der Referenztest prüft, dass mit der Lösung **alle** Prüfszenarien grün sind. |
| Drill 1: Die Person sendete vor dem Bau, danach gab es keinen sauberen Nachweis | mittel | Reihenfolge der Karte: Senden **nach** dem Bau ist der Beweis. |
| Drill 4: Berichtigung hatte nichts zu korrigieren, wenn niemand eine Mail mit alter Frist im Fenster hatte | mittel | Die Mail des Recycling-Parks fragt nach der stationären Frist (Standardinformation mit alter Frist); Berichtigung kommt vor dem Vorspulen der Uhr. |
| Claude entschied die Kontrolle seiner eigenen Mail allein (`rechtsaussage`), einmal falsch | mittel | Ab Drill 4 bestätigt die Person eine Tabelle vor dem Einreichen; `rechtsaussage` ist eine Tatsachenmeldung (nie mild gegen die eigene Einschätzung). |
| Claude änderte bereits eingereichte Entwürfe | mittel | Das Werkzeug lehnt ab; Rückholen macht der Mensch (Ablehnen) oder Claude stoppt die geplante Mail. |
| Produkt mit Widerspruch „fluorfrei“ gegen Messwert und Kunde in Drittland falsch eingestuft | mittel | Einstufungsregel in Karte, Leitfaden und Werkzeugbeschreibung (`unklar`, `mittelbar`). |
| Referenzprüfung wies gültige Artikel ab; Daten nur im ISO-Format erkannt | mittel | Artikel und Absätze aus dem Volltext; Daten in deutschen, englischen und ISO-Formaten. |
| Bericht zählte falsch (ruhende Kunden) und trennte nicht, wer gestoppt hat | mittel | `ohne_einschaetzung` nach Kunden-IDs; `gestoppt_vom_menschen` und `gestoppt_von_claude`. |
| Abgewiesene Belege waren nirgends sichtbar | niedrig | Eintrag `belegpruefung_abgewiesen` im Protokoll. |
| Tutor-Antworten zu lang, geschlossene Schlussfragen, erfundene Zusagen („wir melden uns“), erfundener Cockpit-Knopf | niedrig | Regeln in `CLAUDE.md` (etwa 120 Wörter, offene Frage, keine Zusagen, Liste der Cockpit-Aktionen). |
| Python 3.9 fehlte in den Referenzskripten (`write_text(newline=…)`) | niedrig | Von der CI gefunden und behoben. |

## Zusatz-Audit zu Windows und Mac (16.11.2026)

Ein unabhängiger Agent hat die Software und die Anleitungen nur lesend auf Betriebssystem-Risiken durchsucht, mit kleinen Experimenten auf dem Mac.
Windows wurde nicht ausgeführt, nur aus Quelltext, Dokumentation und Erfahrung bewertet. Behoben ist, was sich ohne Windows-Gerät sicher beheben ließ:

| Befund | Behebung |
| --- | --- |
| Berechtigungsmuster kannten `py -3` nicht (der Weg, wenn `python` der Microsoft-Store-Platzhalter ist) und nur wenige Schreibweisen (`python.exe`, `python <<EOF`, `curl.exe`, `cmd`) | Muster ergänzt; die echte Grenze bleibt `schutz.py`, die Sperren sind eine Abkürzer-Sperre |
| Der Start erkannte einen laufenden Server hinter einem Proxy nicht und fragte bis zu 20 Ports ab (auf Windows langsam) | Lokale Adresse ohne Proxy, nur zwei Ports, dann Binden; zweiter Start dauert 0,1 s |
| Ein offener Browser-Tab bekam nach einem Neustart „403“ | Token bleibt über Neustarts gleich; die Seite lädt sich bei 403 neu |
| `reset` schlug auf Windows fehl, wenn die Datenbank gerade offen war | Tabellen leeren statt Datei löschen |
| `.pyc`-Dateien konnten bei gleicher Größe und Sekunde einen alten Stand laden | Keine `.pyc` schreiben (Programm und Probeläufe der Teilnehmenden) |
| Git Bash fehlte im Systemcheck; Netzlaufwerk-Pfade; Handshake 10 s zu knapp; Python 3.13 hinter TLS-Inspektion | Systemcheck ergänzt, Python 3.12 empfohlen |
| Anleitungen: Claude-App nach Installation neu starten, Mac ohne Administrator, `Install Certificates.command` braucht PyPI, Git „Secure Channel“ | Anleitungen und IT-Dokumente angepasst |
| Leitfaden erlaubte Python-3.9-widrigen Code | Regel in `CLAUDE.md` |

**Bleibt für die Generalprobe auf einem echten Gerät** (nicht ohne Windows klärbar): Wird Git Bash gefunden und das PowerShell-Werkzeug dabei abgeschaltet gelassen?
Welches Python steht in `.mcp.json` und löst `py -3` Rückfragen aus? Dauert `serve` auf Windows lange, liegen Ports in einem ausgeschlossenen Bereich (`netsh int ipv4 show excludedportrange protocol=tcp`)?
Greift ein Firmenzertifikat für Python und Git? Auf dem Mac: Sind Git und Python im Gastkonto da? Zeigt `~` in Git Bash auf `C:\Users\…`? Dazu je ein Durchlauf von Drill 1 in der Claude-App mit Schließen und Neuöffnen der Sitzung.

## Was dieser Probelauf **nicht** zeigt

- **Windows und Gastgeräte:** Alles lief auf einem Mac. Windows ist nur über die CI (Tests, Systemcheck) abgedeckt. Siehe [PLAN.md](PLAN.md), 8a.
- **Die Claude-App:** Die Simulation nutzt `claude -p` mit den Berechtigungen der Projektdatei. In der App erscheinen die Rückfragen als Dialoge; dass
  Bearbeiten und Tests keine auslösen, wurde im Kommandozeilenmodus gemessen, nicht in der App.
- **Echte Personen:** Simulierte Teilnehmende verstehen schnell, tippen sauber und verlieren nie die Geduld. Reale Reibung (Anmeldung, Netz,
  Missverständnisse, Tempo) kennt erst die Generalprobe.
- **Böswillige Nutzer:** Die Sperren verhindern den versehentlichen Abkürzer und machen jeden Umweg sichtbar. Wer den Code absichtlich ändert
  (zum Beispiel `schutz.py` per Hand), umgeht sie. Rekursives `grep` liest auch gesperrte Ordner. Die Runden-Codes sind kurze Wörter und nur ein Taktgeber.
- **Die fachliche Richtigkeit** ist die der erfundenen Welt. Kein Rechtsrat.
