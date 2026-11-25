"""Kommandozeile: python sthamer.py <befehl>. Absichtlich ohne Senden/Freigeben."""
from __future__ import annotations

import argparse
import json
import os
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


WORKTREE_MELDUNG = (
    "STOPP: Diese Sitzung läuft in einer Nebenkopie (Git-Worktree) unter %s, nicht im Ordner %s.\n"
    "Hier würde eine zweite Kommandozentrale mit eigenem Stand entstehen, und deine Bauaufträge kämen nicht an.\n"
    "Bitte eine neue Code-Sitzung im Ordner %s öffnen und dabei vor der ersten Nachricht den Schalter\n"
    "\"Worktree\" unter dem Eingabefeld ausschalten.\n"
    "Nichts wurde eingerichtet oder gestartet."
)


def _worktree_stopp() -> bool:
    """True (und Meldung), wenn wir in einem Worktree laufen: dann nichts einrichten und nichts starten."""
    from .paths import worktree_hauptordner
    haupt = worktree_hauptordner()
    if haupt is None or os.environ.get("STHAMER_WORKTREE_ERLAUBT") == "1":
        return False
    print(WORKTREE_MELDUNG % (ROOT, haupt.name, haupt), file=sys.stderr)
    return True


def cmd_setup(args: argparse.Namespace) -> int:
    if _worktree_stopp():
        return 3
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
    print("  Nächster Schritt: python sthamer.py start")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    if _worktree_stopp():
        return 3
    from .app import starten
    bereit_machen()
    return starten(args.port, args.open)


def _server_info(port: int):
    """Läuft diese Kopie schon? Gibt (Port, URL) zurück, sonst None."""
    import json
    from .app import _gleiche_kopie, laeuft_schon
    kandidaten = []
    try:
        with open(str(state_dir() / "server.json"), "r", encoding="utf-8") as f:
            kandidaten.append(int(json.load(f).get("port")))
    except (OSError, ValueError, TypeError):
        pass
    if port not in kandidaten:
        kandidaten.append(port)
    for p in kandidaten:
        info = laeuft_schon(p)
        if info and _gleiche_kopie(info.get("root", "")):
            return p, "http://127.0.0.1:%d" % p
    return None


def hintergrund_starten(port: int, warten: float = 25.0, browser: bool = True) -> int:
    """Startet die Kommandozentrale losgelöst im Hintergrund und kehrt zurück, sobald sie antwortet.

    Wichtig für den Ein-Satz-Start: Ein Befehl, der nie endet, lässt Claude (und Menschen) hängen. Dieser hier endet nach
    wenigen Sekunden; die Kommandozentrale läuft weiter (Protokoll: .data/server.log). Läuft sie schon, wird sie nur geöffnet.
    """
    import time
    import webbrowser
    bereit = _server_info(port)
    if bereit:
        print("Die Kommandozentrale läuft schon: %s" % bereit[1])
        if browser:
            webbrowser.open(bereit[1])
        return 0
    state_dir().mkdir(parents=True, exist_ok=True)
    logpfad = state_dir() / "server.log"
    log = open(str(logpfad), "ab")
    befehl = [sys.executable, str(ROOT / "sthamer.py"), "serve", "--port", str(port)] + (["--open"] if browser else [])
    optionen = {"cwd": str(ROOT), "stdin": subprocess.DEVNULL, "stdout": log, "stderr": log, "close_fds": True}
    if os.name == "nt":
        optionen["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        optionen["start_new_session"] = True
    try:
        subprocess.Popen(befehl, **optionen)
    except OSError as e:
        print("Die Kommandozentrale ließ sich nicht starten: %s" % e, file=sys.stderr)
        return 1
    finally:
        log.close()
    ende = time.time() + warten
    while time.time() < ende:
        info = _server_info(port)
        if info:
            print("Die Kommandozentrale läuft im Hintergrund: %s" % info[1])
            return 0
        time.sleep(0.5)
    print("Die Kommandozentrale antwortet nicht. Letzte Zeilen des Protokolls (%s):" % logpfad, file=sys.stderr)
    try:
        for zeile in logpfad.read_text(encoding="utf-8", errors="replace").splitlines()[-15:]:
            print("  " + zeile, file=sys.stderr)
    except OSError:
        pass
    return 1


def cmd_start(args: argparse.Namespace) -> int:
    """Alles in einem Befehl: einrichten (idempotent), dann die Kommandozentrale im Hintergrund starten und den Browser öffnen.

    Der Befehl kehrt nach wenigen Sekunden zurück. Mit --vordergrund bleibt er stehen (zum Beobachten der Ausgabe)."""
    rc = cmd_setup(args)
    if rc != 0:
        return rc
    print("Starte die Kommandozentrale ...")
    if getattr(args, "vordergrund", False):
        return cmd_serve(args)
    return hintergrund_starten(args.port, browser=not getattr(args, "kein_browser", False))


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
    # Tabellen leeren statt die Datei zu löschen: so geht es auch bei laufender Kommandozentrale (Windows sperrt offene Dateien)
    from .store import transaktion
    with transaktion() as conn:
        for tabelle in ("ereignisse", "postausgang", "entwuerfe", "einschaetzungen", "aufgaben", "faelle", "nachrichten", "zustand"):
            conn.execute("DELETE FROM %s" % tabelle)
        try:
            conn.execute("DELETE FROM sqlite_sequence")
        except Exception:
            pass
    ordner = outbox_dir()
    if ordner.is_dir() and ordner.name == "postausgang":  # nur der bekannte Ordner, nur Mail-Dateien
        for datei in ordner.glob("*.md"):
            try:
                datei.unlink()
            except OSError:
                pass
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
    st = sub.add_parser("start", help="einrichten und die Kommandozentrale im Browser starten (ein Befehl)")
    st.add_argument("--port", type=int, default=DEFAULT_PORT)
    st.add_argument("--vordergrund", action="store_true", help="nicht im Hintergrund starten (bleibt stehen)")
    st.add_argument("--kein-browser", action="store_true", help="keinen Browser öffnen (z. B. weil die Vorschau der Claude-App öffnet)")
    st.set_defaults(fn=cmd_start, open=True)
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
