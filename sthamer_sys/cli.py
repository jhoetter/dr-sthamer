"""Kommandozeile: python sthamer.py <befehl>. Absichtlich ohne Senden/Freigeben."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from typing import List, Optional

from . import DEFAULT_PORT, SERVICE, __version__, domain
from .paths import ROOT, ensure_utf8_stdio, outbox_dir, state_dir


def bereit_machen() -> None:
    """Datenbank anlegen und die erste Runde Nachrichten abrufen (idempotent)."""
    domain.welle_freischalten(1, akteur="system")


def mcp_konfiguration() -> dict:
    """.mcp.json mit ABSOLUTEM Python-Pfad (umgeht `python3` = Store-Platzhalter unter Windows)."""
    return {"mcpServers": {"sthamer": {
        "command": sys.executable,
        "args": [str(ROOT / "sthamer.py"), "mcp"],
    }}}


def _git(*args: str):
    try:
        return subprocess.run(["git"] + list(args), cwd=str(ROOT), capture_output=True, timeout=60,
                              encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None


def git_vorbereiten() -> List[str]:
    """Speichern des Stands muss auf einem frischen Gastprofil klappen.

    Gastprofile haben oft keine Git-Identität („Author identity unknown“), und im ZIP-Betrieb gibt es keinen Git-Ordner.
    Beides wird hier vorbereitet, nur lokal in diesem Ordner, nie global. Ein Fehler hier bricht das Einrichten nie ab.
    """
    r = _git("--version")
    if r is None or r.returncode != 0:
        return ["Git wurde nicht gefunden: Der Stand lässt sich später nicht speichern."]
    meldungen: List[str] = []
    neu = not (ROOT / ".git").exists()
    if neu:
        r = _git("init", "-q")
        if r is None or r.returncode != 0:
            return ["Git-Ordner konnte nicht angelegt werden."]
        meldungen.append("Git-Ordner angelegt (ZIP-Betrieb).")
    for key, wert in (("user.name", "Workshop-Teilnehmer"), ("user.email", "teilnehmer@workshop.invalid")):
        r = _git("config", key)
        if not (r and r.returncode == 0 and r.stdout.strip()):
            _git("config", "--local", key, wert)
            meldungen.append("Git-%s lokal gesetzt." % ("Name" if key == "user.name" else "Adresse"))
    if neu:
        _git("add", "-A")
        r = _git("commit", "-q", "-m", "Ausgangsstand")
        if r is not None and r.returncode == 0:
            meldungen.append("Ausgangsstand gespeichert.")
    return meldungen


def cmd_setup(args: argparse.Namespace) -> int:
    state_dir().mkdir(parents=True, exist_ok=True)
    bereit_machen()
    ziel = ROOT / ".mcp.json"
    with open(str(ziel), "w", encoding="utf-8", newline="\n") as f:
        json.dump(mcp_konfiguration(), f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(str(state_dir() / "python.txt"), "w", encoding="utf-8") as f:
        f.write(sys.executable + "\n")
    try:
        git_meldungen = git_vorbereiten()
    except Exception as e:  # nie abbrechen
        git_meldungen = ["Git konnte nicht vorbereitet werden: %r" % (e,)]
    print("Einrichtung fertig.")
    print("  Datenbank:        %s" % (state_dir() / "sthamer.db"))
    print("  Claude-Verbindung: %s (Python: %s)" % (ziel.name, sys.executable))
    for m in git_meldungen:
        print("  Git:              %s" % m)
    print("  Nächster Schritt: python sthamer.py serve --open")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .app import starten
    bereit_machen()
    return starten(args.port, args.open)


def cmd_mcp(args: argparse.Namespace) -> int:
    from .mcp_server import lauf
    bereit_machen()
    return lauf()


def cmd_status(args: argparse.Namespace) -> int:
    bereit_machen()
    s = domain.status()
    print("%s %s" % (SERVICE, __version__))
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


def cmd_welle(args: argparse.Namespace) -> int:
    # Läuft nur mit STHAMER_MENSCH=1 (Lehrende, Tests). Teilnehmende rufen Runden im Cockpit ab.
    try:
        r = domain.welle_freischalten(args.welle, args.code, akteur="mensch")
    except domain.FachFehler as e:
        print("Fehler: %s" % e, file=sys.stderr)
        return 1
    print("Runde %d abgerufen: %d neue Nachricht(en)." % (r["welle"], r["neue_nachrichten"]))
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    if not args.yes:
        print("Das löscht deinen lokalen Stand (Fälle, Entwürfe, Postausgang). Mit --yes bestätigen.")
        return 1
    for ziel in (state_dir(), outbox_dir()):
        # nur die beiden bekannten Ordner, nie etwas anderes
        if ziel.exists() and ziel.name in (".data", "postausgang"):
            shutil.rmtree(str(ziel))
    bereit_machen()
    print("Zurückgesetzt. Runde 1 ist wieder abgerufen.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ensure_utf8_stdio()
    p = argparse.ArgumentParser(prog="python sthamer.py", description="sthamer-sys: Regulatorik-Werkstatt (fiktive Daten)")
    sub = p.add_subparsers(dest="befehl", required=True)
    sub.add_parser("setup", help="einrichten (Datenbank, Claude-Verbindung)").set_defaults(fn=cmd_setup)
    s = sub.add_parser("serve", help="Kommandozentrale im Browser starten")
    s.add_argument("--port", type=int, default=DEFAULT_PORT)
    s.add_argument("--open", action="store_true", help="Browser öffnen")
    s.set_defaults(fn=cmd_serve)
    sub.add_parser("mcp", help="MCP-Server über stdio (von Claude gestartet)").set_defaults(fn=cmd_mcp)
    sub.add_parser("status", help="Stand anzeigen").set_defaults(fn=cmd_status)
    w = sub.add_parser("welle", help="nächste Runde Nachrichten abrufen (Code vom Dozenten)")
    w.add_argument("welle", type=int)
    w.add_argument("--code", default="")
    w.set_defaults(fn=cmd_welle)
    r = sub.add_parser("reset", help="lokalen Stand zurücksetzen")
    r.add_argument("--yes", action="store_true")
    r.set_defaults(fn=cmd_reset)
    args = p.parse_args(argv)
    return int(args.fn(args) or 0)
