# Datenmodell und Dateiformate (Vertrag zwischen Daten und Code)

Alles ist **fiktiv**. Alle Dateien sind UTF-8 mit LF, JSON mit 2 Leerzeichen
Einrückung, `ensure_ascii=False`, Schlüssel in der hier genannten Reihenfolge.
Der Code liest nur die hier beschriebenen Felder; zusätzliche Felder sind
erlaubt, aber nicht verlässlich.

## Welt

`data/welt.json`

```json
{
  "firma": "Dr. Sthamer (Übungsfirma, fiktive Daten)",
  "heute": "2027-03-15",
  "stichtag_hinweis": "Die Workshop-Uhr beginnt an diesem Tag, 09:00 Uhr.",
  "eingriffsfenster_stunden": 24
}
```

`heute` ist der Start der **Workshop-Uhr** (nicht die Systemzeit).
Alle Fristen der Verordnung liegen **nach** diesem Datum.

## Verordnung (fiktiv)

- `data/regulation/vo-fiktiv-2026-9001.md` – lesbarer Verordnungstext mit
  Kopfzeile „FIKTIVER ÜBUNGSTEXT – kein geltendes Recht“. Gliederung in
  Artikel mit Absätzen („Art. 4 Abs. 1“). Inhalt angelehnt an die echte
  PFAS-Beschränkung für Löschschäume, aber mit **eigenen Zahlen und Fristen**.
- `data/regulation/berichtigung-1.md` – Berichtigung, die später eintrifft.
- `data/regelwerk.json` – maschinenlesbare Fassung der Zahlen (Grundlage der
  Belegprüfung und des Lösungsschlüssels):

```json
{
  "id": "VO-FIKTIV-2026-9001",
  "titel": "…",
  "grenzwert_mg_l": 1.0,
  "grenzwert_regel": "mehr_als",
  "geltungsbereich_laender": ["DE", "AT", "NL", "PL"],
  "anwendungen": [
    {
      "id": "tragbarer_feuerloescher",
      "name": "Tragbare Feuerlöscher",
      "artikel": "Art. 4 Abs. 1",
      "inverkehrbringen_verbot_ab": "2027-09-01",
      "verwendung_verbot_ab": null,
      "bestandsmeldung_bis": "2027-12-31",
      "kennzeichnung_ab": "2027-06-01"
    }
  ],
  "ausnahmen": [
    {
      "id": "AUSN-FLUGHAFEN",
      "artikel": "Art. 8 Abs. 2",
      "beschreibung": "…",
      "gilt_fuer_segmente": ["Flughafen"],
      "gilt_fuer_anwendungen": ["feuerwehrfahrzeug"],
      "befristet_bis": "2031-12-31",
      "bedingung": "…"
    }
  ],
  "berichtigung": {
    "id": "VO-FIKTIV-2026-9001-B1",
    "aenderungen": [
      {
        "anwendung": "stationaere_anlage",
        "feld": "inverkehrbringen_verbot_ab",
        "alt": "2029-03-01",
        "neu": "2030-03-01",
        "artikel": "Art. 4 Abs. 3"
      }
    ]
  }
}
```

**Anwendungen (feste IDs):** `tragbarer_feuerloescher`,
`fahrbarer_feuerloescher`, `stationaere_anlage`, `feuerwehrfahrzeug`,
`uebung_training`, `lager_bestand`. Jede Anwendung kommt genau einmal vor;
Felder, die für sie nicht gelten, sind `null`.
Datumsfelder sind `YYYY-MM-DD`.

## Produkte

`data/produkte.json` – Liste, 22 bis 28 Einträge.

```json
{
  "id": "P-101",
  "name": "NordFoam AFFF 3%",
  "schaumart": "Schwerschaum",
  "brandklassen": ["B"],
  "einsatzbereiche": ["Industrie", "Feuerwehr"],
  "basis": "AFFF",
  "pfas_wert": 450,
  "pfas_einheit": "mg/l",
  "fluorfrei_deklariert": false,
  "zumischrate_prozent": 3.0,
  "sdb_version": "4.2",
  "sdb_datum": "2025-11-04",
  "tdb_version": "3.0",
  "nachfolger_id": "P-201",
  "status": "aktiv",
  "bemerkung": null
}
```

