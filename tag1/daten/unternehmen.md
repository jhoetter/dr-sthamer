# Dr. Sthamer – Unternehmensprofil (Übungsfirma)

Stand: Februar 2027 · Herausgeber: Geschäftsführung · intern

> Übungsfirma mit fiktiven Daten. Personen, Kunden, Produkte, Zahlen und Ereignisse sind erfunden und
> beschreiben kein reales Unternehmen.

## Wer wir sind

Dr. Sthamer entwickelt, produziert und vertreibt Schaumlöschmittel: Schaummittelkonzentrate für
Feuerwehren, Industrie, Häfen und Schiffe, Flughäfen, Waldbrandbekämpfung, Übungsanlagen und
Löschgerätehersteller. Wir beliefern unsere Kunden direkt, über Händler, über Rahmenverträge und im
Notfallservice rund um die Uhr.

**Das Unternehmen in Zahlen (Gesamtunternehmen, Geschäftsjahr 2026)**

| Kennzahl | Wert |
|---|---|
| Kunden | rund 1.400 in über 50 Ländern |
| Mitarbeitende | rund 260 |
| Produkte im Sortiment | 27 Schaummittel, dazu Zubehör und Dienstleistungen |
| Standorte | Werk Nord (Produktion, Labor, Verwaltung), Vertriebsbüro Süd |

Die Daten im Ordner `daten/` sind ein **Übungsausschnitt**: ausgewählte Kunden mit ihren Lieferstellen
und Aufträgen. Zahlen aus diesem Ausschnitt sind nicht die Zahlen des Gesamtunternehmens und umgekehrt.

## Umstellungsprogramm „FreeFoam“

Seit 2023 stellen wir unsere Kunden von fluorhaltigen Altprodukten (Nummern P-1xx) auf fluorfreie
Nachfolger (Nummern P-2xx) um. Die ersten fluorfreien Nachfolger kamen 2021 auf den Markt. Welches
Produkt welchen Vorgänger ersetzt, steht in der Produkttabelle (Spalte `nachfolger_id`).

**Ziele der Geschäftsführung:** Fluorfrei-Anteil am Absatz 2026 mindestens 60 %, 2027 mindestens 80 %.
Wie der Anteil gerechnet wird, steht verbindlich in `kennzahlen.json`.

Programmleitung: Dr. Henrike Vossberg. Sie berichtet der Geschäftsführung und dem Beirat.

Eine EU-Beschränkung für fluorhaltige Schaumlöschmittel ist angekündigt; der Text wird im März 2027
erwartet. Bis dahin gilt: keine Aussagen an Kunden dazu.

## Wichtige Daten

| Wann | Was |
|---|---|
| 2021 | erste fluorfreie Nachfolgeprodukte im Sortiment |
| 2023 | Start Umstellungsprogramm FreeFoam |
| 01.07.2024 | Wechsel vom alten auf das neue ERP-System; Aufträge bis 30.06.2024 stammen aus dem alten ERP |
| 2026 | Probeumstellungen bei Industriekunden, unter anderem Raffinerie Küstenmark |
| 28.02.2027 | Stichtag des Übungsausschnitts |

## Organisation (Auszug)

```
Geschäftsführerin
├── Programmleitung Fluorfrei-Umstellung (Produktmanagement & Daten)   Dr. Henrike Vossberg
├── Leitung Regulatory Affairs
├── Vertrieb
│   ├── Vertriebsinnendienst, Werk Nord                                 Trainee: Lina Osterkamp
│   └── Angebotsmanagement (Tender Desk), Vertriebsbüro Süd             Leitung: Mathis Grevenbroich
├── Anwendungstechnik & Kundendienst, Werk Nord                          Teamleitung: Birte Lohmeyer
│   ├── Außendienst-Anwendungstechnik
│   ├── Labor Schaumanalyse
│   ├── Reklamationen
│   └── Notfallservice
└── Produktion, Einkauf, Finanzen, IT
```

- **Birte Lohmeyer** führt 14 Personen, davon 6 direkt.
- **Beirat:** Vorsitzender aus dem Gesellschafterkreis; ein externes Mitglied, früher Finanzchef eines
  Chemieunternehmens.

## Systeme

- **ERP** (alt bis 30.06.2024, neu ab 01.07.2024): Aufträge, Lieferungen, Gutschriften, Preise.
- **CRM:** Kunden, Ansprechpartner, Anlagen und Lieferstellen, Kontakte.
- **Kundenportal** mit KI-Assistent: Kunden stellen Fragen und melden Reklamationen.
- **Labor-Datenbank:** Prüfberichte, Rückstellmuster.

Interne E-Mail-Adressen: `vorname.nachname@sthamer-uebung.example.com`.
