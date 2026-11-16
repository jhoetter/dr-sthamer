# Installation auf Windows

Diese Anleitung bringt dein Gerät in etwa **20 Minuten** an den Start. Du
brauchst **keine Administratorrechte** und **kein Vorwissen**. Nach jedem
Schritt steht, woran du erkennst, dass es geklappt hat. Wenn nicht: ganz unten
steht die Fehlerbehebung, und wir helfen dir vor Ort.

Du installierst vier Dinge: **Python**, **Git**, die **Claude-App** und
**unseren Ordner** `dr-sthamer`. Alle Daten im Workshop sind erfunden.

> Die Download-Seiten ändern sich. Wir nennen deshalb nur die Seiten, nicht
> die genauen Dateinamen. Wenn ein Fenster anders aussieht als hier
> beschrieben: nimm die Standardwerte und ruf uns.

## Vorweg: das Terminal öffnen

Ein „Terminal“ ist ein Fenster, in das du Befehle tippst.

1. Drücke die **Windows-Taste**.
2. Tippe **Eingabeaufforderung** (oder **PowerShell**).
3. Drücke **Enter**.

**So erkennst du, dass es geklappt hat:** Ein schwarzes oder blaues Fenster
öffnet sich. Davor steht etwas wie `C:\Users\dein-name>`.

Befehle tippst du dort ein und bestätigst sie mit **Enter**. Du kannst sie auch
aus dieser Anleitung kopieren und mit Rechtsklick einfügen.

---

## Schritt 1: Python installieren

1. Öffne im Browser **python.org/downloads**.
2. Lade **Python 3.12** (nicht 3.13: es prüft Zertifikate strenger und macht
   hinter einer Firmen-Prüfung eher Probleme) als **„Windows installer (64-bit)“**
   herunter. (Auf der Seite „Download Python“ siehst du oft nur die neueste
   Version. Geh dann auf **python.org/downloads/windows** und wähle dort die
   Version 3.12.)
3. Starte die heruntergeladene Datei.
4. Im ersten Fenster:
   - Setze das Häkchen **„Add python.exe to PATH“** (unten im Fenster).
   - Lass das Häkchen **„Use admin privileges when installing py.exe“** bzw.
     **„Install launcher for all users“** **AUS**. So braucht die Installation
     keine Administratorrechte.
5. Klicke auf **„Install Now“** (nicht „Customize“).
6. Wenn „Setup was successful“ erscheint: **Close**.

**So erkennst du, dass es geklappt hat:** **Beende die Claude-App und öffne sie
neu**, falls sie schon lief (sie kennt neu installierte Programme erst nach dem
Neustart). Öffne außerdem ein **neues** Terminal (ein altes kennt Python noch
nicht) und tippe:

```
python --version
```

Es erscheint `Python 3.12.x`.

- Öffnet sich stattdessen der **Microsoft Store**: siehe Fehlerbehebung
  „python öffnet den Store“.
- Fragt der Installer nach einem **Administrator-Kennwort**: Abbrechen und uns
  Bescheid sagen. Die IT kann Python vorab installieren.

*Alternative, falls Schritt 1 nicht klappt:* Im **Microsoft Store** nach
**„Python 3.12“** suchen und installieren (braucht keinen Administrator).

## Schritt 2: Git installieren

Git holt unseren Ordner auf dein Gerät und die Claude-App braucht es auf Windows.

1. Öffne im Browser **git-scm.com/download/win**.
2. Lade den **„64-bit Git for Windows Setup“** herunter (der erste Link).
3. Starte die Datei.
   Fragt Windows nach einem Administrator-Kennwort, **klicke „Abbrechen“**: Git
   lässt sich auch **nur für dich** installieren. Starte die Datei dann noch
   einmal, am besten direkt aus dem Download-Ordner per Doppelklick, ohne
   „Als Administrator ausführen“.
4. Klicke dich durch die Fenster mit **„Next“**. **Alle Standardeinstellungen
   sind richtig.** Nur eine Frage ist wichtig:
   **„Choosing the default editor used by Git“**: Wähle
   **„Use Notepad as Git's default editor“**. (Der Standard-Editor „Vim“ ist
   für Einsteiger verwirrend.)
   Hinter einer **Firmen-Prüfung des Datenverkehrs (TLS-Inspektion)** wähle bei
   **„Choosing the HTTPS transport backend“** die Option **„Use the native
   Windows Secure Channel library“**, sonst vertraut Git dem Firmenzertifikat nicht.
5. Am Ende: **„Install“**, dann **„Finish“**. Danach die Claude-App beenden und
   neu öffnen, falls sie schon lief.