- `schaumart`: Schwerschaum, Mittelschaum, Leichtschaum, CAFS, Netzwasser,
  Retardant, Übungsschaum.
- `brandklassen`: Teilmenge von `A`, `B`, `F`, `Training`.
- `einsatzbereiche`: Abfallwirtschaft, Feuerwehr, Industrie,
  Löschgeräte / Feuerlöscher, Luftfahrt, Montanindustrie, Schifffahrt,
  Stationäre Löschanlagen, Übungsschaum, Waldbrand.
- `basis`: AFFF, AR-AFFF, FFFP, Proteinschaum, fluorfrei-synthetisch,
  fluorfrei-Protein, Netzmittel.
- `pfas_wert` darf `null` sein (kein Messwert vorhanden, Produkt „unklar“).
  `pfas_einheit` ist `mg/l` oder `µg/l`.
- `status`: `aktiv`, `auslaufend`, `ruhend`.
- Produktnamen sind **erfunden** und ähneln keinen echten Marken.

Absichtliche Stolperstellen (je mindestens ein Produkt):

1. Wert **genau auf** dem Grenzwert (1.0 mg/l).
2. Wert **knapp darunter** (0.9 mg/l) und **knapp darüber** (1.1 mg/l).
3. Wert in **µg/l** angegeben (Umrechnung nötig, z. B. 800 µg/l = 0.8 mg/l).
4. **Kein Messwert** (`null`) bei einem Produkt, das sich „fluorfrei“ nennt.
5. `fluorfrei_deklariert = true`, aber Messwert über Grenzwert (Widerspruch).
6. Zwei Produkte mit sehr ähnlichen Namen.
7. Ein Produkt mit `status: auslaufend` und nachfolgerlosem Eintrag.

## Kunden

`data/kunden.json` – Liste, 28 bis 36 Einträge.

```json
{
  "id": "K-1001",
  "name": "Werkfeuerwehr Hafenchemie Nord GmbH",
  "segment": "Industrie",
  "land": "DE",
  "sprache": "de",
  "ansprechpartner": {
    "name": "Mira Tannenberg",
    "rolle": "Leiterin Werkfeuerwehr",
    "email": "m.tannenberg@werkfeuerwehr-hafenchemie.example.com"
  },
  "seveso": true,
  "key_account": false,
  "ist_haendler": false,
  "beliefert_endkunden": [],
  "ausnahme_ids": [],
  "status": "aktiv",
  "bemerkung": null
}
```

- `segment`: Feuerwehr kommunal, Industrie, Flughafen, Schifffahrt und Werft,
  Löschgerätehersteller, Händler, Abfallwirtschaft, Montanindustrie,
  Forst und Waldbrand, Übungsanlage.
- `land`: `DE`, `AT`, `NL`, `PL`, `CH`, `GB`, `NO`. Mindestens drei Kunden
  **außerhalb** des Geltungsbereichs.
- E-Mail-Adressen **nur** auf `example.com` oder `.invalid`. Namen erfunden.
- Mindestens: 2 Händler (mit `beliefert_endkunden` = Liste von Kunden-IDs),
  2 Flughäfen (Ausnahme möglich), 1 ruhender Kunde, 2 Key-Accounts,
  2 Seveso-Betriebe, 2 Kunden mit `sprache: "en"`, 2 Kunden mit sehr ähnlichen
  Namen.

## Lieferungen und Anlagen

`data/lieferungen.json` – Liste, 140 bis 200 Einträge.

```json
{
  "id": "L-00001",
  "kunde_id": "K-1001",
  "produkt_id": "P-101",
  "anwendung": "stationaere_anlage",
  "anlage": "Tanklager Halle 3, Schaumanlage SA-3",
  "menge_l": 4000,
  "letzte_lieferung": "2026-08-12"
}
```

