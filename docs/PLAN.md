# Plan: Dr. Sthamer × ITMP SG – Workshop „Agentische Systeme“

> **Status:** Arbeitsstand vom 12.11.2026, zur Abstimmung zwischen Johannes,
> Falk und Marc. Alles Fettgedruckte unter „Offene Fragen“ entscheiden wir,
> bevor wir den Rest bauen.

## 1. Worum es geht

Wir übertragen das Prinzip von Pfefferminzia (HSG-Workshop, Versicherung) auf
**Dr. Sthamer**, einen Hersteller von Schaumlöschmitteln, der bei uns
(ITMP SG) einen Workshop gebucht hat. Gleiche Lernidee, anderer Fall:

> Die EU erlässt eine neue Verordnung. Wer ist betroffen, wer muss was bis
> wann erfahren, und was darf ein Agent davon selbst erledigen?

Alle Daten sind **fiktiv, aber von Sthamer inspiriert** (Schaumarten,
Brandklassen, Einsatzbereiche, Umstellungsprozess, Kundensegmente von der
Website). Keine echten Kunden, Produkte oder Verordnungstexte in den Übungen.
Das System heißt **`sthamer-sys`**, das Repo `dr-sthamer`.

| Pfefferminzia (HSG) | Sthamer (ITMP SG) |
| --- | --- |
| Versicherungs-Werkstatt, Kommandozentrale | `sthamer-sys`, Kommandozentrale „Regulatorik“ |
| Eingehende Mail → Ticket | Eingehende Verordnung / Kundenanfrage → Fall |
| Kunde, Vertrag, Tarifgeneration | Kunde, Lieferung/Anlage, Produkt (+ Datenblatt-Stand) |
| Pflichtfreigabe bei Leben | Pflichtfreigabe bei **Rechtsaussagen** und kritischen Kunden |
| Eingriffsfenster bei Haftpflicht | Eingriffsfenster bei **Standardinformationen und Fristen-Erinnerungen** |
| AgentMail-Inbox je Person | **Keine Inbox:** Eingang = lokale Dateien, Versand = Postausgang-Ordner |
| HSG-Logo, Falk Uebernickel | ITMP-SG-Logo, gleiche Lehrpersonen (Falk, Marc, Johannes) |

## 2. Rahmen und Annahmen

- **Teilnehmende:** Mitarbeitende von Dr. Sthamer (Fachbereiche, kaum
  Programmiererfahrung angenommen), ca. 10–16 Personen.
- **Geräte:** Arbeitsgeräte von Sthamer mit **Gastbenutzer** und **Gäste-WLAN**.
  Ein Gerät ist ein Mac, alle anderen Windows. Wir gehen davon aus, dass
  Teilnehmende **keine Administratorrechte** haben.
- **Software:** Python 3, Git, die Claude-App (Code). Alle bekommen
  **Claude Pro**. Kein Node, kein `uv`, kein `pip install`.
- **Kein Mailserver:** Eingänge kommen als Dateien (Welle für Welle vom
  Dozenten freigegeben), „Senden“ legt eine Datei im Postausgang ab. Echte
  Mails gehen standardmäßig nie raus. **Optionaler Live-Modus mit AgentMail**
  (noch nicht gebaut): ein Postfach und ein eigener Schlüssel je Person, Import nur von
  der Absenderadresse der Lehrenden, Senden nur an eine feste Empfängerliste; die
  Dateien bleiben als Rückfall. Dafür braucht das WLAN `api.agentmail.to`.
- **Sprache:** Deutsch (UI, Claude als Tutor, Anleitungen).
- **Format (entschieden):** drei Tage, Mi–Fr 25.–27.11.2026 (Tag 3: eigener Fall, „Bring Your Own Case“, Leitung Dr. Marc Kohler, Ablauf offen). Tag 1 (Mi, 25.11.2026, Falk): „AI Augmentation“, Ordner `tag1/`.
  Tag 2 (Do, 26.11.2026, Johannes): dieser Plan, ein Workshop-Tag mit fünf Drills
  (Abschnitt 5), baukastenartig kürzbar auf einen halben Tag.

