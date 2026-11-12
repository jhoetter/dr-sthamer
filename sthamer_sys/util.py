from __future__ import annotations

import json
import re
import unicodedata


def jetzt(conn=None) -> str:
    """„Jetzt“ in der Übungswelt: Übungstag aus data/welt.json, Uhrzeit der echten Uhr plus Vorspulen.

    Die Übungsuhr kann nur im Cockpit vorgespult werden (Drill 4). `conn` vermeidet eine zweite Verbindung.
    """
    from . import uhr
    return uhr.jetzt(conn)


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def loads(text, default=None):
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return default


def slug(text: str, maxlen: int = 40) -> str:
    """Dateinamen-tauglich: ASCII, Kleinbuchstaben, Bindestriche."""
    norm = unicodedata.normalize("NFKD", text or "")
    norm = norm.encode("ascii", "ignore").decode("ascii").lower()
    norm = re.sub(r"[^a-z0-9]+", "-", norm).strip("-")
    return (norm or "ohne-titel")[:maxlen].strip("-") or "ohne-titel"