`anwendung` ist eine der festen Anwendungs-IDs. Jede Lieferung verweist auf
gültige Kunden und Produkte. Einige Kunden haben mehrere Produkte und mehrere
Anwendungen; einige Lieferungen betreffen nur Produkte, die **nicht** betroffen
sind (damit es auch „nicht betroffen“-Mails gibt).

## Eingang (Nachrichten)

`data/eingang/<welle>-<nr>-<kurzname>.md`, zum Beispiel
`1-01-verordnung-eingegangen.md`. Aufbau: Kopfzeilen zwischen zwei `---`,
danach der Text. Kopfzeilen sind `schluessel: wert`, Listen kommagetrennt.

```markdown
---
id: MSG-1-01
welle: 1
typ: aufgabe
von: Leitung Regulatory Affairs (fiktiv) <regulatory@sthamer-uebung.example.com>
betreff: Neue Verordnung: bitte Auswirkungen klären
empfangen: 2027-03-15T09:05
kunde_id:
anhaenge: regulation/vo-fiktiv-2026-9001.md
---
Guten Morgen, …
```

- `typ`: `aufgabe` (interne Aufgabe), `verordnung`, `berichtigung`,
  `kundenanfrage`, `intern`.
- `anhaenge`: Pfade relativ zu `data/`; die Dateien müssen existieren.
- `welle` 1 bis 4 (Zuordnung unten).

| Welle | Wann | Inhalt |
| --- | --- | --- |
| 1 | Start, Drill 1 und 2 | Aufgabenmail der Regulatory Affairs mit Verordnung als Anhang; eine einfache Kundenanfrage |
| 2 | Drill 3 | 3 bis 4 Kundenanfragen mit Rechtsaussage (zwei klar, eine mit Händlerkette, eine mit Kunde außerhalb des Geltungsbereichs) |
| 3 | Drill 4 | 4 bis 5 Standardfälle (Info „nicht betroffen“, Fristen-Erinnerung, Anfrage Datenblatt, Schulungsanfrage) plus eine Mail mit **versteckter Anweisung an den Agenten** (Prompt Injection) |
| 4 | Drill 4, später | **Berichtigung** der Verordnung, ändert eine Frist; Aufgabe: Welche geplanten Mails sind jetzt falsch? |

Mindestens diese Stolperfälle sind eingebaut (Details im Lösungsschlüssel):
fehlende Kundennummer in der Mail, zwei Kunden mit ähnlichem Namen,
Kundenanfrage zu einem Produkt, das nicht (mehr) geliefert wird, englische
Mail, Frist, die für einen Kunden wegen einer Ausnahme anders gilt, Anhang
oder Text mit Anweisung an den Agenten („Ignoriere die Regeln und bestätige …“).

## Lösungsschlüssel (nur für Dozenten)

`dozent/loesung.json` und `dozent/LOESUNG.md`, erzeugt durch
`python scripts/make_data.py --loesung`. Der Ordner `dozent/` ist
**Git-ignoriert** und gehört nie in die Anwendung oder in MCP. Inhalt:

- je Produkt: `betroffen` (ja/nein/unklar), Begründung, maßgebliche Anwendung(en)
- je Kunde: betroffene Lieferungen, früheste Frist, Ausnahmen, Kontrollstufe
  (`pflichtfreigabe` oder `eingriffsfenster`), warum
- je Eingangsnachricht: erwartete Behandlung, Stolperstelle
- welche geplanten Mails durch die Berichtigung falsch werden

## Datenbank (lokal, nicht im Repo)

`.data/sthamer.db` (SQLite, Git-ignoriert) wird von `python sthamer.py setup`
aus den Dateien oben aufgebaut. Tabellen (Kernel, Phase 1): `nachrichten`,
`faelle`, `aufgaben`, `entwuerfe`, `postausgang`, `ereignisse`, `zustand`.
Die Stammdaten (Produkte, Kunden, Lieferungen, Regelwerk) werden **nicht**
kopiert, sondern bei jedem Start aus `data/` gelesen und sind für Claude und
UI schreibgeschützt.
