# Entscheidungsvorlage A-04 · Löschgeräte Norddeutschland GmbH (K-1020), Nachbestellung Serie LG-6

An: Vertriebsinnendienst (Versand durch Angebotsassistent oder Innendienst) · Stichtag 01.03.2027 · Datenbasis: Angebotseingang A-04 (Mail vom 24.02.2027), RL-ANG-2026, KO-2026, Preisliste 2026, Kundenstamm, Aufträge, Herstellkosten (Übungsausschnitt, fiktive Daten). Alle Beträge EUR, netto ohne Umsatzsteuer. Rechnung: `skripte/a04_rechnung.py`.

## 1 Vorgang in Kürze

Einzelbestellung für die Befüllung der tragbaren 6-l-Schaumlöscher der Serie LG-6: Extinx Portable AFFF 3 % (P-106), 7 IBC + 1 Fass + 8 Kanister = 7.360 l, Expresslieferung bis Freitag 05.03.2027 (Zuschlag übernimmt der Kunde), 30 Tage netto, zu Standardkonditionen nach Preisliste. Nach Angabe des Kunden läuft LG-6 nicht über seinen Rahmenvertrag. **Ergebnis: Auftragswert EUR 24.953,72, Klasse A, bis EUR 25.000 darf der Angebotsassistent selbst versenden. Zwei Punkte sind vorher zu klären (Lagerbestand für Express, Rahmenvertrag), siehe Abschnitt 9.**

## 2 Stand-Datum, Preisliste und Richtlinie

- Angebotsdatum: 01.03.2027 (Stichtag, annahmeweise; das Angebot geht heute hinaus). Maßgeblich sind **RL-ANG-2026 und Preisliste 2026** (§ 6 Nr. 1); Preisliste 2027 ist erst für April 2027 angekündigt.
- Gültigkeit 60 Tage: bis 30.04.2027 (§ 6 Nr. 3).
- Antwortfrist: Mail vom Mittwoch 24.02.2027, 3 Arbeitstage = Montag 01.03.2027 (§ 10 Nr. 6). **Frist läuft heute ab, noch nicht überschritten.** Antwort oder Zwischenbescheid muss heute hinausgehen.

## 3 Unterlagen

| Unterlage | Status |
|---|---|
| Bestellmail vom 24.02.2027 | liegt vor |
| Rahmenvertrag des Kunden (LG-2, LG-9, FL-50) | erwähnt in der Mail, liegt nicht bei |
| Lagerbestand P-106 | nicht im Angebotseingang, nicht belegt |
| Ältere Aufträge P-106 (Rahmenvertrag, Preis je IBC EUR 3.174,00) | liegen in `daten/auftraege.csv`; nicht Grundlage dieses Angebots |

## 4 Preisrechnung Schritt für Schritt

1. **Listenpreise 2026 (P-106):** IBC EUR 3.588,00 · Fass EUR 756,60 · Kanister EUR 84,24.
2. **Menge:** 7 × 1.000 + 1 × 200 + 8 × 20 = **7.360 l**. Die Bestellung entspricht der Regel „möglichst große Gebinde" (§ 6 Nr. 2); keine Wahl nötig.
3. **Rabatt (§ 3):**
   - Mengenrabatt: 7.360 l ≥ 5.000 l, unter 20.000 l → **6 %** (nur höchste Stufe, § 3 Nr. 1).
   - Projektrabatt: **entfällt**. Tragbare Löscher sind keine stationäre Anlage, und eine Nachbestellung gibt ihn nie (§ 3 Nr. 2).
   - Rahmenvertragsrabatt: **entfällt**, Serie LG-6 ist nach Angabe des Kunden nicht im Rahmenvertrag, und er kann ohnehin nicht neben dem Mengenrabatt stehen (§ 3 Nr. 3).
   - Händlerkondition: **entfällt**, `ist_haendler` = nein (§ 3 Nr. 4).
   - Der Kunde bittet um „Standardkonditionen nach Preisliste"; die 6 % folgen genau aus der Staffel, sind also kein Rabatt über der Staffel.
4. **Positionen** (Listenwert × (1 − 6 %), je Position auf Cent, § 3 Nr. 5):

| Position | Listenwert | Netto nach 6 % |
|---|---:|---:|
| 7 IBC × 3.588,00 | 25.116,00 | 23.609,04 |
| 1 Fass × 756,60 | 756,60 | 711,20 |
| 8 Kanister × 84,24 | 673,92 | 633,48 |
| **Summe** | **26.546,52** | **24.953,72** |

