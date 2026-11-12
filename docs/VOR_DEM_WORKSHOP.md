# Vor dem Workshop: deine Checkliste

Ein paar Dinge brauchen **etwas Vorlauf**. Erledige sie **eine Woche vorher**,
dann startet der Workshop-Tag ohne Wartezeit. Alles ist in 20 bis 30 Minuten
gemacht.

## Eine Woche vorher

1. **Claude-Konto anlegen und Claude Pro aktivieren.**
   - Du bekommst von uns (oder von Sthamer) eine **Einladung oder einen Zugang
     zu Claude Pro**. Nimm sie an, bevor der Workshop beginnt.
   - Lege das Konto **auf deinem eigenen Gerät** an (privater Rechner oder
     Handy). Auf dem Gastgerät hast du am Workshop-Tag keinen Zugriff auf dein
     Firmenpostfach.
   - Halte dein **Handy bereit**: Bei der Anmeldung kann eine
     **Telefon-Bestätigung** (SMS-Code) verlangt werden. Das geht nur einmalig.
2. **Anmeldung testen.** Öffne **claude.ai** im Browser, melde dich an und
   stelle eine Frage („Erkläre mir in drei Sätzen, was ein Schaumlöschmittel
   ist“). Schau in den Einstellungen nach, dass dein Konto als **Pro** geführt
   wird (die Bezeichnung kann leicht abweichen). Klappt etwas nicht: sag uns
   noch in dieser Woche Bescheid, nicht erst am Workshop-Tag.
3. **Zugriff auf deine Mail am Handy** prüfen. Die Anmeldung auf dem Gastgerät
   funktioniert über einen **Code oder Link per Mail**. Du brauchst also die
   Mail-App auf dem Handy, mit dem Postfach, das du für Claude angegeben hast.
4. **Nichts Echtes mitbringen.** Im Workshop sind **alle Daten erfunden**.
   Bring bitte **keine echten Kundendaten, Preise, Rezepturen oder Verordnungs-
   entwürfe** auf das Gastgerät und kopiere nichts Internes in Claude. Wenn du
   eigene Fälle für den „Bring Your Own Case“-Teil im Kopf hast: notiere sie in
   Stichworten ohne echte Namen.
5. **Ladekabel** und ein Headset oder Kopfhörer einpacken (für die Pause
   nicht nötig, aber praktisch für Videos).

## Am Workshop-Tag: Test 5 Minuten vorher

Am Gastgerät, **bevor wir anfangen** (so entdecken wir Probleme früh):

1. **Im Gäste-WLAN anmelden.** Öffne den Browser und rufe eine beliebige Seite
   auf. Meldet das WLAN eine Anmeldeseite, melde dich dort an.
2. **Claude öffnen:** `claude.ai` im Browser oder die Claude-App. Du bist
   angemeldet? Dann erscheint dein Konto, und du siehst den Bereich **„Code“**.
3. **Terminal öffnen** (siehe `docs/INSTALL_WINDOWS.md` bzw. `docs/INSTALL_MAC.md`,
   Abschnitt „Das Terminal öffnen“). Im Ordner `dr-sthamer`:

   ```
   python check.py
   ```

   (Mac: `python3 check.py`.)
4. **Ergebnis lesen:** Jede Zeile OK, ACHTUNG oder FEHLER. Bei FEHLER: Hand
   heben und den **Support-Code** vom Ende der Ausgabe nennen.

**Bereit, wenn:** Claude geöffnet und angemeldet ist, `check.py` ohne FEHLER
endet und du dein Handy für einen eventuellen Anmeldecode zur Hand hast.

## Wenn etwas nicht klappt

- **Konto oder Einladung:** Schreib uns noch in der Woche vorher.
- **Installation auf dem Gastgerät:** Die Anleitung steht in
  [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) bzw. [INSTALL_MAC.md](INSTALL_MAC.md).
- **Am Tag selbst:** Hand heben. Zur Not arbeitest du zu zweit an einem Gerät
  („Buddy-Modus“), das ist im Workshop völlig in Ordnung.

## Beim ersten Öffnen in der Claude-App

Die App stellt zwei Rückfragen: **„Vertraust du diesem Ordner?“** und **„Darf das Werkzeug sthamer-sys
verwendet werden?“** Beide Male **Ja**. Ohne diese Zustimmung kann Claude die Werkzeuge nicht benutzen. Beim
allerersten Start fehlen sie ohnehin noch: Claude bittet dich dann, eine **neue Sitzung im selben Ordner** zu öffnen
und „weiter mit Drill 1“ zu schreiben.