### Offene Fragen

1. **Termin, Dauer, Teilnehmerzahl?** (Annahme: 1 Tag, 10–16 Personen.)
2. ~~Zeitreihenfolge mit Falk~~ **Entschieden:** Falks Block liegt als Tag 1 davor (Mi, 25.11.2026);
   die Nummerierung der Drills von Tag 2 bleibt.
3. **Rechte auf den Gastgeräten:** Dürfen Gastbenutzer Software
   **ohne Administrator** installieren (Python und Git gehen per Benutzer-
   Installation, die Claude-App muss geprüft werden)? Geht GitHub im Gäste-WLAN?
4. **Repo öffentlich oder privat?** Teilnehmende haben keinen GitHub-Account.
   Privat funktioniert nur mit ZIP-Verteilung (Abschnitt 7). Empfehlung:
   **bis zur Freigabe durch Sthamer privat, spätestens am Vortag öffentlich**
   (alles synthetisch, keine Geheimnisse im Repo).
5. **Logo und Namen:** ITMP-SG-Logo bitte als SVG/PNG ins Repo legen
   (`web/logo-itmp.svg`). Darf der Name „Dr. Sthamer“ auf Folien und im
   Cockpit stehen oder lieber „Schaumwerk Nord (fiktiv)“?
6. **Kann Sthamer vorab eine echte, aber unkritische Verordnung** (oder
   Kundenmail-Vorlage) beisteuern, die wir im Bonus-Teil nutzen?

## 3. Das Zielbild: sechs Bausteine

Jedes agentische System besteht aus **Eingängen, Wissen, Werkzeugen,
Kontrollen, Oberfläche und Protokoll** (wie bei Pfefferminzia).

| Baustein | In `sthamer-sys` |
| --- | --- |
| Eingänge | Verordnung (Text/PDF), Berichtigung, Kundenanfragen, Fristen-Wecker |
| Wissen | Produktkatalog mit Fluorgehalt und Datenblatt-Stand, Kundenstamm, Lieferungen/Anlagen, Verordnungstext |
| Werkzeuge | MCP-Werkzeuge: lesen, Entwurf anlegen, Notiz, Betroffenheit belegen. **Es gibt absichtlich kein Werkzeug zum Senden oder Freigeben.** |
| Kontrollen | Pflichtfreigabe (Mensch, Vier-Augen) und Eingriffsfenster (automatisch nach Verzögerung, Mensch kann stoppen) |
| Oberfläche | Cockpit im Browser: Eingang, Fälle, Regelwerk, Produkte, Kunden, Freigaben, Postausgang, Protokoll |
| Protokoll | Jeder Schritt (Entwurf, Änderung, Freigabe, Stopp, Versand) mit Belegen |

## 4. Use Cases

### Kernfall (trägt den ganzen Tag): „Neue Verordnung – wer muss was erfahren?“

Eine neue (fiktive, an die echte PFAS-Beschränkung für Löschschäume
angelehnte) EU-Verordnung kommt als Eingang. Claude liest sie, der Mensch
entscheidet, was daraus für Sthamer folgt:

1. **Regelwerks-Steckbrief:** Was gilt (Grenzwert, Anwendungen), ab wann
   (Stichtage je Anwendung), für wen (Hersteller, Händler, Verwender)?
2. **Betroffene Produkte:** Fluorgehalt gegen Grenzwert, je Anwendung; mit
   Beleg (Artikel + Produktdatenblatt).
3. **Betroffene Kunden:** Lieferungen/Anlagen der Bestandskunden gegen
   die betroffenen Produkte und die Fristen der jeweiligen Anwendung.
4. **Kundeninformation vorbereiten:** je Kundensegment eine Mail mit Frist,
   betroffenen Produkten, Handlungsoption (z. B. fluorfreie Alternative,
   Umstellungskonzept), mit Belegen.
5. **Kontrolle:** wer prüft, wer sendet, was läuft automatisch?

