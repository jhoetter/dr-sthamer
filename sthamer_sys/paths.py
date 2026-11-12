"""Pfade und Konsolen-Einstellungen. Nur Standardbibliothek, Python >= 3.9."""
from __future__ import annotations

import os
import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
ROOT = PKG_DIR.parent


def data_dir() -> Path:
    """Stammdaten (schreibgeschützt für App und Claude)."""
    return Path(os.environ.get("STHAMER_DATA_DIR") or ROOT / "data")


def state_dir() -> Path:
    """Lokaler Zustand (SQLite, Port-Datei); Git-ignoriert."""
    return Path(os.environ.get("STHAMER_STATE_DIR") or ROOT / ".data")


def outbox_dir() -> Path:
    """Postausgang: hier landen „gesendete“ Mails als Dateien; nichts verlässt das Gerät."""
    return Path(os.environ.get("STHAMER_OUTBOX_DIR") or ROOT / "postausgang")


def web_dir() -> Path:
    return ROOT / "web"


def db_path() -> Path:
    return state_dir() / "sthamer.db"


def ensure_utf8_stdio() -> None:
    """Windows-Konsolen nutzen oft cp1252; Umlaute dürfen nie zum Absturz führen."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass
