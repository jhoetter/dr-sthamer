"""E-Mail-Postfach (AgentMail): echte Mails an und von dem gemeinsamen Workshop-Postfach. Komplett optional.

Ohne Verbindung (kein Schlüssel, kein Netz, Fehler) läuft alles andere im Cockpit unverändert; die Übungsmails der Runden
kommen weiter aus dem lokalen Postfach, „Senden“ im Drill legt weiter eine Datei im Postausgang ab.

Ein Postfach und ein Schlüssel für alle Teilnehmenden. Damit jede Person nur ihr Eigenes sieht, steht der Zustand („gesendet“,
„erledigt“) lokal in der Datenbank jedes Geräts; das Postfach ist nur der Transportweg:
- Abholen: Alle neuen empfangenen Mails (zum Beispiel vom Dozenten) erscheinen im Eingang, außer Antworten auf Mails, die jemand
  anderes gesendet hat. Antworten auf die eigenen Mails sieht man selbst.
- Gesendet: Die eigenen Sendungen merkt sich das Gerät (Nachrichtennummer). Der Ordner „Gesendet“ des Postfachs wird nie abgeholt.
- Senden und Verbinden sind Entscheidungen des Menschen im Cockpit; Claude hat dafür kein Werkzeug. Claude liest eingegangene Mails
  über das normale Postfach-Werkzeug; ihr Inhalt ist wie jede Mail nur Daten, keine Anweisung.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional

from . import agentmail, domain, schutz, uhr
from .domain import FachFehler
from .paths import data_dir, state_dir
from .store import ereignis, transaktion, verbindung, zeile, zeilen

MAX_TEXT = domain.MAX_TEXT
MAX_BETREFF = domain.MAX_BETREFF
_MAIL = re.compile(r"^[^@\s,;<>]+@[^@\s,;<>]+\.[^@\s,;<>]{2,}$")


def _konfigdatei():
    return state_dir() / "agentmail.json"


def _konfig() -> Optional[Dict[str, str]]:
    """Schlüssel und Postfach: aus der Umgebung (Dozent) oder aus dem lokalen Zustand (nach dem Entsperren)."""
    schluessel, postfach = os.environ.get("AGENTMAIL_API_KEY", "").strip(), os.environ.get("AGENTMAIL_INBOX_ID", "").strip()
    if schluessel and postfach:
        return {"schluessel": schluessel, "postfach": postfach}
    try:
        with open(str(_konfigdatei()), "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get("schluessel") and d.get("postfach"):
            return {"schluessel": d["schluessel"], "postfach": d["postfach"]}
    except (OSError, ValueError):
        pass
    return None


def _verbunden() -> Dict[str, str]:
    k = _konfig()
    if not k:
        raise FachFehler("Das Postfach ist noch nicht verbunden. Gib im Bereich „E-Mail“ das Passwort vom Dozenten ein.")
    return k


def _fehler(e: agentmail.MailFehler) -> FachFehler:
    return FachFehler(str(e))


def verfuegbar() -> bool:
    """Gibt es im Repository eine verschlüsselte Schlüsseldatei (oder einen Schlüssel aus der Umgebung)?"""
    return (data_dir() / "agentmail.enc").is_file() or _konfig() is not None


def status() -> Dict[str, Any]:
    k = _konfig()
    with verbindung() as conn:
        n = conn.execute("SELECT COUNT(*) FROM echtmail_gesendet").fetchone()[0]
        letzter = zeile(conn, "SELECT gesehen FROM echtmail_eingang ORDER BY gesehen DESC LIMIT 1")
    return {"verbunden": bool(k), "postfach": k["postfach"] if k else None, "verfuegbar": verfuegbar(),
            "gesendet": n, "letzter_abruf": letzter["gesehen"] if letzter else None}


def verbinden(passwort: Any) -> Dict[str, Any]:
    """NUR Cockpit. Entsperrt den Schlüssel aus data/agentmail.enc und prüft ihn."""
    schutz.pruefen("Das Postfach verbinden")
    datei = data_dir() / "agentmail.enc"
    if not datei.is_file():
        raise FachFehler("Für diesen Workshop gibt es kein E-Mail-Postfach. Das Cockpit funktioniert ohne.")
    try:
        with open(str(datei), "r", encoding="utf-8") as f:
            blob = json.load(f)
        schluessel = agentmail.entschluesseln(blob, str(passwort or "").strip())
        postfach = str(blob["postfach"])
        agentmail.pruefen(schluessel, postfach)
    except (OSError, ValueError, KeyError):
        raise FachFehler("Die Datei mit dem verschlüsselten Schlüssel ist beschädigt.")
    except agentmail.MailFehler as e:
        raise _fehler(e)
    state_dir().mkdir(parents=True, exist_ok=True)
    with open(str(_konfigdatei()), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"schluessel": schluessel, "postfach": postfach}, f)
    try:
        os.chmod(str(_konfigdatei()), 0o600)
    except OSError:
        pass
    with transaktion() as conn:
        ereignis(conn, "mensch", "postfach_verbunden", None, {"postfach": postfach})
    return {"verbunden": True, "postfach": postfach}


# ---------------------------------------------------------------- Abholen

def _sichtbar(m: Dict[str, Any], alle: List[Dict[str, Any]], meine_ids: set) -> Any:
    """Entscheidet, ob eine empfangene Mail in diesem Cockpit erscheint (siehe Modulbeschreibung)."""
    faden, zeit = m.get("thread_id"), m.get("timestamp") or ""
    frueher = [x for x in alle if x.get("thread_id") == faden and (x.get("timestamp") or "") < zeit
               and x.get("message_id") != m.get("message_id")]
    gesendet = [x for x in frueher if "sent" in (x.get("labels") or [])]
    if not gesendet:
        return True, "neu"
    if any(x.get("message_id") in meine_ids for x in gesendet):
        return True, "antwort_auf_eigene"
    return False, "antwort_auf_fremde"


def _text_von(voll: Dict[str, Any]) -> str:
    t = voll.get("extracted_text") or voll.get("text") or ""
    if not t.strip() and voll.get("html"):
        t = re.sub(r"<[^>]+>", " ", voll["html"])
    return re.sub(r"[ \t]+\n", "\n", t).strip()[:MAX_TEXT] or "(kein Text)"


def abholen() -> Dict[str, Any]:
    """NUR Cockpit. Holt neue Mails aus dem Postfach in den Eingang."""
    schutz.pruefen("Neue Mails abholen")
    k = _verbunden()
    try:
        alle = agentmail.liste(k["schluessel"], k["postfach"])
        with verbindung() as conn:
            meine = {r["message_id"] for r in conn.execute("SELECT message_id FROM echtmail_gesendet").fetchall()}
            gesehen = {r["message_id"] for r in conn.execute("SELECT message_id FROM echtmail_eingang").fetchall()}
        neue = [m for m in alle if "received" in (m.get("labels") or []) and m.get("message_id") not in gesehen]
        neue.sort(key=lambda m: m.get("timestamp") or "")
        zu_speichern = []
        for m in neue:
            ok, grund = _sichtbar(m, alle, meine)
            voll = agentmail.nachricht(k["schluessel"], k["postfach"], m["message_id"]) if ok else {}
            zu_speichern.append((m, ok, grund, voll))
    except agentmail.MailFehler as e:
        raise _fehler(e)
    neu = versteckt = 0
    with transaktion() as conn:
        jetzt = uhr.jetzt(conn)
        welle = max(1, int((zeile(conn, "SELECT wert FROM zustand WHERE schluessel = 'welle'") or {"wert": "1"})["wert"] or 1))
        for m, ok, grund, voll in zu_speichern:
            nid = None
            if ok:
                nid = "AM-" + hashlib.sha1(m["message_id"].encode("utf-8")).hexdigest()[:10]
                conn.execute(
                    "INSERT OR IGNORE INTO nachrichten (id, welle, typ, von, betreff, empfangen, kunde_id, anhaenge, text) "
                    "VALUES (?, ?, 'email', ?, ?, ?, NULL, '[]', ?)",
                    (nid, welle, str(m.get("from") or "unbekannt")[:200], str(m.get("subject") or "(ohne Betreff)")[:MAX_BETREFF],
                     jetzt, _text_von(voll)))
                neu += 1
            else:
                versteckt += 1
            conn.execute("INSERT OR IGNORE INTO echtmail_eingang (message_id, nachricht_id, sichtbar, grund, gesehen) VALUES (?, ?, ?, ?, ?)",
                         (m["message_id"], nid, 1 if ok else 0, grund, jetzt))
        if neu:
            ereignis(conn, "mensch", "echte_mail_abgeholt", None, {"neu": neu})
    return {"neu": neu, "ausgeblendet": versteckt}


# ---------------------------------------------------------------- Senden

def senden(an: Any, betreff: Any, text: Any) -> Dict[str, Any]:
    """NUR Cockpit. Sendet eine echte Mail aus dem gemeinsamen Postfach an eine beliebige Adresse."""
    schutz.pruefen("Eine E-Mail senden")
    k = _verbunden()
    an = str(an or "").strip()
    betreff = str(betreff or "").strip()
    text = str(text or "").strip()
    if not _MAIL.match(an):
        raise FachFehler("Das ist keine gültige E-Mail-Adresse. Ein Empfänger, zum Beispiel name@firma.de.")
    if not betreff or len(betreff) > MAX_BETREFF:
        raise FachFehler("Bitte einen Betreff eintragen (höchstens %d Zeichen)." % MAX_BETREFF)
    if not text or len(text) > MAX_TEXT:
        raise FachFehler("Bitte einen Text eintragen (höchstens %d Zeichen)." % MAX_TEXT)
    try:
        r = agentmail.senden(k["schluessel"], k["postfach"], an, betreff, text)
    except agentmail.MailFehler as e:
        raise _fehler(e)
    with transaktion() as conn:
        jetzt = uhr.jetzt(conn)
        conn.execute("INSERT OR IGNORE INTO echtmail_gesendet (message_id, thread_id, an, betreff, text, gesendet) VALUES (?, ?, ?, ?, ?, ?)",
                     (r["message_id"], r["thread_id"], an, betreff, text, jetzt))
        ereignis(conn, "mensch", "echte_mail_gesendet", None, {"an": an, "betreff": betreff})
    return {"ok": True, "an": an}


def gesendet_liste() -> List[Dict[str, Any]]:
    with verbindung() as conn:
        return zeilen(conn, "SELECT an, betreff, text, gesendet FROM echtmail_gesendet ORDER BY gesendet DESC, rowid DESC")