Die Datenlage hat bewusst Stolperstellen (siehe `docs/DATENMODELL.md`):
Fluorgehalt knapp unter und genau auf dem Grenzwert, mg/l gegen µg/l,
Produkt ohne Messwert, Händler, die weiterverkaufen, Kunden außerhalb der EU,
Kunden mit Ausnahme, eine **Berichtigung**, die am Nachmittag eine Frist
ändert, und eine Kundenmail mit versteckter Anweisung an den Agenten.

### Weitere Use Cases (für Bonus, Reserve und „Bring Your Own Case“)

| # | Use Case | Auslöser | Kontrollmuster | Lerneffekt |
| --- | --- | --- | --- | --- |
| A | **Verordnung → Kundeninformation** (Kernfall) | EU-Verordnung | Pflichtfreigabe + Eingriffsfenster | alle sechs Bausteine |
| B | **Sicherheits- und Technisches Datenblatt aktualisieren:** welche Datenblätter ändern sich (Abschnitt 2/3/15), Änderungsliste und Entwurf | Verordnung / Grenzwert | Pflichtfreigabe (Regulatory Affairs) | Wissen, Belege, Versionsstand |
| C | **Umstellungs-Leads:** Kunden mit fluorhaltigem AFFF in stationären Anlagen finden, Phase 1 („Datenaufnahme der Anlage“) als Fragebogen vorbereiten | Betroffenheit | Eingriffsfenster | von Compliance zu Vertrieb, Sthamers Umstellungsprozess |
| D | **Kundenanfrage beantworten:** „Dürfen wir unseren Schaum X noch nachfüllen?“ belegt aus Verordnung und Datenblatt | eingehende Mail | Pflichtfreigabe (Rechtsauskunft) | belegter Entwurf, Grenze der Aussage |
| E | **Fristen-Wächter:** 180/90/30 Tage vor dem Stichtag automatisch erinnern | Zeit | Eingriffsfenster, Workshop-Uhr | Automation, Doppelversand ausschließen |
| F | **Berichtigung kommt, Mails sind schon geplant:** welche geplanten Mails sind jetzt falsch, stoppen, korrigieren | neuer Eingang | Eingriffsfenster zahlt sich aus | Kontrolle, Protokoll |
| G | **Händlerkette:** Händler muss an Endkunden weitergeben; wer informiert wen? | Kundentyp | Pflichtfreigabe | Grenzen der Automation |
| H | **Schulungs- und Notfalldienst-Hinweise:** Notfallservice und Schulungen für neue Kennzeichnung ankündigen | Verordnung | Eingriffsfenster | Cross-Selling mit Augenmaß |
| I | **Horizon Scanning:** wöchentlich neue Verordnungen und ECHA-Konsultationen sichten | Zeit | nur lesen | Grenze: Agent darf beobachten, nicht handeln |

Für Freitag/BYOC (Marc): Sthamer-Teams bringen eigene Fälle mit, etwa
Wirksamkeits- und Einzelnachweise, Schaumanalyse-Aufträge, Reklamationen,
Ausschreibungsunterlagen, Zertifikate und Zulassungen.

### Realer Anker (nur für Bonus, nicht als Rechtsauskunft)

Die echte Beschränkung ist **Verordnung (EU) 2025/1988** (PFAS in
Feuerlöschschäumen, REACH-Anhang XVII). Nach Sekundärquellen (UBA, IHK,
BVBF/DGUV) gilt ein Grenzwert von 1 mg/l und gestaffelte Fristen je Anwendung.
Wir haben den EUR-Lex-Originaltext **nicht** geprüft. Für die Übungen nutzen
wir deshalb eine **erfundene Verordnung mit anderen Zahlen**, damit nichts
davon als Rechtsstand missverstanden wird. Im Bonus-Teil können Teilnehmende
den echten Text aus EUR-Lex in Claude geben und die Ergebnisse mit dem
Steckbrief der fiktiven Fassung vergleichen.

