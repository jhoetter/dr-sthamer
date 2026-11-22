# Datenkatalog – Übungsausschnitt Dr. Sthamer

Stand: Stichtag 28.02.2027 · Übungsfirma mit fiktiven Daten

Dieser Katalog erklärt jede Tabelle im Ordner `daten/` und die Bedeutung jeder Spalte. Kunden,
Produkte und Lieferstellen sind abgeleitet aus dem Datensatz, mit dem an Tag 2 gearbeitet wird; Aufträge,
Preislisten und alle weiteren Tabellen wurden für Tag 1 ergänzt.

## Allgemeine Regeln

- **Format:** CSV, UTF-8 (mit BOM), Trennzeichen Komma, erste Zeile = Spaltennamen.
- **Datum:** ISO-Format `JJJJ-MM-TT` (zum Beispiel `2026-04-12`). Leeres Feld = kein Wert.
- **Zahlen:** Dezimalpunkt, kein Tausendertrennzeichen (`1250.5`). Erst in Berichten und im Dashboard
  schreiben wir deutsch (1.250,5).
- **Kennungen:** Kunden `K-1001` bis `K-1032`; Produkte `P-101` bis `P-121` und `P-201` bis `P-207`;
  Lieferstellen `LS-0001` ff.
- **Interessenten** ohne Kundenstamm haben Nummern ab `K-9001`. Sie kommen nur in Unterlagen von Tag 1
  vor (Angebotseingang), nicht in den Tabellen.
- **Übungsausschnitt:** Die Tabellen enthalten ausgewählte Kunden, nicht das ganze Unternehmen.
  Firmenzahlen aus `unternehmen.md` gelten für das Gesamtunternehmen.

## kunden.csv – Kundenstamm (eine Zeile je Kunde)

| Spalte | Bedeutung |
|---|---|
| `id` | Kundennummer (`K-1001` …) |
| `name` | Firmenname des Kunden |
| `segment` | Kundensegment, zum Beispiel Industrie, Feuerwehr kommunal, Schifffahrt und Werft, Flughafen, Händler, Löschgerätehersteller, Abfallwirtschaft, Montanindustrie, Forst und Waldbrand, Übungsanlage |
| `land` | Land des Kunden als Ländercode (DE, AT, NL, PL, NO, GB, CH) |
| `sprache` | Korrespondenzsprache (`de`, `en`) |
| `ansprechpartner_name` | Hauptansprechpartner beim Kunden |
| `ansprechpartner_rolle` | Funktion des Ansprechpartners |
| `ansprechpartner_email` | E-Mail-Adresse des Ansprechpartners (fiktiv) |
| `key_account` | `ja`/`nein`: Kunde wird als Schlüsselkunde betreut |
| `ist_haendler` | `ja`/`nein`: Kunde kauft zum Weiterverkauf |
| `beliefert_endkunden` | bei Händlern: Kundennummern der Endkunden, die über diesen Händler beliefert werden, getrennt durch `;`; sonst leer |
| `status` | `aktiv` oder `ruhend` laut Kundenstamm. Der Status sagt nichts darüber, wann zuletzt bestellt wurde |

## produkte.csv – Produktstamm (eine Zeile je Produkt)

| Spalte | Bedeutung |
|---|---|
| `id` | Produktnummer (`P-101` …) |
| `name` | Artikelbezeichnung |
| `schaumart` | Produktgruppe: Schwerschaum, Mittelschaum, Netzwasser, Übungsschaum, Retardant, CAFS (Druckluftschaum) |
| `einsatzbereiche` | typische Einsatzbereiche, getrennt durch `;` |
| `status` | `aktiv` oder `auslaufend` |
| `eingefuehrt_am` | Datum der Markteinführung; vorher wurde das Produkt nicht geliefert |
| `ausgelaufen_am` | Datum, ab dem nicht mehr geliefert wird; leer, solange das Produkt lieferbar ist |

