"""SQLite-Speicher für den lokalen Zustand. Kurze Verbindungen, UTF-8, keine Pakete."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from .paths import db_path, state_dir
from .util import dumps, jetzt, loads

SCHEMA = """
CREATE TABLE IF NOT EXISTS zustand (schluessel TEXT PRIMARY KEY, wert TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS nachrichten (
  id TEXT PRIMARY KEY, welle INTEGER NOT NULL, typ TEXT NOT NULL, von TEXT NOT NULL,
  betreff TEXT NOT NULL, empfangen TEXT NOT NULL, kunde_id TEXT,
  anhaenge TEXT NOT NULL DEFAULT '[]', text TEXT NOT NULL, gelesen INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS faelle (
  id INTEGER PRIMARY KEY AUTOINCREMENT, nachricht_id TEXT UNIQUE, titel TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'neu', kunde_id TEXT, erstellt TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS aufgaben (
  id INTEGER PRIMARY KEY AUTOINCREMENT, fall_id INTEGER NOT NULL, art TEXT NOT NULL,
  titel TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'offen', erstellt TEXT NOT NULL, erledigt TEXT
);
CREATE TABLE IF NOT EXISTS entwuerfe (
  id INTEGER PRIMARY KEY AUTOINCREMENT, fall_id INTEGER NOT NULL, an TEXT NOT NULL,
  betreff TEXT NOT NULL, text TEXT NOT NULL, belege TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'entwurf', von TEXT NOT NULL, erstellt TEXT NOT NULL, geaendert TEXT NOT NULL,
  stufe TEXT, stufe_gruende TEXT NOT NULL DEFAULT '[]', rechtsaussage INTEGER NOT NULL DEFAULT 0,
  sende_am TEXT, freigabe_von TEXT, freigabe_zeit TEXT, ablehnung TEXT
);
CREATE TABLE IF NOT EXISTS einschaetzungen (
  kunde_id TEXT PRIMARY KEY, ergebnis TEXT NOT NULL, begruendung TEXT NOT NULL, belege TEXT NOT NULL DEFAULT '[]',
  stichtag TEXT, von TEXT NOT NULL, zeit TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS postausgang (
  id INTEGER PRIMARY KEY AUTOINCREMENT, entwurf_id INTEGER NOT NULL UNIQUE, an TEXT NOT NULL,
  betreff TEXT NOT NULL, text TEXT NOT NULL, gesendet TEXT NOT NULL, datei TEXT
);
CREATE TABLE IF NOT EXISTS ereignisse (
  id INTEGER PRIMARY KEY AUTOINCREMENT, zeit TEXT NOT NULL, akteur TEXT NOT NULL, art TEXT NOT NULL,
  fall_id INTEGER, details TEXT NOT NULL DEFAULT '{}'
);
"""


_NEUE_SPALTEN = {
    "entwuerfe": [("stufe", "TEXT"), ("stufe_gruende", "TEXT NOT NULL DEFAULT '[]'"),
                  ("rechtsaussage", "INTEGER NOT NULL DEFAULT 0"), ("sende_am", "TEXT"), ("freigabe_von", "TEXT"),
                  ("freigabe_zeit", "TEXT"), ("ablehnung", "TEXT")],
}
_bereit: set = set()


def _vorbereiten(conn: sqlite3.Connection) -> None:
    """Tabellen anlegen und Spalten ergänzen, falls der lokale Stand älter ist."""
    conn.executescript(SCHEMA)
    for tabelle, spalten in _NEUE_SPALTEN.items():
        vorhanden = {r["name"] for r in conn.execute("PRAGMA table_info(%s)" % tabelle).fetchall()}
        for name, typ in spalten:
            if name not in vorhanden:
                conn.execute("ALTER TABLE %s ADD COLUMN %s %s" % (tabelle, name, typ))


@contextmanager
def verbindung() -> Iterator[sqlite3.Connection]:
    state_dir().mkdir(parents=True, exist_ok=True)
    pfad = str(db_path())
    conn = sqlite3.connect(pfad, timeout=15, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        if pfad not in _bereit:
            _vorbereiten(conn)
            _bereit.add(pfad)
        yield conn
    finally:
        conn.close()


@contextmanager
def transaktion() -> Iterator[sqlite3.Connection]:
    with verbindung() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            yield conn
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        else:
            conn.execute("COMMIT")


def zeilen(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def zeile(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    r = conn.execute(sql, params).fetchone()
    return dict(r) if r else None


def ereignis(conn: sqlite3.Connection, akteur: str, art: str, fall_id: Optional[int] = None,
             details: Optional[Dict[str, Any]] = None) -> None:
    """Protokolleintrag. akteur: mensch | claude | system."""
    conn.execute(
        "INSERT INTO ereignisse (zeit, akteur, art, fall_id, details) VALUES (?, ?, ?, ?, ?)",
        (jetzt(conn), akteur, art, fall_id, dumps(details or {})),
    )


def zustand_lesen(conn: sqlite3.Connection, schluessel: str, default: Optional[str] = None) -> Optional[str]:
    r = conn.execute("SELECT wert FROM zustand WHERE schluessel = ?", (schluessel,)).fetchone()
    return r["wert"] if r else default


def zustand_setzen(conn: sqlite3.Connection, schluessel: str, wert: str) -> None:
    conn.execute(
        "INSERT INTO zustand (schluessel, wert) VALUES (?, ?) "
        "ON CONFLICT(schluessel) DO UPDATE SET wert = excluded.wert",
        (schluessel, wert),
    )


def entpacken(row: Optional[Dict[str, Any]], *json_felder: str) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    for f in json_felder:
        row[f] = loads(row.get(f), [] if f != "details" else {})
    return row
