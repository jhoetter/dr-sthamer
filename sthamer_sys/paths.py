"""Pfade und Konsolen-Einstellungen. Nur Standardbibliothek, Python >= 3.9."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

PKG_DIR = Path(__file__).resolve().parent
ROOT = PKG_DIR.parent


def worktree_hauptordner(root: Optional[Path] = None) -> Optional[Path]:
    """Ist dieser Ordner eine zusätzliche Git-Arbeitskopie (Worktree), gibt das den Hauptordner zurück, sonst None.

    Die Claude-App kann eine Sitzung in `<Ordner>/.claude/worktrees/<name>` starten. Dort hätte die Kommandozentrale
    eine eigene Datenbank, und Bauaufträge landeten in einer Kopie, die das Cockpit nicht lädt. Deshalb erkennen wir das.
    """
    root = Path(root or ROOT)
    git = root / ".git"
    try:
        if not git.is_file():
            return None  # Hauptordner (.git ist ein Ordner) oder ZIP-Betrieb (kein .git)
        inhalt = git.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return None
    if not inhalt.startswith("gitdir:"):
        return None
    gitdir = Path(inhalt[len("gitdir:"):].strip())
    if not gitdir.is_absolute():
        gitdir = (root / gitdir).resolve()
    # <Hauptordner>/.git/worktrees/<name>
    if gitdir.parent.name == "worktrees" and gitdir.parent.parent.name == ".git":
        return gitdir.parent.parent.parent
    return None


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