Gebinde und Listenpreise stehen in den Preislisten, Herstellkosten in `herstellkosten.csv`.

## lieferstellen.csv – Lieferstellen und Anlagen (eine Zeile je Lieferstelle)

Eine Lieferstelle ist ein Ort beim Kunden, an den wir ein Produkt liefern: eine Löschanlage, ein
Fahrzeug, ein Lager, ein Übungsplatz. Ein Kunde kann viele Lieferstellen haben.

| Spalte | Bedeutung |
|---|---|
| `lieferstelle_id` | Nummer der Lieferstelle (`LS-0001` …) |
| `kunde_id` | Kunde, zu dem die Lieferstelle gehört |
| `anlage` | Bezeichnung beim Kunden, zum Beispiel „Verladestation, Schaumanlage“ oder „Tanklager“ |
| `anwendung` | Art der Verwendung: `stationaere_anlage` (fest eingebaute Löschanlage), `feuerwehrfahrzeug`, `lager_bestand` (Vorrat beim Kunden), `uebung_training`, `tragbarer_feuerloescher`, `fahrbarer_feuerloescher` |
| `aktuelles_produkt_id` | Produkt, das zuletzt an diese Lieferstelle geliefert wurde |
| `fuellmenge_l` | Füllmenge der Anlage bzw. übliche Bestandsmenge in Litern |
| `letzte_lieferung` | Datum der letzten Lieferung an diese Lieferstelle |
| `erstbefuellung_am` | Datum der Erstbefüllung, wenn die Lieferstelle seit 01.01.2021 neu dazugekommen ist (neue Anlage, neues Fahrzeug, neues Lager); leer = schon vorher beliefert |

## auftraege.csv – Auftragspositionen 01.01.2021 bis 28.02.2027 (eine Zeile je Position)

| Spalte | Bedeutung |
|---|---|
| `auftrag_id` | Auftragsnummer |
| `position` | Positionsnummer im Auftrag; `auftrag_id` und `position` bezeichnen zusammen eine Position |
| `auftragsdatum` | Datum, an dem der Auftrag erfasst wurde |
| `lieferdatum` | **Buchungsdatum im Lager** (Warenausgang), nicht der Tag der Zustellung beim Kunden. Kann auf ein Wochenende oder einen Feiertag fallen |
| `kunde_id` | Kunde |
| `lieferstelle_id` | Lieferstelle, an die geliefert wurde |
| `produkt_id` | Produkt |
| `anwendung` | Anwendung der Lieferstelle (Werte wie in `lieferstellen.csv`) |
| `menge` | Menge in der Einheit der Spalte `einheit` |
| `einheit` | Gebinde: `l` (lose), `IBC` (1.000 l), `Fass` (200 l), `Kanister` (20 l) |
| `menge_l` | Menge in Litern. In Positionen aus dem alten ERP teilweise leer; dann aus `menge` und `einheit` umrechnen |
| `preis_netto_je_einheit` | Nettopreis je Einheit in der Währung der Spalte `waehrung` |
| `waehrung` | `EUR`, `CHF`, `GBP` oder `NOK`. Umrechnung in EUR mit den Konzernkursen aus `kennzahlen.json` |
| `nettobetrag` | `menge` × `preis_netto_je_einheit`, in der Auftragswährung |
| `vertriebsweg` | `direkt`, `Händler`, `Rahmenvertrag`, `Notfallservice`. Erstbefüllungen neuer Anlagen laufen als Projekt immer `direkt`, auch bei Kunden mit Rahmenvertrag (außer bei Händlern) |
| `auftragsart` | `Nachfüllung` (wiederkehrender Bedarf einer bestehenden Lieferstelle), `Erstbefüllung` (erste Befüllung einer neuen Anlage, eines neuen Fahrzeugs oder Lagers; einmaliges Projektgeschäft), `Notfall` (Lieferung des Notfallservice), `Muster`. Gutschriften und Retouren tragen die Auftragsart der ursprünglichen Lieferung |
| `art` | `Lieferung`, `Gutschrift`, `Retoure` oder `Muster`. Gutschriften und Retouren haben negative Mengen und Beträge; Muster werden mit 0 EUR berechnet |
| `quellsystem` | `ERP-alt` (Aufträge bis 30.06.2024) oder `ERP-neu` (ab 01.07.2024) |