**So erkennst du, dass es geklappt hat:** Öffne ein **neues** Terminal und tippe:

```
git --version
```

Es erscheint `git version 2.xx.x.windows.x`.

## Schritt 3: Claude-App installieren und anmelden

1. Öffne im Browser **claude.ai/download** und lade die App für **Windows** herunter.
2. Starte die Datei und folge den Fenstern. Fragt die Installation nach einem
   Administrator-Kennwort: Abbrechen und uns Bescheid sagen.
3. Öffne die **Claude-App** und melde dich an. Die Anmeldung geht meist so:
   Du gibst deine E-Mail-Adresse ein, und Claude schickt dir einen **Code oder
   Link per Mail**. **Die Mail kommt in deinem Postfach an, am besten schaust du
   auf deinem eigenen Handy nach.** Auf dem Gastgerät hast du ja keinen Zugriff
   auf dein Firmenpostfach.
4. Du musst ein **Claude-Pro-Konto** haben (das bekommst du über uns, siehe
   [VOR_DEM_WORKSHOP.md](VOR_DEM_WORKSHOP.md)).

**So erkennst du, dass es geklappt hat:** In der App siehst du oben die
Bereiche, darunter **„Code“**, und du kannst dich mit deinem Namen angemeldet
sehen.

## Schritt 4: Unseren Ordner holen (klonen)

Wichtig ist **wo** der Ordner liegt: direkt in deinem **Benutzerordner**
(`C:\Users\dein-name\dr-sthamer`), **nicht** auf dem Schreibtisch, nicht in
Dokumenten und nicht in OneDrive. Diese Ordner werden oft umgeleitet und
machen Probleme.

1. Öffne ein **neues** Terminal. Es startet schon in deinem Benutzerordner
   (`C:\Users\dein-name`).
2. Tippe:

```
git clone https://github.com/jhoetter/dr-sthamer.git
```

3. Danach:

```
cd dr-sthamer
```

**So erkennst du, dass es geklappt hat:** Der Befehl zeigt am Ende
`Resolving deltas: 100%` (oder ähnlich) und vor dem Cursor steht jetzt
`C:\Users\dein-name\dr-sthamer>`.

- Fragt GitHub nach **Benutzername und Passwort**: Fenster schließen und den
  **ZIP-Weg** unten nehmen. Du brauchst kein GitHub-Konto.
- Kommt eine rote Fehlermeldung: siehe Fehlerbehebung.

### Alternative: ZIP-Weg (ohne Git)

Wenn Klonen nicht geht, brauchst du Git gar nicht für den Start:

1. Wir geben dir die Datei **dr-sthamer.zip** (per Stick, Mail oder Link).
   Auch von GitHub geht es: Seite
   `github.com/jhoetter/dr-sthamer` → grüner Knopf **„Code“** → **„Download ZIP“**.
2. Lege die ZIP-Datei in deinen Benutzerordner `C:\Users\dein-name`.
3. **Rechtsklick auf die Datei → „Alle extrahieren …“**, Ziel
   `C:\Users\dein-name`, **„Extrahieren“**.
4. Benenne den entstandenen Ordner in **`dr-sthamer`** um (er heißt oft
   `dr-sthamer-main`).
5. Öffne den Ordner. **Der richtige Ordner ist der, in dem direkt die Datei
   `check.py` liegt.** Manchmal liegt er einen Ordner tiefer (doppelt
   verschachtelt): Dann zieh den inneren Ordner nach oben.
6. Öffne ein Terminal und tippe `cd dr-sthamer`.

## Schritt 5: Den Systemcheck laufen lassen

Im Terminal, im Ordner `dr-sthamer`:

```
python check.py
```

Der Check prüft Python, Git, Schreibrechte, Umlaute und das Internet (GitHub,
Claude, Python). Jede Zeile ist **OK**, **ACHTUNG** oder **FEHLER**.

- **Alles OK:** Super, weiter zu Schritt 6.
- **ACHTUNG:** meist kein Hindernis. Lies die Zeile „Was tun?“ darunter.
  Ein Hinweis zu OneDrive oder zum Schreibtisch heißt: Ordner verschieben
  (siehe Schritt 4).
- **FEHLER:** Lies die Zeile „Was tun?“. Löse sie, wenn du kannst, und sag
  uns sonst Bescheid. Am Ende steht ein **Support-Code**
  (`STH-W11-PY312-…`): Lies ihn uns vor oder tipp ihn ab, dann sehen wir sofort,
  was auf deinem Gerät nicht passt.

