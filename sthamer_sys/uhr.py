"""Übungsuhr: Datum aus data/welt.json, Uhrzeit läuft in Echtzeit, Vorspulen nur im Cockpit."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from . import daten


def _offset(conn) -> int:
    r = conn.execute("SELECT wert FROM zustand WHERE schluessel = 'uhr_offset_s'").fetchone()
    try:
        return int(r["wert"]) if r else 0
    except (TypeError, ValueError):
        return 0


def jetzt_dt(conn=None) -> datetime:
    from .store import verbindung
    real = datetime.now().replace(microsecond=0)
    try:
        tag = daten.welt().get("heute")
        basis = datetime.strptime(tag + " " + real.strftime("%H:%M:%S"), "%Y-%m-%d %H:%M:%S") if tag else real
    except Exception:
        basis = real
    if conn is None:
        with verbindung() as c:
            off = _offset(c)
    else:
        off = _offset(conn)
    return basis + timedelta(seconds=off)


def jetzt(conn=None) -> str:
    return jetzt_dt(conn).isoformat(timespec="seconds")


def plus_stunden(iso: str, stunden: float) -> str:
    return (datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=stunden)).isoformat(timespec="seconds")


def verstrichen(iso: Optional[str], conn=None) -> bool:
    return bool(iso) and iso <= jetzt(conn)
