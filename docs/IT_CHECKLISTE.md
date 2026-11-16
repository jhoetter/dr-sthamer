# Workshop „Agentische Systeme“ bei Dr. Sthamer: Was die IT bereitstellen muss

Kurzfassung für die IT-Leitung. Alle Details, Domainlisten und die Fehlersuche stehen in [IT_VORAB.md](IT_VORAB.md).

**Worum es geht:** Alle Teilnehmenden arbeiten an einem Sthamer-Arbeitsgerät mit **Gastbenutzer im Gäste-WLAN**. Sie benutzen die
**Claude-App** (Bereich „Code“) und eine kleine Übungs-Software, die lokal auf dem Gerät läuft. Alle Daten im Workshop sind
**erfunden**. Es gibt keine Anbindung an Sthamer-Systeme und keinen Mailversand.

| | |
| --- | --- |
| Termin | ______________ |
| Teilnehmende | ____ (geplant 10 bis 16), dazu **2 Reservegeräte** |
| Ansprechperson ITMP SG | Johannes Hötter, ______________ |
| Ansprechperson IT Sthamer (am Tag erreichbar) | ______________ |

## Das brauchen wir

**1. Geräte und Gastbenutzer**
- Ein Gastbenutzer pro Teilnehmendem. Ein Gerät ist ein Mac, alle anderen Windows (10 oder 11).
- Das Profil **bleibt den ganzen Tag bestehen** (kein Löschen beim Abmelden, kein Neustart zwischendurch).
- Der Benutzerordner liegt **nicht in OneDrive** und ist nicht umgeleitet; der Gast darf in sein Profil schreiben.

**2. Software, bitte vorab auf allen Geräten installieren**

| Software | Hinweis |
| --- | --- |
| **Claude-App** (Desktop, Bereich „Code“) | Download über `claude.ai/download`. Für alle Benutzer installieren. |
| **Git** | Windows: „Git for Windows“ (`git-scm.com`). Mac: Befehlszeilentools oder Git von git-scm.com, **bitte vorab** (die Apple-Befehlszeilentools brauchen in der Regel Administratorrechte). |
| **Python 3** | **Version 3.12** (3.13 prüft Zertifikate strenger und macht hinter einer TLS-Inspektion eher Probleme). Windows: „Add python.exe to PATH“ aktivieren, **nicht** nur den Platzhalter aus dem Microsoft Store. Am Mac reicht das Python der Apple-Befehlszeilentools (3.9, kommt mit Git zusammen, also ebenfalls vorab). |
| Ein aktueller **Browser** (Chrome oder Edge) | Die Übungs-Software öffnet sich im Browser auf dem eigenen Gerät. |

Sind die Programme vorinstalliert, entfällt der Installationsteil für die Teilnehmenden. Ist das nicht möglich, müssen
Benutzer-Installationen **ohne Administratorrechte** erlaubt sein (siehe Punkt 5).

**3. Claude-Konten**
- Jede teilnehmende Person hat ein **Claude-Pro-Konto**. Die Anmeldung läuft per E-Mail-Code oder Link. Auf dem Gastgerät gibt es
  **keinen Zugriff auf das Firmenpostfach**: Der Code muss auf dem **Handy** oder in einem Webmail-Zugang ankommen.
- Mit der Einladung bitte **eine Woche vorher** anmelden lassen (siehe `VOR_DEM_WORKSHOP.md`).
- Nach dem Installieren die **Claude-App beenden und neu öffnen**, sonst kennt sie die neuen Programme nicht.

**4. Netzwerk (Gäste-WLAN)**
- Freigabe von **`claude.ai`**, **`api.anthropic.com`** (am einfachsten `*.claude.ai` und `*.anthropic.com`) und **`github.com`**
  (dazu `codeload.github.com` und `*.githubusercontent.com`) auf Port 443.
- **Optional, wenn wir E-Mail live mitbringen (AgentMail): `api.agentmail.to`** auf Port 443. Es laufen nur Mails zwischen unseren eigenen Testpostfächern; eine Dauerverbindung brauchen wir nicht.
- **Repo, das wir nutzen: `https://github.com/jhoetter/dr-sthamer`.** Die Teilnehmenden laden es per HTTPS (Port 443) herunter; SSH (Port 22) ist nicht nötig.
- **TLS-Inspektion** für diese Domains ausnehmen oder das Prüfzertifikat im Windows-Zertifikatspeicher verteilen. Bei Git for Windows dann „Windows Secure Channel“ als HTTPS-Backend wählen; am Mac liest das Apple-Python das Zertifikat nicht aus dem Schlüsselbund, deshalb dort besser ausnehmen.
- Sitzungsdauer des WLAN-Portals **mindestens 10 Stunden**. Das WLAN muss **bis zu 16 Geräte gleichzeitig** tragen (Downloads, laufende Claude-Sitzungen).
- Falls ein **Proxy** Pflicht ist: Adresse und Anmeldeart vorab nennen.