5. **Auftragswert (§ 2 Nr. 1): EUR 24.953,72.** Abstand zur Grenze 25.000: **EUR 46,28**. Ohne den Mengenrabatt läge der Wert bei EUR 26.546,52 (über 25.000, Klasse B); die Einstufung hängt also an der korrekt gewährten Staffel. Eine Änderung der Menge oder ein Wegfall des Rabatts erfordert neue Einstufung (§ 8 Nr. 5).
6. **Nicht im Auftragswert:** Expresszuschlag EUR 450,00 je Lieferung (§ 6 Nr. 4); Fracht entfällt, frei Haus ab Nettowarenwert 2.500 (§ 6 Nr. 5). Rechnungssumme netto also EUR 25.403,72 (24.953,72 + 450,00), zählt aber nicht für Grenzen.
7. **Marge:** nicht verlangt, Auftragswert nicht über 25.000 (§ 2 Nr. 3).

## 5 Prüfumfang und Anlagenprüfung

- Bis 25.000: Preisliste, Rabatt nach Staffel, Kundenstatus, Zahlungsziel (§ 2 Nr. 3), alle geprüft. Kein Deckungsbeitrag, keine Bonitätsprüfung nötig.
- Bestandskunde: letzte Lieferung (ohne Muster) 15.05.2026, innerhalb von 24 Monaten (§ 4 Nr. 3).
- Zahlung: 30 Tage netto = Standard (§ 4 Nr. 1).
- Anlagenprüfung: **nicht erforderlich**. Befüllung tragbarer Löscher des Kunden in seiner Produktion, keine stationäre Anlage (§ 2 Nr. 4), keine Aussage zu einer Anlage des Kunden. Das Angebot macht nur Produktangaben nach TDB.

## 6 Angebotsklasse mit Punkten

| Merkmal | Wert | Punkte | Paragraf |
|---|---|---:|---|
| Auftragswert | 24.953,72 (bis 25.000) | 0 | § 8 Nr. 2, § 2 Nr. 1 |
| Rabatt | genau nach Staffel (6 %) | 0 | § 3 Nr. 1 |
| Technik | nur Produktdaten nach TDB | 0 | § 5 |
| Vertrag | Standardbedingungen, Einzelbestellung | 0 | § 6 Nr. 6 |
| Zahlung | 30 Tage netto, Bonität nicht erforderlich | 0 | § 4 |
| Kundenstatus | Bestandskunde | 0 | § 4 Nr. 3 |
| Währung und Lieferort | EUR, Lieferort Werk des Kunden, DE | 0 | § 7 Nr. 3 |
| **Summe** | | **0** | |

Mindestklassen: keine (keine technische Zusage, keine Rechtsaussage, keine Ausschreibung, Auftragswert nicht über 150.000). **Ergebnis: Klasse A** (§ 8 Nr. 3).

## 7 Wer entscheidet: System oder Mensch

- **Klasse A bis 25.000: Der Angebotsassistent darf das Angebot selbst versenden** (§ 9 Nr. 1 und 2; KO-2026 § 2), sobald die Rückfragen aus Abschnitt 9 geklärt sind. Auch der Vertriebsinnendienst darf freigeben.
- **Hier entscheidet ein Mensch (Leitung Vertrieb)**, falls eine Lieferzeit zugesagt werden soll, die kürzer ist als die Standard-Expresszeit von 3 Arbeitstagen ab Bestellung (§ 6 Nr. 4, KO § 2). Das ist der Fall, wenn die Ware am 05.03. nur mit früherer Verladung ankäme, etwa weil die Bestellung erst nach Dienstag 02.03. bestätigt wird.
- Verkauf oder Absage: Eine Absage träfe immer ein Mensch; sie ist nicht vorgesehen.
- Unterschrift: Über 25.000 zählt nicht, Auftragswert liegt darunter; keine Zwei-Personen-Zeichnung (KO § 6).

## 8 Empfehlung

Angebot (Bestätigung der Bestellung) zur Preisliste 2026 mit 6 % Mengenrabatt versenden: 7 IBC, 1 Fass, 8 Kanister P-106, Auftragswert EUR 24.953,72, Expresszuschlag EUR 450,00 gesondert, frei Haus, 30 Tage netto, gültig bis 30.04.2027. **Vorher** Lagerbestand für die Express-Zusage klären. Die Lieferung bis 05.03. nur zusagen, wenn die Bestellung bis Dienstag 02.03. bestätigt ist und die Ware am Lager ist, sonst Leitung Vertrieb. Das Datum steht im Angebot, nicht mündlich (§ 10 Nr. 5).

