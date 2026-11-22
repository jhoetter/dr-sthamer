# Dr. Sthamer – Unternehmensprofil (Übungsfirma)

Stand: Februar 2027 · Herausgeber: Geschäftsführung · intern

> Übungsfirma mit fiktiven Daten. Personen, Kunden, Produkte, Zahlen und Ereignisse sind erfunden und
> beschreiben kein reales Unternehmen.

## Wer wir sind

Dr. Sthamer entwickelt, produziert und vertreibt Schaumlöschmittel: Schaummittelkonzentrate für
Feuerwehren, Industrie, Häfen und Schiffe, Flughäfen, Waldbrandbekämpfung, Übungsanlagen und
Löschgerätehersteller. Dazu kommen Beratung beim Einsatz, Kundenschulungen und ein Notfallservice rund
um die Uhr.

**Das Unternehmen in Zahlen (Gesamtunternehmen, Geschäftsjahr 2026)**

| Kennzahl | Wert |
|---|---|
| Kunden | rund 1.400 in über 50 Ländern |
| Mitarbeitende | rund 260 |
| Produkte im Sortiment | 27 Schaummittel, dazu Zubehör und Dienstleistungen |
| Standorte | Werk Nord (Produktion, Labor, Verwaltung), Vertriebsbüro Süd |

Die Daten im Ordner `daten/` sind ein **Übungsausschnitt**: ausgewählte Kunden mit ihren Lieferstellen
und Aufträgen. Zahlen aus diesem Ausschnitt sind nicht die Zahlen des Gesamtunternehmens und umgekehrt.

## Wie wir Geld verdienen

Unser Geschäft hat drei Teile, die sich sehr unterschiedlich verhalten:

- **Nachfüllgeschäft:** Bestehende Anlagen, Fahrzeuge, Lager und Übungsplätze brauchen regelmäßig
  Nachschub – nach Einsätzen und Übungen, wenn Bestände ablaufen oder Lager umgeschlagen werden. Das ist
  der größte und gleichmäßigste Teil unseres Absatzes.
- **Projektgeschäft:** Wird beim Kunden eine neue Löschanlage gebaut, ein Fahrzeug angeschafft oder ein
  Lager eingerichtet, liefern wir die **Erstbefüllung**. Bei großen stationären Anlagen sind das auf einen
  Schlag mehrere tausend Liter. Wie viele Projekte in einem Jahr fertig werden, können wir kaum
  beeinflussen; die Menge schwankt deshalb stark von Jahr zu Jahr.
- **Notfallservice:** Nach einem Großeinsatz liefern wir innerhalb von Stunden, mit Zuschlag und
  Expressfracht. Solche Lieferungen sind selten, aber sehr groß, und sie sind nicht planbar.

Wir verkaufen über vier **Vertriebswege**: direkt an Endkunden, über Händler (die an Feuerwehren und
Betriebe weiterverkaufen), über Rahmenverträge mit festen Konditionen und über den Notfallservice.
Welche Lieferung zu welcher Auftragsart gehört, steht in der Auftragstabelle (Spalte `auftragsart`).

## Ziele und Fragen für 2027

Die Geschäftsführung hat für 2026 ein Budget beschlossen (Herbst 2025); es ist zugleich das Ziel für das
Jahr. Die Ziele für den Übungsausschnitt (Nettoumsatz, Absatz, Deckungsbeitrag) stehen verbindlich in
`kennzahlen.json`, das Budget je Monat, Segment und Vertriebsweg in `budget_2026.csv`.

Für das Gesamtunternehmen hat die Geschäftsführung vier Leitlinien ausgegeben:

1. das Nachfüllgeschäft mit bestehenden Kunden sichern und ausbauen,
2. das Händlernetz stärken, vor allem in den Nachbarländern,
3. weniger abhängig werden von einzelnen Großprojekten und wenigen großen Kunden,
4. die Listenpreiserhöhung von 4 % zum 01.01.2026 im Markt durchsetzen.

Im März 2027 berichtet die Geschäftsführung dem Beirat über das Geschäftsjahr 2026 und schlägt die
Prioritäten für 2027 vor. Die Leitfrage dafür: **Wo wachsen wir, wo verlieren wir – und was heißt das
für 2027?**

## Wichtige Daten

| Wann | Was |
|---|---|
| 01.07.2024 | Wechsel vom alten auf das neue ERP-System; Aufträge bis 30.06.2024 stammen aus dem alten ERP |
| Herbst 2025 | Budget 2026 beschlossen |
| 01.01.2026 | neue Preisliste, Listenpreise im Schnitt plus 4 % |
| 22.09.2026 | größter Notfalleinsatz des Jahres (Industriekunde, Tankpark) |
| 28.02.2027 | Stichtag des Übungsausschnitts |
| März 2027 | Beiratssitzung: Geschäftsjahr 2026 und Prioritäten 2027 |

## Organisation (Auszug)

```
Geschäftsführerin
├── Unternehmensentwicklung                                              Leitung: Dr. Henrike Vossberg
├── Finanzen & Controlling, Werk Nord                                    Leitung Controlling: Jasper Dierksmeyer
├── Vertrieb
│   ├── Vertriebsinnendienst, Werk Nord                                  Trainee: Lina Osterkamp
│   └── Angebotsmanagement (Tender Desk), Vertriebsbüro Süd              Leitung: Mathis Grevenbroich
├── Anwendungstechnik & Kundendienst, Werk Nord                          Teamleitung: Birte Lohmeyer
│   ├── Außendienst-Anwendungstechnik
│   ├── Labor (Prüfaufträge, Rückstellmuster)
│   ├── Reklamationen
│   └── Notfallservice
└── Produktion, Einkauf, IT
```

- **Dr. Henrike Vossberg** leitet die Unternehmensentwicklung (Analysen zur Geschäftsentwicklung,
  Strategie, Beiratsunterlagen) und berichtet an die Geschäftsführerin.
- **Jasper Dierksmeyer** verantwortet Budget, Plan-Ist-Vergleich und Deckungsbeitragsrechnung.
- **Birte Lohmeyer** führt 14 Personen, davon 6 direkt.
- **Beirat:** Vorsitzender aus dem Gesellschafterkreis; ein externes Mitglied, früher Finanzchef eines
  Chemieunternehmens.

## Systeme

- **ERP** (alt bis 30.06.2024, neu ab 01.07.2024): Aufträge, Lieferungen, Gutschriften, Preise.
- **CRM:** Kunden, Ansprechpartner, Anlagen und Lieferstellen.
- **Kundenportal:** Bestellungen, Fragen und Reklamationen der Kunden.

Interne E-Mail-Adressen: `vorname.nachname@sthamer-uebung.example.com`.