## 5. Tagesbogen (Vorschlag, 1 Tag)

| Zeit | Block | Inhalt |
| --- | --- | --- |
| 09:00 | Input | Von der Frage zum Agenten, MCP, Verifizierbarkeit, die zwei Kontrollmuster. Danach: ein Satz an Claude, jede Person hat ihre Kommandozentrale. |
| 10:00 | **Drill 1 · Die Verordnung kommt** | Verordnung im Eingang. Claude erstellt den Steckbrief, Mensch prüft Fristen, Claude entwirft *eine* Kundenmail, Mensch sendet (Postausgang). Bauauftrag: Aufgabe erledigt sich beim Senden. |
| 11:15 | **Drill 2 · Wer ist betroffen? Mit Beleg** | Betroffenheit Produkte und Kunden mit Artikel- und Datenblattbeleg. Bauauftrag: Belegprüfung beim Speichern (Zitate müssen existieren, Fristen müssen stimmen). |
| 12:15 | Mittag | |
| 13:15 | **Drill 3 · Rechtsaussagen: Pflichtfreigabe** | Zwei Mails, eine freigeben, eine ablehnen (Claude hat kein Freigabe-Werkzeug). Edit entwertet die Freigabe. |
| 14:30 | **Drill 4 · Standardinfo: Eingriffsfenster** | Info-Mails laufen nach 24 h automatisch; Workshop-Uhr vorspulen. **Berichtigung trifft ein:** eine Mail ändern, eine stoppen. Doppelversand per Prüfszenario ausschließen. |
| 15:45 | **Drill 5 · Bericht an die Geschäftsführung** | Kennzahlen aus dem Protokoll: Wie viele Kunden betroffen, wie viele Mails automatisch, wie viele freigegeben, wie viele gestoppt; Empfehlung und Grenze der Aussage. (Kein Video, kein Node.) |
| 16:45 | Whiteboard | Wo darf der Agent bei **uns** handeln? Automation Contract; Ausblick auf Freitag („Bring Your Own Case“). |

Rhythmus pro Drill wie bei Pfefferminzia: Claude fragen → Mensch prüft und
entscheidet → selbst bauen (kleiner Bauauftrag) → Ergebnis belegen. Drei
Arbeitsweisen (geführt / bauend / ausbauend), Rettungsnetz über Checkpoints
(`drill-02-start` …) auf einem Branch `reference`.

## 6. Technische Entscheidungen

**Leitlinie: so wenig Voraussetzungen wie möglich.** Pfefferminzia braucht
`uv`, PyPI-Pakete (FastAPI, MCP-SDK, Kryptografie) und eine AgentMail-Anbindung.
Auf Gästegeräten im Gäste-WLAN ist jede dieser Abhängigkeiten ein Ausfallrisiko
(Proxy, TLS-Inspektion, gesperrte Domains, keine Compiler, keine
Administratorrechte). Darum:

| Entscheidung | Begründung |
| --- | --- |
| **Nur Python-Standardbibliothek**, keine Pakete, kein `pip` | Nach „Python + Git“ läuft alles; kein Netzwerkzugriff auf PyPI nötig |
| **Python ≥ 3.9** | Auf dem Mac liefert Apple 3.9 mit; Windows installiert 3.12 |
| Web-Oberfläche: `http.server` + eine statische HTML/JS-Seite, nur `127.0.0.1` | kein Node, kein Build, nichts im Netz erreichbar |
| Speicher: `sqlite3` (Standardbibliothek) in `.data/`, Startdaten aus `data/*.json` | sauberer Reset, Daten im Repo reviewbar |
| **MCP über stdio, selbst geschrieben (JSON-RPC)**, ohne MCP-SDK | kein Paket, kein Port, kein Firewall-Dialog; `.mcp.json` wird beim Setup mit dem **absoluten Python-Pfad** erzeugt (umgeht das Windows-Problem `python3` = Store-Platzhalter) |
| Jedes Feature auch per CLI (`python sthamer.py …`) | Rückfall, falls MCP auf einem Gerät nicht verbindet |
| Dateien immer UTF-8, `.gitattributes` mit LF | Umlaute und Windows-Zeilenenden |
| Klonen nach `%USERPROFILE%\dr-sthamer` (kein OneDrive, kein Desktop) | OneDrive-Ordnerumleitung bricht Git und Python |
| Postausgang statt Mail | nichts verlässt das Gerät; Dozenten-Inbox später optional |
| Modell auf **Sonnet, Stufe „Mittel“** in `.claude/settings.json` | Claude Pro hat Nutzungsgrenzen; alle erleben dasselbe |
| Wellen: Eingänge werden mit einem **Freigabecode** vom Dozenten nacheinander freigeschaltet | gleicher Takt für alle, ohne Mailserver |