Zeigt `python` einen Fehler, probiere `py check.py`.

**So erkennst du, dass es geklappt hat:** Am Ende steht „Alles grün“ oder
„Fast alles gut“, und es gibt **keine** Zeile mit FEHLER.

## Schritt 6: Claude startet die Kommandozentrale

1. Öffne die **Claude-App** und wähle den Bereich **„Code“**.
2. Starte eine **neue Sitzung** und wähle als Ordner **`dr-sthamer`** in deinem
   Benutzerordner.
3. Schreibe in das Eingabefeld:

> Richte alles nach der README ein und starte die Kommandozentrale. Ich bin in Drill 1.

Claude richtet alles ein und öffnet die Kommandozentrale im Browser
(`http://127.0.0.1:3005`). Beim ersten Öffnen fragt die App, ob du dem **Ordner** vertraust: **Ja**. Wenn gefragt wird, ob das Werkzeug **„sthamer-sys“**
verwendet werden darf: **Ja**.

*Kurzer Weg, wenn du Schritt 4 noch nicht gemacht hast* (Python und Git sind
installiert): Starte die Sitzung in deinem Benutzerordner und schreibe:

> Klone https://github.com/jhoetter/dr-sthamer in den Ordner dr-sthamer in meinem Benutzerordner, richte alles nach der README ein und starte die Kommandozentrale. Ich bin in Drill 1.

**So erkennst du, dass es geklappt hat:** Im Browser siehst du die
Kommandozentrale mit dem Posteingang.

---

## Fehlerbehebung

**`python` öffnet den Microsoft Store.**
Windows hat einen „Platzhalter“ für Python. Schließe den Store. Dann entweder
Schritt 1 wiederholen (mit dem Häkchen „Add python.exe to PATH“) oder `py`
statt `python` benutzen (`py check.py`). Ganz sicher geht es so:
**Windows-Taste → „App-Ausführungsaliase“** tippen → die Schalter bei
**„python.exe“** und **„python3.exe“** auf **Aus** stellen.

**`git` oder `python` wird „nicht erkannt“, obwohl ich es installiert habe.**
Du hast noch das **alte** Terminal. Schließe es und öffne ein **neues**.
Hilft das nicht: Gerät einmal neu starten.

**Der Installer fragt nach einem Administrator-Kennwort.**
Abbrechen. Python und Git gehen auch nur für dich. Fragt es trotzdem: sag uns
Bescheid, die IT kann beides vorab installieren.

**Windows meldet „Der Computer wurde durch Windows geschützt“ (SmartScreen).**
Klicke **„Weitere Informationen“** und dann **„Trotzdem ausführen“**. Fehlt
dieser Knopf, ist es durch die IT gesperrt: sag uns Bescheid.

**„Die Ausführung von Skripts ist auf diesem System deaktiviert“ (PowerShell).**
Öffne stattdessen die **Eingabeaufforderung** (Windows-Taste, „Eingabeaufforderung“
tippen). Dort tritt der Fehler nicht auf.

**`git clone` meldet einen Netzwerk- oder Zertifikatsfehler / GitHub nicht erreichbar.**
Das Gäste-WLAN verlangt vielleicht eine Anmeldung: Öffne einen Browser,
rufe irgendeine Seite auf und melde dich im WLAN an. Geht es dann immer noch
nicht: **ZIP-Weg** (Schritt 4).

**`python check.py` zeigt rote Zeilen bei „Internet“.**
Gleiche Ursache wie oben: erst im Browser im Gäste-WLAN anmelden, dann den
Check wiederholen. Bleibt es rot: Support-Code notieren und uns Bescheid sagen.
Der Workshop geht trotzdem, solange mindestens **claude.ai** erreichbar ist.

**Der Check meldet „Port 3005 ist belegt“.**
Kein Problem: Die Kommandozentrale sucht sich automatisch einen freien Port.
Claude sagt dir die Adresse, wenn sie von `http://127.0.0.1:3005` abweicht.

**Ein Sicherheitsprogramm blockiert Python oder die Kommandozentrale.**
Sag uns Bescheid und nenne die Meldung. Mach nichts Eigenes an den
Sicherheitseinstellungen.

**Im Browser öffnet sich nichts.**
Öffne selbst einen Browser und tippe in die Adresszeile `127.0.0.1:3005`.

**Gar nichts geht.**
Setz dich zu einer Nachbarin oder einem Nachbarn („Buddy-Modus“): Zu zweit an
einem Gerät kommt ihr genauso durch den Workshop. Wir lösen dein Gerät in der
Pause.