**5. Rechte und Sicherheitssoftware**
- **Python-Skripte** aus dem Benutzerprofil dürfen laufen (bei AppLocker oder WDAC prüfen), ebenso ein **lokaler Webserver auf
  127.0.0.1** (Port 3005). Es wird nichts im Netz geöffnet und kein eingehender Port gebraucht.
- Virenschutz und EDR: Ein Ausschluss ist nicht nötig, aber bitte **im Probelauf** auf Warnungen achten.

**6. Probelauf am Vortag (eine Stunde, bitte unbedingt)**
- Ein **Probe-Gastkonto** je Gerätetyp (einmal Windows, einmal Mac) im Gäste-WLAN, mit einer Ansprechperson der IT.
- Wir spielen den Anfang durch (Anmeldung in Claude, Software starten) und halten Blockierungen aus dem Proxy- oder Firewall-Protokoll fest. Das ist die wichtigste Einzelmaßnahme.

**7. Am Workshop-Tag**
- Die IT-Ansprechperson ist **erreichbar** (Name, Telefon oben eintragen).
- Zwei Reservegeräte stehen bereit (zu zweit an einem Gerät arbeiten ist unser Notfallweg).
- Wir bringen einen **USB-Stick** mit Installern und Übungs-Software mit, falls Downloads oder GitHub nicht klappen. Bitte prüfen, ob USB-Speicher auf den Geräten per Richtlinie erlaubt ist.

**8. Nach dem Workshop**
- Gastprofile löschen oder zurücksetzen. In der Claude-App abmelden. Der Ordner `dr-sthamer` enthält nur erfundene Daten und kann gelöscht werden.

## Was **nicht** nötig ist

`pip`, PyPI, Node.js, Docker, Administratorrechte zur Laufzeit, eingehende Ports, Zugriff auf Sthamer-Systeme oder Mailserver.

## Welche Daten wohin gehen

- Was Teilnehmende in Claude schreiben, geht an **Anthropic** (über `claude.ai` und `api.anthropic.com`). Es sind **erfundene Daten**; echte
  Kunden-, Preis- oder Rezepturdaten bitte nicht eingeben (wir weisen im Workshop ausdrücklich darauf hin).
- Bei Live-E-Mail laufen die Übungsmails über den Dienst **AgentMail** (`agentmail.to`). Die Postfächer gehören uns, der Inhalt ist erfunden, und es gibt keine Anbindung an Sthamers Mailserver.
- Die Übungs-Software kommt von **GitHub** (`https://github.com/jhoetter/dr-sthamer`) und läuft **nur lokal** auf dem Gerät. „Senden“ legt Mails nur als Datei im
  Ordner `postausgang` ab, es verlässt nichts das Gerät.

## Offen, das wir beim Probelauf klären

- Ob sich die **Claude-App ohne Administratorrechte** installieren lässt und welche Download-Hosts sie nutzt.
- Ob „Claude Code“ in der App auf Windows **zwingend Git** voraussetzt (nach unserem Kenntnisstand ja, deshalb Git vorab).
- Ob weitere Anthropic-Hosts für Anmeldung und Aktualisierung freigegeben werden müssen.
- Wie sich die Gastprofile bei Neustart und Abmeldung verhalten.

## Checkliste zum Abhaken

- [ ] Gastbenutzer für alle Teilnehmenden plus 2 Reservegeräte, Profile bleiben bestehen
- [ ] Claude-App, Git und Python 3 auf allen Geräten installiert (oder Benutzer-Installation erlaubt)
- [ ] Browser vorhanden, Benutzerordner nicht in OneDrive
- [ ] Claude-Pro-Konten angelegt, Anmeldung eine Woche vorher getestet, E-Mail-Code auf dem Handy erreichbar
- [ ] Domains freigegeben (`claude.ai`, `api.anthropic.com`, `github.com`; bei Live-E-Mail zusätzlich `api.agentmail.to`), TLS-Inspektion ausgenommen
- [ ] WLAN: Sitzung mindestens 10 Stunden, Kapazität für 16 Geräte
- [ ] Python-Skripte und lokaler Webserver (127.0.0.1) erlaubt, Sicherheitssoftware geprüft
- [ ] Probelauf am Vortag mit Windows- und Mac-Gastkonto durchgeführt, Blockierungen freigegeben
- [ ] IT-Ansprechperson am Workshop-Tag benannt und erreichbar
