# Tag 2: Material zum Vortrag

Die Anwendung für Tag 2 („Agentische Systeme“, Donnerstag, 26.11.2026) liegt an der **Wurzel** des Repos, nicht hier. Dieser Ordner enthält nur das Begleitmaterial.

## Vortrag «Jede Aufgabe zuerst agentisch» (Johannes Hötter)

`impuls/Impuls — Jede Aufgabe zuerst agentisch.html` im Browser öffnen: 37 Folien, eine Datei (reveal.js, Schriften und ITMP-Logo eingebettet), die Bilder liegen in `impuls/assets/agentisch/`. Läuft ohne Internet. Pfeiltasten blättern, **S** öffnet die Referentenansicht mit Notizen, **F** Vollbild, **ESC** Übersicht.

Inhalt in vier Teilen:

1. **Einstieg:** Humanity's Last Exam (Stand 25. November 2026: Claude Fable 5.2 mit 74,2 % laut Anthropic) und METR-Aufgabenhorizont (Q4-Update vom 20. November 2026: Verdopplung etwa alle 3,6 Monate, bis zu 27 Stunden auf der prüfbaren Teilmenge). Die Notizen (Taste S) nennen die Quellen und sagen, wo die Zahlen nicht direkt vergleichbar sind.
2. **Aus der Praxis:** wie Johannes agentisch arbeitet (Token, Kosten, Google Ads, Dashboards, Videos, Beispiele mit Screenshots).
3. **Das Prinzip:** jede Aufgabe zuerst agentisch versuchen, Verifier's Law, Agent und Tracker.
4. **Größer gedacht:** System-Denken, Law of Amplification (Erzeugen ×100, Prüfen bleibt menschlich), Personas, offene Frage zur Zusammenarbeit von Menschen und Agenten. Es folgen die Folien «Sechs Bausteine» und «Zwei Kontrollen» (das Raster für den Tag), dann «Wo darf der Agent handeln?» und zuletzt die Passwort-Folie für das E-Mail-Postfach.

Herkunft: Das Deck stammt aus dem Repo `jhoetter/pfefferminzia` (Juni 2026) und ist hier auf den Workshop bei Dr. Sthamer angepasst (ITMP-Logo, Fußzeile, Überleitung zur Regulatorik-Werkstatt). Die Inhalte der Folien sind sonst unverändert. Die Folie «Kern AI gegründet. Verkauft. Wieder am Bauen.» ist der Stand von Juni 2026.

Platz im Ablauf: Donnerstag 09:00 bis 09:45, „Input“ (darf länger gehen; vertiefen auf der Tonspur). Die Datei selbst ist die Quelle und kann direkt bearbeitet werden.

**Passwort-Folie:** Sie zeigt das Passwort aus der lokalen `.env` (Zeile `POSTFACH_PASSWORT=…` im Hauptordner). Einmal `python3 scripts/passwort_folie.py` ausführen; das schreibt `impuls/passwort.js`. Beide Dateien sind von Git ausgeschlossen und kommen nie ins Repository. Fehlt `passwort.js`, steht auf der Folie «steht an der Tafel».