## preisliste_2025.csv und preisliste_2026.csv – Listenpreise

| Spalte | Bedeutung |
|---|---|
| `produkt_id` | Produkt |
| `gebinde` | `IBC`, `Fass`, `Kanister` (und `l` für lose Lieferung, wo angeboten) |
| `preis_netto_eur` | Listenpreis netto je Gebinde in EUR, vor Rabatten |
| `gueltig_ab` | Datum, ab dem der Preis gilt. Eine Preisliste gilt bis zum Beginn der nächsten |

Welche Preisliste für ein Angebot gilt, richtet sich nach dem Angebotsdatum.

## kennzahlen.json – Definitionen und Vorgaben

| Schlüssel | Bedeutung |
|---|---|
| `stichtag` | letzter Tag mit Daten (28.02.2027) |
| `heute` | „heute“ in der Übung (01.03.2027) |
| `waehrung_konzern` | Berichtswährung des Konzerns (EUR) |
| `konzernkurse` | je Jahr ein Kurs je Fremdwährung (CHF, GBP, NOK) in EUR; gilt für alle Umrechnungen in Berichten |
| `ziele` | Ziele der Geschäftsführung für 2026 (= Budget 2026): Nettoumsatz, Absatz, Deckungsbeitrag und DB-Marge des Übungsausschnitts, zum Plankurs, ohne Notfallservice |
| `definitionen` | verbindliche Definitionen: `bereinigung`, `umrechnung_gebinde`, `absatz_l`, `nettoumsatz`, `wachstum`, `auftragsart`, `nachfuell_anteil`, `top5_anteil`, `aktiver_kunde`, `kundenstatus` (aktiv / ruhend / verloren); für die Finanzanalyse `deckungsbeitrag`, `umrechnung_fremdwaehrung`, `rabattquote` und `plan_ist_bruecke` |
| `ampel_wachstum` | Regel für die Wachstumsampel (Veränderung des Nettoumsatzes 2026 gegen 2025 je Gruppe) |

Bei Widerspruch zwischen diesem Katalog und `kennzahlen.json` gilt `kennzahlen.json`.

## Weitere Tabellen

### reklamationen.csv – Reklamationen 2024 bis Februar 2027

| Spalte | Bedeutung |
|---|---|
| `rekl_id` | Vorgangsnummer der Reklamation (`R-JJJJ-nnn`) |
| `eingang` | Datum des Eingangs |
| `kunde_id` | Kunde |
| `produkt_id` | Produkt der beanstandeten Lieferung |
| `kategorie` | Art der Beanstandung: Lieferverzug, Lieferung/Menge, Gebinde/Verpackung, Beschädigte Ware, Rechnung, Dokumentation |
| `tage_bis_antwort` | Arbeitstage vom Eingang bis zur ersten Antwort an den Kunden |
| `status` | Stand des Vorgangs: offen, abgeschlossen, abgeschlossen (Kulanz), abgelehnt |

## Finanzdaten

Die folgenden vier Tabellen gehören zur Finanzanalyse (Deckungsbeitrag, Plan-Ist 2026, Fremdwährung und
Preise). Wie Deckungsbeitrag, Rabattquote und die Plan-Ist-Abweichung gerechnet werden, steht verbindlich in
`kennzahlen.json` unter `definitionen`.

### herstellkosten.csv – Herstellkosten je Produkt und Jahr (eine Zeile je Produkt und Jahr)

