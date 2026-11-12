from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime


def jetzt() -> str:
    """„Jetzt“ in der Übungswelt: Datum aus data/welt.json (Übungstag), Uhrzeit der echten Uhr.

    Phase 2 ersetzt das durch die vorspulbare Workshop-Uhr.
    """
    real = datetime.now().replace(microsecond=0)
    try:
        from . import daten
        tag = daten.welt().get("heute")
        if tag:
            return "%sT%s" % (tag, real.strftime("%H:%M:%S"))
    except Exception:
        pass
    return real.isoformat(timespec="seconds")


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
