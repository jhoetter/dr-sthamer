"""Ein Kunde in allen Quellen: K-1004 Stahlwerk Ruhrtal AG (Drill 0, Etappe 5). Nur Lesen."""
import csv
from collections import defaultdict, Counter

KID = "K-1004"


def lies(pfad):
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


kunde = [k for k in lies("daten/kunden.csv") if k["id"] == KID][0]
print("KUNDENSTAMM:", {k: kunde[k] for k in ("id", "name", "segment", "land", "key_account", "ist_haendler", "status")})

produkte = {p["id"]: p for p in lies("daten/produkte.csv")}
ls = [r for r in lies("daten/lieferstellen.csv") if r["kunde_id"] == KID]
print("\nLIEFERSTELLEN:", len(ls))
for r in ls:
    p = produkte.get(r["aktuelles_produkt_id"], {})
    print(" ", r["lieferstelle_id"], r["anlage"], "|", r["anwendung"], "|", r["aktuelles_produkt_id"], p.get("name"),
          "|", r["fuellmenge_l"], "l | letzte Lieferung", r["letzte_lieferung"], "| Erstbefüllung", r["erstbefuellung_am"] or "-")

umr = {"IBC": 1000, "Fass": 200, "Kanister": 20, "l": 1}
gesehen = set()
je_jahr = defaultdict(lambda: defaultdict(float))
pos = defaultdict(lambda: defaultdict(int))
erstbef = defaultdict(list)
ohne_liter = 0
doppel = 0
for r in lies("daten/auftraege.csv"):
    if r["kunde_id"] != KID:
        continue
    key = (r["auftrag_id"], r["position"])
    if key in gesehen:
        doppel += 1
        continue
    gesehen.add(key)
    if r["art"] == "Muster":
        continue
    if r["menge_l"] == "":
        liter = float(r["menge"]) * umr[r["einheit"]]
        ohne_liter += 1
    else:
        liter = float(r["menge_l"])
    jahr = r["lieferdatum"][:4]
    je_jahr[jahr][r["auftragsart"]] += liter
    pos[jahr][r["auftragsart"]] += 1
    if r["auftragsart"] == "Erstbefüllung" and r["art"] == "Lieferung":
        erstbef[r["lieferstelle_id"]].append((r["lieferdatum"], liter))

arten = ["Nachfüllung", "Erstbefüllung", "Notfall"]
print("\nAUFTRÄGE (Absatz in Litern netto, ohne Muster, ohne Doppelimporte: %d ausgeschlossen; %d Positionen ohne Literangabe umgerechnet)" % (doppel, ohne_liter))
print("Jahr   " + "  ".join("%14s" % a for a in arten) + "      gesamt   Positionen")
for jahr in sorted(je_jahr):
    zeile = [je_jahr[jahr].get(a, 0.0) for a in arten]
    print(jahr + ("*" if jahr == "2027" else " ") + "  " + "  ".join("%14.0f" % z for z in zeile) +
          "  %10.0f   %s" % (sum(zeile), sum(pos[jahr].values())))
print("* 2027 = Jan.-Feb., Teiljahr")

print("\nNachfüll-Positionen: durchschnittl. Liter je Position und Erstbefüllungs-Liter je Position")
nf = [0.0, 0]
eb = [0.0, 0]
for r in lies("daten/auftraege.csv"):
    if r["kunde_id"] == KID and r["art"] == "Lieferung":
        liter = float(r["menge_l"]) if r["menge_l"] else float(r["menge"]) * umr[r["einheit"]]
        if r["auftragsart"] == "Nachfüllung":
            nf[0] += liter
            nf[1] += 1
        elif r["auftragsart"] == "Erstbefüllung":
            eb[0] += liter
            eb[1] += 1
print("  Nachfüllung: %.0f l in %d Positionen = %.0f l je Position" % (nf[0], nf[1], nf[0] / max(nf[1], 1)))
print("  Erstbefüllung: %.0f l in %d Positionen = %.0f l je Position" % (eb[0], eb[1], eb[0] / max(eb[1], 1)))

rk = [r for r in lies("daten/reklamationen.csv") if r["kunde_id"] == KID]
print("\nREKLAMATIONEN:", len(rk))
for r in rk:
    print(" ", r["rekl_id"], r["eingang"], r["produkt_id"], r["kategorie"], r["tage_bis_antwort"], "Tage", r["status"])
print("  Status:", dict(Counter(r["status"] for r in rk)))

print("\nNEU SEIT 2021 (Erstbefüllung_am in Lieferstellen):")
for r in ls:
    if r["erstbefuellung_am"]:
        print(" ", r["lieferstelle_id"], r["anlage"], "Erstbefüllung am", r["erstbefuellung_am"],
              "| Erstbefüllungs-Positionen im Auftrag:", erstbef.get(r["lieferstelle_id"]))
print("Lieferstellen mit Aufträgen, aber ohne Erstbefüllungs-Datum und ohne Erstbefüllungsposition: alt, schon vor 2021 beliefert")
# Konsistenz: Lieferstellen im Auftrag vs. Stamm
ls_ids = {r["lieferstelle_id"] for r in ls}
ls_auftr = set()
for r in lies("daten/auftraege.csv"):
    if r["kunde_id"] == KID:
        ls_auftr.add(r["lieferstelle_id"])
print("In Aufträgen genannte Lieferstellen, die nicht in der Lieferstellentabelle stehen:", sorted(ls_auftr - ls_ids))
print("Lieferstellen ohne Auftrag:", sorted(ls_ids - ls_auftr))
