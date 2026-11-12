"""Akzeptanzprüfung für die Bauaufträge der Drills.  python scripts/akzeptanz.py <1-5> [--root ORDNER]

Prüft den Code in ORDNER (Standard: dieses Repo) gegen die Szenarien der Drill-Karten. Arbeitet mit eigenem
temporärem Zustand; die lokale Datenbank der Person bleibt unberührt. Ausgabe: BESTANDEN / NICHT BESTANDEN je
Szenario, OPTIONAL für Szenarien, die die Person anders entscheiden darf. Exit-Code 1 bei NICHT BESTANDEN.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import threading
from pathlib import Path

if sys.version_info < (3, 9):
    sys.exit("Python 3.9 oder neuer nötig.")

ERG = []


def pruefe(name, bedingung, optional=False, detail=""):
    ok = bool(bedingung)
    ERG.append((name, ok, optional))
    marke = "BESTANDEN" if ok else ("OPTIONAL " if optional else "NICHT BESTANDEN")
    print("  %-16s %s%s" % (marke, name, (" – " + detail) if (detail and not ok) else ""))


def wirft(fn):
    try:
        fn()
    except Exception:
        return True
    return False


def start(root: Path, tmp: Path):
    os.environ["STHAMER_DATA_DIR"] = str(root / "data")
    os.environ["STHAMER_STATE_DIR"] = str(tmp / ".data")
    os.environ["STHAMER_OUTBOX_DIR"] = str(tmp / "postausgang")
    sys.path.insert(0, str(root))
    for m in [m for m in sys.modules if m == "sthamer_sys" or m.startswith("sthamer_sys.")]:
        del sys.modules[m]
    import sthamer_sys.domain as domain
    from sthamer_sys import daten, store
    daten.leeren()
    domain.welle_freischalten(1, akteur="system")
    return domain, daten, store


def setze_welle(store, n):
    with store.transaktion() as c:
        store.zustand_setzen(c, "welle", str(n))


def entwurf(domain, fall_id, an="a.lindemann@ff-bergheim-land.example.com", text="Guten Tag, danke für Ihre Anfrage.", belege=None):
    belege = belege if belege is not None else [{"typ": "artikel", "ref": "Art. 4 Abs. 4"}, {"typ": "produkt", "ref": "P-102"},
                                               {"typ": "kunde", "ref": "K-1010"}]
    return domain.entwurf_anlegen(fall_id, an, "Antwort", text, belege, "claude")["entwurf_id"]


def drill1(domain, daten, store):
    a = domain.fall_anlegen("MSG-1-02")["fall_id"]
    b = domain.fall_anlegen("MSG-1-01")["fall_id"]
    e = entwurf(domain, a)
    domain.senden(e)
    ta = domain.fall(a)["aufgaben"]
    tb = domain.fall(b)["aufgaben"]
    pruefe("Nach dem Senden ist die Aufgabe des Falls erledigt", ta and all(t["status"] == "erledigt" for t in ta))
    pruefe("Die Aufgabe eines anderen Falls bleibt offen", tb and all(t["status"] == "offen" for t in tb))
    pruefe("Zweimal senden ist nicht möglich", wirft(lambda: domain.senden(e)))
    # Senden schlägt fehl (Empfänger wird nachträglich ungültig): die Aufgabe darf sich nicht erledigen
    e2 = entwurf(domain, b, an="regulatory@sthamer-uebung.example.com", belege=[{"typ": "nachricht", "ref": "MSG-1-01"}])
    alt = daten.interne_domain
    daten.interne_domain = lambda: "gibt-es-nicht.invalid"
    try:
        fehlgeschlagen = wirft(lambda: domain.senden(e2))
    finally:
        daten.interne_domain = alt
    offen = [t["status"] for t in domain.fall(b)["aufgaben"]]
    pruefe("Schlägt das Senden fehl, bleibt die Aufgabe offen", fehlgeschlagen and offen and all(x == "offen" for x in offen))
    domain.senden(e2)
    pruefe("Die interne Mail erledigt die Aufgabe ihres Falls", all(t["status"] == "erledigt" for t in domain.fall(b)["aufgaben"]))


def drill2(domain, daten, store):
    f = domain.fall_anlegen("MSG-1-02")["fall_id"]
    pruefe("Erfundener Artikel wird abgewiesen", wirft(lambda: entwurf(domain, f, belege=[{"typ": "artikel", "ref": "Art. 99 Abs. 9"}])))
    pruefe("Erfundenes Produkt wird abgewiesen", wirft(lambda: entwurf(domain, f, belege=[{"typ": "produkt", "ref": "P-999"}])))
    pruefe("Erfundener Kunde wird abgewiesen", wirft(lambda: entwurf(domain, f, belege=[{"typ": "kunde", "ref": "K-9999"}])))
    ok = not wirft(lambda: entwurf(domain, f))
    pruefe("Ein Entwurf mit echten Belegen wird gespeichert", ok)
    pruefe("„betroffen“ ohne Artikel und Produkt als Beleg wird abgewiesen",
           wirft(lambda: domain.einschaetzung_festhalten("K-1010", "betroffen", "Weil ich es sage.", [], None, "claude")))
    pruefe("„betroffen“ mit Artikel und Produkt wird festgehalten",
           not wirft(lambda: domain.einschaetzung_festhalten("K-1010", "betroffen", "P-102 hat 620 mg/l, Art. 4 Abs. 4.",
                                                            [{"typ": "artikel", "ref": "Art. 4 Abs. 4"}, {"typ": "produkt", "ref": "P-102"}],
                                                            "2028-09-01", "claude")))
    pruefe("Ein Datum im Text, das keine Frist des Regelwerks ist, wird abgewiesen",
           wirft(lambda: entwurf(domain, f, text="Das Verbot gilt ab 2031-01-01.")), optional=True)


def ent(domain, eid):
    return next(e for e in domain.entwuerfe() if e["id"] == eid)


def drill3(domain, daten, store):
    setze_welle(store, 3)
    f = domain.fall_anlegen("MSG-1-02")["fall_id"]
    ka = [k for k in daten.kunden() if k["key_account"] and k["status"] == "aktiv" and k["land"] == "DE" and not k.get("seveso")][0]
    an = ka["ansprechpartner"]["email"]
    e = entwurf(domain, f, an=an, belege=[{"typ": "kunde", "ref": ka["id"]}])
    r = domain.einreichen(e, False)
    pruefe("Key Account geht in Pflichtfreigabe", r["status"] == "zur_freigabe")
    domain.freigeben(e)
    pruefe("Der freigegebene Entwurf steht auf „freigegeben“", ent(domain, e)["status"] == "freigegeben")
    vorher = len(domain.protokoll())
    domain.entwurf_aendern(e, {"text": "Guten Tag, hier steht jetzt ein anderer Text."}, "mensch")
    st = ent(domain, e)["status"]
    delta = len(domain.protokoll()) - vorher
    pruefe("Nach einer Änderung ist die Freigabe erloschen", st != "freigegeben", detail="Status ist noch " + st)
    pruefe("Das Protokoll hält die erloschene Freigabe fest", delta >= 2, optional=True)
    pruefe("Der geänderte Entwurf lässt sich nicht ohne neue Freigabe senden", wirft(lambda: domain.senden(e)))
    # Claude ändert: dieselbe Wirkung
    g = domain.fall_anlegen("MSG-1-02")["fall_id"]
    e2 = entwurf(domain, g, an=an, belege=[{"typ": "kunde", "ref": ka["id"]}])
    domain.einreichen(e2, False)
    domain.freigeben(e2)
    domain.entwurf_aendern(e2, {"betreff": "Neuer Betreff"}, "claude")
    pruefe("Auch eine Änderung durch Claude entwertet die Freigabe", wirft(lambda: domain.senden(e2)))
    # Speichern ohne Änderung
    h = domain.fall_anlegen("MSG-1-02")["fall_id"]
    e3 = entwurf(domain, h, an=an, belege=[{"typ": "kunde", "ref": ka["id"]}])
    domain.einreichen(e3, False)
    domain.freigeben(e3)
    domain.entwurf_aendern(e3, {"text": ent(domain, e3)["text"]}, "mensch")
    pruefe("Speichern ohne Änderung entwertet die Freigabe nicht", ent(domain, e3)["status"] == "freigegeben", optional=True)


def im_ausgang(domain, eid):
    return sum(1 for p in domain.postausgang() if p["entwurf_id"] == eid)


def drill4(domain, daten, store):
    setze_welle(store, 4)
    f = domain.fall_anlegen("MSG-1-02")["fall_id"]
    a = entwurf(domain, f, text="Guten Tag, Entwurf A.")
    r = domain.einreichen(a, False)
    pruefe("Standardinformation wird eingeplant", r["status"] == "geplant")
    domain.entwurf_aendern(a, {"text": "Guten Tag, dieser Text wurde nach der Planung geändert."}, "mensch")
    st = ent(domain, a)
    pruefe("Nach einer Änderung ist der Termin abgebrochen", st["status"] != "geplant" and not st["sende_am"],
           detail="Status ist noch %s" % st["status"])
    domain.uhr_vorspulen(30)
    pruefe("Der geänderte Entwurf geht nicht automatisch raus", im_ausgang(domain, a) == 0)
    # genau einmal
    g = domain.fall_anlegen("MSG-1-02")["fall_id"]
    b = entwurf(domain, g, text="Guten Tag, Entwurf B.")
    domain.einreichen(b, False)
    domain.uhr_vorspulen(30)
    pruefe("Nach dem Fenster geht die Mail genau einmal raus", im_ausgang(domain, b) == 1)
    domain.uhr_vorspulen(30)
    pruefe("Weiteres Vorspulen sendet nichts doppelt", im_ausgang(domain, b) == 1)
    # gestoppt
    h = domain.fall_anlegen("MSG-1-01")["fall_id"]
    c = entwurf(domain, h, an="regulatory@sthamer-uebung.example.com", belege=[{"typ": "nachricht", "ref": "MSG-1-01"}])
    domain.einreichen(c, False)
    domain.stoppen(c)
    domain.uhr_vorspulen(30)
    pruefe("Eine gestoppte Mail geht nie raus", im_ausgang(domain, c) == 0)
    # gleichzeitig
    k = domain.fall_anlegen("MSG-1-02")["fall_id"]
    d = entwurf(domain, k, text="Guten Tag, Entwurf D, parallel verarbeitet.")
    domain.einreichen(d, False)
    with store.transaktion() as cx:
        cx.execute("UPDATE entwuerfe SET sende_am = ? WHERE id = ?", ("2000-01-01T00:00:00", d))
    ts = [threading.Thread(target=domain.faellige_senden) for _ in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    pruefe("Vier gleichzeitige Läufe senden dieselbe Mail nur einmal", im_ausgang(domain, d) == 1)


BASIS_SCHLUESSEL = {"stand", "einschaetzungen", "entwuerfe", "versand", "kontrolle", "frist", "grenze",
                    "ohne_einschaetzung", "aktive_kunden", "betroffen", "nicht_betroffen", "mittelbar", "unklar", "gesamt",
                    "von_claude", "offen", "gesendet", "mit_pflichtfreigabe", "automatisch_nach_fenster", "direkt_vom_menschen",
                    "freigegeben", "abgelehnt", "gestoppt", "wartet_auf_freigabe", "eingeplant", "informationspflicht_bis", "tage_bis"}


def alle_schluessel(d, out=None):
    out = set() if out is None else out
    if isinstance(d, dict):
        for k, v in d.items():
            out.add(k)
            alle_schluessel(v, out)
    return out


def drill5(domain, daten, store, root):
    setze_welle(store, 4)
    try:
        b = domain.bericht()
        pruefe("bericht() läuft ohne Daten ohne Fehler", isinstance(b, dict))
    except Exception as e:
        pruefe("bericht() läuft ohne Daten ohne Fehler", False, detail=repr(e))
        return
    neu = alle_schluessel(b) - BASIS_SCHLUESSEL
    pruefe("bericht() enthält eine eigene Kennzahl", bool(neu), detail="keine neuen Felder")
    if neu:
        print("    eigene Kennzahl(en): %s" % ", ".join(sorted(neu)))
    f = domain.fall_anlegen("MSG-1-02")["fall_id"]
    e = entwurf(domain, f)
    domain.einreichen(e, False)
    domain.uhr_vorspulen(30)
    try:
        b2 = domain.bericht()
        pruefe("bericht() läuft auch mit Daten", b2["versand"]["gesendet"] == 1)
    except Exception as ex:
        pruefe("bericht() läuft auch mit Daten", False, detail=repr(ex))
    datei = root / "bericht.md"
    text = datei.read_text(encoding="utf-8") if datei.is_file() else ""
    pruefe("bericht.md liegt im Ordner und ist nicht leer", len(text.strip()) > 200)
    pruefe("Der Bericht nennt die Grenze der Aussage", "grenze" in text.lower())
    pruefe("Der Bericht nennt die Frist 30.06.2027", "30.06.2027" in text or "2027-06-30" in text or "30. Juni 2027" in text)


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    p = argparse.ArgumentParser()
    p.add_argument("drill", type=int, choices=[1, 2, 3, 4, 5])
    p.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = p.parse_args()
    root = Path(a.root).resolve()
    print("Akzeptanzprüfung Drill %d (%s)" % (a.drill, root))
    with tempfile.TemporaryDirectory(prefix="sthamer-akzeptanz-") as t:
        domain, daten, store = start(root, Path(t))
        if a.drill == 5:
            drill5(domain, daten, store, root)
        else:
            {1: drill1, 2: drill2, 3: drill3, 4: drill4}[a.drill](domain, daten, store)
    fehl = [n for n, ok, opt in ERG if not ok and not opt]
    opt = [n for n, ok, o in ERG if not ok and o]
    print("%d von %d Szenarien bestanden%s." % (sum(1 for _, ok, _o in ERG if ok), len(ERG), (", %d optional offen" % len(opt)) if opt else ""))
    return 1 if fehl else 0


if __name__ == "__main__":
    sys.exit(main())
