# Für die IT von Dr. Sthamer: Vorbereitung der Gastgeräte

Dieses Dokument richtet sich an die IT. Die Kurzfassung auf einer Seite steht in [IT_CHECKLISTE.md](IT_CHECKLISTE.md). Es beschreibt, was die Gastgeräte und
das Gäste-WLAN für den dreitägigen Workshop (Mi–Fr) (ITMP SG, Veranstalter mit Dr. Sthamer als Kunde) brauchen:
Tag 1 „AI Augmentation“ (Mi 25.11.2026), Tag 2 **„Agentische Systeme“** (Do 26.11.2026) und Tag 3 (Fr 27.11.2026, eigener Fall). Alle Tage nutzen dieselben Geräte, dieselbe Software
und denselben Ordner `dr-sthamer`; das Profil muss also über Nacht erhalten bleiben. Es ist bewusst kurz und enthält eine
Checkliste zum Abhaken.

**Worum es geht:** Alle Teilnehmenden arbeiten an einem Sthamer-Arbeitsgerät mit
einem **Gastbenutzer** im **Gäste-WLAN**. Sie installieren **Python 3** und
**Git**, laden ein Übungs-Repo mit **ausschließlich erfundenen Daten** und
benutzen die **Claude-App** (Claude Pro, Bereich „Code“). Alles läuft lokal auf
dem Gerät. Es gibt **keine** Anbindung an Sthamer-Systeme, keine echten Daten
und keinen Mailversand.

> **Ehrlicher Stand:** Die Domainliste unten stammt aus unserem Kenntnisstand,
> nicht aus einer Messung. Wir bitten darum, sie **mit einem Probe-Gastkonto am
> Vortag zu prüfen** (siehe Abschnitt 5). Was wir nicht sicher wissen, ist
> markiert.

## 1. Was ein Gastbenutzer können muss

| Anforderung | Warum | Wenn nicht möglich |
| --- | --- | --- |
| **Software für den eigenen Benutzer installieren** (ohne Administratorrechte) | Python und Git lassen sich pro Benutzer installieren, die Claude-App ebenfalls (zu prüfen) | **Besser:** die IT installiert Python 3.12 (für alle Benutzer, „Add to PATH“), Git for Windows und die Claude-App **vorab** auf den Geräten. Dann entfällt der Installationsteil für die Teilnehmenden. |
| **Programme aus dem Benutzerprofil ausführen** (`%LocalAppData%\Programs\...`) | Die Benutzer-Installation legt Python und Git dorthin | Bei **AppLocker/WDAC**-Regeln, die nur `Program Files` erlauben, läuft eine Benutzer-Installation **nicht**. Dann vorab für alle installieren (siehe oben). |
| **Schreibrecht im Benutzerprofil** | Der Ordner `dr-sthamer` liegt unter `C:\Users\<Gast>\dr-sthamer`, dazu eine lokale Datenbank | – |
| **Skripte (Python, `.py`) dürfen laufen** | check.py und die Anwendung sind Python-Skripte | Freigabe oder Vorab-Installation |
| **Lokaler Webserver auf 127.0.0.1** (Port 3005, bei Belegung ein anderer; an Tag 1 zusätzlich Port 8137 für die Ergebnisseiten) | Die Kommandozentrale und die Dashboards von Tag 1 sind Webseiten auf dem eigenen Gerät | Lokale Firewall darf Loopback nicht blockieren. Es wird **nichts** im Netz geöffnet. |
| **Ein Profil, das den Tag über bestehen bleibt** | Temporäre Gast- oder „TEMP“-Profile löschen beim Abmelden alles | Während des Workshops nicht abmelden/neu starten. Nach einem Neustart müssen die Teilnehmenden sich neu in Claude anmelden. |

**Nicht nötig:** `pip`, PyPI, Node.js, npm, Docker, Administratorrechte zur
Laufzeit, offene eingehende Ports.

**Hinweise zu Windows und Mac (aus unserem Audit des Programms):**

