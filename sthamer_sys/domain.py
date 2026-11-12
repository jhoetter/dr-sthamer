"""Fachlogik. Claude (über MCP) und das Cockpit (HTTP) rufen dieselben Funktionen.

Wichtig für den Workshop: Es gibt hier absichtlich keine Funktion, die Claude
zum Senden oder Freigeben nutzen kann. `senden` wird nur vom Cockpit aufgerufen.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import belegpruefung, daten, kontrollen, uhr
from .paths import outbox_dir
from .store import (ereignis, entpacken, transaktion, verbindung, zeile, zeilen,
                    zustand_lesen, zustand_setzen)
from .util import dumps, jetzt, loads, slug

MAX_TEXT = 20000
MAX_BETREFF = 200
MAX_BELEGE = 50
BELEG_TYPEN = ("artikel", "produkt", "kunde", "lieferung", "nachricht", "datenblatt")


class FachFehler(Exception):
    """Fehler, die der Mensch (oder Claude) verstehen und beheben kann."""


# ---------------------------------------------------------------- Setup / Wellen

def wellen_code_ok(welle: int, code: str) -> bool:
    cfg = daten.wellen().get(str(welle), {})
    soll = cfg.get("code_sha256")
    if not soll:
        return True
    return hashlib.sha256((code or "").strip().lower().encode("utf-8")).hexdigest() == soll


def aktuelle_welle() -> int:
    with verbindung() as conn:
        return int(zustand_lesen(conn, "welle", "0") or 0)


def welle_freischalten(welle: int, code: Optional[str] = None, akteur: str = "mensch") -> Dict[str, Any]:
    """Postfach abrufen: gibt alle Nachrichten bis einschließlich `welle` frei."""
    verfuegbar = sorted({m["welle"] for m in daten.nachrichten_alle()})
    if welle not in verfuegbar:
        raise FachFehler("Diese Runde gibt es nicht.")
    if welle > aktuelle_welle() and not wellen_code_ok(welle, code or ""):
        raise FachFehler("Der Code passt nicht. Bitte noch einmal beim Dozenten nachfragen.")
    neu = 0
    with transaktion() as conn:
        for m in daten.nachrichten_alle():
            if m["welle"] > welle:
                continue
            cur = conn.execute(
                "INSERT OR IGNORE INTO nachrichten (id, welle, typ, von, betreff, empfangen, kunde_id, anhaenge, text) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (m["id"], m["welle"], m["typ"], m["von"], m["betreff"], m["empfangen"],
                 m["kunde_id"], dumps(m["anhaenge"]), m["text"]),
            )
            neu += cur.rowcount
        if welle > int(zustand_lesen(conn, "welle", "0") or 0):
            zustand_setzen(conn, "welle", str(welle))
        if neu:
            ereignis(conn, akteur, "postfach_abgerufen", None, {"welle": welle, "neu": neu})
    return {"welle": welle, "neue_nachrichten": neu}


def naechste_welle_code_hinweis() -> Optional[int]:
    aktuell = aktuelle_welle()
    weitere = sorted(w for w in {m["welle"] for m in daten.nachrichten_alle()} if w > aktuell)
    return weitere[0] if weitere else None


# ---------------------------------------------------------------- Lesen: Eingang & Fälle

def eingang() -> List[Dict[str, Any]]:
    with verbindung() as conn:
        rows = zeilen(conn, "SELECT n.*, f.id AS fall_id FROM nachrichten n "
                            "LEFT JOIN faelle f ON f.nachricht_id = n.id ORDER BY n.empfangen, n.id")
    for r in rows:
        r["anhaenge"] = loads(r["anhaenge"], [])
        r["text_kurz"] = (r["text"][:160] + "…") if len(r["text"]) > 160 else r["text"]
    return rows


def nachricht(nachricht_id: str) -> Dict[str, Any]:
    with verbindung() as conn:
        r = zeile(conn, "SELECT n.*, f.id AS fall_id FROM nachrichten n "
                        "LEFT JOIN faelle f ON f.nachricht_id = n.id WHERE n.id = ?", (nachricht_id,))
        if not r:
            raise FachFehler("Diese Nachricht ist nicht im Postfach (vielleicht noch nicht abgerufen).")
        conn.execute("UPDATE nachrichten SET gelesen = 1 WHERE id = ?", (nachricht_id,))
    r["anhaenge"] = loads(r["anhaenge"], [])
    return r


def faelle() -> List[Dict[str, Any]]:
    with verbindung() as conn:
        rows = zeilen(conn, "SELECT * FROM faelle ORDER BY id")
        for r in rows:
            r["offene_aufgaben"] = conn.execute(
                "SELECT COUNT(*) FROM aufgaben WHERE fall_id = ? AND status = 'offen'", (r["id"],)).fetchone()[0]
            r["entwuerfe"] = conn.execute(
                "SELECT COUNT(*) FROM entwuerfe WHERE fall_id = ? AND status != 'gesendet'", (r["id"],)).fetchone()[0]
    return rows


def fall(fall_id: int) -> Dict[str, Any]:
    with verbindung() as conn:
        f = zeile(conn, "SELECT * FROM faelle WHERE id = ?", (fall_id,))
        if not f:
            raise FachFehler("Diesen Fall gibt es nicht.")
        f["nachricht"] = zeile(conn, "SELECT * FROM nachrichten WHERE id = ?", (f["nachricht_id"],))
        if f["nachricht"]:
            f["nachricht"]["anhaenge"] = loads(f["nachricht"]["anhaenge"], [])
        f["aufgaben"] = zeilen(conn, "SELECT * FROM aufgaben WHERE fall_id = ? ORDER BY id", (fall_id,))
        f["entwuerfe"] = [entpacken(e, "belege", "stufe_gruende") for e in
                          zeilen(conn, "SELECT * FROM entwuerfe WHERE fall_id = ? ORDER BY id", (fall_id,))]
        f["protokoll"] = [entpacken(e, "details") for e in
                          zeilen(conn, "SELECT * FROM ereignisse WHERE fall_id = ? ORDER BY id", (fall_id,))]
    return f


_AUFGABEN_TITEL = {
    "kundenanfrage": ("antworten", "Kundenanfrage beantworten"),
    "aufgabe": ("bearbeiten", "Aufgabe bearbeiten"),
    "verordnung": ("pruefen", "Verordnung prüfen"),
    "berichtigung": ("pruefen", "Berichtigung prüfen"),
    "intern": ("bearbeiten", "Hinweis bearbeiten"),
}


def fall_anlegen(nachricht_id: str, akteur: str = "mensch") -> Dict[str, Any]:
    """Aus einer Nachricht einen Fall mit einer Aufgabe machen (idempotent)."""
    with transaktion() as conn:
        n = zeile(conn, "SELECT * FROM nachrichten WHERE id = ?", (nachricht_id,))
        if not n:
            raise FachFehler("Diese Nachricht ist nicht im Postfach.")
        vorhanden = zeile(conn, "SELECT id FROM faelle WHERE nachricht_id = ?", (nachricht_id,))
        if vorhanden:
            return {"fall_id": vorhanden["id"], "neu": False}
        cur = conn.execute(
            "INSERT INTO faelle (nachricht_id, titel, status, kunde_id, erstellt) VALUES (?, ?, 'neu', ?, ?)",
            (nachricht_id, n["betreff"], n["kunde_id"], jetzt()),
        )
        fid = cur.lastrowid
        art, titel = _AUFGABEN_TITEL.get(n["typ"], ("bearbeiten", "Aufgabe bearbeiten"))
        conn.execute("INSERT INTO aufgaben (fall_id, art, titel, status, erstellt) VALUES (?, ?, ?, 'offen', ?)",
                     (fid, art, titel, jetzt()))
        ereignis(conn, akteur, "fall_angelegt", fid, {"nachricht_id": nachricht_id})
    return {"fall_id": fid, "neu": True}


def notiz(fall_id: int, text: str, akteur: str) -> Dict[str, Any]:
    text = _text_pruefen(text, "Notiz", 4000)
    with transaktion() as conn:
        if not zeile(conn, "SELECT id FROM faelle WHERE id = ?", (fall_id,)):
            raise FachFehler("Diesen Fall gibt es nicht.")
        ereignis(conn, akteur, "notiz", fall_id, {"text": text})
    return {"ok": True}


# ---------------------------------------------------------------- Verordnung (rundenabhängig)

def sichtbare_texte() -> List[str]:
    """Verordnungstexte, die an eine schon abgerufene Nachricht angehängt sind.

    So taucht die Berichtigung erst auf, wenn ihre Runde abgerufen wurde.
    """
    with verbindung() as conn:
        rows = conn.execute("SELECT anhaenge FROM nachrichten").fetchall()
    angehaengt = set()
    for r in rows:
        for a in loads(r["anhaenge"], []):
            if a.startswith("regulation/"):
                angehaengt.add(a.split("/", 1)[1])
    return sorted(n for n in daten.verordnungen() if n in angehaengt)


def haupttext(namen: List[str]) -> Optional[str]:
    for n in namen:
        if "berichtigung" not in n.lower():
            return n
    return namen[0] if namen else None


def regelwerk_sichtbar() -> Dict[str, Any]:
    """Regelwerk-Zahlen und Texte; die Berichtigung nur, wenn sie schon im Postfach liegt."""
    namen = sichtbare_texte()
    rw = dict(daten.regelwerk())
    if not any("berichtigung" in n.lower() for n in namen):
        rw.pop("berichtigung", None)
    return {"regelwerk": rw, "verfuegbar": namen, "haupttext": haupttext(namen)}


def verordnungstext(name: Optional[str] = None) -> Dict[str, Any]:
    namen = sichtbare_texte()
    name = name or haupttext(namen)
    if name is None:
        raise FachFehler("Es liegt noch keine Verordnung im Postfach.")
    if name not in namen:
        raise FachFehler("Dieser Text liegt nicht im Postfach (oder noch nicht abgerufen).")
    return {"name": name, "text": daten.verordnung_text(name)}


# ---------------------------------------------------------------- Stammdaten (lesen)

def _mg_pro_l(p: Dict[str, Any]) -> Optional[float]:
    """Messwert in mg/l (nur zur Anzeige; die Bewertung bleibt Aufgabe von Mensch und Claude)."""
    wert = p.get("pfas_wert")
    if wert is None:
        return None
    return float(wert) / 1000.0 if p.get("pfas_einheit") == "µg/l" else float(wert)


def produkte_liste(suche: str = "", schaumart: str = "", nur_ohne_messwert: bool = False) -> List[Dict[str, Any]]:
    out = []
    for p in daten.produkte():
        if suche and suche.lower() not in (p["name"] + " " + p["id"]).lower():
            continue
        if schaumart and p.get("schaumart") != schaumart:
            continue
        if nur_ohne_messwert and p.get("pfas_wert") is not None:
            continue
        out.append(dict(p))
    return out


def kunden_liste(suche: str = "", segment: str = "") -> List[Dict[str, Any]]:
    out = []
    for k in daten.kunden():
        if suche and suche.lower() not in (k["name"] + " " + k["id"]).lower():
            continue
        if segment and k.get("segment") != segment:
            continue
        out.append({
            "id": k["id"], "name": k["name"], "segment": k["segment"], "land": k["land"],
            "status": k["status"], "seveso": k["seveso"], "key_account": k["key_account"],
            "ist_haendler": k.get("ist_haendler", False),
        })
    return out


def kunde_detail(kunde_id: str) -> Dict[str, Any]:
    k = daten.kunde(kunde_id)
    if not k:
        raise FachFehler("Diesen Kunden gibt es nicht.")
    ls = []
    for l in daten.lieferungen():
        if l["kunde_id"] != kunde_id:
            continue
        p = daten.produkt(l["produkt_id"]) or {}
        ls.append(dict(l, produkt_name=p.get("name"), pfas_wert=p.get("pfas_wert"),
                       pfas_einheit=p.get("pfas_einheit")))
    return dict(k, lieferungen=ls)


def produkt_detail(produkt_id: str) -> Dict[str, Any]:
    p = daten.produkt(produkt_id)
    if not p:
        raise FachFehler("Dieses Produkt gibt es nicht.")
    kunden_ids = sorted({l["kunde_id"] for l in daten.lieferungen() if l["produkt_id"] == produkt_id})
    return dict(p, pfas_mg_l_umgerechnet=_mg_pro_l(p), geliefert_an=kunden_ids)


# ---------------------------------------------------------------- Fähigkeiten je Runde

def faehigkeiten(welle: Optional[int] = None) -> Dict[str, bool]:
    """Was in der Kommandozentrale schon freigeschaltet ist (Runde 2: Freigabe, 3: Fenster und Uhr, 4: Bericht)."""
    w = aktuelle_welle() if welle is None else welle
    return {"freigabe": w >= 2, "fenster": w >= 3, "bericht": w >= 4}


def _faehig(conn, name: str) -> bool:
    w = int(zustand_lesen(conn, "welle", "0") or 0)
    return faehigkeiten(w)[name]


# ---------------------------------------------------------------- Entwürfe, Kontrollen, Senden

OFFEN = ("entwurf", "zur_freigabe", "freigegeben", "geplant")  # noch nicht gesendet


def _text_pruefen(text: Any, name: str, maxlen: int) -> str:
    if not isinstance(text, str) or not text.strip():
        raise FachFehler("%s darf nicht leer sein." % name)
    if len(text) > maxlen:
        raise FachFehler("%s ist zu lang (höchstens %d Zeichen)." % (name, maxlen))
    return text.strip()


def _empfaenger_pruefen(an: Any) -> str:
    an = _text_pruefen(an, "Empfänger", 200).lower()
    if an in daten.erlaubte_empfaenger() or an.endswith("@" + daten.interne_domain()):
        return an
    raise FachFehler(
        "Empfänger %s ist kein bekannter Kontakt. Entwürfe gehen nur an Kunden aus dem Kundenstamm "
        "oder an interne Adressen." % an)


def _belege_pruefen(belege: Any) -> List[Dict[str, str]]:
    if belege is None:
        return []
    if not isinstance(belege, list) or len(belege) > MAX_BELEGE:
        raise FachFehler("Belege müssen eine Liste sein (höchstens %d)." % MAX_BELEGE)
    out = []
    for b in belege:
        if not isinstance(b, dict) or b.get("typ") not in BELEG_TYPEN or not isinstance(b.get("ref"), str):
            raise FachFehler("Jeder Beleg braucht typ (%s) und ref." % ", ".join(BELEG_TYPEN))
        out.append({"typ": b["typ"], "ref": b["ref"][:200], "hinweis": str(b.get("hinweis", ""))[:300]})
    return out


def _belegpruefung(an: str, betreff: str, text: str, belege: List[Dict[str, str]]) -> None:
    probleme = belegpruefung.pruefe_entwurf(an, betreff, text, belege)
    if probleme:
        raise FachFehler("Belegprüfung: " + " ".join(probleme))


def entwurf_anlegen(fall_id: int, an: str, betreff: str, text: str, belege: Any, akteur: str) -> Dict[str, Any]:
    an = _empfaenger_pruefen(an)
    betreff = _text_pruefen(betreff, "Betreff", MAX_BETREFF)
    text = _text_pruefen(text, "Text", MAX_TEXT)
    belege = _belege_pruefen(belege)
    _belegpruefung(an, betreff, text, belege)
    with transaktion() as conn:
        f = zeile(conn, "SELECT id, status FROM faelle WHERE id = ?", (fall_id,))
        if not f:
            raise FachFehler("Diesen Fall gibt es nicht.")
        jetzt = uhr.jetzt(conn)
        cur = conn.execute(
            "INSERT INTO entwuerfe (fall_id, an, betreff, text, belege, status, von, erstellt, geaendert) "
            "VALUES (?, ?, ?, ?, ?, 'entwurf', ?, ?, ?)",
            (fall_id, an, betreff, text, dumps(belege), akteur, jetzt, jetzt))
        eid = cur.lastrowid
        if f["status"] == "neu":
            conn.execute("UPDATE faelle SET status = 'in_bearbeitung' WHERE id = ?", (fall_id,))
        ereignis(conn, akteur, "entwurf_angelegt", fall_id, {"entwurf_id": eid, "an": an, "belege": len(belege)})
    return {"entwurf_id": eid}


def entwurf_aendern(entwurf_id: int, felder: Dict[str, Any], akteur: str) -> Dict[str, Any]:
    erlaubt = {"an", "betreff", "text", "belege"}
    if not felder or set(felder) - erlaubt:
        raise FachFehler("Änderbar sind: an, betreff, text, belege.")
    with transaktion() as conn:
        e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ?", (entwurf_id,))
        if not e:
            raise FachFehler("Diesen Entwurf gibt es nicht.")
        if e["status"] not in OFFEN:
            raise FachFehler("Dieser Entwurf ist schon gesendet und nicht mehr änderbar.")
        neu = {
            "an": _empfaenger_pruefen(felder["an"]) if "an" in felder else e["an"],
            "betreff": _text_pruefen(felder["betreff"], "Betreff", MAX_BETREFF) if "betreff" in felder else e["betreff"],
            "text": _text_pruefen(felder["text"], "Text", MAX_TEXT) if "text" in felder else e["text"],
            "belege": _belege_pruefen(felder["belege"]) if "belege" in felder else loads(e["belege"], []),
        }
        _belegpruefung(neu["an"], neu["betreff"], neu["text"], neu["belege"])
        jetzt = uhr.jetzt(conn)
        conn.execute("UPDATE entwuerfe SET an=?, betreff=?, text=?, belege=?, geaendert=? WHERE id=?",
                     (neu["an"], neu["betreff"], neu["text"], dumps(neu["belege"]), jetzt, entwurf_id))
        # DRILL 3 (Bauauftrag): Wer einen freigegebenen Entwurf ändert, entwertet die Freigabe.
        #   Heute bleibt der Status unverändert: Die Freigabe gilt für einen Text, den niemand freigegeben hat.
        # DRILL 4 (Bauauftrag): Wer einen eingeplanten Entwurf ändert, bricht den Termin ab.
        #   Heute geht die geänderte Mail trotzdem automatisch raus.
        ereignis(conn, akteur, "entwurf_geaendert", e["fall_id"], {"entwurf_id": entwurf_id, "felder": sorted(felder)})
    return {"ok": True}


def entwuerfe(fall_id: Optional[int] = None) -> List[Dict[str, Any]]:
    sql = ("SELECT e.*, f.titel AS fall_titel, f.kunde_id AS kunde_id FROM entwuerfe e "
           "JOIN faelle f ON f.id = e.fall_id %s ORDER BY e.id")
    with verbindung() as conn:
        rows = zeilen(conn, sql % ("WHERE e.fall_id = ?" if fall_id is not None else ""),
                      (fall_id,) if fall_id is not None else ())
    out = []
    for r in rows:
        r = entpacken(r, "belege", "stufe_gruende")
        k = daten.kunde_zu_email(r["an"]) or (daten.kunde(r["kunde_id"]) if r.get("kunde_id") else None)
        r["kunde_name"] = k["name"] if k else None
        out.append(r)
    return out


def einreichen(entwurf_id: int, rechtsaussage: bool, akteur: str = "claude") -> Dict[str, Any]:
    """Ab Runde 2: Der Entwurf wird einer Kontrolle zugeordnet (Pflichtfreigabe oder Eingriffsfenster)."""
    with transaktion() as conn:
        if not _faehig(conn, "freigabe"):
            raise FachFehler("Einreichen gibt es erst ab Drill 3. Bis dahin sendet der Mensch direkt im Cockpit.")
        e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ?", (entwurf_id,))
        if not e:
            raise FachFehler("Diesen Entwurf gibt es nicht.")
        if e["status"] != "entwurf":
            raise FachFehler("Dieser Entwurf ist schon eingereicht oder gesendet.")
        _belegpruefung(e["an"], e["betreff"], e["text"], loads(e["belege"], []))
        kunde = daten.kunde_zu_email(e["an"])
        stufe, gruende = kontrollen.stufe_fuer(kunde, bool(rechtsaussage), _faehig(conn, "fenster"),
                                               daten.regelwerk().get("geltungsbereich_laender"))
        jetzt = uhr.jetzt(conn)
        if stufe == kontrollen.PFLICHTFREIGABE:
            conn.execute("UPDATE entwuerfe SET status='zur_freigabe', stufe=?, stufe_gruende=?, rechtsaussage=?, sende_am=NULL, "
                         "ablehnung=NULL, geaendert=? WHERE id=?", (stufe, dumps(gruende), int(bool(rechtsaussage)), jetzt, entwurf_id))
            ereignis(conn, akteur, "zur_freigabe", e["fall_id"], {"entwurf_id": entwurf_id, "stufe": stufe, "gruende": gruende})
            return {"entwurf_id": entwurf_id, "stufe": stufe, "gruende": gruende, "status": "zur_freigabe"}
        sende_am = uhr.plus_stunden(jetzt, float(daten.welt().get("eingriffsfenster_stunden", 24)))
        conn.execute("UPDATE entwuerfe SET status='geplant', stufe=?, stufe_gruende=?, rechtsaussage=?, sende_am=?, "
                     "ablehnung=NULL, geaendert=? WHERE id=?", (stufe, dumps(gruende), int(bool(rechtsaussage)), sende_am, jetzt, entwurf_id))
        ereignis(conn, akteur, "geplant", e["fall_id"], {"entwurf_id": entwurf_id, "stufe": stufe, "sende_am": sende_am})
        return {"entwurf_id": entwurf_id, "stufe": stufe, "gruende": gruende, "status": "geplant", "sende_am": sende_am}


def freigeben(entwurf_id: int, akteur: str = "mensch") -> Dict[str, Any]:
    """NUR Cockpit. Der Mensch gibt den Entwurf frei, so wie er jetzt dasteht."""
    with transaktion() as conn:
        e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ?", (entwurf_id,))
        if not e:
            raise FachFehler("Diesen Entwurf gibt es nicht.")
        if e["status"] != "zur_freigabe":
            raise FachFehler("Dieser Entwurf wartet nicht auf eine Freigabe.")
        conn.execute("UPDATE entwuerfe SET status='freigegeben', freigabe_von=?, freigabe_zeit=? WHERE id=?",
                     (akteur, uhr.jetzt(conn), entwurf_id))
        ereignis(conn, akteur, "freigegeben", e["fall_id"], {"entwurf_id": entwurf_id})
    return {"ok": True}


def ablehnen(entwurf_id: int, grund: Any, akteur: str = "mensch") -> Dict[str, Any]:
    """NUR Cockpit. Der Entwurf geht mit Begründung zurück; Claude kann ihn überarbeiten."""
    grund = _text_pruefen(grund, "Begründung", 1000)
    with transaktion() as conn:
        e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ?", (entwurf_id,))
        if not e:
            raise FachFehler("Diesen Entwurf gibt es nicht.")
        if e["status"] not in ("zur_freigabe", "freigegeben"):
            raise FachFehler("Dieser Entwurf liegt nicht zur Freigabe vor.")
        conn.execute("UPDATE entwuerfe SET status='entwurf', ablehnung=?, freigabe_von=NULL, freigabe_zeit=NULL WHERE id=?",
                     (grund, entwurf_id))
        ereignis(conn, akteur, "abgelehnt", e["fall_id"], {"entwurf_id": entwurf_id, "grund": grund})
    return {"ok": True}


def stoppen(entwurf_id: int, akteur: str = "mensch") -> Dict[str, Any]:
    """Cockpit oder Claude (Bremsen ist erlaubt, Beschleunigen nie): nimmt eine eingeplante Mail aus der Warteschlange."""
    with transaktion() as conn:
        e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ?", (entwurf_id,))
        if not e:
            raise FachFehler("Diesen Entwurf gibt es nicht.")
        if e["status"] != "geplant":
            raise FachFehler("Dieser Entwurf ist nicht eingeplant (vielleicht schon gesendet).")
        conn.execute("UPDATE entwuerfe SET status='entwurf', sende_am=NULL WHERE id=?", (entwurf_id,))
        ereignis(conn, akteur, "versand_gestoppt", e["fall_id"], {"entwurf_id": entwurf_id})
    return {"ok": True}


def _ablegen(conn, e: Dict[str, Any], akteur: str, automatisch: bool) -> Dict[str, Any]:
    """Legt die Mail als Datei im Postausgang ab (nichts wird wirklich verschickt)."""
    _empfaenger_pruefen(e["an"])
    ordner = outbox_dir()
    ordner.mkdir(parents=True, exist_ok=True)
    jetzt = uhr.jetzt(conn)
    stamp = jetzt.replace(":", "").replace("-", "").replace("T", "-")
    datei = ordner / ("%s-F%04d-E%d-%s.md" % (stamp, e["fall_id"], e["id"], slug(e["betreff"])))
    belege = loads(e["belege"], [])
    beleg_zeilen = "\n".join("- %s: %s %s" % (b["typ"], b["ref"], b.get("hinweis", "")) for b in belege)
    inhalt = ("---\nan: %s\nbetreff: %s\nfall: F-%04d\nentwurf: %d\nvon_entwurf: %s\nkontrolle: %s\nautomatisch: %s\ngesendet: %s\n---\n%s\n\n"
              "%s\n" % (e["an"], e["betreff"].replace("\n", " "), e["fall_id"], e["id"], e["von"], e.get("stufe") or "direkt",
                        "ja" if automatisch else "nein", jetzt, e["text"],
                        ("Belege:\n" + beleg_zeilen) if beleg_zeilen else ""))
    with open(str(datei), "w", encoding="utf-8", newline="\n") as f:
        f.write(inhalt)
    conn.execute("UPDATE entwuerfe SET status = 'gesendet', geaendert = ? WHERE id = ?", (jetzt, e["id"]))
    conn.execute("INSERT INTO postausgang (entwurf_id, an, betreff, text, gesendet, datei) VALUES (?, ?, ?, ?, ?, ?)",
                 (e["id"], e["an"], e["betreff"], e["text"], jetzt, datei.name))
    conn.execute("UPDATE faelle SET status = 'gesendet' WHERE id = ?", (e["fall_id"],))
    # DRILL 1 (Bauauftrag): Die Aufgabe des Falls bleibt hier bewusst offen.
    # Teilnehmende bauen, dass sie sich beim Senden selbst erledigt.
    ereignis(conn, akteur, "gesendet", e["fall_id"], {"entwurf_id": e["id"], "an": e["an"], "datei": datei.name,
                                                     "automatisch": automatisch, "kontrolle": e.get("stufe")})
    return {"ok": True, "datei": datei.name}


def senden(entwurf_id: int, akteur: str = "mensch") -> Dict[str, Any]:
    """NUR Cockpit. Bis Runde 1 sendet der Mensch direkt; ab Runde 2 nur freigegebene Entwürfe."""
    with transaktion() as conn:
        e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ?", (entwurf_id,))
        if not e:
            raise FachFehler("Diesen Entwurf gibt es nicht.")
        if e["status"] == "gesendet":
            raise FachFehler("Dieser Entwurf wurde schon gesendet.")
        if e["status"] == "geplant":
            raise FachFehler("Der Versand ist eingeplant und geht automatisch raus. Du kannst ihn nur stoppen.")
        if _faehig(conn, "freigabe"):
            if e["status"] == "zur_freigabe":
                raise FachFehler("Dieser Entwurf wartet auf deine Freigabe.")
            if e["status"] != "freigegeben":
                raise FachFehler("Dieser Entwurf wurde noch nicht eingereicht und freigegeben.")
        return _ablegen(conn, e, akteur, automatisch=False)


def faellige_senden() -> int:
    """Eingeplante Mails, deren Frist nach Übungsuhr verstrichen ist, gehen raus (genau einmal)."""
    with verbindung() as conn:
        jetzt = uhr.jetzt(conn)
        ids = [r["id"] for r in conn.execute(
            "SELECT id FROM entwuerfe WHERE status = 'geplant' AND sende_am IS NOT NULL AND sende_am <= ?", (jetzt,)).fetchall()]
    n = 0
    for eid in ids:
        with transaktion() as conn:
            e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ? AND status = 'geplant'", (eid,))
            if not e:
                continue
            _ablegen(conn, e, "system", automatisch=True)
            n += 1
    return n


def uhr_vorspulen(stunden: Any, akteur: str = "mensch") -> Dict[str, Any]:
    """NUR Cockpit. Die Übungsuhr läuft sonst in Echtzeit; hier springt sie vor, und fällige Mails gehen raus."""
    try:
        stunden = float(stunden)
    except (TypeError, ValueError):
        raise FachFehler("Stunden müssen eine Zahl sein.")
    if not 0 < stunden <= 24 * 14:
        raise FachFehler("Bitte zwischen einer Stunde und 14 Tagen vorspulen.")
    with transaktion() as conn:
        if not _faehig(conn, "fenster"):
            raise FachFehler("Die Übungsuhr gibt es erst ab Drill 4.")
        alt = int(zustand_lesen(conn, "uhr_offset_s", "0") or 0)
        zustand_setzen(conn, "uhr_offset_s", str(alt + int(stunden * 3600)))
        ereignis(conn, akteur, "uhr_vorgespult", None, {"stunden": stunden, "jetzt": uhr.jetzt(conn)})
    n = faellige_senden()
    return {"jetzt": uhr.jetzt(), "automatisch_gesendet": n}


# ---------------------------------------------------------------- Einschätzungen (Betroffenheit)

ERGEBNISSE = ("betroffen", "nicht_betroffen", "mittelbar", "unklar")


def einschaetzung_festhalten(kunde_id: str, ergebnis: str, begruendung: Any, belege: Any, stichtag: Optional[str],
                             akteur: str) -> Dict[str, Any]:
    if not daten.kunde(kunde_id):
        raise FachFehler("Diesen Kunden gibt es nicht.")
    if ergebnis not in ERGEBNISSE:
        raise FachFehler("Ergebnis muss eines sein von: %s." % ", ".join(ERGEBNISSE))
    begruendung = _text_pruefen(begruendung, "Begründung", 2000)
    belege = _belege_pruefen(belege)
    if stichtag is not None and not (isinstance(stichtag, str) and len(stichtag) == 10 and stichtag[4] == "-" and stichtag[7] == "-"):
        raise FachFehler("Stichtag im Format JJJJ-MM-TT angeben oder weglassen.")
    probleme = belegpruefung.pruefe_einschaetzung(kunde_id, ergebnis, begruendung, belege)
    if probleme:
        raise FachFehler("Belegprüfung: " + " ".join(probleme))
    with transaktion() as conn:
        conn.execute(
            "INSERT INTO einschaetzungen (kunde_id, ergebnis, begruendung, belege, stichtag, von, zeit) VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(kunde_id) DO UPDATE SET ergebnis=excluded.ergebnis, begruendung=excluded.begruendung, "
            "belege=excluded.belege, stichtag=excluded.stichtag, von=excluded.von, zeit=excluded.zeit",
            (kunde_id, ergebnis, begruendung, dumps(belege), stichtag, akteur, uhr.jetzt(conn)))
        ereignis(conn, akteur, "einschaetzung", None, {"kunde_id": kunde_id, "ergebnis": ergebnis})
    return {"ok": True}


def einschaetzungen() -> List[Dict[str, Any]]:
    with verbindung() as conn:
        rows = zeilen(conn, "SELECT * FROM einschaetzungen ORDER BY kunde_id")
    return [entpacken(r, "belege") for r in rows]


# ---------------------------------------------------------------- Postausgang, Protokoll, Bericht, Stand

def postausgang() -> List[Dict[str, Any]]:
    with verbindung() as conn:
        return zeilen(conn, "SELECT * FROM postausgang ORDER BY id DESC")


def protokoll(limit: int = 200) -> List[Dict[str, Any]]:
    with verbindung() as conn:
        rows = zeilen(conn, "SELECT * FROM ereignisse ORDER BY id DESC LIMIT ?", (int(limit),))
    return [entpacken(r, "details") for r in rows]


def bericht() -> Dict[str, Any]:
    """Zahlen für den Bericht an die Geschäftsführung, ausschließlich aus dem Protokoll und den Entwürfen.

    DRILL 5 (Bauauftrag): Teilnehmende ergänzen hier eine eigene Kennzahl und zeigen sie im Bericht.
    """
    with verbindung() as conn:
        ents = zeilen(conn, "SELECT * FROM entwuerfe")
        ev = zeilen(conn, "SELECT * FROM ereignisse")
        eins = zeilen(conn, "SELECT ergebnis, COUNT(*) AS n FROM einschaetzungen GROUP BY ergebnis")
        jetzt = uhr.jetzt(conn)
    zaehl = {k: 0 for k in ERGEBNISSE}
    zaehl.update({r["ergebnis"]: r["n"] for r in eins})
    aktive = [k for k in daten.kunden() if k.get("status") == "aktiv"]
    arten = {}
    for e in ev:
        arten[e["art"]] = arten.get(e["art"], 0) + 1
    gesendet = [e for e in ents if e["status"] == "gesendet"]
    auto = sum(1 for e in ev if e["art"] == "gesendet" and loads(e["details"], {}).get("automatisch"))
    frist = daten.regelwerk().get("informationspflicht_bis")
    tage = None
    if frist:
        from datetime import datetime
        tage = (datetime.strptime(frist, "%Y-%m-%d") - datetime.strptime(jetzt[:10], "%Y-%m-%d")).days
    return {
        "stand": jetzt,
        "einschaetzungen": dict(zaehl, ohne_einschaetzung=max(len(aktive) - sum(zaehl.values()), 0), aktive_kunden=len(aktive)),
        "entwuerfe": {"gesamt": len(ents), "von_claude": sum(1 for e in ents if e["von"] == "claude"),
                      "offen": sum(1 for e in ents if e["status"] in OFFEN)},
        "versand": {"gesendet": len(gesendet),
                    "mit_pflichtfreigabe": sum(1 for e in gesendet if e["stufe"] == kontrollen.PFLICHTFREIGABE),
                    "automatisch_nach_fenster": auto,
                    "direkt_vom_menschen": sum(1 for e in gesendet if not e["stufe"])},
        "kontrolle": {"freigegeben": arten.get("freigegeben", 0), "abgelehnt": arten.get("abgelehnt", 0),
                      "gestoppt": arten.get("versand_gestoppt", 0), "wartet_auf_freigabe": sum(1 for e in ents if e["status"] == "zur_freigabe"),
                      "eingeplant": sum(1 for e in ents if e["status"] == "geplant")},
        "frist": {"informationspflicht_bis": frist, "tage_bis": tage},
        "grenze": "Alle Zahlen stammen aus der Übungswelt (erfundene Daten) und zeigen, was das System festgehalten hat, "
                  "nicht, ob eine Rechtsauskunft richtig war.",
    }


def status() -> Dict[str, Any]:
    with verbindung() as conn:
        zahlen = {
            "nachrichten": conn.execute("SELECT COUNT(*) FROM nachrichten").fetchone()[0],
            "faelle": conn.execute("SELECT COUNT(*) FROM faelle").fetchone()[0],
            "offene_aufgaben": conn.execute("SELECT COUNT(*) FROM aufgaben WHERE status='offen'").fetchone()[0],
            "entwuerfe": conn.execute("SELECT COUNT(*) FROM entwuerfe WHERE status != 'gesendet'").fetchone()[0],
            "gesendet": conn.execute("SELECT COUNT(*) FROM postausgang").fetchone()[0],
            "ungelesen": conn.execute("SELECT COUNT(*) FROM nachrichten WHERE gelesen = 0").fetchone()[0],
            "faelle_offen": conn.execute("SELECT COUNT(*) FROM faelle WHERE status != 'gesendet'").fetchone()[0],
            "zur_freigabe": conn.execute("SELECT COUNT(*) FROM entwuerfe WHERE status IN ('zur_freigabe')").fetchone()[0],
            "geplant": conn.execute("SELECT COUNT(*) FROM entwuerfe WHERE status = 'geplant'").fetchone()[0],
            "einschaetzungen": conn.execute("SELECT COUNT(*) FROM einschaetzungen").fetchone()[0],
            "produkte": len(daten.produkte()),
            "kunden": len(daten.kunden()),
        }
        jetzt = uhr.jetzt(conn)
    w = aktuelle_welle()
    return dict(zahlen, welle=w, faehigkeiten=faehigkeiten(w), naechste_welle=naechste_welle_code_hinweis(),
                firma=daten.welt().get("firma"), heute=daten.welt().get("heute"), jetzt=jetzt)
