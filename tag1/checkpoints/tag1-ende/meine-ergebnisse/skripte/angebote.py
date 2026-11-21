# Reiter „Angebote“ und Entscheidungsvorlagen (Drill 3)
# Erzeugt: meine-ergebnisse/entscheidungsvorlage-a-NN.md und meine-ergebnisse/dashboard-daten/angebote.js
# Regeln: regelwerke/RL-ANG-2026.md und KO-2026.md. Preisliste nach Angebotsdatum (§ 6 Nr. 1), Rabatte addiert (§ 3 Nr. 5).
# Ein neuer Vorgang kommt als weitere Funktion unten dazu und wird in VORGAENGE eingetragen.
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from angebote_kern import (BASIS, D, HK, KZ, PREIS, cent, de, eur, fracht_je_liter, klasse_nach_punkten, kurs, md_html, pct,
                           position)

HEUTE = datetime.date(2027, 3, 1)
STICHTAG = "28.02.2027"

# Entscheidungen der Person (Etappe 2 und 3). Leer = alle Spannen offen.
ENTSCHIEDEN = {
    "A-01": {"wer": "Mathis Grevenbroich, Leiter Angebotsmanagement (Tender Desk)", "datum": "01.03.2027"},
}
# Schlusszeile „Entscheid durch: …“ (wird in Etappe 3 verlangt)
MIT_ENTSCHEIDZEILE = True

KOPF = ("Stichtag der Daten " + STICHTAG + " · Stand der Vorlage Montag, 01.03.2027 · Datenbasis: Übungsausschnitt "
        "(Stammdaten, Preislisten, Herstellkosten; Beträge netto in EUR) · Regeln: RL-ANG-2026 und KO-2026")


def datum(d):
    return d.strftime("%d.%m.%Y")


def tabelle(kopf, zeilen):
    s = "| " + " | ".join(kopf) + " |\n|" + "---|" * len(kopf) + "\n"
    for z in zeilen:
        s += "| " + " | ".join(str(c) for c in z) + " |\n"
    return s


def liste(items):
    return "\n".join("- " + i for i in items) + "\n"


def entscheidzeile(vid, name=None):
    if not MIT_ENTSCHEIDZEILE:
        return ""
    e = ENTSCHIEDEN.get(vid)
    if e:
        return "\nEntscheid durch: " + e["wer"] + ", Datum: " + e["datum"] + "\n"
    return "\nEntscheid durch: offen, Datum: offen\n"