Entwurf der Kundenantwort (Sprache der Anfrage, ohne Klasse, Marge, Bonität, Kompetenzen):

> Guten Tag Herr Prahl, vielen Dank für Ihre Bestellung der Serie LG-6. Wir bieten Ihnen an: Extinx Portable AFFF 3 % (P-106), 7 IBC 1.000 l zu je 3.588,00, 1 Fass 200 l zu 756,60, 8 Kanister 20 l zu je 84,24 (Listenpreise netto). Mengenrabatt 6 % auf die Gesamtmenge von 7.360 l. Nettowarenwert nach Rabatt EUR 24.953,72. Expresslieferung (innerhalb von 3 Arbeitstagen nach Bestelleingang, sofern die Ware am Lager ist): Zuschlag EUR 450,00. Fracht: frei Haus. Zahlungsziel 30 Tage netto ab Rechnungsdatum. Angebot gültig bis 30.04.2027. [Liefertermin nach Klärung des Lagerbestands] Mit freundlichen Grüßen, Vertriebsinnendienst

Prüfung des Entwurfs gegen die Verbotsliste (§ 10 Nr. 2, § 1 Nr. 4):

| Inhalt | Verboten? | Ergebnis |
|---|---|---|
| Angebotsklasse, Punkte | ja | nicht enthalten |
| Deckungsbeitrag, Marge | ja | nicht enthalten |
| interne Bonität, Kompetenzen mit Namen | ja | nicht enthalten |
| Aussagen über andere Kunden (Rahmenvertragspreise) | ja | nicht enthalten |
| Rechtsauskunft | ja | nicht enthalten |
| technische Zusage zu Anlagen | ja | nicht enthalten |
| Pflichtangaben: Produkt, Gebinde, Menge, Preis je Gebinde, Rabatt mit Satz, Fracht, Lieferzeit, Zahlung, Gültigkeit | verlangt | enthalten (Lieferzeit nach Klärung) |

## 9 Offene Rückfragen

1. **Lagerbestand P-106 (7 IBC, 1 Fass, 8 Kanister):** Express (3 Arbeitstage) gilt nur, wenn die Ware am Lager ist (§ 6 Nr. 4). Bestand liegt dem Vorgang nicht bei. Wer klärt: Vertriebsinnendienst mit Disposition.
2. **Rahmenvertrag:** Die Mail sagt, LG-6 sei nicht im Rahmenvertrag; der Vertrag liegt nicht bei und ist nicht geprüft. Frühere P-106-Lieferungen an den Kunden liefen über den Rahmenvertrag (EUR 3.174,00 je IBC statt Liste EUR 3.588,00). Bevor das Angebot hinausgeht, im Vertrag bestätigen lassen, dass LG-6 nicht zu den Rahmenvertragsserien gehört. Das Angebot würde sonst an der falschen Preisgrundlage rechnen. Der Kunde bat ausdrücklich um Listenpreise.
3. **Liefertermin 05.03.2027:** nur zusagbar, wenn die Bestellung bis Dienstag 02.03. bestätigt ist; sonst Leitung Vertrieb (siehe Abschnitt 7).
4. **Angebotsdatum:** angenommen 01.03.2027. Verschiebt sich der Versand, gilt das spätere Datum; Rabatt und Klasse bleiben, solange Menge und Preisliste gleich sind.

## 10 Was nicht in die Entscheidung einfließen darf

- Frühere Rahmenvertragspreise (EUR 3.174,00 je IBC) oder frühere Rabatte als Maßstab: Der Kunde verlangt Standardkonditionen, „wie immer" ist kein Rabattgrund (§ 3 Nr. 6).
- Die mündliche oder gewohnte Praxis („wie gewohnt", „wie immer") sowie die Größe oder Key-Account-Eigenschaft des Kunden: begründen weder einen Rabatt noch eine Händlerkondition (§ 3 Nr. 4).
- Annahmen über Lagerbestand und den Rahmenvertrag, die nicht vorliegen (§ 1 Nr. 1).
- Der Zeitdruck der Produktion des Kunden: begründet keinen Rabatt und keine Lieferzeit unter Standard.

Entscheid durch: offen, Datum: offen