- **Python 3.12** nehmen, nicht 3.13: Es prüft Zertifikate strenger und macht hinter einer TLS-Inspektion eher Probleme.
- **Git Bash** muss mitinstalliert sein („Git for Windows“ mit den Standardeinstellungen). Die Claude-App führt Befehle auf Windows darüber aus; fehlt es, geht es nicht.
- Nach dem Installieren die **Claude-App beenden und neu öffnen**, sonst kennt sie die neuen Programme nicht.
- **TLS-Inspektion:** Windows-Python nutzt den Windows-Zertifikatspeicher, ein verteiltes Prüfzertifikat greift also. Git for Windows braucht dazu das HTTPS-Backend „Windows Secure Channel“. Das Apple-Python am Mac nutzt den Schlüsselbund nicht: dort die Domains ausnehmen.
- **Mac:** Die Apple-Befehlszeilentools (Git **und** Python 3 kommen damit) brauchen in der Regel Administratorrechte, im Gastkonto also **vorab installieren**.
- Der Benutzerordner liegt **lokal** (kein Netzlaufwerk), die Datenbank macht sonst Fehler.
- **PAC- und WPAD-Dateien** zur automatischen Proxy-Erkennung kennt die Software nicht. Für die Probe: Ist ein Proxy Pflicht, dann bitte als feste Adresse nennen.

## 2. Gäste-WLAN: Domains, die erreichbar sein müssen (HTTPS, Port 443)

Bitte **vollständig mit Unterdomains** freigeben (Wildcard), wo angegeben.

**Pflicht für den Ablauf (Claude und Repo):**

| Domain | Wofür | Sicherheit der Angabe |
| --- | --- | --- |
| `claude.ai` | Anmeldung, Claude-App und Claude Code | sicher |
| `api.anthropic.com` | Claude-Modellzugriff | sicher |
| `github.com` | Repo klonen | sicher |
| `codeload.github.com` | ZIP-Download des Repos | wahrscheinlich |
| `raw.githubusercontent.com` | einzelne Dateien | wahrscheinlich, evtl. nicht nötig |
| `objects.githubusercontent.com`, `release-assets.githubusercontent.com` | Release-Dateien (Git for Windows, Offline-Paket) | wahrscheinlich: GitHub hat die Hosts für Release-Downloads geändert |
| `api.agentmail.to` | **Nur bei Live-E-Mail (AgentMail):** Übungsmails zwischen unseren Testpostfächern abrufen und senden (HTTPS, einfache Abfragen, keine Dauerverbindung) | sicher (aus der Schnittstellenbeschreibung des Anbieters); ob wir den EU-Endpunkt `api.agentmail.eu` nutzen, klären wir vorab |

**Nur nötig, wenn die Teilnehmenden selbst installieren:**

| Domain | Wofür | Sicherheit der Angabe |
| --- | --- | --- |
| `python.org`, `www.python.org` | Python-Installer | sicher |
| `git-scm.com` | Git-Downloadseite | sicher |
| `github.com/git-for-windows/...` und die GitHub-Release-Hosts oben | Git-for-Windows-Installer | wahrscheinlich |
| Download-Host der Claude-App (Link von `claude.ai/download`) | Installer der Claude-App | **unbekannt**: wir ermitteln den Host bei der Probe (Browser-Entwicklertools, Reiter „Netzwerk“) |

**Möglicherweise zusätzlich nötig (nicht verifiziert):** weitere Hosts von
`anthropic.com`/`claude.com` für Anmeldung und Auto-Update der Claude-App
(z. B. Dienst-Subdomains), außerdem Telemetrie-Hosts. Bitte beim Probelauf
Blockierungen im Proxy- oder Firewall-Protokoll ansehen und dort nachfreigeben.
Eine pauschale Freigabe von `*.anthropic.com` und `*.claude.ai` ist die
einfachste Lösung, falls eure Richtlinie das zulässt.

**Nicht nötig:** `pypi.org`, `files.pythonhosted.org`, `npmjs.org`, eine eigene Mail-Domain, Zugriff auf Sthamers Mailserver, WebSocket-Verbindungen.

## 3. Proxy, TLS-Inspektion, Anmeldeseite

- **TLS-Inspektion** (Aufbrechen von HTTPS): Claude und Git können damit
  Zertifikatsfehler melden, wenn das Zertifikat der Prüfinstanz auf dem Gerät
  nicht vertraut wird. Bitte **für die oben genannten Domains ausnehmen** oder
  das Prüfzertifikat auf den Geräten installieren.
- **Anmeldeseite des Gäste-WLANs (Captive Portal):** Teilnehmende melden sich
  einmal im Browser an. Bitte eine **Sitzungsdauer von mindestens 10 Stunden**
  einstellen, damit niemand mitten im Workshop herausfliegt, und keine
  Begrenzung pro Gerät unter dem, was ein Download von etwa 300 MB je Gerät
  braucht (Python, Git, Claude-App; bei 16 Geräten rund 5 GB insgesamt).
