"""Schlanker Client für die AgentMail-Schnittstelle (nur HTTPS mit urllib, kein Paket) und die Verschlüsselung der Postfach-Schlüssel.

Warum selbst gebaut: Das Python-Paket von AgentMail zieht Abhängigkeiten nach; dieser Workshop installiert nichts. Es werden nur
fünf Aufrufe gebraucht (Postfach lesen, Nachricht lesen, senden). Fehler werden als `MailFehler` mit einer verständlichen
deutschen Meldung gemeldet; der Rest des Cockpits läuft unabhängig davon weiter.

Verschlüsselung: Der Schlüssel liegt nur verschlüsselt im öffentlichen Repository (`data/agentmail.enc`) und wird im Cockpit
mit einem Passwort entsperrt, das der Dozent erst am Workshop-Tag nennt. Verfahren (ausschließlich Standardbibliothek):
PBKDF2-HMAC-SHA256 (viele Durchläufe) leitet zwei Schlüssel ab; ein Datenstrom aus HMAC-SHA256 verschlüsselt, ein zweiter
HMAC sichert gegen Fehleingaben und Veränderung. Das reicht für einen kurzlebigen Übungsschlüssel, der nach dem Workshop
gelöscht wird; es ist kein Ersatz für ein geprüftes Verfahren.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASIS = "https://api.agentmail.to/v0"
TIMEOUT = 20
ITERATIONEN = 200_000
VERSION = 1


class MailFehler(Exception):
    """Fehler mit verständlicher Meldung für Menschen."""


def basis_url() -> str:
    return (os.environ.get("AGENTMAIL_BASE_URL") or BASIS).rstrip("/")


# ---------------------------------------------------------------- Schnittstelle

def _anfrage(schluessel: str, methode: str, pfad: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    daten = json.dumps(body).encode("utf-8") if body is not None else None
    req = Request(basis_url() + pfad, data=daten, method=methode, headers={
        "Authorization": "Bearer " + schluessel, "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "sthamer-sys"})
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            roh = r.read().decode("utf-8")
            return json.loads(roh) if roh.strip() else {}
    except HTTPError as e:
        e.close()
        if e.code in (401, 403):
            raise MailFehler("Das Postfach lehnt den Zugang ab. Der Schlüssel stimmt nicht oder gilt nicht mehr.")
        if e.code == 404:
            raise MailFehler("Das Postfach wurde nicht gefunden.")
        if e.code == 429:
            raise MailFehler("Zu viele Anfragen in kurzer Zeit. Bitte eine halbe Minute warten und noch einmal versuchen.")
        if e.code == 400 or e.code == 422:
            raise MailFehler("Die Mail wurde vom Dienst abgelehnt (zum Beispiel wegen einer ungültigen Adresse).")
        raise MailFehler("Der Mail-Dienst meldet einen Fehler (%d). Bitte später noch einmal versuchen." % e.code)
    except (URLError, OSError, TimeoutError):
        raise MailFehler("Keine Verbindung zum Mail-Dienst. Prüfe das Netz; der Rest des Cockpits funktioniert weiter.")
    except ValueError:
        raise MailFehler("Unerwartete Antwort vom Mail-Dienst.")


def _box(postfach: str) -> str:
    return "/inboxes/" + quote(postfach, safe="")


def senden(schluessel: str, postfach: str, an: str, betreff: str, text: str) -> Dict[str, str]:
    """Sendet eine Mail aus dem Postfach. Gibt message_id und thread_id zurück."""
    d = _anfrage(schluessel, "POST", _box(postfach) + "/messages/send", {"to": [an], "subject": betreff, "text": text})
    mid = d.get("message_id")
    if not mid:
        raise MailFehler("Der Mail-Dienst hat den Versand nicht bestätigt.")
    return {"message_id": mid, "thread_id": d.get("thread_id") or ""}


def liste(schluessel: str, postfach: str, limit: int = 100, seiten: int = 3) -> List[Dict[str, Any]]:
    """Neueste Nachrichten (empfangene und gesendete) ohne Text, bis zu `seiten` Seiten."""
    alle: List[Dict[str, Any]] = []
    token = ""
    for _ in range(seiten):
        pfad = _box(postfach) + "/messages?limit=%d" % limit + (("&page_token=" + quote(token, safe="")) if token else "")
        d = _anfrage(schluessel, "GET", pfad)
        alle.extend(d.get("messages") or [])
        token = d.get("next_page_token") or ""
        if not token:
            break
    return alle


def nachricht(schluessel: str, postfach: str, message_id: str) -> Dict[str, Any]:
    return _anfrage(schluessel, "GET", _box(postfach) + "/messages/" + quote(message_id, safe=""))


def pruefen(schluessel: str, postfach: str) -> None:
    """Prüft, ob Schlüssel und Postfach zusammenpassen (liest eine Nachricht)."""
    _anfrage(schluessel, "GET", _box(postfach) + "/messages?limit=1")


# ---------------------------------------------------------------- Verschlüsselung

def _ableiten(passwort: str, salt: bytes, iterationen: int) -> Dict[str, bytes]:
    roh = hashlib.pbkdf2_hmac("sha256", passwort.encode("utf-8"), salt, iterationen, dklen=64)
    return {"enc": roh[:32], "mac": roh[32:]}


def _strom(enc: bytes, nonce: bytes, laenge: int) -> bytes:
    out = b""
    zaehler = 0
    while len(out) < laenge:
        out += hmac.new(enc, nonce + zaehler.to_bytes(8, "big"), hashlib.sha256).digest()
        zaehler += 1
    return out[:laenge]


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def verschluesseln(klartext: str, passwort: str, postfach: str, iterationen: int = ITERATIONEN) -> Dict[str, Any]:
    """Erzeugt den Inhalt von data/agentmail.enc. Das Postfach (die Adresse) steht unverschlüsselt dabei."""
    if len(passwort) < 8:
        raise MailFehler("Das Passwort ist zu kurz (mindestens 8 Zeichen).")
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(16)
    k = _ableiten(passwort, salt, iterationen)
    ct = _xor(klartext.encode("utf-8"), _strom(k["enc"], nonce, len(klartext.encode("utf-8"))))
    tag = hmac.new(k["mac"], b"v%d" % VERSION + postfach.encode("utf-8") + salt + nonce + ct, hashlib.sha256).digest()
    b64 = lambda b: base64.b64encode(b).decode("ascii")  # noqa: E731
    return {"v": VERSION, "postfach": postfach, "iterationen": iterationen, "salt": b64(salt), "nonce": b64(nonce),
            "ct": b64(ct), "tag": b64(tag)}


def entschluesseln(blob: Dict[str, Any], passwort: str) -> str:
    try:
        salt, nonce = base64.b64decode(blob["salt"]), base64.b64decode(blob["nonce"])
        ct, tag = base64.b64decode(blob["ct"]), base64.b64decode(blob["tag"])
        postfach = str(blob["postfach"])
        iterationen = int(blob["iterationen"])
    except (KeyError, ValueError, TypeError):
        raise MailFehler("Die Datei mit dem verschlüsselten Schlüssel ist beschädigt.")
    k = _ableiten(passwort or "", salt, iterationen)
    soll = hmac.new(k["mac"], b"v%d" % int(blob.get("v", VERSION)) + postfach.encode("utf-8") + salt + nonce + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(soll, tag):
        raise MailFehler("Das Passwort passt nicht. Bitte noch einmal beim Dozenten nachfragen.")
    return _xor(ct, _strom(k["enc"], nonce, len(ct))).decode("utf-8")
