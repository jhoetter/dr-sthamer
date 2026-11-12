"""Fachlogik. Claude (über MCP) und das Cockpit (HTTP) rufen dieselben Funktionen.

Wichtig für den Workshop: Es gibt hier absichtlich keine Funktion, die Claude
zum Senden oder Freigeben nutzen kann. `senden` wird nur vom Cockpit aufgerufen.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import daten
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
                "SELECT COUNT(*) FROM entwuerfe WHERE fall_id = ? AND status = 'entwurf'", (r["id"],)).fetchone()[0]
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
        f["entwuerfe"] = [entpacken(e, "belege") for e in
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


# ---------------------------------------------------------------- Entwürfe und Senden

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


def entwurf_anlegen(fall_id: int, an: str, betreff: str, text: str, belege: Any, akteur: str) -> Dict[str, Any]:
    an = _empfaenger_pruefen(an)
    betreff = _text_pruefen(betreff, "Betreff", MAX_BETREFF)
    text = _text_pruefen(text, "Text", MAX_TEXT)
    belege = _belege_pruefen(belege)
    with transaktion() as conn:
        f = zeile(conn, "SELECT id, status FROM faelle WHERE id = ?", (fall_id,))
        if not f:
            raise FachFehler("Diesen Fall gibt es nicht.")
        cur = conn.execute(
            "INSERT INTO entwuerfe (fall_id, an, betreff, text, belege, status, von, erstellt, geaendert) "
            "VALUES (?, ?, ?, ?, ?, 'entwurf', ?, ?, ?)",
            (fall_id, an, betreff, text, dumps(belege), akteur, jetzt(), jetzt()))
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
        if e["status"] != "entwurf":
            raise FachFehler("Dieser Entwurf ist schon gesendet und nicht mehr änderbar.")
        neu = {
            "an": _empfaenger_pruefen(felder["an"]) if "an" in felder else e["an"],
            "betreff": _text_pruefen(felder["betreff"], "Betreff", MAX_BETREFF) if "betreff" in felder else e["betreff"],
            "text": _text_pruefen(felder["text"], "Text", MAX_TEXT) if "text" in felder else e["text"],
            "belege": dumps(_belege_pruefen(felder["belege"])) if "belege" in felder else e["belege"],
        }
        conn.execute("UPDATE entwuerfe SET an=?, betreff=?, text=?, belege=?, geaendert=? WHERE id=?",
                     (neu["an"], neu["betreff"], neu["text"], neu["belege"], jetzt(), entwurf_id))
        ereignis(conn, akteur, "entwurf_geaendert", e["fall_id"],
                 {"entwurf_id": entwurf_id, "felder": sorted(felder)})
    return {"ok": True}


def entwuerfe(fall_id: Optional[int] = None) -> List[Dict[str, Any]]:
    with verbindung() as conn:
        if fall_id is None:
            rows = zeilen(conn, "SELECT * FROM entwuerfe ORDER BY id")
        else:
            rows = zeilen(conn, "SELECT * FROM entwuerfe WHERE fall_id = ? ORDER BY id", (fall_id,))
    return [entpacken(r, "belege") for r in rows]


def senden(entwurf_id: int, akteur: str = "mensch") -> Dict[str, Any]:
    """NUR für das Cockpit. Legt die Mail als Datei im Postausgang ab (nichts wird wirklich verschickt)."""
    with transaktion() as conn:
        e = zeile(conn, "SELECT * FROM entwuerfe WHERE id = ?", (entwurf_id,))
        if not e:
            raise FachFehler("Diesen Entwurf gibt es nicht.")
        if e["status"] != "entwurf":
            raise FachFehler("Dieser Entwurf wurde schon gesendet.")
        _empfaenger_pruefen(e["an"])
        ordner = outbox_dir()
        ordner.mkdir(parents=True, exist_ok=True)
        stamp = jetzt().replace(":", "").replace("-", "").replace("T", "-")
        datei = ordner / ("%s-F%04d-%s.md" % (stamp, e["fall_id"], slug(e["betreff"])))
        belege = loads(e["belege"], [])
        beleg_zeilen = "\n".join("- %s: %s %s" % (b["typ"], b["ref"], b.get("hinweis", "")) for b in belege)
        inhalt = ("---\nan: %s\nbetreff: %s\nfall: F-%04d\nentwurf: %d\nvon_entwurf: %s\ngesendet: %s\n---\n%s\n\n"
                  "%s\n" % (e["an"], e["betreff"].replace("\n", " "), e["fall_id"], e["id"], e["von"], jetzt(),
                            e["text"], ("Belege:\n" + beleg_zeilen) if beleg_zeilen else "")).replace("\r\n", "\n")
        with open(str(datei), "w", encoding="utf-8", newline="\n") as f:
            f.write(inhalt)
        conn.execute("UPDATE entwuerfe SET status = 'gesendet', geaendert = ? WHERE id = ?", (jetzt(), entwurf_id))
        conn.execute("INSERT INTO postausgang (entwurf_id, an, betreff, text, gesendet, datei) VALUES (?, ?, ?, ?, ?, ?)",
                     (entwurf_id, e["an"], e["betreff"], e["text"], jetzt(), datei.name))
        conn.execute("UPDATE faelle SET status = 'gesendet' WHERE id = ?", (e["fall_id"],))
        # DRILL 1 (Bauauftrag): Die Aufgabe des Falls bleibt hier bewusst offen.
        # Teilnehmende bauen, dass sie sich beim Senden selbst erledigt.
        ereignis(conn, akteur, "gesendet", e["fall_id"], {"entwurf_id": entwurf_id, "an": e["an"], "datei": datei.name})
    return {"ok": True, "datei": datei.name}


def postausgang() -> List[Dict[str, Any]]:
    with verbindung() as conn:
        return zeilen(conn, "SELECT * FROM postausgang ORDER BY id DESC")


def protokoll(limit: int = 200) -> List[Dict[str, Any]]:
    with verbindung() as conn:
        rows = zeilen(conn, "SELECT * FROM ereignisse ORDER BY id DESC LIMIT ?", (int(limit),))
    return [entpacken(r, "details") for r in rows]


def status() -> Dict[str, Any]:
    with verbindung() as conn:
        zahlen = {
            "nachrichten": conn.execute("SELECT COUNT(*) FROM nachrichten").fetchone()[0],
            "faelle": conn.execute("SELECT COUNT(*) FROM faelle").fetchone()[0],
            "offene_aufgaben": conn.execute("SELECT COUNT(*) FROM aufgaben WHERE status='offen'").fetchone()[0],
            "entwuerfe": conn.execute("SELECT COUNT(*) FROM entwuerfe WHERE status='entwurf'").fetchone()[0],
            "gesendet": conn.execute("SELECT COUNT(*) FROM postausgang").fetchone()[0],
        }
    return dict(zahlen, welle=aktuelle_welle(), naechste_welle=naechste_welle_code_hinweis(),
                firma=daten.welt().get("firma"), heute=daten.welt().get("heute"))