- **Proxy:** Falls ein Proxy Pflicht ist, bitte die Adresse und die Frage der
  Anmeldung am Proxy vorab nennen. Wir sehen im Systemcheck nur, **ob** ein
  Proxy eingestellt ist, nie seine Zugangsdaten.
- **Client-Isolation** im Gäste-WLAN ist unproblematisch: Die Geräte müssen sich
  nicht gegenseitig erreichen.

## 4. Sicherheitssoftware

- **Defender / Virenschutz:** Ein Ausschluss ist **nicht nötig**, aber bitte am
  Probegerät prüfen, ob `python.exe` Skripte aus dem Benutzerprofil ausführen
  darf und ob der lokale Webserver (127.0.0.1) nicht gestört wird.
- **AppLocker / WDAC / Intune-Richtlinien:** siehe Abschnitt 1, Zeile 2.
- **EDR-Produkte:** Python-Skripte, die einen lokalen Server starten, lösen bei
  manchen Produkten Warnungen aus. Bitte Warnungen beim Probelauf ansehen.
- **SmartScreen:** Installer können „Der Computer wurde durch Windows geschützt“
  melden. Die Teilnehmenden klicken „Weitere Informationen → Trotzdem
  ausführen“. Falls das gesperrt ist: Vorab-Installation (Abschnitt 1).

## 5. Probelauf am Vortag (bitte unbedingt)

Wir bitten um **ein Probe-Gastkonto** mit demselben Gerätetyp und denselben
WLAN-Regeln wie am Workshop-Tag (am besten einmal Windows und einmal Mac) und
eine Stunde Zeit mit einem Ansprechpartner der IT:

1. Im Gäste-WLAN anmelden.
2. Installation nach `docs/INSTALL_WINDOWS.md` bzw. `docs/INSTALL_MAC.md`.
3. `python check.py` ausführen; Ergebnis und Support-Code festhalten.
4. In der Claude-App anmelden, Bereich „Code“ öffnen.
5. Kommandozentrale starten und einen Durchlauf von Drill 1 machen.
6. Alles Blockierte im Proxy- oder Firewall-Protokoll notieren und freigeben.

## 6. Checkliste zum Abhaken

**Geräte und Konten**

- [ ] Gastbenutzer pro Teilnehmendem (plus 2 Reservegeräte) vorbereitet
- [ ] Gastprofil bleibt den ganzen Tag bestehen (kein Löschen beim Abmelden)
- [ ] Benutzer-Installation erlaubt **oder** Python 3.12, Git, Claude-App vorab installiert
- [ ] AppLocker/WDAC-Regeln geprüft (Programme aus dem Benutzerprofil)
- [ ] Skripte und lokaler Webserver auf 127.0.0.1 erlaubt

**Netzwerk**

- [ ] Domains aus Abschnitt 2 freigegeben (mit Probe-Konto geprüft)
- [ ] TLS-Inspektion für diese Domains ausgenommen oder Zertifikat verteilt
- [ ] WLAN-Sitzung mindestens 10 Stunden, Bandbreite für 16 Geräte gleichzeitig geprüft
- [ ] Proxy-Angaben (falls vorhanden) an uns übermittelt

**Probelauf**

- [ ] Probe-Gastkonto (Windows) am Vortag durchgespielt
- [ ] Probe-Gastkonto (Mac) am Vortag durchgespielt
- [ ] Support-Codes und Blockierungen notiert und an uns gesendet

**Am Workshop-Tag**

- [ ] Ansprechperson der IT (Name, Telefon): ______________________
- [ ] Erreichbar von __:__ bis __:__ Uhr, Ersatzperson: ______________________
- [ ] Zwei Reservegeräte bereit (Buddy-Modus)
- [ ] Offline-Paket (USB-Stick) liegt bereit (siehe `docs/OFFLINE_PAKET.md`)

## 7. Was wir *nicht* wissen (und beim Probelauf klären)

- Die genauen Download-Hosts der Claude-App und weitere benötigte Anthropic-Domains.
- Ob die Claude-App sich **ohne Administratorrechte** installieren lässt.
- Ob die Claude-App im Bereich „Code“ auf Windows **zwingend Git** voraussetzt
  (nach unserem Kenntnisstand ja).
- Wie sich die Gastprofile bei Neustart und Abmeldung verhalten.
- Wie das Gäste-WLAN mit 16 gleichzeitigen Downloads umgeht.