## 7. Wirklich sicher bei allen: Maßnahmenplan

Das Ziel ist, dass **jede Person nach 20 Minuten eine laufende Kommandozentrale
hat**, auch mit Gastkonto, Gäste-WLAN und ohne Administratorrechte.

| Risiko | Gegenmaßnahme | Wo |
| --- | --- | --- |
| Gast hat keine Rechte für Installationen | Benutzer-Installation von Python und Git (kein Admin nötig); mit IT vorab klären, was das Gastprofil darf | `docs/INSTALL_WINDOWS.md`, `docs/IT_VORAB.md` |
| Gäste-WLAN blockiert Domains | Domainliste an die IT: `github.com`, `claude.ai`, `api.anthropic.com`, `python.org`, `git-scm.com`, Download-Hosts; **Test mit Gastkonto vorab** | `docs/IT_VORAB.md` |
| Python oder Git fehlen, Version falsch, `python3` ist der Store-Platzhalter | **Systemcheck** `python check.py` (grün/rot auf Deutsch, mit Lösungshinweis und Support-Code) | `check.py` |
| Klonen scheitert (privat, Proxy, kein Git) | **ZIP-Fallback** (GitHub „Download ZIP“ bzw. Release-Datei); zusätzlich **USB-Stick/Freigabe** mit Python-Installern, Git-Installer, Claude-Installer und Repo-ZIP | `docs/OFFLINE_PAKET.md` (geplant) |
| PyPI/Pakete nicht erreichbar | gibt es nicht: keine Pakete | Architektur |
| Port belegt, Firewall-Dialog | nur `127.0.0.1`, freier Port wird gesucht, stdio-MCP ohne Port | `sthamer_sys/app.py` |
| MCP verbindet nicht | CLI-Rückfall, Setup erzeugt `.mcp.json` mit absolutem Pfad, Check testet `initialize` | `check.py`, `setup` |
| Umlaute / Zeilenenden / Pfade mit Leerzeichen | UTF-8 überall, `.gitattributes`, Tests mit Leerzeichen und Umlaut im Pfad | Tests |
| Claude-Konto: Anmeldung per Mail-Code, Telefonprüfung | Konto **eine Woche vorher** auf eigenem Gerät anlegen und Pro-Einladung annehmen; Anmeldung auf dem Gastgerät einmal probieren | `docs/VOR_DEM_WORKSHOP.md` (geplant) |
| Pro-Limit während des Tages erreicht | Sonnet/Mittel, kurze Aufträge, Buddy-Modus (zu zweit an einem Gerät), Drill-Karten ohne Claude | Konzept |
| Sicherheitssoftware blockiert Skripte | **Probe auf einem echten Gastgerät**, mind. ein Tag vorher | Generalprobe |
| Unterschiedliche Systeme (Win 10/11, Mac, Python 3.9–3.13) | **CI-Matrix** auf Windows, macOS und Linux mit Python 3.9, 3.12, 3.13 | `.github/workflows/ci.yml` |
| Jemand hängt trotzdem | Buddy-Modus, Dozenten-Rechner, vorbereitetes Gerät als Reserve, Checkpoint-Tags | Runbook |

