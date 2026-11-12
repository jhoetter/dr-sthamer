# Installation auf dem Mac

Diese Anleitung bringt dein Mac-Gerät in etwa **20 Minuten** an den Start
(plus Wartezeit beim Herunterladen). Du brauchst kein Vorwissen. Nach jedem
Schritt steht, woran du erkennst, dass es geklappt hat. Alle Daten im Workshop
sind erfunden.

Du brauchst: **Git**, **Python 3**, die **Claude-App** und **unseren Ordner**
`dr-sthamer`. Die „Befehlszeilentools“ von Apple bringen Git **und** Python 3
in einem Rutsch mit. Das reicht für uns.

> **Gastkonto auf dem Mac:** Ist dein Konto das eingebaute macOS-**„Gast“**-Konto,
> werden beim Abmelden **alle Dateien gelöscht**. Das ist für den Workshop
> in Ordnung, du musst dich aber nach dem Neustart neu in Claude anmelden. Sag
> uns Bescheid, wenn du etwas behalten willst.

## Vorweg: das Terminal öffnen

1. Drücke **Cmd + Leertaste** (Spotlight).
2. Tippe **Terminal** und drücke **Enter**.

**So erkennst du, dass es geklappt hat:** Ein Fenster mit einer Textzeile
öffnet sich. Befehle tippst du dort ein und bestätigst mit **Enter**.

---

## Schritt 1: Git und Python (Befehlszeilentools)

Tippe im Terminal:

```
git --version
```

- Erscheint `git version 2.xx …`: Die Tools sind schon da. Weiter zu Schritt 2.
- Erscheint ein Fenster **„Das Tool ‚git‘ erfordert die Befehlszeilen-Entwicklertools“**:
  Klicke **„Installieren“**, stimme den Bedingungen zu und warte. Das dauert je
  nach WLAN **5 bis 20 Minuten**. Das Fenster zeigt einen Fortschrittsbalken.
  Es kann nach einem Kennwort fragen: Dein Mac-Kennwort funktioniert, bei einem
  Gastgerät nutze das Kennwort, das du von uns oder der IT bekommen hast.
  Lässt es sich nicht installieren: sag uns Bescheid.

**So erkennst du, dass es geklappt hat:** Nach der Installation:

```
git --version
python3 --version
```

Beide zeigen eine Version. `python3` zeigt meist **Python 3.9.x**: Das ist
genug für uns.

*Alternative für ein neueres Python:* Von **python.org/downloads** das
macOS-Paket („macOS 64-bit universal2 installer“) für Python 3.12 oder 3.13
laden und starten. Danach **einmal** im Ordner **Programme → Python 3.xx** die
Datei **„Install Certificates.command“** per Doppelklick ausführen. Dieser
Schritt sorgt dafür, dass Python sichere Internetverbindungen akzeptiert.
Ohne ihn meldet der Check später Zertifikatsfehler.

## Schritt 2: Claude-App installieren und anmelden

1. Öffne im Browser **claude.ai/download** und lade die App für **Mac** herunter.
2. Öffne die heruntergeladene Datei (`.dmg`) und **ziehe Claude in den Ordner
   „Programme“**.
3. Öffne Claude aus „Programme“. macOS fragt beim ersten Start:
   **„Claude ist eine aus dem Internet geladene App. Möchtest du sie öffnen?“**
   Klicke **„Öffnen“**. (Das ist der übliche Sicherheitsdialog, kein Problem.)
4. Melde dich an: Du gibst deine E-Mail-Adresse ein, und Claude schickt dir einen
   **Code oder Link per Mail**. Schau dafür am besten auf deinem **eigenen
   Handy** nach.
5. Du brauchst ein **Claude-Pro-Konto** (siehe
   [VOR_DEM_WORKSHOP.md](VOR_DEM_WORKSHOP.md)).

**So erkennst du, dass es geklappt hat:** In der App siehst du oben den Bereich
**„Code“**, und du bist angemeldet.

*Meldet macOS eine App als „nicht verifiziert“ und lässt sich nicht öffnen:*
**Systemeinstellungen → Datenschutz & Sicherheit**, ganz unten bei der
gesperrten App auf **„Trotzdem öffnen“** klicken. Fehlt dieser Knopf, ist es
gesperrt: sag uns Bescheid.

## Schritt 3: Unseren Ordner holen