# ------------------------------------------------------------------ A-01
def a01():
    vid = "A-01"
    ent = ENTSCHIEDEN.get(vid)
    liste26 = "2026"
    p1 = position(liste26, "P-204", {"IBC": 1, "Fass": 3}, "0.08")
    p2 = position(liste26, "P-204", {"Fass": 3}, "0.03")
    liste_sum = cent(p1["listenwert"] + p2["listenwert"])
    netto = cent(p1["netto"] + p2["netto"])
    rabatt_eur = cent(liste_sum - netto)
    alt_netto = D("10285.75")  # wie im Angebot vom 14.07.2026 ausgewiesen
    alt_liste = D("11822.71")
    diff = cent(netto - alt_netto)
    # Zerlegung der Differenz: Preisliste, dann Rabatt
    mit_liste26_13 = position(liste26, "P-204", {"IBC": 1, "Fass": 6}, "0.13")["netto"]
    eff_liste = cent(mit_liste26_13 - alt_netto)
    eff_rabatt = cent(netto - mit_liste26_13)
    gueltig_alt = datetime.date(2026, 7, 14) + datetime.timedelta(days=60)
    gueltig_neu = HEUTE + datetime.timedelta(days=60)
    liter = p1["liter"] + p2["liter"]
    hk_l = HK[("P-204", "2026")]
    hk = cent(hk_l * liter)
    db_neu = cent(netto - hk)
    db_alt = cent(alt_netto - hk)
    marge_neu = db_neu / netto
    marge_alt = db_alt / alt_netto
    alt_rabatt_auf_liste = 1 - alt_netto / liste_sum

    S = []
    S.append(("Vorgang in Kürze",
              "Die Reederei Ostsee Linien AG (K-1018, Bestandskunde, nicht als Händler geführt) will die Umstellung der Maschinenräume "
              "der Fähren Baltic Star und Baltic Wind auf FreeFoam Marine 3 % (P-204) bestellen, zu den Preisen des Angebots "
              "AN-2026-0714-018 vom 14.07.2026: 2.200 l, davon 1.600 l Erstbefüllung und 600 l Reserve; Werftzeit Ende März und April 2027. "
              "Der Angebotsassistent hat das Angebot am 14.07.2026 erstellt und automatisch versandt, ohne Vermerk einer Prüfung durch eine Person.\n\n"
              "Der Kunde fragt in seiner Mail vom 02.02.2027: (1) Hat ein System den Rabatt berechnet, und hat jemand geprüft? "
              "(2) Stehen ihm Händlerkonditionen zu, wie der Außendienst am Telefon gesagt habe? (3) Entgegenkommen wegen eines "
              "Wettbewerberangebots, das rund 20 % darunter liege. Dazu bittet er um eine schriftliche Bestätigung, dass die Umstellung "
              "„ohne Anpassung der Anlagen“ möglich ist.\n"))
    S.append(("Stand-Datum, Preisliste und Richtlinie",
              liste([
                  "**Stand:** Montag, 01.03.2027 (Daten bis " + STICHTAG + "). Antwort an den Kunden ist überfällig: Die Mail kam am 02.02.2027, "
                  "drei Arbeitstage waren am 05.02.2027 um (RL § 10 Nr. 6).",
                  "**Angebot vom 14.07.2026:** Angebotsdatum ab 01.01.2026, also gilt RL-ANG-2026 (Geltungsbereich) und die **Preisliste 2026** (RL § 6 Nr. 1: "
                  "Preisliste am Angebotsdatum, nicht Anfrage- oder Lieferdatum). Der Assistent hat mit Bezugsdatum 04.12.2025 (Anfrage) die Preisliste 2025 genommen.",
                  "**Gültigkeit:** 60 Kalendertage, bis " + datum(gueltig_alt) + ". Das Angebot ist abgelaufen; die Bestellung vom 02.02.2027 braucht ein neues Angebot "
                  "mit der dann gültigen Preisliste und Richtlinie (RL § 6 Nr. 3).",
                  "**Neues Angebot (Datum 01.03.2027, Annahme):** Preisliste 2026 gilt bis zur Preisliste 2027 (angekündigt für April 2027, RL § 6 Nr. 1), "
                  "RL-ANG-2026. Gültig dann bis " + datum(gueltig_neu) + ". Währung EUR, kein Umrechnungskurs nötig.",
              ])))
    S.append(("Vorliegende und nur erwähnte Unterlagen",
              "**Liegt im Angebotseingang vor:**\n\n" +
              liste([
                  "Anfrage vom 04.12.2025 (Lars Hinrichsen, Technischer Inspektor)",
                  "Angebot AN-2026-0714-018 vom 14.07.2026 (Version „maschinell erstellt“)",
                  "Rabattrechnung des Angebotsassistenten, Version 2.3, Lauf 14.07.2026 06:12",
                  "Kundenmail vom 02.02.2027",
                  "Stammdaten: Kunde K-1018, Lieferstellen LS-0082 und LS-0083, Produkt P-204 (Nachfolger von P-104), Preislisten 2025 und 2026",
              ]) +
              "\n**Nur erwähnt, liegt nicht bei:**\n\n" +
              liste([
                  "Angebot des Wettbewerbers „rund 20 % unter Ihrem Preis“: erwähnt in der Kundenmail, keine Kopie, kein Datum, kein Produkt, keine Menge (RL § 1 Nr. 3)",
                  "Mündliche Aussage des Außendienstes zu Händlerkonditionen im Herbst: erwähnt in der Kundenmail, kein Vermerk im Angebotseingang (RL § 10 Nr. 5)",
                  "Datenaufnahme der beiden Maschinenräume: in den Stammdaten kein Datum (`datenaufnahme_am` leer), keine Zumischrate laut Anlagendokumentation",
              ])))
    # Preisrechnung
    zeilen = []
    for pos_name, p, satz_text in (("1 Erstbefüllung Baltic Star und Baltic Wind (1.600 l)", p1, "8 % = 3 % Mengenrabatt (§ 3 Nr. 1) + 5 % Projektrabatt, einmal je Angebot (§ 3 Nr. 2)"),
                                   ("2 Reserve Bordlager (600 l)", p2, "3 % Mengenrabatt (§ 3 Nr. 1)")):
        for z in p["zeilen"]:
            zeilen.append([pos_name, z["gebinde"] + " " + str(z["liter"] // z["anzahl"]) + " l", z["anzahl"], de(z["listenpreis"]), de(z["listenwert"]), satz_text, de(z["netto"])])
            pos_name = "″"
            satz_text = "″"
    pruef = tabelle(
        ["Prüfpunkt", "Angebotsassistent am 14.07.2026", "Richtlinie zum Angebotsdatum", "Ergebnis"],
        [
            ["Preisliste", "Liste 2025 nach Anfragedatum 04.12.2025 (IBC 5.219,23; Fass 1.100,58)", "Liste 2026 nach Angebotsdatum (IBC " + de(PREIS[("2026", "P-204", "IBC")]) + "; Fass " + de(PREIS[("2026", "P-204", "Fass")]) + "), § 6 Nr. 1", "falsch, zu niedrige Preise"],
            ["Mengenrabatt", "3 % auf 2.200 l", "3 % (ab 1.000 l, unter 5.000 l), § 3 Nr. 1", "richtig"],
            ["Projektrabatt", "5 % je Schiff, also 10 %, auf alle Positionen", "5 % einmal je Angebot, nur auf die Erstbefüllung 1.600 l, § 3 Nr. 2", "falsch: doppelt und auch auf die Reserve"],
            ["Rabatt je Position", "13 % auf alle Positionen", "Erstbefüllung 8 %, Reserve 3 %, addiert, § 3 Nr. 5", "falsch, Rabatt über der Staffel (§ 3 Nr. 6)"],
            ["Netto", "EUR " + de(alt_netto) + " (Liste EUR " + de(alt_liste) + ")", "EUR " + de(netto) + " (Liste EUR " + de(liste_sum) + ")", "zu niedrig um EUR " + de(diff)],
            ["Klasse und Freigabe", "Klasse A, automatisch versandt", "4 Punkte, Mindestklasse C: Klasse C, Freigabe Leitung Angebotsmanagement, § 8, § 9", "falsch; nach § 9 Nr. 2 darf der Assistent nur Klasse A bis 25.000 versenden"],
            ["Aussage zur Technik", "„Umstellung erfolgt ohne Anpassung Ihrer Anlagen“", "technische Zusage (§ 5 Nr. 2): nur Anwendungstechnik, nur nach Datenaufnahme (§ 5 Nr. 3, KO § 4)", "unzulässig; der Assistent erzeugt nie technische Zusagen (§ 9 Nr. 2)"],
            ["Gültigkeit", "bis " + datum(gueltig_alt), "60 Kalendertage, § 6 Nr. 3", "richtig gerechnet, inzwischen abgelaufen"],
        ])
    S.append(("Preisrechnung Schritt für Schritt",
              "### a) Prüfung der Rechnung des Angebotsassistenten (Angebotsdatum 14.07.2026)\n\n" + pruef +
              "\nDie Differenz von EUR " + de(diff) + " setzt sich zusammen aus der falschen Preisliste (EUR " + de(eff_liste) + ") und dem zu hohen Rabatt (EUR " + de(eff_rabatt) +
              "). Das Angebot weist EUR " + de(alt_netto) + " aus; Nachrechnen je Gebinde ergibt wegen Rundung je Zeile einen Cent mehr.\n\n"
              "### b) Neues Angebot nach Richtlinie (Angebotsdatum 01.03.2027, Preisliste 2026)\n\n" +
              tabelle(["Position", "Gebinde", "Anzahl", "Listenpreis je Gebinde EUR", "Listenwert EUR", "Rabatt", "Netto EUR"], zeilen) +
              "\nGebinde nach § 6 Nr. 2: möglichst große Gebinde ohne Überschreiten der Menge (1.600 l = 1 IBC + 3 Fass, 600 l = 3 Fass). "
              "Mengenrabatt nach der Gesamtmenge 2.200 l desselben Produkts: Stufe ab 1.000 l, die Stufe ab 5.000 l ist nicht erreicht. "
              "Händlerkondition entfällt (K-1018 ist kein Händler, § 3 Nr. 4).\n\n" +
              tabelle(["Schritt", "EUR"], [
                  ["Listenwert Preisliste 2026", de(liste_sum)],
                  ["Rabatte (Mengen- und Projektrabatt)", "−" + de(rabatt_eur)],
                  ["**Auftragswert** (Nettowarenwert nach Rabatten, ohne Fracht und Zuschläge, § 2 Nr. 1)", "**" + de(netto) + "**"],
                  ["Fracht (Kiel, Deutschland, frei Haus ab Nettowarenwert 2.500, § 6 Nr. 5)", "0,00, zählt nie zum Auftragswert"],
              ]) +
              "\nZahlungsziel 30 Tage netto (§ 4 Nr. 1), Lieferzeit 10 Arbeitstage ab Werk Nord (§ 6 Nr. 4), gültig bis " + datum(gueltig_neu) + ".\n"))
    S.append(("Prüfumfang und Datenaufnahme",
              "**Prüfumfang:** Auftragswert EUR " + de(netto) + " liegt bis 25.000: Pflichtprüfung Preisliste, Rabatt nach Staffel, Kundenstatus, Zahlungsziel (§ 2 Nr. 3). "
              "Kundenstatus: Bestandskunde (letzte Lieferung 29.01.2027, Muster zählen nicht, § 4 Nr. 3). Bonitätsprüfung nicht erforderlich (Bestandskunde unter 25.000, § 4 Nr. 2). "
              "Deckungsbeitrag ist unter 25.000 nicht Pflicht; zur Information: Herstellkosten P-204 2026 EUR " + de(hk_l, 3) + " je Liter, " + de(liter, 0) + " l = EUR " + de(hk) +
              "; DB vor Fracht EUR " + de(db_neu) + " (Marge vor Fracht " + pct(marge_neu) + "); Fracht frei Haus ist nicht belegt.\n\n"
              "**Datenaufnahme:** Es geht um die Umstellung stationärer Anlagen (Maschinenräume LS-0082 Baltic Star und LS-0083 Baltic Wind, fluorhaltig P-104 mit Nachfolger P-204 laut Stammdaten; "
              "deshalb ist der Projektrabatt berechtigt). Unter 25.000 ist die Datenaufnahme empfohlen, nicht Pflicht (§ 2 Nr. 4). "
              "**Aber:** Der Kunde verlangt eine schriftliche Bestätigung „ohne Anpassung der Anlagen“. Das ist eine technische Zusage (§ 5 Nr. 2). Sie gibt nur die Anwendungstechnik, "
              "nur nach Datenaufnahme der Anlage (§ 5 Nr. 3, KO § 4 Nr. 1). In den Stammdaten fehlt das Datum der Datenaufnahme für beide Maschinenräume. "
              "**Hier entscheidet ein Mensch:** Anwendungstechnik. Ohne Datenaufnahme geht keine Zusage hinaus; das Angebot nennt die Produktdaten nach Datenblatt und schlägt Datenaufnahme "
              "und Probeverschäumung als ersten Schritt vor (§ 5 Nr. 5).\n"))
    kl = tabelle(
        ["Merkmal (§ 8 Nr. 2)", "Angebot 14.07.2026 wie versandt", "Neues Angebot 01.03.2027", "Begründung"],
        [
            ["Auftragswert (§ 2 Nr. 1)", "0", "0", "EUR " + de(alt_netto) + " und EUR " + de(netto) + ", beide bis 25.000"],
            ["Rabatt (§ 3)", "2", "0", "damals 13 % statt 8 % und 3 %: über der Staffel (§ 3 Nr. 6); neu genau nach Staffel"],
            ["Technik (§ 2 Nr. 4, § 5)", "2", "2", "damals Zusage „ohne Anpassung“ enthalten; heute Zusage verlangt"],
            ["Vertrag (§ 5 Nr. 4, § 6 Nr. 6)", "0", "0", "Standardbedingungen, einmalige Lieferung"],
            ["Zahlung (§ 4)", "0", "0", "30 Tage netto, Bonität nicht erforderlich"],
            ["Kundenstatus (§ 4 Nr. 3)", "0", "0", "Bestandskunde"],
            ["Währung und Lieferort (§ 7 Nr. 3)", "0", "0", "EUR, Lieferort Kiel in der EU"],
            ["**Summe**", "**4**", "**2**", ""],
            ["Klasse nach Punkten (§ 8 Nr. 3)", "C", "B", "3 bis 4 = C, 1 bis 2 = B"],
            ["Mindestklasse (§ 8 Nr. 4)", "C", "C", "technische Zusage verlangt oder enthalten"],
            ["**Ergebnis**", "**C**", "**C**", "Mindestklasse geht vor; der Assistent hatte A vergeben"],
        ])
    S.append(("Angebotsklasse mit Punkten", kl))
    ent_tab = tabelle(
        ["Frage", "Wer entscheidet", "Regel"],
        [
            ["Freigabe des neuen Angebots, Klasse C bis 150.000", "**Hier entscheidet ein Mensch:** Leitung Angebotsmanagement (Tender Desk)", "§ 9 Nr. 1, KO § 2"],
            ["Versand durch den Angebotsassistenten", "System darf nicht: nur Klasse A bis 25.000", "§ 9 Nr. 2, KO § 2"],
            ["Technische Zusage „ohne Anpassung“", "**Hier entscheidet ein Mensch:** Anwendungstechnik, schriftlich, nach Datenaufnahme", "§ 5 Nr. 3, KO § 4 Nr. 1"],
            ["Reaktion auf das Wettbewerberangebot", "nur wenn eine schriftliche Kopie vorliegt, dann Leitung Vertrieb", "§ 1 Nr. 3, KO § 2"],
            ["Korrektur des Fehlers zu Gunsten oder Lasten des Kunden", "zuständige Stelle nach § 9: Leitung Angebotsmanagement", "§ 10 Nr. 3"],
        ])
    S.append(("Wer entscheidet: System oder Mensch", ent_tab + "\nDer Angebotsassistent darf nur einen Entwurf mit Klasse und Regelpfad vorlegen und versendet nur Klasse A bis 25.000. Am 14.07.2026 hat er ein Angebot der Klasse C versandt (Verstoß gegen § 9 Nr. 2).\n"))
    # Empfehlung
    wahl_offen = (
        "**Wahl offen, bis der Leiter Angebotsmanagement entscheidet: Preis der Bestellung.** Die Richtlinie lässt hier einen Spielraum bei der Korrektur eines Fehlers des Systems (§ 10 Nr. 3), "
        "die zuständige Stelle entscheidet.\n\n" +
        tabelle(["Möglichkeit", "Preis EUR", "Folge nach Richtlinie"], [
            ["a) Alten Preis halten", de(alt_netto), "entspricht " + pct(alt_rabatt_auf_liste) + " Rabatt auf Liste 2026, abgelaufener Preis = Rabatt über der Staffel (§ 3 Nr. 6, § 6 Nr. 3), Nachlass EUR " + de(diff) + "; Klasse bleibt C; nie automatisch zulässig"],
            ["b) Neues Angebot nach Richtlinie", de(netto), "+EUR " + de(diff) + " (+" + pct(diff / alt_netto) + ") gegenüber dem alten Angebot; keine Staffelüberschreitung; Fehler wird dem Kunden offen benannt (§ 10 Nr. 3)"],
            ["c) Neues Angebot nach Richtlinie und gezielte Kulanz", "zwischen beiden", "jeder Nachlass über der Staffel ist Rabatt über der Staffel, mit Begründung in dieser Vorlage (§ 3 Nr. 6)"],
        ]) +
        "\n**Vorschlag: b).** Begründung: Die Richtlinie kennt keinen Anspruch auf einen abgelaufenen Preis; der Kunde darf aber erfahren, dass der Fehler bei uns lag, und bekommt ihn offen benannt. "
        "Der alte Preis läge noch über den Herstellkosten (Marge vor Fracht " + pct(marge_alt) + " gegen " + pct(marge_neu) + "), aber das Argument „der Fehler war unserer“ ist eine Kulanzentscheidung, keine Regel.\n")
    wahl_ent = None
    if ent:
        wahl_ent = ("**Preis der Bestellung: entschieden durch mich (" + ent["wer"] + ", " + ent["datum"] + "). Neues Angebot nach Richtlinie zu EUR " + de(netto) +
                    ", Preisliste 2026, kein Entgegenkommen beim Preis über der Staffel; der Fehler des Angebotsassistenten wird dem Kunden offen benannt (§ 10 Nr. 3).** "
                    "Die Freigabe des Angebots bleibt bei der Leitung Angebotsmanagement (Klasse C, § 9 Nr. 1), die technische Zusage bei der Anwendungstechnik (§ 5 Nr. 3).\n")
    S.append(("Empfehlung",
              (wahl_ent if ent else wahl_offen) + "\n"
              "**Schritte:**\n\n" +
              liste([
                  "Zwischenbescheid an den Kunden sofort, mit nächstem Schritt (§ 10 Nr. 6); die Antwort auf die Mail vom 02.02.2027 ist überfällig.",
                  "Antwort 1 (System): ja, der Angebotsassistent hat das Angebot vom 14.07.2026 berechnet und versandt, eine Prüfung durch eine Person gab es nicht; die Rechnung war fehlerhaft (§ 10 Nr. 3).",
                  "Antwort 2 (Händlerkonditionen): nein, K-1018 ist nicht als Händler geführt; Mehrfachstandorte oder Schiffe ändern das nicht (§ 3 Nr. 4). Die mündliche Aussage des Außendienstes ist nicht im Angebot, sie wird geklärt und nicht übernommen (§ 10 Nr. 5).",
                  "Antwort 3 (Wettbewerber): ohne schriftliche Kopie fließt der genannte Preis nicht ein (§ 1 Nr. 3).",
                  "Antwort 4 (Bestätigung „ohne Anpassung“): jetzt nicht; Anwendungstechnik macht zuerst die Datenaufnahme beider Maschinenräume (§ 5 Nr. 3 und 5).",
                  "Das Schreiben nennt keine Klasse, keine Marge, keine Bonität (§ 10 Nr. 2).",
              ])))
    S.append(("Offene Rückfragen",
              liste([
                  "Anwendungstechnik: Termin für die Datenaufnahme der Maschinenräume vor der Werftzeit Ende März und April 2027.",
                  "Kunde: Kopie des Wettbewerberangebots (Datum, Produkt, Menge), falls er sich darauf berufen will.",
                  "Außendienst: Wer hat im Herbst am Telefon was gesagt, mit Datum?",
                  "Kunde: Wunschtermin für den Abruf; Lieferung Kiel, Gebindewahl bestätigen (IBC und Fass).",
                  "Wahl zum Preis (siehe Empfehlung)." if not ent else "Gültigkeit des neuen Angebots bis " + datum(gueltig_neu) + " dem Werfttermin gegenüberstellen.",
              ])))
    S.append(("Was nicht in die Entscheidung einfließen darf",
              liste([
                  "Händlerkondition: K-1018 ist kein Händler; „mehrere Schiffe“ ist kein Merkmal der Richtlinie (§ 3 Nr. 4).",
                  "Der genannte Wettbewerberpreis ohne schriftliche Kopie (§ 1 Nr. 3).",
                  "Die mündliche Aussage des Außendienstes (§ 10 Nr. 5).",
                  "Das Anfragedatum als Datum für die Preisliste (§ 6 Nr. 1).",
                  "Projektrabatt zweimal oder auf die Reservemenge (§ 3 Nr. 2).",
                  "Fracht und Zuschläge im Auftragswert (§ 2 Nr. 1).",
                  "Die Klasse „A“ und die Rechnung des Assistenten als Grundlage (§ 9 Nr. 4).",
                  "Angebotsklasse, Marge und Bonität im Schreiben an den Kunden (§ 10 Nr. 2).",
              ])))
    pfad = [
        {"schritt": "Prüfumfang", "angabe": "Auftragswert EUR " + de(netto) + ", ohne Fracht und Zuschläge", "par": "§ 2 Nr. 1 und 3", "ergebnis": "bis 25.000: Preisliste, Staffel, Kundenstatus, Zahlungsziel"},
        {"schritt": "Datenaufnahme", "angabe": "stationäre Anlagen, Wert unter 25.000, Zusage „ohne Anpassung“ verlangt", "par": "§ 2 Nr. 4, § 5 Nr. 3", "ergebnis": "empfohlen, für jede Zusage Voraussetzung; fehlt in den Stammdaten", "mensch": True, "wer": "Anwendungstechnik"},
        {"schritt": "Preisliste und Rabatte", "angabe": "Liste 2026 am Angebotsdatum; 3 % Menge, 5 % Projekt einmal auf 1.600 l", "par": "§ 6 Nr. 1, § 3 Nr. 1, 2, 5", "ergebnis": "8 % Erstbefüllung, 3 % Reserve; kein Händler"},
        {"schritt": "Angebotsklasse", "angabe": "2 Punkte, Mindestklasse C", "par": "§ 8 Nr. 2 bis 4", "ergebnis": "Klasse C (Assistent: A)"},
        {"schritt": "Preis der Bestellung", "angabe": "alter Preis EUR " + de(alt_netto) + " oder neues Angebot EUR " + de(netto), "par": "§ 3 Nr. 6, § 6 Nr. 3, § 10 Nr. 3",
         "ergebnis": ("entschieden durch mich: neues Angebot" if ent else "Wahl offen"), "mensch": True, "wer": "Leitung Angebotsmanagement"},
        {"schritt": "Kompetenz", "angabe": "Klasse C bis 150.000", "par": "§ 9 Nr. 1 und 2, KO § 2", "ergebnis": "Freigabe Leitung Angebotsmanagement; System darf nicht versenden", "mensch": True, "wer": "Leitung Angebotsmanagement"},
    ]
    return {
        "id": vid, "kunde": "K-1018 Reederei Ostsee Linien AG", "titel": "Rückfrage zum Angebot vom Juli 2026, Bestellung zum alten Preis",
        "auftragswert": netto, "klasse": "C", "entscheidet": "Leitung Angebotsmanagement",
        "empfehlung": ("Neues Angebot nach Richtlinie, entschieden durch mich" if ent else "Neues Angebot nach Richtlinie vorgeschlagen, Wahl offen"),
        "abschnitte": S, "pfad": pfad,
    }


# ------------------------------------------------------------------ A-02
def a02():
    vid = "A-02"
    ent = ENTSCHIEDEN.get(vid)
    ibc, kan = 18, 300
    lj = position("2026", "P-201", {"IBC": ibc, "Kanister": kan}, "0")
    liste_jahr = lj["listenwert"]
    liter_jahr = lj["liter"]
    hk_l = HK[("P-201", "2026")]
    hk_jahr = cent(hk_l * liter_jahr)
    fr = fracht_je_liter()
    fr_jahr = cent(fr["Stückgut"] * 18000 + fr["Paket"] * 6000)
    ff_marge = D("0.230")  # Finanzkommentar: DB-Marge fluorfrei 2026

    def zeile(satz):
        p = position("2026", "P-201", {"IBC": ibc, "Kanister": kan}, satz)
        u = p["netto"]
        db_vor = cent(u - hk_jahr)
        db_nach = cent(db_vor - fr_jahr)
        return {"u": u, "db_vor": db_vor, "m_vor": db_vor / u, "db_nach": db_nach, "m_nach": db_nach / u, "drei": cent(u * 3)}

    z10, z8, z18 = zeile("0.10"), zeile("0.08"), zeile("0.18")
    wert = z10["drei"]
    # Rabatt, bei dem die Marge nach geschaetzter Fracht den Wert des Finanzkommentars erreicht
    r_nach = 1 - (hk_jahr + fr_jahr) / (liste_jahr * (1 - ff_marge))
    r_vor = 1 - hk_jahr / (liste_jahr * (1 - ff_marge))
    gesamt_liste = cent(liste_jahr * 3)
    punkte_zahlung = 1
    summe = 4 + 0 + 0 + 2 + punkte_zahlung + 1 + 0
    summe_alt = summe - punkte_zahlung

    S = []
    S.append(("Vorgang in Kürze",
              "Der Zweckverband Feuerwehrbedarf Lindenmoor (K-9001, Interessent, öffentlicher Auftraggeber) schreibt einen Rahmenvertrag über fluorfreies Schwerschaum-Mittel 3 % für "
              "14 Gerätehäuser und ein Zentrallager aus: 01.07.2027 bis 30.06.2030, geschätzt 24.000 l je Jahr (18.000 l IBC, 6.000 l Kanister, 300 Stück), Menge nicht verbindlich, "
              "keine Verlängerungsoption. Abgabe bis Montag, 22.03.2027, 12:00 Uhr; Bieterfragen bis 08.03.2027. Der Angebotsassistent hat einen Entwurf gerechnet (10 % Mengenrabatt "
              "plus 8 % Rahmenvertragsrabatt = 18 %); Lina Osterkamp fragt, ob sie ihn so hochladen soll.\n\n"
              "Produkt: Die Ausschreibung nennt kein Produkt; angenommen wird FreeFoam 3 % (P-201), wie im Entwurf des Assistenten.\n"))
    S.append(("Stand-Datum, Preisliste und Richtlinie",
              liste([
                  "**Stand:** Montag, 01.03.2027. Angebotsdatum ist der Tag der Abgabe, spätestens 22.03.2027.",
                  "**Preisliste 2026** (RL § 6 Nr. 1): Sie gilt bis zur Preisliste 2027, angekündigt für April 2027; Abgabe liegt davor. Die Preise im Vertrag sind für das erste Vertragsjahr fest, danach nach Vorgabe des Kunden.",
                  "**RL-ANG-2026** und **KO-2026** (Angebotsdatum ab 01.01.2026). Für Rahmenverträge zählt die Menge über die ganze Laufzeit ohne Preisgleitung (RL § 2 Nr. 1).",
                  "Währung EUR.",
              ])))
    S.append(("Vorliegende und nur erwähnte Unterlagen",
              "**Liegt im Angebotseingang vor:**\n\n" + liste([
                  "Auszug aus den Vergabeunterlagen (Gegenstand, Laufzeit, Menge, Bedingungen, einzureichende Unterlagen, Zuschlagskriterien: Preis 70 %, Lieferfähigkeit und Logistik 20 %, Referenzen 10 %)",
                  "Interne Begleitnotiz von Lina Osterkamp vom 15.02.2027",
                  "Stammdaten: Preisliste 2026, Herstellkosten P-201 2026",
              ]) + "\n**Nur erwähnt, liegt nicht bei:**\n\n" + liste([
                  "Referenzliste aus 2024: Linas Notiz sagt „liegt bei“, im Angebotseingang liegt keine Referenzliste. Verlangt sind mindestens drei Referenzen öffentlicher Feuerwehren aus den letzten drei Jahren; ob die Liste aus 2024 dafür taugt und freigegeben ist, ist nicht belegt (RL § 2 Nr. 3 und 5)",
                  "Entwurf des Angebotsassistenten mit 18 %: nur in Linas Notiz beschrieben, keine Datei",
                  "Anlage 1 (Preisblatt), Anlage 3 (Referenzen), Eigenerklärung zur Lieferfähigkeit, Technisches Datenblatt und Sicherheitsdatenblatt, Muster 20 l: vom Kunden verlangt, bei uns nicht erstellt",
              ])))
    rab_tab = tabelle(["Rabatt auf Liste", "Nettoumsatz je Jahr EUR", "Auftragswert 3 Jahre EUR", "Paragraf", "Ergebnis"], [
        ["0 % (Liste 2026)", de(liste_jahr), de(gesamt_liste), "§ 6 Nr. 1", "Ausgangspunkt"],
        ["10 % Mengenrabatt", de(z10["u"]), de(z10["drei"]), "§ 3 Nr. 1", "nach Staffel"],
        ["bis 8 % Rahmenvertragsrabatt", de(z8["u"]), de(z8["drei"]), "§ 3 Nr. 3", "nach Staffel, aber nur mit fester Abnahmemenge"],
        ["18 % (Entwurf des Assistenten: 10 % + 8 %)", de(z18["u"]), de(z18["drei"]), "§ 3 Nr. 3 und 6", "**unzulässig**: Rahmenrabatt ersetzt den Mengenrabatt, kein Zusammenzählen"],
    ])
    S.append(("Preisrechnung Schritt für Schritt",
              "**Listenpreise 2026 für P-201:** IBC 1.000 l EUR " + de(PREIS[("2026", "P-201", "IBC")]) + ", Kanister 20 l EUR " + de(PREIS[("2026", "P-201", "Kanister")]) + ".\n\n" +
              tabelle(["Schritt", "Rechnung", "EUR"], [
                  ["IBC je Jahr", str(ibc) + " × " + de(PREIS[("2026", "P-201", "IBC")]), de(position("2026", "P-201", {"IBC": ibc}, "0")["listenwert"])],
                  ["Kanister je Jahr", str(kan) + " × " + de(PREIS[("2026", "P-201", "Kanister")]), de(position("2026", "P-201", {"Kanister": kan}, "0")["listenwert"])],
                  ["Listenwert je Jahr", "24.000 l", de(liste_jahr)],
                  ["Listenwert drei Jahre", "× 3, ohne Preisgleitung (§ 2 Nr. 1)", de(gesamt_liste)],
              ]) + "\n" + rab_tab +
              "\nDer Rabatt des Entwurfs ist nicht zulässig. Der Auftragswert über die Laufzeit liegt bei jedem zulässigen Rabatt über 150.000 (mit 10 %: EUR " + de(z10["drei"]) + "). "
              "Fracht frei Verwendungsstelle und Zuschläge zählen nicht zum Auftragswert (§ 2 Nr. 1, § 6 Nr. 5). Muster 20 l sind kostenlos (§ 3 Nr. 7).\n"))
    db_tab = tabelle(
        ["Rabatt", "Nettoumsatz je Jahr", "Herstellkosten je Jahr", "DB vor Fracht", "Marge vor Fracht", "Fracht je Jahr (geschätzt)", "Marge nach geschätzter Fracht", "gegen 23,0 % fluorfrei 2026"],
        [
            ["8 %", de(z8["u"]), de(hk_jahr), de(z8["db_vor"]), pct(z8["m_vor"]), de(fr_jahr), pct(z8["m_nach"]), "darüber" if z8["m_nach"] >= ff_marge else "darunter"],
            ["10 %", de(z10["u"]), de(hk_jahr), de(z10["db_vor"]), pct(z10["m_vor"]), de(fr_jahr), pct(z10["m_nach"]), "darüber" if z10["m_nach"] >= ff_marge else "darunter"],
            ["18 % (Entwurf)", de(z18["u"]), de(hk_jahr), de(z18["db_vor"]), pct(z18["m_vor"]), de(fr_jahr), pct(z18["m_nach"]), "darüber" if z18["m_nach"] >= ff_marge else "darunter"],
        ])
    S.append(("Prüfumfang und Datenaufnahme",
              "**Prüfumfang:** Auftragswert über 150.000: zusätzlich zu Preisliste, Staffel, Kundenstatus und Zahlungsziel auch Deckungsbeitrag, Bonität, Lieferfähigkeit (Stufe 25.000,01 bis 150.000) "
              "sowie Vertragsprüfung, Liefer- und Rohstoffplanung und Referenzen nur aus der freigegebenen Referenzliste (§ 2 Nr. 3). "
              "Bonität: Interessent über 10.000 wäre zu prüfen; öffentliche Auftraggeber werden ohne Prüfung zu ihren Zahlungsbedingungen beliefert, wenn diese 30 Tage nicht überschreiten (§ 4 Nr. 2 und 4). "
              "Der Kunde zahlt 30 Tage nach Rechnungseingang; ob das „30 Tage nicht überschreitet“, sagt die Richtlinie nicht (siehe Klasse).\n\n"
              "**Datenaufnahme:** nicht erforderlich. Es geht um Lieferung für Feuerwehrfahrzeuge und tragbare Zumischer, nicht um Erstbefüllung oder Umstellung einer stationären Löschanlage (§ 2 Nr. 4). "
              "Eine technische Zusage über das Datenblatt hinaus ist nicht verlangt.\n\n"
              "### Deckungsbeitrag: Trägt die Marge den Rabatt?\n\n"
              "Vergleichswert: DB-Marge fluorfreie Produkte 2026 im Übungsausschnitt " + pct(ff_marge) + " (Finanzkommentar: Deckungsbeitrag nach Herstellkosten und Fracht ÷ Nettoumsatz, 104 Positionen, Ist, Konzernkurs 2026). "
              "Das ist ein Durchschnitt, keine Mindestmarge; die Richtlinie nennt keine.\n\n" + db_tab +
              "\nRechnung: Herstellkosten P-201 2026 EUR " + de(hk_l, 3) + " je Liter (Rohstoff und Fertigung) × 24.000 l. Fracht geschätzt aus dem Übungsausschnitt: IBC als Stückgut zu EUR " + de(fr["Stückgut"], 3) +
              " je Liter, Kanister als Paket zu EUR " + de(fr["Paket"], 3) + " je Liter (alle Sendungen, ohne Zielort); das ist **eine Annahme, nicht belegt**.\n\n"
              "**Ergebnis:** Der Entwurf mit 18 % trägt nicht: Marge nach geschätzter Fracht " + pct(z18["m_nach"]) + " gegen " + pct(ff_marge) + ". Mit 10 % sind es " + pct(z10["m_nach"]) + ", mit 8 % " + pct(z8["m_nach"]) +
              ". Die Marge von " + pct(ff_marge) + " bleibt bis zu einem Rabatt von " + pct(r_nach) + " erhalten (nach geschätzter Fracht; vor Fracht " + pct(r_vor) + ").\n\n"
              "**Was fehlt:**\n\n" + liste([
                  "Tatsächliche Fracht: Lieferung frei Verwendungsstelle an 14 Gerätehäuser und ein Zentrallager innerhalb von 5 Arbeitstagen; die Frachttabelle kennt weder diese Orte noch Mengen je Abruf",
                  "Herstellkosten 2027 bis 2030: es gibt nur 2026; der Kunde lässt ab Jahr 2 Preise nach seinem Index gleiten (höchstens +3 % je Jahr, Senkungen voll weitergeben)",
                  "Kosten der Vertragsstrafe (0,5 % des Abrufwerts je Arbeitstag, höchstens 5 %) und der Lager- und Kapitalbindung bei 5 Arbeitstagen Lieferzeit",
                  "Kosten für Muster 20 l, Ausschreibungsaufwand, Zahlungsziel ab Rechnungseingang",
                  "Eine Marge des Produkts P-201 selbst: 2026 nur 8 Positionen im Übungsausschnitt, unter 20 Positionen ist das eine Lücke",
              ])))
    pkte = tabelle(["Merkmal (§ 8 Nr. 2)", "Punkte", "Begründung"], [
        ["Auftragswert (§ 2 Nr. 1)", "4", "EUR " + de(z10["drei"]) + " über Laufzeit, über 150.000"],
        ["Rabatt (§ 3)", "0", "10 % genau nach Staffel (§ 3 Nr. 1); mit dem Entwurf von 18 % wären es 2 (§ 3 Nr. 6)"],
        ["Technik (§ 2 Nr. 4, § 5)", "0", "nur Produktdaten nach Datenblatt, keine stationäre Anlage"],
        ["Vertrag (§ 5 Nr. 4, § 6 Nr. 6)", "2", "Laufzeit 3 Jahre, Preisgleitung nach Index des Kunden (nicht unsere Standardklausel), Vertragsstrafe, Bedingungen des Kunden"],
        ["Zahlung (§ 4)", str(punkte_zahlung) + " (**Wahl offen**: 0 oder 1)", "30 Tage nach Rechnungseingang statt ab Rechnungsdatum; Bonität bei öffentlichem Auftraggeber nicht erforderlich (§ 4 Nr. 4)"],
        ["Kundenstatus (§ 4 Nr. 3)", "1", "Interessent, kein Kunde (K-9001)"],
        ["Währung und Lieferort (§ 7 Nr. 3)", "0", "EUR; Lieferorte nicht genannt, Annahme in der EU (Rückfrage)"],
        ["**Summe**", "**" + str(summe) + "** (bei Zahlung 0: " + str(summe_alt) + ")", "7 und mehr = Klasse E"],
        ["Mindestklassen (§ 8 Nr. 4)", "D und E", "öffentliche Ausschreibung: mindestens D; Auftragswert über 150.000: mindestens E"],
        ["**Ergebnis**", "**Klasse E**", "in beiden Fällen E"],
    ])
    S.append(("Angebotsklasse mit Punkten", pkte))
    wer = tabelle(["Frage", "Wer entscheidet", "Regel"], [
        ["Teilnahme an der Ausschreibung oder Absage", "**Hier entscheidet ein Mensch:** Geschäftsführung", "§ 9 Nr. 3, KO § 2"],
        ["Freigabe Klasse E und Rahmenvertrag über 150.000", "**Hier entscheidet ein Mensch:** Geschäftsführung, Unterschrift durch zwei Personen", "§ 9 Nr. 1, KO § 2 und § 6"],
        ["Vertragsstrafe, Haftungsübernahme", "**Hier entscheidet ein Mensch:** Geschäftsführung", "§ 5 Nr. 4, KO § 2"],
        ["Lieferzeit 5 Arbeitstage (Standard 10 Arbeitstage)", "**Hier entscheidet ein Mensch:** Leitung Vertrieb", "§ 6 Nr. 4, KO § 2"],
        ["Zahlungsziel, wenn über 30 Tage gerechnet", "**Hier entscheidet ein Mensch:** Leitung Vertrieb", "§ 4 Nr. 1, KO § 2"],
        ["Hochladen des Entwurfs des Assistenten", "System darf nicht versenden; Entwurf nur zur Vorlage", "§ 9 Nr. 2"],
    ])
    S.append(("Wer entscheidet: System oder Mensch", wer))
    wahl_offen = (
        "**Wahl offen, bis entschieden ist: Rabatt in der Ausschreibung.** Die Richtlinie lässt eine Spanne (Rahmenvertragsrabatt „bis 8 %“), und sie sagt nicht, was bei unverbindlicher Menge gilt.\n\n" +
        tabelle(["Möglichkeit", "Folge"], [
            ["a) 10 % Mengenrabatt nach Staffel", "Auftragswert EUR " + de(z10["drei"]) + "; schon die Jahresmenge 24.000 l erreicht die Stufe ab 20.000 l; Marge nach geschätzter Fracht " + pct(z10["m_nach"]) + "; Rahmenrabatt entfällt, weil die Menge nicht fest ist (§ 3 Nr. 3)"],
            ["b) Rahmenvertragsrabatt bis 8 %", "nur mit fester Abnahmemenge; die Unterlagen nennen die Menge „nicht verbindlich“; ersetzt den Mengenrabatt; EUR " + de(z8["drei"]) + " bei 8 %"],
            ["c) 18 % wie im Entwurf", "unzulässig (§ 3 Nr. 3), Rabatt über der Staffel (§ 3 Nr. 6), trägt die Marge nicht"],
        ]) +
        "\n**Vorschlag: a).** Begründung: Er folgt der Staffel ohne Auslegung der Abnahmemenge, ist für den Preis (70 % der Zuschlagskriterien) günstiger als b), und die Marge nach geschätzter Fracht liegt über dem Wert aus dem Finanzkommentar. "
        "Offen bleibt, ob bei fester Abnahmemenge der Rahmenrabatt (bis 8 %) an die Stelle des höheren Mengenrabatts treten muss; das regelt die Richtlinie nicht. Die Bieterfrage bis 08.03.2027 klärt, ob die Menge verbindlich ist.\n\n"
        "**Wahl offen: Punkt für das Zahlungsziel** (0 oder 1, Klasse E in beiden Fällen). Vorschlag: 1 Punkt, weil die Frist erst mit Rechnungseingang beginnt und das länger ist als der Standard ab Rechnungsdatum.\n")
    S.append(("Empfehlung",
              wahl_offen + "\n**Schritte:**\n\n" + liste([
                  "Lina Osterkamp antworten: Entwurf **nicht hochladen** (18 % nicht zulässig, System darf nichts versenden, § 3 Nr. 3, § 9 Nr. 2).",
                  "Der Geschäftsführung die Teilnahme vorlegen, mit Kalkulation nach Vorschlag a), den Vertragsbedingungen des Kunden (Index, Vertragsstrafe, 5 Arbeitstage) und diesen Rückfragen; Entscheidung vor dem 08.03.2027, damit Bieterfragen noch möglich sind.",
                  "Bieterfragen bis 08.03.2027: Ist die Menge verbindlich? Lieferland der Gerätehäuser? Beginn der Zahlungsfrist? Anforderung an die Referenzen?",
                  "Referenzen: freigegebene Referenzliste beschaffen und gegen die Drei-Jahres-Anforderung prüfen; ohne sie keine Abgabe (§ 2 Nr. 3).",
                  "Lieferfähigkeit und Rohstoffplanung für 24.000 l je Jahr mit Lager und Einkauf klären (§ 2 Nr. 3).",
              ])))
    S.append(("Offene Rückfragen",
              liste([
                  "Geschäftsführung: Teilnahme ja oder nein; Vertragsstrafe und Index-Klausel akzeptabel?",
                  "Leitung Vertrieb: Lieferzeit 5 Arbeitstage und Zahlungsziel ab Rechnungseingang.",
                  "Vertrieb: freigegebene Referenzliste (Stand und Eignung) liegt nicht bei.",
                  "Kunde (Bieterfragen bis 08.03.2027): Mindestabnahme, Lieferländer, Zahlungsfrist, Preisgleitung.",
                  "Logistik: Frachtangebot für 14 Gerätehäuser und Zentrallager; Lagerbestand und Rohstoffplanung.",
                  "Controlling: Herstellkosten 2027 bis 2030.",
                  "Rabatt und Zahlungsziel-Punkt (siehe Empfehlung).",
              ])))
    S.append(("Was nicht in die Entscheidung einfließen darf",
              liste([
                  "Die Aussage des Assistenten, der Entwurf sei „sehr wettbewerbsfähig“: er hat Rabatte zusammengezählt, die nicht zusammengehören (§ 3 Nr. 3).",
                  "Ein Zusammenzählen von Mengenrabatt und Rahmenvertragsrabatt (§ 3 Nr. 3 und 5).",
                  "Referenzen, die nicht aus der freigegebenen Liste stammen, oder Referenzen älter als drei Jahre (§ 2 Nr. 3).",
                  "Fracht, Muster und Zuschläge im Auftragswert (§ 2 Nr. 1).",
                  "Die Preisgleitung des Kunden als „unsere Standardklausel“ (§ 6 Nr. 6).",
                  "Sitzland oder Art des Auftraggebers als Ersatz für Preis oder Rabatt (§ 1 Nr. 2); der öffentliche Auftraggeber erhält keinen Sonderpreis.",
                  "Marge und Klasse in jedem Schreiben an den Kunden oder in den Vergabeunterlagen (§ 10 Nr. 2).",
              ])))
    pfad = [
        {"schritt": "Prüfumfang", "angabe": "Auftragswert EUR " + de(z10["drei"]) + " über drei Jahre, ohne Fracht", "par": "§ 2 Nr. 1 und 3", "ergebnis": "über 150.000: Vertragsprüfung, Planung, Referenzliste"},
        {"schritt": "Datenaufnahme", "angabe": "keine stationäre Anlage, keine Zusage verlangt", "par": "§ 2 Nr. 4", "ergebnis": "nicht erforderlich"},
        {"schritt": "Rabatt", "angabe": "10 % Staffel oder bis 8 % Rahmenvertrag; Entwurf 18 %", "par": "§ 3 Nr. 1, 3 und 6", "ergebnis": "18 % unzulässig; Wahl offen", "mensch": True, "wer": "Leitung Angebotsmanagement schlägt vor, Geschäftsführung gibt frei"},
        {"schritt": "Deckungsbeitrag", "angabe": "Marge nach geschätzter Fracht " + pct(z10["m_nach"]) + " bei 10 %, " + pct(z18["m_nach"]) + " bei 18 %", "par": "§ 2 Nr. 3", "ergebnis": "10 % trägt gegen 23,0 %, 18 % nicht"},
        {"schritt": "Vertrag", "angabe": "3 Jahre, Index-Gleitung, Vertragsstrafe, Bedingungen des Kunden", "par": "§ 5 Nr. 4, § 6 Nr. 6", "ergebnis": "2 Punkte; Vertragsstrafe", "mensch": True, "wer": "Geschäftsführung"},
        {"schritt": "Angebotsklasse", "angabe": str(summe) + " Punkte (bei Zahlung 0: " + str(summe_alt) + "), Mindestklassen D und E", "par": "§ 8 Nr. 2 bis 4", "ergebnis": "Klasse E"},
        {"schritt": "Lieferzeit", "angabe": "5 Arbeitstage gegen Standard 10", "par": "§ 6 Nr. 4, KO § 2", "ergebnis": "Zusage unter Standard", "mensch": True, "wer": "Leitung Vertrieb"},
        {"schritt": "Kompetenz", "angabe": "Klasse E, Rahmenvertrag über 150.000, Teilnahme an Ausschreibung", "par": "§ 9 Nr. 1 und 3, KO § 2", "ergebnis": "Geschäftsführung; System darf nichts versenden", "mensch": True, "wer": "Geschäftsführung"},
    ]
    return {
        "id": vid, "kunde": "K-9001 Zweckverband Feuerwehrbedarf Lindenmoor", "titel": "Ausschreibung Rahmenvertrag 2027 bis 2030",
        "auftragswert": z10["drei"], "klasse": "E", "entscheidet": "Geschäftsführung",
        "empfehlung": "Teilnahme der Geschäftsführung vorlegen, 10 % Mengenrabatt, nicht 18 %; Wahl offen",
        "abschnitte": S, "pfad": pfad,
    }


# ------------------------------------------------------------------ A-03
def a03():
    vid = "A-03"
    b1 = position("2026", "P-204", {"IBC": 4}, "0.11")
    b2 = position("2026", "P-204", {"IBC": 2}, "0.06")
    liste_sum = cent(b1["listenwert"] + b2["listenwert"])
    netto = cent(b1["netto"] + b2["netto"])
    nok = kurs(2027, "NOK")
    netto_nok = cent(netto / nok)
    budget_nok = D(650000)
    budget_eur = cent(budget_nok * nok)
    liter = b1["liter"] + b2["liter"]
    hk_l = HK[("P-204", "2026")]
    hk = cent(hk_l * liter)
    db = cent(netto - hk)
    S = []
    S.append(("Vorgang in Kürze",
              "Nordic Offshore Services AS (K-1019, Norwegen, Bestandskunde, nicht als Händler geführt) will die Schaumberieselungsanlage der Plattform Nord-3 im Wartungsfenster Mai 2027 auf FreeFoam Marine 3 % (P-204) umstellen: "
              "4.000 l Erstbefüllung und 2.000 l Reserve, bevorzugt IBC, Lieferung an die Versorgungsbasis in Westnorwegen. Der Kunde verlangt außerdem: (1) Preise in NOK, Budget NOK 650.000 einschließlich Fracht; "
              "(2) eine schriftliche Garantie, dass das Produkt unter Offshore-Bedingungen mindestens so gut wirkt wie das installierte; (3) eine schriftliche Bestätigung zur angekündigten EU-Beschränkung; (4) 45 Tage Zahlungsziel. "
              "Anfrage vom 16.02.2027, Angebot gewünscht bis Ende Februar; die Antwort ist überfällig (drei Arbeitstage am 19.02.2027, RL § 10 Nr. 6).\n"))
    S.append(("Stand-Datum, Preisliste und Richtlinie",
              liste([
                  "**Stand:** Montag, 01.03.2027; Angebotsdatum angenommen 01.03.2027.",
                  "**Preisliste 2026** (RL § 6 Nr. 1), gültig bis zur Preisliste 2027 (angekündigt April 2027).",
                  "**RL-ANG-2026** und **KO-2026**.",
                  "**Währung:** Kalkuliert wird in EUR; umgerechnet zum Konzernkurs des Kalenderjahres des Angebotsdatums (2027 = Kurs 2026): 1 NOK = EUR " + de(nok, 4) + " (§ 7 Nr. 2). Für alle Grenzen gilt der EUR-Betrag.",
              ])))
    S.append(("Vorliegende und nur erwähnte Unterlagen",
              "**Liegt im Angebotseingang vor:**\n\n" + liste([
                  "Anfrage (RFQ) vom 16.02.2027 auf Englisch (Henrik Solberg, Fire Safety Manager)",
                  "Interne Notiz des Vertriebsinnendienstes vom 17.02.2027 (Vorsortierung des Assistenten, Hinweis des Außendienstes)",
                  "Stammdaten: Kunde K-1019, Lieferstellen LS-0086 Plattform Nord-3 (derzeit P-117, fluorhaltig, Füllmenge 4.000 l), LS-0088 Pilotanlage (Datenaufnahme 19.03.2024), Preisliste 2026, Konzernkurs",
              ]) + "\n**Nur erwähnt, liegt nicht bei:**\n\n" + liste([
                  "Technisches Datenblatt, in dem FreeFoam Marine als „fluorfrei deklariert“ steht: erwähnt in der internen Notiz, nicht im Ordner",
                  "Datenaufnahme der Anlage Nord-3: in den Stammdaten kein Datum; die Datenaufnahme der Pilotanlage (LS-0088) gilt nur für diese Anlage",
                  "Zahlungserfahrung mit dem Kunden („zahlen erfahrungsgemäß spät“): Aussage des Außendienstes ohne Beleg",
                  "Ergebnis der letzten Bonitätsprüfung: nicht im Ordner",
                  "Genehmigtes Budget NOK 650.000: Angabe des Kunden, ohne Beleg",
              ])))
    zeilen = []
    for name, p, rt in (("1 Erstbefüllung Nord-3 (4.000 l)", b1, "11 % = 6 % Mengenrabatt (§ 3 Nr. 1) + 5 % Projektrabatt (§ 3 Nr. 2)"),
                        ("2 Reserve Plattformlager (2.000 l)", b2, "6 % Mengenrabatt (§ 3 Nr. 1)")):
        for z in p["zeilen"]:
            zeilen.append([name, "IBC 1.000 l", z["anzahl"], de(z["listenpreis"]), de(z["listenwert"]), rt, de(z["netto"])])
    S.append(("Preisrechnung Schritt für Schritt",
              tabelle(["Position", "Gebinde", "Anzahl", "Listenpreis je Gebinde EUR", "Listenwert EUR", "Rabatt", "Netto EUR"], zeilen) +
              "\nMengenrabatt nach der Gesamtmenge 6.000 l desselben Produkts: Stufe ab 5.000 l (6 %), die Stufe ab 20.000 l ist nicht erreicht. "
              "Projektrabatt: Nord-3 ist eine stationäre Anlage mit fluorhaltigem P-117, dessen Nachfolger laut Stammdaten P-204 ist; er gilt einmal und nur auf die Erstbefüllung 4.000 l (Füllmenge laut Stammdaten 4.000 l), nicht auf die Reserve. "
              "Händlerkondition entfällt (kein Händler, § 3 Nr. 4).\n\n" +
              tabelle(["Schritt", "Betrag"], [
                  ["Listenwert Preisliste 2026", eur(liste_sum)],
                  ["Rabatte", "−" + eur(liste_sum - netto)],
                  ["**Auftragswert** (ohne Fracht, § 2 Nr. 1), in EUR", "**" + eur(netto) + "**"],
                  ["Angebotswährung NOK zum Konzernkurs " + de(nok, 4) + " (§ 7 Nr. 2)", "NOK " + de(netto_nok)],
                  ["Budget des Kunden NOK 650.000, in EUR zum selben Kurs (enthält Fracht)", eur(budget_eur)],
              ]) +
              "\nFracht: Lieferung FCA Werk Nord, Fracht nach Angebot der Spedition als eigene Position, Zoll und Einfuhr trägt der Kunde (§ 6 Nr. 5, § 7 Nr. 1); sie zählt nie zum Auftragswert. "
              "Das Budget des Kunden enthält Fracht, unser Preis nicht: Die beiden Beträge sind nicht vergleichbar, solange das Frachtangebot fehlt. Das Budget ändert keine Grenze (§ 7 Nr. 2). "
              "Angebot auf Englisch, zulässig (§ 7 Nr. 5).\n"))
    S.append(("Prüfumfang und Datenaufnahme",
              "**Prüfumfang:** Auftragswert " + eur(netto) + " liegt zwischen 25.000,01 und 150.000: zusätzlich zur Grundprüfung Deckungsbeitrag, Bonität, Lieferfähigkeit (§ 2 Nr. 3). "
              "Deckungsbeitrag: Herstellkosten P-204 2026 EUR " + de(hk_l, 3) + " je Liter × 6.000 l = " + eur(hk) + "; DB vor Fracht " + eur(db) + ", Marge vor Fracht " + pct(db / netto) + "; "
              "bei FCA Werk Nord zahlt der Kunde die Fracht, in unserem Deckungsbeitrag steht keine (Annahme). Bonität: Bestandskunde (letzte Lieferung 08.02.2027) mit Auftragswert über 25.000, zu prüfen, wenn die letzte Prüfung älter als zwölf Monate ist (§ 4 Nr. 2); "
              "das Datum der letzten Prüfung liegt nicht vor, dann gilt „nicht geprüft“. Lieferfähigkeit: 6 IBC für Mai 2027, Lagerbestand nicht belegt.\n\n"
              "**Datenaufnahme: Pflicht.** Erstbefüllung und Umstellung einer stationären Anlage (Plattform Nord-3) ab 25.000 (§ 2 Nr. 4). Die Stammdaten (LS-0086) haben kein Datum der Datenaufnahme und keine eingestellte Zumischrate "
              "am Zumischer, nur die Zumischrate laut CRM 3,0 %. Die Datenaufnahme macht die Anwendungstechnik, **bevor das Angebot verbindlich wird**. Ohne sie gibt es keine technische Zusage (§ 5 Nr. 3). "
              "**Hier entscheidet ein Mensch:** Anwendungstechnik. Bis zur Datenaufnahme nennt das Angebot die Daten nach Datenblatt und schlägt Datenaufnahme und Probeverschäumung als ersten Schritt vor (§ 5 Nr. 5). "
              "Das Wartungsfenster im Mai 2027 braucht den Termin vorher.\n"))
    pkte = tabelle(["Merkmal (§ 8 Nr. 2)", "Punkte", "Begründung"], [
        ["Auftragswert (§ 2 Nr. 1)", "2", eur(netto) + ", zwischen 25.000,01 und 150.000"],
        ["Rabatt (§ 3)", "0", "6 % Mengenrabatt und 5 % Projektrabatt genau nach Staffel; kein Rabatt über der Staffel angefragt (der Wettbewerb spielt keine Rolle)"],
        ["Technik (§ 2 Nr. 4, § 5)", "2", "technische Zusage über das Datenblatt hinaus verlangt („mindestens so gut wie bisher“, Garantie)"],
        ["Vertrag (§ 5 Nr. 4, § 6 Nr. 6)", "0", "Standardbedingungen, Einmallieferung; die verlangte Garantie wird nicht gegeben (§ 5 Nr. 4)"],
        ["Zahlung (§ 4)", "1", "45 Tage statt 30 Tage netto; Bonität nicht geprüft"],
        ["Kundenstatus (§ 4 Nr. 3)", "0", "Bestandskunde: Lieferung am 08.02.2027"],
        ["Währung und Lieferort (§ 7 Nr. 3)", "1", "NOK als Angebotswährung und Lieferort außerhalb der EU (FCA Werk Nord, Lieferung nach Westnorwegen). Das Sitzland als solches zählt nicht (§ 1 Nr. 2)"],
        ["**Summe**", "**6**", "5 bis 6 = Klasse D"],
        ["Mindestklassen (§ 8 Nr. 4)", "C und D", "C wegen technischer Zusage, D wegen verlangter Rechtsaussage (§ 1 Nr. 4, § 7 Nr. 4)"],
        ["**Ergebnis**", "**Klasse D**", "nach Punkten D, Mindestklasse D"],
    ])
    S.append(("Angebotsklasse mit Punkten", pkte))
    wer = tabelle(["Frage", "Wer entscheidet", "Regel"], [
        ["Freigabe des Angebots, Klasse D bis 150.000", "**Hier entscheidet ein Mensch:** Leitung Vertrieb", "§ 9 Nr. 1, KO § 2"],
        ["Bestätigung zur angekündigten EU-Beschränkung", "**Hier entscheidet ein Mensch:** Regulatory Affairs, nur sie. Vertrieb, Tender Desk, Anwendungstechnik und Systeme antworten nicht, auch nicht vorläufig. Der Kunde erfährt nur, dass die Frage dort geprüft wird.", "§ 1 Nr. 4, § 7 Nr. 4, KO § 3"],
        ["Technische Zusage „mindestens so gut wie bisher“", "**Hier entscheidet ein Mensch:** Anwendungstechnik, schriftlich, nach Datenaufnahme Nord-3", "§ 5 Nr. 3, KO § 4 Nr. 1"],
        ["Pauschale Garantie der Löschwirkung", "wird nicht gegeben; Ausnahmen und Haftungsübernahmen entscheidet die Geschäftsführung", "§ 5 Nr. 4, KO § 4 Nr. 2"],
        ["Zahlungsziel 45 Tage; Vorkasse oder Sicherheiten", "**Hier entscheidet ein Mensch:** Leitung Vertrieb, Gründe in dieser Vorlage", "§ 4 Nr. 1 und 5, KO § 2"],
        ["Versand durch den Angebotsassistenten", "System darf nicht (Klasse D, Zusage, Rechtsfrage)", "§ 9 Nr. 2"],
    ])
    S.append(("Wer entscheidet: System oder Mensch", wer))
    S.append(("Empfehlung",
              "**Wahl offen, bis entschieden ist:**\n\n" +
              tabelle(["Frage", "Möglichkeiten", "Vorschlag und Grund"], [
                  ["Zahlungsziel", "30 Tage netto (Standard) · 45 Tage mit Freigabe der Leitung Vertrieb", "30 Tage: Der Wunsch folgt keiner Regel der Richtlinie, Bonität ist nicht geprüft; 45 Tage nur nach Bonitätsprüfung und Entscheid der Leitung Vertrieb (§ 4, KO § 2)"],
                  ["Vorkasse", "keine · Vorkasse oder Sicherheit (Leitung Vertrieb)", "keine auf Grundlage der Herkunft: Der Hinweis des Außendienstes beruht auf dem Sitzland, nicht auf belegter Zahlungserfahrung (§ 1 Nr. 2). Erst wenn die Buchhaltung eine belegte Zahlungserfahrung nennt, kann die Leitung Vertrieb entscheiden"],
                  ["Garantie", "nicht geben · Ausnahme durch Geschäftsführung", "nicht geben (§ 5 Nr. 4); die Anwendungstechnik prüft eine Zusage für die Anlage nach Datenaufnahme"],
              ]) +
              "\n**Schritte:**\n\n" + liste([
                  "Zwischenbescheid an den Kunden sofort (§ 10 Nr. 6): Anfrage ist eingegangen, nächster Schritt ist die Datenaufnahme, Regulatory Affairs prüft die Frage zur EU-Regel und antwortet. Mehr nicht.",
                  "Anwendungstechnik: Datenaufnahme Nord-3 vor dem Wartungsfenster Mai 2027 planen (Pflicht, § 2 Nr. 4).",
                  "Regulatory Affairs: die Frage des Kunden weiterleiten (KO § 3). Das Datenblatt „fluorfrei deklariert“ ist keine Antwort darauf, und der Tender Desk schreibt dazu nichts.",
                  "Angebot erst nach Datenaufnahme verbindlich machen; vorher nur Entwurf an die Leitung Vertrieb (Klasse D).",
                  "Preise in NOK anbieten auf Wunsch, kalkuliert in EUR (" + eur(netto) + " = NOK " + de(netto_nok) + " zum Kurs " + de(nok, 4) + "), Fracht FCA als eigene Position nach Frachtangebot.",
              ])))
    S.append(("Offene Rückfragen",
              liste([
                  "Anwendungstechnik: Termin Datenaufnahme Nord-3 (eingestellte Zumischrate am Zumischer, Zumischrate laut Anlagendokumentation, Füllmenge, Restbestand und Reinigung des Tanks, letzte Prüfung).",
                  "Regulatory Affairs: Frage des Kunden zur angekündigten EU-Beschränkung; der Tender Desk nimmt dazu keine Stellung.",
                  "Buchhaltung: Datum der letzten Bonitätsprüfung und belegte Zahlungserfahrung mit K-1019.",
                  "Lager: Lieferfähigkeit 6 IBC für Mai 2027.",
                  "Spedition: Frachtangebot FCA Werk Nord nach Westnorwegen; Kunde: Klärung Lieferort und Zollabwicklung.",
                  "Kunde: Beleg für das genehmigte Budget NOK 650.000, falls es für die Entscheidung gebraucht wird.",
                  "Leitung Vertrieb: Zahlungsziel und Vorkasse (siehe Empfehlung).",
              ])))
    S.append(("Was nicht in die Entscheidung einfließen darf",
              liste([
                  "Das Sitzland Norwegen als Grund für Vorkasse, Rabatt, Zahlungsziel oder Klasse (§ 1 Nr. 2). Die Klasse hängt nur an NOK und dem Lieferort außerhalb der EU (§ 7 Nr. 3).",
                  "Die Aussage des Außendienstes „zahlen erfahrungsgemäß spät“ ohne Beleg (§ 1 Nr. 2, § 4).",
                  "Die Deklaration „fluorfrei“ im Datenblatt als Antwort auf die Rechtsfrage (§ 1 Nr. 4, KO § 3).",
                  "Die Vorsortierung des Angebotsassistenten „Kunde NO“ (§ 1 Nr. 2).",
                  "Das Budget NOK 650.000 für Grenzen oder Klasse (§ 7 Nr. 2) und als Rabattanlass (§ 3 Nr. 6).",
                  "Die Datenaufnahme der Pilotanlage LS-0088 als Ersatz für Nord-3 (§ 2 Nr. 4).",
                  "Fracht im Auftragswert (§ 2 Nr. 1).",
                  "Klasse, Marge und Bonität im Schreiben an den Kunden (§ 10 Nr. 2).",
              ])))
    pfad = [
        {"schritt": "Prüfumfang", "angabe": "Auftragswert " + eur(netto) + ", ohne Fracht", "par": "§ 2 Nr. 1 und 3", "ergebnis": "25.000,01 bis 150.000: Deckungsbeitrag, Bonität, Lieferfähigkeit"},
        {"schritt": "Datenaufnahme", "angabe": "stationäre Anlage Nord-3, Wert ab 25.000", "par": "§ 2 Nr. 4, § 5 Nr. 3", "ergebnis": "Pflicht, in den Stammdaten nicht vorhanden", "mensch": True, "wer": "Anwendungstechnik"},
        {"schritt": "Preis und Währung", "angabe": "Liste 2026; 6 % + 5 % auf 4.000 l, 6 % auf 2.000 l; NOK zum Kurs " + de(nok, 4), "par": "§ 3, § 6 Nr. 1, § 7 Nr. 2", "ergebnis": eur(netto) + " = NOK " + de(netto_nok)},
        {"schritt": "Technische Zusage und Garantie", "angabe": "„mindestens so gut wie bisher“, Garantie unter Offshore-Bedingungen", "par": "§ 5 Nr. 2 bis 4, KO § 4", "ergebnis": "Zusage nur nach Datenaufnahme; Garantie nicht", "mensch": True, "wer": "Anwendungstechnik, Geschäftsführung für Ausnahmen"},
        {"schritt": "Rechtsfrage EU-Beschränkung", "angabe": "Bestätigung der Konformität verlangt", "par": "§ 1 Nr. 4, § 7 Nr. 4, KO § 3", "ergebnis": "Wir antworten nicht; Weiterleitung", "mensch": True, "wer": "Regulatory Affairs"},
        {"schritt": "Zahlung", "angabe": "45 Tage, Bonität nicht geprüft, Vorkasse-Hinweis", "par": "§ 4 Nr. 1 und 5, § 1 Nr. 2", "ergebnis": "Wahl offen; Herkunft zählt nicht", "mensch": True, "wer": "Leitung Vertrieb"},
        {"schritt": "Angebotsklasse", "angabe": "6 Punkte, Mindestklassen C und D", "par": "§ 8 Nr. 2 bis 4", "ergebnis": "Klasse D"},
        {"schritt": "Kompetenz", "angabe": "Klasse D bis 150.000", "par": "§ 9 Nr. 1 und 2, KO § 2", "ergebnis": "Freigabe Leitung Vertrieb; System darf nichts versenden", "mensch": True, "wer": "Leitung Vertrieb"},
    ]
    return {
        "id": vid, "kunde": "K-1019 Nordic Offshore Services AS", "titel": "Anfrage auf Englisch, Garantie, Bestätigung, NOK",
        "auftragswert": netto, "klasse": "D", "entscheidet": "Leitung Vertrieb",
        "empfehlung": "Datenaufnahme zuerst, keine Garantie, Rechtsfrage an Regulatory Affairs",
        "abschnitte": S, "pfad": pfad,
    }


# ------------------------------------------------------------------ A-04
def a04():
    vid = "A-04"
    p = position("2026", "P-202", {"IBC": 6, "Fass": 2}, "0.06")
    liste_sum = p["listenwert"]
    netto = p["netto"]
    abstand = cent(D(25000) - netto)
    express = D(450)
    liter = p["liter"]
    hk_l = HK[("P-202", "2026")]
    hk = cent(hk_l * liter)
    db = cent(netto - hk)
    gueltig = HEUTE + datetime.timedelta(days=60)
    S = []
    S.append(("Vorgang in Kürze",
              "Löschgeräte Norddeutschland GmbH (K-1020, Bestandskunde, Key Account, nicht als Händler geführt) bestellt per Mail vom 24.02.2027 FreeFoam 6 % (P-202) für die Befüllung der "
              "6-l-Schaumlöscher der Serie LG-6: 6 IBC und 2 Fass = 6.400 l, zu Standardkonditionen, als Expresslieferung bis Freitag, 05.03.2027 (Produktion läuft am Montag, 08.03.2027 an), "
              "Expresszuschlag übernimmt der Kunde, Zahlung 30 Tage netto. Das Muster FreeFoam 6 % vom Juni 2026 hat der Kunde geprüft.\n"))
    S.append(("Stand-Datum, Preisliste und Richtlinie",
              liste([
                  "**Stand:** Montag, 01.03.2027; Angebotsdatum angenommen 01.03.2027.",
                  "**Preisliste 2026** (RL § 6 Nr. 1), gültig bis zur Preisliste 2027 (angekündigt April 2027); **RL-ANG-2026** und **KO-2026**.",
                  "Gültig 60 Kalendertage, bis " + datum(gueltig) + " (§ 6 Nr. 3). Währung EUR.",
                  "Antwort an den Kunden: drei Arbeitstage nach der Mail vom 24.02.2027 endeten am 01.03.2027 (§ 10 Nr. 6); das Angebot geht heute hinaus.",
              ])))
    S.append(("Vorliegende und nur erwähnte Unterlagen",
              "**Liegt im Angebotseingang vor:**\n\n" + liste([
                  "Bestellmail vom 24.02.2027 (Wolfgang Prahl, Leiter Produktion)",
                  "Stammdaten: Kunde K-1020 (kein Händler), Lieferstellen LS-0089 (Befüllung Serie LG-6) und LS-0093 (Muster fluorfrei, 19.06.2026), Produkt P-202, Preisliste 2026, Herstellkosten 2026",
              ]) + "\n**Nur erwähnt, liegt nicht bei:**\n\n" + liste([
                  "Prüfergebnis des Musters FreeFoam 6 % durch den Kunden: nur genannt („Prüfung abgeschlossen“), kein Bericht im Ordner",
                  "Lagerbestand P-202 für die Expresslieferung: nicht im Ordner",
              ])))
    S.append(("Preisrechnung Schritt für Schritt",
              tabelle(["Position", "Gebinde", "Anzahl", "Listenpreis je Gebinde EUR", "Listenwert EUR", "Rabatt", "Netto EUR"],
                      [["FreeFoam 6 % (P-202)", z["gebinde"] + " " + str(z["liter"] // z["anzahl"]) + " l", z["anzahl"], de(z["listenpreis"]), de(z["listenwert"]),
                        "6 % Mengenrabatt (§ 3 Nr. 1)", de(z["netto"])] for z in p["zeilen"]]) +
              "\nMengenrabatt nach der Gesamtmenge 6.400 l desselben Produkts: Stufe ab 5.000 l, die Stufe ab 20.000 l ist nicht erreicht. Kein Projektrabatt (Nachbestellung, keine stationäre Anlage, § 3 Nr. 2); "
              "keine Händlerkondition (Key Account ist kein Händlerkennzeichen, § 3 Nr. 4). Gebinde wie bestellt: 6 IBC und 2 Fass.\n\n" +
              tabelle(["Schritt", "EUR"], [
                  ["Listenwert Preisliste 2026", de(liste_sum)],
                  ["Mengenrabatt 6 %", "−" + de(liste_sum - netto)],
                  ["**Auftragswert** (ohne Fracht, Zuschläge, Umsatzsteuer, § 2 Nr. 1)", "**" + de(netto) + "**"],
                  ["Expresszuschlag je Lieferung (§ 6 Nr. 4), eigene Position", de(express) + " (zählt nicht zum Auftragswert)"],
                  ["Fracht (Deutschland, frei Haus ab Nettowarenwert 2.500, § 6 Nr. 5)", "0,00 (zählt nicht zum Auftragswert)"],
              ]) +
              "\n**Grenze 25.000:** Der Auftragswert liegt EUR " + de(abstand) + " darunter. Mit dem Expresszuschlag wären es EUR " + de(netto + express) + ", also darüber; der Zuschlag zählt aber nach § 2 Nr. 1 nicht dazu. "
              "Eine Änderung der Menge um ein Fass (EUR " + de(position("2026", "P-202", {"Fass": 1}, "0.06")["netto"]) + ") würde die Grenze überschreiten und die Klasse ändern.\n"))
    S.append(("Prüfumfang und Datenaufnahme",
              "**Prüfumfang:** Auftragswert EUR " + de(netto) + " bis 25.000: Preisliste, Rabatt nach Staffel, Kundenstatus, Zahlungsziel (§ 2 Nr. 3). Kundenstatus: Bestandskunde (letzte Lieferung 15.05.2026; das Muster vom 19.06.2026 zählt nicht, § 4 Nr. 3). "
              "Bonität nicht erforderlich (§ 4 Nr. 2). Zahlungsziel 30 Tage netto, Standard (§ 4 Nr. 1). Deckungsbeitrag nicht Pflicht; zur Information: Herstellkosten P-202 2026 EUR " + de(hk_l, 3) +
              " je Liter × " + de(liter, 0) + " l = EUR " + de(hk) + ", DB vor Fracht EUR " + de(db) + " (Marge vor Fracht " + pct(db / netto) + "), Fracht frei Haus nicht belegt.\n\n"
              "**Datenaufnahme:** nicht erforderlich: Befüllung tragbarer Löscher, keine stationäre Anlage (§ 2 Nr. 4). Das Angebot nennt nur Produktdaten nach Datenblatt. "
              "**Hinweis:** Als Einsatzbereiche von P-202 nennt der Produktstamm Feuerwehr und Industrie, nicht Löschgeräte. Das Angebot darf deshalb keine Aussage zur Eignung für die Löscher der Serie LG-6 enthalten; das wäre eine technische Zusage der Anwendungstechnik (§ 5 Nr. 2 und 3).\n"))
    pkte = tabelle(["Merkmal (§ 8 Nr. 2)", "Punkte", "Begründung"], [
        ["Auftragswert (§ 2 Nr. 1)", "0", "EUR " + de(netto) + ", bis 25.000"],
        ["Rabatt (§ 3)", "0", "6 % genau nach Staffel; „Standardkonditionen“ verlangt"],
        ["Technik (§ 2 Nr. 4, § 5)", "0", "nur Produktdaten nach Datenblatt, keine stationäre Anlage, keine Zusage verlangt"],
        ["Vertrag (§ 5 Nr. 4, § 6 Nr. 6)", "0", "Standardbedingungen, einmalige Lieferung"],
        ["Zahlung (§ 4)", "0", "30 Tage netto, Bonität nicht erforderlich"],
        ["Kundenstatus (§ 4 Nr. 3)", "0", "Bestandskunde"],
        ["Währung und Lieferort (§ 7 Nr. 3)", "0", "EUR, Lieferort Werk des Kunden in Deutschland"],
        ["**Summe**", "**0**", "0 = Klasse A"],
        ["Mindestklassen (§ 8 Nr. 4)", "keine", "keine Zusage, keine Rechtsaussage, keine Ausschreibung, Auftragswert nicht über 150.000"],
        ["**Ergebnis**", "**Klasse A**", ""],
    ])
    S.append(("Angebotsklasse mit Punkten", pkte))
    wer = tabelle(["Frage", "Wer entscheidet", "Regel"], [
        ["Freigabe Klasse A bis 25.000", "Vertriebsinnendienst; **automatischer Versand durch den Angebotsassistenten ist zulässig**", "§ 9 Nr. 1 und 2, KO § 2"],
        ["Expresslieferung innerhalb von 3 Arbeitstagen", "Standardleistung gegen Zuschlag, wenn die Ware am Lager ist; Lagerbestand vorher klären. Kürzere Zusagen nur die Leitung Vertrieb", "§ 6 Nr. 4, KO § 2"],
        ["Technische Zusage zur Eignung für die Löscher der Serie LG-6", "nicht im Angebot; falls verlangt: Anwendungstechnik, dann mindestens Klasse C", "§ 5 Nr. 3, § 8 Nr. 4"],
    ])
    S.append(("Wer entscheidet: System oder Mensch", wer + "\nIn diesem Vorgang muss kein Mensch eine Regel entscheiden; ob das Angebot automatisch hinausgeht, hängt von der Lagerbestätigung und der Arbeitsregel des Tender Desk ab.\n"))
    S.append(("Empfehlung",
              liste([
                  "Angebot zum Auftragswert EUR " + de(netto) + " (Preisliste 2026, 6 % Mengenrabatt) mit Expresszuschlag EUR " + de(express) + " als eigene Position erstellen und versenden, sobald der Lagerbestand 6 IBC und 2 Fass bestätigt ist.",
                  "Ohne Lagerbestätigung dem Kunden die Standardlieferzeit von 10 Arbeitstagen nennen, nicht Express zusagen (§ 6 Nr. 4); der Termin 05.03.2027 wäre dann nicht zu halten.",
                  "Keinen Satz zur Eignung für die Löscher der Serie LG-6 aufnehmen.",
              ])))
    S.append(("Offene Rückfragen",
              liste([
                  "Lager: Bestand P-202 (6 IBC und 2 Fass) für Expresslieferung bis 05.03.2027.",
                  "Vertriebsinnendienst: Prüfbericht des Kunden zum Muster FreeFoam 6 % vom Juni 2026, falls er für die Akte gebraucht wird.",
              ])))
    S.append(("Was nicht in die Entscheidung einfließen darf",
              liste([
                  "Der Expresszuschlag und die Fracht im Auftragswert (§ 2 Nr. 1); sie hätten die Grenze 25.000 überschritten.",
                  "„Key Account“ als Rabattgrund oder als Händlerkondition (§ 3 Nr. 4).",
                  "Der Projektrabatt auf eine Nachbestellung (§ 3 Nr. 2).",
                  "Die Aussage „geeignet für die Löscher der Serie LG-6“ (§ 5 Nr. 2).",
                  "Klasse, Marge und Bonität im Schreiben an den Kunden (§ 10 Nr. 2).",
              ])))
    pfad = [
        {"schritt": "Prüfumfang", "angabe": "Auftragswert EUR " + de(netto) + " (EUR " + de(abstand) + " unter 25.000), ohne Express und Fracht", "par": "§ 2 Nr. 1 und 3", "ergebnis": "bis 25.000: Preisliste, Staffel, Kundenstatus, Zahlungsziel"},
        {"schritt": "Datenaufnahme", "angabe": "tragbare Löscher, keine stationäre Anlage", "par": "§ 2 Nr. 4", "ergebnis": "nicht erforderlich"},
        {"schritt": "Preisliste und Rabatt", "angabe": "Liste 2026; 6 % Mengenrabatt auf 6.400 l", "par": "§ 6 Nr. 1, § 3 Nr. 1", "ergebnis": "kein Projektrabatt, keine Händlerkondition"},
        {"schritt": "Express und Lieferfähigkeit", "angabe": "3 Arbeitstage gegen Zuschlag EUR " + de(express) + ", wenn am Lager", "par": "§ 6 Nr. 4", "ergebnis": "Lagerbestand offen"},
        {"schritt": "Angebotsklasse", "angabe": "0 Punkte, keine Mindestklasse", "par": "§ 8 Nr. 2 bis 4", "ergebnis": "Klasse A"},
        {"schritt": "Kompetenz", "angabe": "Klasse A bis 25.000", "par": "§ 9 Nr. 1 und 2, KO § 2", "ergebnis": "Vertriebsinnendienst; automatischer Versand zulässig", "ok": True},
    ]
    return {
        "id": vid, "kunde": "K-1020 Löschgeräte Norddeutschland GmbH", "titel": "Nachbestellung, Expresslieferung",
        "auftragswert": netto, "klasse": "A", "entscheidet": "Vertriebsinnendienst",
        "empfehlung": "Angebot erstellen, Versand zulässig nach Lagerbestätigung",
        "abschnitte": S, "pfad": pfad,
    }


VORGAENGE = [a01, a02, a03, a04]


def vorlage_md(v):
    s = "# Entscheidungsvorlage " + v["id"] + " · " + v["kunde"] + "\n\n"
    s += "*" + KOPF + "*\n\n"
    s += "**" + v["titel"] + "** · Auftragswert EUR " + de(v["auftragswert"]) + " · Angebotsklasse " + v["klasse"] + " · entscheidet: " + v["entscheidet"] + "\n\n"
    for i, (t, md) in enumerate(v["abschnitte"], 1):
        s += "## " + str(i) + " " + t + "\n\n" + md.rstrip() + "\n\n"
    s += entscheidzeile(v["id"])
    return s.rstrip() + "\n"


def main():
    erg = []
    daten = []
    for f in VORGAENGE:
        v = f()
        md = vorlage_md(v)
        pfad_name = os.path.join(BASIS, "meine-ergebnisse", "entscheidungsvorlage-" + v["id"].lower() + ".md")
        with open(pfad_name, "w", encoding="utf-8") as fh:
            fh.write(md)
        erg.append(pfad_name)
        daten.append({
            "id": v["id"], "kunde": v["kunde"], "titel": v["titel"], "auftragswert": float(v["auftragswert"]), "klasse": v["klasse"],
            "entscheidet": v["entscheidet"], "empfehlung": v["empfehlung"], "pfad": v["pfad"],
            "vorlage_html": md_html(md),
        })
    js = "/* erzeugt von skripte/angebote.py – nicht von Hand ändern */\nvar ANGEBOTE = " + json.dumps(
        {"stichtag": STICHTAG, "stand": "01.03.2027", "vorgaenge": daten}, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out = os.path.join(BASIS, "meine-ergebnisse", "dashboard-daten", "angebote.js")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(js)
    for p in erg:
        print("geschrieben:", p)
    print("geschrieben:", out)
    for d in daten:
        print(d["id"], "Auftragswert", d["auftragswert"], "Klasse", d["klasse"], "entscheidet", d["entscheidet"])


if __name__ == "__main__":
    main()
