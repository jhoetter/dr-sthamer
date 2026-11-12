# Offline-Paket (USB-Stick oder Netzlaufwerk)

Das Paket ist unser **Rückfall**, wenn Downloads oder Klonen auf den
Gastgeräten nicht klappen (Gäste-WLAN langsam oder gesperrt, GitHub nicht
erreichbar, 16 Geräte laden gleichzeitig). Es ersetzt **nicht** die
Internetverbindung zu Claude: Die Claude-App braucht immer Zugang zu
`claude.ai` und `api.anthropic.com`.

## Inhalt

Alles liegt in einem Ordner **`sthamer-offline`** auf 2 bis 3 USB-Sticks
(oder einer Freigabe, die auch im Gäste-WLAN erreichbar ist).

| Datei oder Ordner | Zweck | Quelle (Seite, nicht fester Link) | Version / geprüft am |
| --- | --- | --- | --- |
| `python-windows-x64.exe` | Python 3.12 oder 3.13, „Windows installer (64-bit)“ | python.org/downloads/windows | ________ |
| `python-macos.pkg` | Python 3.12 oder 3.13, „macOS 64-bit universal2 installer“ | python.org/downloads/macos | ________ |
| `git-windows-x64.exe` | Git for Windows, „64-bit Setup“ | git-scm.com/download/win | ________ |
| `Claude-Windows.exe` | Claude-App für Windows | claude.ai/download | ________ |
| `Claude-Mac.dmg` | Claude-App für Mac | claude.ai/download | ________ |
| `dr-sthamer.zip` | Repo-Stand (ohne `.git`), mit Ordner `dr-sthamer/` | selbst erzeugt (unten) | Commit ________ |
| `SHA256SUMS.txt` | Prüfsummen aller Dateien | selbst erzeugt | ________ |
| `LIESMICH.txt` | Kurzanleitung (Verweis auf `docs/INSTALL_*.md`, die als Ordner `docs/` mitliegen) | – | – |

Den Ordner `docs/` aus dem Repo mitkopieren, damit die Anleitung **ohne
Internet lesbar** ist.

### Lizenz und Weitergabe

- **Python** (PSF-Lizenz) und **Git** (GPL v2) sind Open Source und dürfen
  unverändert weitergegeben werden. Die Lizenztexte liegen den Installern bei.
- **Claude-App:** Wir wissen **nicht sicher**, ob die Weitergabe des Installers
  durch Dritte erlaubt ist. Bitte vor dem Erstellen die Nutzungsbedingungen von
  Anthropic prüfen. Im Zweifel legen wir den Installer nur auf unsere eigenen
  Sticks, geben ihn nicht öffentlich weiter und löschen ihn nach dem Workshop.
- **Alle Teilnehmenden-Daten im Paket sind erfunden.** Keine Schlüssel,
  Zugangsdaten oder `.env`-Dateien auf den Stick legen.

## Paket erzeugen (Checkliste)

*(Ein Skript dafür folgt später, jetzt manuell.)*

1. [ ] Aktuellen Stand von `main` ziehen, Tests laufen lassen
   (`python -m unittest discover -s tests`) und `python check.py --offline`.
2. [ ] Repo-ZIP bauen, **mit** Ordner `dr-sthamer/` darin (so entpackt es sich
   ohne doppelte Verschachtelung):

   ```
   git archive --format=zip --prefix=dr-sthamer/ -o dr-sthamer.zip HEAD
   ```

3. [ ] Installer von den Seiten in der Tabelle herunterladen; bei Python
   die **Version 3.12 oder 3.13** wählen, nicht „Python install manager“.
4. [ ] Prüfsummen erzeugen und in `SHA256SUMS.txt` speichern:
   - Mac: `shasum -a 256 *.exe *.pkg *.dmg *.zip > SHA256SUMS.txt`
   - Windows: `certutil -hashfile <Datei> SHA256`
5. [ ] Den Stick auf **einem sauberen Windows-Gerät und einem Mac** durchspielen
   (Abschnitt „Ablauf“).
6. [ ] Stick mehrfach kopieren (2 bis 3 Stück) und beschriften.
7. [ ] Version und Datum in der Tabelle oben eintragen.

## Ablauf der Offline-Installation (für Teilnehmende)

**Windows**

1. Stick einstecken, Ordner `sthamer-offline` öffnen.
2. `python-windows-x64.exe` starten: **„Add python.exe to PATH“** anhaken,
   „Use admin privileges when installing py.exe“ **AUS**, **Install Now**.
3. `git-windows-x64.exe` starten: überall **Next**, beim Editor
   **„Use Notepad“** wählen.
4. `Claude-Windows.exe` starten, anmelden (Internet nötig).
5. `dr-sthamer.zip` in den Benutzerordner `C:\Users\<du>` kopieren,
   **Rechtsklick → Alle extrahieren…** in denselben Ordner. Es entsteht
   `C:\Users\<du>\dr-sthamer`.
6. Neues Terminal öffnen: `cd dr-sthamer`, dann `python check.py`.
7. Weiter wie in `docs/INSTALL_WINDOWS.md`, **Schritt 6**.

**Mac**

1. Terminal öffnen und `git --version` tippen. Erscheint der
   Befehlszeilentools-Dialog, ist das die Git/Python-Installation (Internet
   nötig). Alternativ `python-macos.pkg` doppelklicken und installieren.
2. `Claude-Mac.dmg` öffnen, App nach „Programme“ ziehen, öffnen, anmelden.
3. `dr-sthamer.zip` in den Benutzerordner kopieren und doppelklicken.
4. Terminal: `cd ~/dr-sthamer`, dann `python3 check.py`.
5. Weiter wie in `docs/INSTALL_MAC.md`, **Schritt 5**.

## Prüfung der Dateien (empfohlen)

Wer sichergehen will, vergleicht die Prüfsumme (SHA-256) einer Datei mit
`SHA256SUMS.txt`:

- Windows: `certutil -hashfile python-windows-x64.exe SHA256`
- Mac: `shasum -a 256 python-macos.pkg`

Stimmen die Werte nicht überein: Datei **nicht** ausführen, uns Bescheid sagen.

## Was wir noch nicht wissen

- Ob die Claude-App sich ohne Administratorrechte installieren lässt (steht im
  Probelauf an, siehe [IT_VORAB.md](IT_VORAB.md)).
- Ob die Dateinamen der Installer beim Download von den Seiten so ausfallen,
  wie wir sie oben benannt haben (wir benennen sie beim Kopieren um).