**Generalprobe (Pflicht):** Mindestens ein Sthamer-Gastgerät, bestenfalls
Windows und Mac, am Vortag mit einem Sthamer-IT-Kontakt: Installation nach
Anleitung, `python check.py`, Claude-Login, Kommandozentrale starten, einen
Drill-1-Durchlauf. Alles, was dabei stockt, kommt in die Anleitung oder ins
Offline-Paket.

## 8. Phasen und Status

| Phase | Inhalt | Status |
| --- | --- | --- |
| 0 | Repo, Plan, Datenmodell | **fertig** |
| 1 | Anleitungen Windows/Mac, IT-Vorab, Vorab-Checkliste, Offline-Paket (Checkliste), `check.py`, CI (Windows, macOS, Linux) | **fertig**, auf Windows noch nicht real getestet |
| 1 | Datensatz: 27 Produkte, 32 Kunden, 149 Lieferungen, fiktive Verordnung mit Berichtigung, 15 Mails in 4 Runden, Lösungsschlüssel | **fertig** |
| 1 | Kern: Speicher, Cockpit im Sthamer-Branding, MCP über stdio, Runden mit Code, Code lädt sich selbst nach | **fertig** |
| 2 | Pflichtfreigabe, Eingriffsfenster, Übungsuhr, Einschätzungen, Bericht, Protokoll; Schutz der Menschen-Aktionen | **fertig** |
| 2 | Agenda, Drill-Karten, Akzeptanzprüfung je Bauauftrag, Referenzlösungen und Rettungsweg (`lehrer/`), Runbook | **fertig** |
| 2 | **Probelauf** mit simulierten Teilnehmenden, ganzer Tag ([PROBELAUF_2026-11-12.md](PROBELAUF_2026-11-12.md)) | **fertig** |
| 3 | **Generalprobe mit Sthamer-Gastgerät** (Windows und Mac), Korrekturen | offen |
| 3 | Folien für den Input, ITMP-Logo, Offline-Paket bauen (Skript), Repo-Verteilung klären | offen |

## 8a. Was noch nicht verifiziert ist

Auf einem echten Gastgerät prüfen (`python check.py --netz`, ganzer Ablauf nach Anleitung):

- Sperren AppLocker/WDAC Python oder Git aus `%LocalAppData%`? (Gegenmaßnahme: die IT installiert vorab.)
- Wird das Gastprofil beim Abmelden oder Neustart gelöscht?
- Reicht die Domainliste im Gäste-WLAN? (Liste in `docs/IT_VORAB.md` ist teils vermutet.)
- Lässt sich die **Claude-App ohne Administrator** installieren, braucht sie auf Windows Git, und klappt die Mail-Anmeldung auf dem Gastgerät?
- Verbindet die Claude-App mit der `.mcp.json` (absoluter Python-Pfad) sauber?
- Dürfen wir den Claude-Installer ins Offline-Paket legen? (Python und Git ja, Open Source.)
- Windows-Installer-Beschriftungen von Python/Git stimmen mit der Anleitung überein?
- Zusatz-Audit (siehe [PROBELAUF_2026-11-12.md](PROBELAUF_2026-11-12.md)): Git Bash gefunden? `py -3` ohne Rückfragen? Portbereiche? Firmenzertifikat für Python und Git? Mac-Gastkonto mit Git und Python?

Nicht getestet: Windows (nur CI), Claude-App-Anbindung mit echtem Client (der MCP-Server ist per Protokolltest geprüft).

## 9. Spielregeln für Inhalte

- Alle Personen, Firmen, Mails, Lieferungen, Messwerte und die Verordnung
  sind **erfunden**. Kunden-E-Mail-Adressen nur auf `example.com` oder
  `.invalid`, damit nie etwas an echte Menschen gehen kann.
- Produktnamen sind erfunden und lehnen sich nicht an Sthamer-Marken an.
- Kein Rechtsrat: Das System zeigt, wie man einen **prüfbaren Prozess** baut,
  nicht, was rechtlich gilt.
- Keine Geheimnisse, Schlüssel oder `.env` im Repo.