Der Ordner liegt in deinem **Benutzerordner**: `~/dr-sthamer` (nicht auf dem
Schreibtisch, nicht in iCloud Drive).

Tippe im Terminal:

```
cd ~
git clone https://github.com/jhoetter/dr-sthamer.git
cd dr-sthamer
```

**So erkennst du, dass es geklappt hat:** Der Befehl endet ohne rote
Fehlermeldung, und `ls` zeigt unter anderem `check.py` und `README.md`.

**Geht Klonen nicht** (GitHub fragt nach einem Kennwort, oder das WLAN
blockiert es)? Nimm den **ZIP-Weg**: Wir geben dir die Datei `dr-sthamer.zip`.
Lege sie in deinen Benutzerordner und doppelklicke sie. Es entsteht ein Ordner;
benenne ihn in `dr-sthamer` um. Der richtige Ordner ist der, in dem direkt
`check.py` liegt. Dann im Terminal: `cd ~/dr-sthamer`.

## Schritt 4: Den Systemcheck laufen lassen

Im Terminal, im Ordner `dr-sthamer`:

```
python3 check.py
```

Jede Zeile ist **OK**, **ACHTUNG** oder **FEHLER**.

- **Alles OK / nur ACHTUNG:** weiter zu Schritt 5. Lies die Zeile
  „Was tun?“ unter jeder Warnung.
- **FEHLER:** Lies „Was tun?“. Sag uns sonst Bescheid und lies uns den
  **Support-Code** vor (`STH-MAC-PY39-…`, steht am Ende).

**So erkennst du, dass es geklappt hat:** Am Ende steht „Alles grün“ oder
„Fast alles gut“ und es gibt keine Zeile mit FEHLER.

## Schritt 5: Claude startet die Kommandozentrale

1. Öffne die **Claude-App** und wähle den Bereich **„Code“**.
2. Starte eine **neue Sitzung** mit dem Ordner **`dr-sthamer`** in deinem
   Benutzerordner.
3. Schreibe:

> Richte alles nach der README ein und starte die Kommandozentrale. Ich bin in Drill 1.

Beim ersten Öffnen fragt die App, ob du dem **Ordner** vertraust: **Ja**. Wenn gefragt wird, ob das Werkzeug **„sthamer-sys“** verwendet werden darf: **Ja**.

*Kurzer Weg, wenn du Schritt 3 noch nicht gemacht hast* (Git und Python sind
installiert): Starte die Sitzung in deinem Benutzerordner und schreibe:

> Klone https://github.com/jhoetter/dr-sthamer in den Ordner dr-sthamer in meinem Benutzerordner, richte alles nach der README ein und starte die Kommandozentrale. Ich bin in Drill 1.

**So erkennst du, dass es geklappt hat:** Im Browser siehst du die
Kommandozentrale unter `http://127.0.0.1:3005` mit dem Posteingang.

---

## Fehlerbehebung

**Das Fenster „Befehlszeilentools“ erscheint nicht.**
Tippe im Terminal `xcode-select --install`. Erscheint wieder nichts oder
kommt eine Fehlermeldung, sag uns Bescheid.

**`python3` zeigt „command not found“.**
Die Befehlszeilentools fehlen noch (Schritt 1) oder die Installation läuft noch.
Warte auf das Ende, öffne ein **neues** Terminal und versuche es erneut.

**Der Check meldet bei „Internet“ einen Zertifikatsfehler, obwohl der Browser geht.**
Hast du Python von python.org installiert? Dann einmal **„Install Certificates.command“**
im Ordner **Programme → Python 3.xx** ausführen (siehe Schritt 1). Sonst: Das
Gäste-WLAN verlangt vielleicht eine Anmeldung im Browser. Öffne eine Seite und
melde dich an. Danach den Check wiederholen.

**Der Check meldet „Port 3005 ist belegt“.**
Kein Problem: Die Kommandozentrale sucht sich einen freien Port. Claude nennt
dir die Adresse, wenn sie abweicht.

**Eine Meldung „… möchte Zugriff auf Dateien im Ordner Dokumente/Schreibtisch“.**
Das kann **„Erlauben“**. Besser ist: Der Ordner liegt gar nicht dort, sondern
direkt in `~/dr-sthamer`.

**Gar nichts geht.**
Setz dich zu jemandem dazu („Buddy-Modus“). Zu zweit an einem Gerät kommt ihr
genauso durch den Workshop. Wir lösen dein Gerät in der Pause.