| Spalte | Bedeutung |
|---|---|
| `produkt_id` | Produkt |
| `jahr` | Kalenderjahr (2021 bis 2027); es gilt das Jahr des Lieferdatums |
| `rohstoff_eur_l` | Rohstoffkosten je Liter Konzentrat in EUR (Standardkosten des Jahres) |
| `fertigung_eur_l` | Fertigungskosten je Liter in EUR (Mischen, Abfüllen, Gebinde, Qualitätsprüfung) |

Herstellkosten je Liter = `rohstoff_eur_l` + `fertigung_eur_l`. Fracht ist **nicht** enthalten, sie steht in
`fracht.csv`.

### fracht.csv – Frachtkosten je Auftrag (eine Zeile je Auftrag)

| Spalte | Bedeutung |
|---|---|
| `auftrag_id` | Auftragsnummer wie in `auftraege.csv` |
| `versanddatum` | frühestes Lieferdatum der Positionen des Auftrags |
| `kunde_id` | Kunde |
| `versandart` | `Paket`, `Stückgut`, `Tankwagen` (lose Ware) oder `Express` (Notfallservice) |
| `liter` | Liter aller Positionen des Auftrags, Doppelimporte nur einmal gezählt |
| `frachtkosten_eur` | Frachtkosten in EUR, die wir tragen (Lieferung frei Haus); nicht in `nettobetrag` enthalten |

Nur Aufträge mit Lieferungen oder Mustern haben Fracht; Gutschriften und Retouren nicht. Ein Auftrag kann
mehrere Positionen haben: Für Auswertungen je Produkt, Schaumart, Segment oder Vertriebsweg wird die Fracht
nach Litern auf die Positionen verteilt.

### kurse.csv – Plankurse und Ist-Monatskurse 2026 (eine Zeile je Monat und Währung)

| Spalte | Bedeutung |
|---|---|
| `monat` | Monat (`2026-01` … `2026-12`) |
| `waehrung` | `CHF`, `GBP` oder `NOK` |
| `ist_kurs_eur` | durchschnittlicher Kurs des Monats: 1 Einheit Fremdwährung = x EUR |
| `plankurs_eur` | Kurs, mit dem das Budget 2026 gerechnet wurde (für alle Monate gleich) |

Der Durchschnitt der zwölf Ist-Monatskurse ergibt den Konzernkurs 2026 aus `kennzahlen.json`. Berichte über
das Ist rechnen mit dem Konzernkurs; der Plan-Ist-Vergleich rechnet das Ist mit dem Kurs des Liefermonats.

### budget_2026.csv – Budget 2026 (eine Zeile je Monat, Segment und Vertriebsweg)

| Spalte | Bedeutung |
|---|---|
| `monat` | Monat (`2026-01` … `2026-12`) |
| `segment` | Kundensegment (wie in `kunden.csv`) |
| `vertriebsweg` | `direkt`, `Händler` oder `Rahmenvertrag` (wie in `auftraege.csv`) |
| `menge_l` | geplante Liter (netto, ohne Muster) |
| `preis_eur_l` | geplanter Nettopreis je Liter in EUR (zum Plankurs) |
| `umsatz_eur` | geplanter Nettoumsatz in EUR = `menge_l` × `preis_eur_l` |
| `db_eur` | geplanter Deckungsbeitrag in EUR nach Herstellkosten und Fracht |

Das Budget wurde im Herbst 2025 von der Geschäftsführung beschlossen; es schreibt das Ist 2025 je Segment
und Vertriebsweg mit einem Wachstum je Vertriebsweg fort, zu den Nettopreisen 2025. Die Auftragsart ist
im Budget nicht getrennt geplant. Einsätze des Notfallservice sind nicht budgetiert. Zeilen ohne geplante
Menge fehlen.

## Was es in diesen Daten nicht gibt

Rezepturen, Inhaltsstoffe, Prüfwerte, Sicherheits- und Technische Datenblätter sind nicht Teil des
Übungsausschnitts. Aussagen über Eigenschaften oder Wirksamkeit einzelner Produkte lassen sich aus diesen
Tabellen nicht ableiten.
