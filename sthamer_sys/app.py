"""Cockpit-Server: nur 127.0.0.1, nur Standardbibliothek.

Schutz gegen versehentliche Fremdzugriffe: Host-Prüfung (gegen DNS-Rebinding),
Token für alle Aktionen des Menschen (Senden usw.) und Content-Type-Prüfung.
Das ist eine Kontrolle für den Workshop, kein Ersatz für getrennte Rechte in
einem echten System.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.error import URLError
from urllib.request import urlopen

from . import DEFAULT_PORT, SERVICE, daten, domain
from .paths import ROOT, state_dir, web_dir

MAX_BODY = 1_000_000
TYPEN = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
         ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png"}


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != "nt"  # unter Windows würde das doppeltes Binden erlauben

    def __init__(self, adresse: Tuple[str, int]):
        super().__init__(adresse, Handler)
        self.token = secrets.token_urlsafe(16)
        self.port = adresse[1]


class Handler(BaseHTTPRequestHandler):
    server_version = SERVICE
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:  # ruhig; Fehler gehen nach stderr
        pass

    # ------------------------------------------------------------ Hilfen
    def _senden(self, status: int, body: bytes, typ: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj: Any, status: int = 200) -> None:
        self._senden(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _fehler(self, status: int, text: str) -> None:
        self._json({"fehler": text}, status)

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return host in ("127.0.0.1", "localhost")

    def _origin_ok(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        port = self.server.server_address[1]
        return origin in ("http://127.0.0.1:%d" % port, "http://localhost:%d" % port)

    # ------------------------------------------------------------ GET
    def do_GET(self) -> None:  # noqa: N802
        if not self._host_ok():
            return self._fehler(403, "Host nicht erlaubt.")
        pfad = self.path.split("?", 1)[0]
        try:
            if pfad.startswith("/api/"):
                return self._get_api(pfad[5:])
            return self._statisch(pfad)
        except domain.FachFehler as e:
            self._fehler(400, str(e))
        except FileNotFoundError as e:
            self._fehler(404, str(e))
        except Exception as e:
            sys.stderr.write("Fehler bei %s: %r\n" % (pfad, e))
            self._fehler(500, "Interner Fehler (siehe Konsole).")

    def _statisch(self, pfad: str) -> None:
        name = "index.html" if pfad in ("/", "") else pfad.lstrip("/")
        datei = (web_dir() / name).resolve()
        if web_dir().resolve() not in datei.parents or not datei.is_file() or datei.suffix not in TYPEN:
            return self._fehler(404, "Nicht gefunden.")
        body = datei.read_bytes()
        if name == "index.html":
            body = body.replace(b"{{TOKEN}}", self.server.token.encode("ascii"))  # type: ignore[attr-defined]
        self._senden(200, body, TYPEN[datei.suffix])

    def _get_api(self, route: str) -> None:
        teile = route.strip("/").split("/")
        k = teile[0]
        arg = teile[1] if len(teile) > 1 else None
        if k == "health":
            return self._json({"ok": True, "service": SERVICE, "root": str(ROOT), "pid": os.getpid()})
        if k == "status":
            return self._json(domain.status())
        if k == "nachrichten":
            return self._json(domain.eingang())
        if k == "nachricht" and arg:
            return self._json(domain.nachricht(arg))
        if k == "faelle":
            return self._json(domain.faelle())
        if k == "fall" and arg and arg.isdigit():
            return self._json(domain.fall(int(arg)))
        if k == "entwuerfe":
            return self._json(domain.entwuerfe())
        if k == "regelwerk":
            rw = domain.regelwerk_sichtbar()
            return self._json({"regelwerk": rw["regelwerk"], "verfuegbar": rw["verfuegbar"], "haupttext": rw["haupttext"],
                               "texte": {n: daten.verordnung_text(n) for n in rw["verfuegbar"]}})
        if k == "produkte":
            return self._json(domain.produkte_liste())
        if k == "produkt" and arg:
            return self._json(domain.produkt_detail(arg))
        if k == "kunden":
            return self._json(domain.kunden_liste())
        if k == "kunde" and arg:
            return self._json(domain.kunde_detail(arg))
        if k == "einschaetzungen":
            return self._json(domain.einschaetzungen())
        if k == "bericht":
            if not domain.faehigkeiten()["bericht"]:
                raise domain.FachFehler("Der Bericht ist erst ab Drill 5 freigeschaltet.")
            datei = ROOT / "bericht.md"
            text = datei.read_text(encoding="utf-8") if datei.is_file() else None
            return self._json({"zahlen": domain.bericht(), "text": text})
        if k == "postausgang":
            return self._json(domain.postausgang())
        if k == "protokoll":
            return self._json(domain.protokoll())
        self._fehler(404, "Unbekannte Adresse.")

    # ------------------------------------------------------------ POST (Aktionen des Menschen)
    def do_POST(self) -> None:  # noqa: N802
        if not self._host_ok() or not self._origin_ok():
            return self._fehler(403, "Nicht erlaubt.")
        if not secrets.compare_digest(self.headers.get("X-Sthamer-Token") or "", self.server.token):  # type: ignore[attr-defined]
            return self._fehler(403, "Aktion nur über das Cockpit im Browser möglich.")
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            return self._fehler(415, "JSON erwartet.")
        try:
            laenge = int(self.headers.get("Content-Length") or 0)
            if laenge > MAX_BODY:
                return self._fehler(413, "Zu groß.")
            roh = self.rfile.read(laenge) if laenge else b"{}"
            body = json.loads(roh.decode("utf-8") or "{}")
            if not isinstance(body, dict):
                return self._fehler(400, "Objekt erwartet.")
            return self._json(self._post_api(self.path.split("?", 1)[0], body))
        except domain.FachFehler as e:
            self._fehler(400, str(e))
        except (ValueError, KeyError) as e:
            self._fehler(400, "Ungültige Eingabe: %s" % e)
        except Exception as e:
            sys.stderr.write("Fehler bei POST %s: %r\n" % (self.path, e))
            self._fehler(500, "Interner Fehler (siehe Konsole).")

    def _post_api(self, pfad: str, body: Dict[str, Any]) -> Any:
        m = re.fullmatch(r"/api/(welle|fall|notiz|entwurf|senden|freigeben|ablehnen|stoppen|uhr)(?:/(\d+))?", pfad)
        if not m:
            raise domain.FachFehler("Unbekannte Aktion.")
        art, nr = m.group(1), m.group(2)
        if art == "welle":
            return domain.welle_freischalten(int(body["welle"]), str(body.get("code", "")), akteur="mensch")
        if art == "fall":
            return domain.fall_anlegen(str(body["nachricht_id"]), akteur="mensch")
        if art == "notiz":
            return domain.notiz(int(body["fall_id"]), body.get("text"), akteur="mensch")
        if art == "entwurf" and nr:
            return domain.entwurf_aendern(int(nr), body, akteur="mensch")
        if art == "senden" and nr:
            return domain.senden(int(nr), akteur="mensch")
        if art == "freigeben" and nr:
            return domain.freigeben(int(nr), akteur="mensch")
        if art == "ablehnen" and nr:
            return domain.ablehnen(int(nr), body.get("grund"), akteur="mensch")
        if art == "stoppen" and nr:
            return domain.stoppen(int(nr), akteur="mensch")
        if art == "uhr":
            return domain.uhr_vorspulen(body.get("stunden"), akteur="mensch")
        raise domain.FachFehler("Unbekannte Aktion.")


# ---------------------------------------------------------------- Start

def laeuft_schon(port: int) -> Optional[Dict[str, Any]]:
    try:
        with urlopen("http://127.0.0.1:%d/api/health" % port, timeout=1.5) as r:
            info = json.loads(r.read().decode("utf-8"))
        return info if info.get("service") == SERVICE else None
    except (URLError, OSError, ValueError):
        return None


def _gleiche_kopie(root: str) -> bool:
    try:
        return bool(root) and os.path.exists(root) and os.path.samefile(root, str(ROOT))
    except OSError:
        return False


def _worker() -> None:
    """Prüft alle 5 Sekunden, ob eine eingeplante Mail nach Übungsuhr fällig ist (nur dieser Prozess sendet)."""
    import time
    while True:
        try:
            domain.faellige_senden()
        except Exception as e:  # nie abbrechen
            sys.stderr.write("Worker-Fehler: %r\n" % (e,))
        time.sleep(5)


def starten(port: int = DEFAULT_PORT, oeffnen: bool = False) -> int:
    """Cockpit starten. Läuft diese Kopie schon, wird sie nur geöffnet."""
    for p in range(port, port + 20):
        info = laeuft_schon(p)
        if info and _gleiche_kopie(info.get("root", "")):
            print("Die Kommandozentrale läuft schon: http://127.0.0.1:%d" % p)
            if oeffnen:
                webbrowser.open("http://127.0.0.1:%d" % p)
            return 0
    server = None
    for p in range(port, port + 20):
        try:
            server = Server(("127.0.0.1", p))
            break
        except OSError:
            continue
    if server is None:
        print("Kein freier Port zwischen %d und %d gefunden." % (port, port + 19), file=sys.stderr)
        return 1
    url = "http://127.0.0.1:%d" % server.port
    state_dir().mkdir(parents=True, exist_ok=True)
    threading.Thread(target=_worker, daemon=True).start()
    with open(str(state_dir() / "server.json"), "w", encoding="utf-8") as f:
        json.dump({"port": server.port, "pid": os.getpid(), "url": url}, f)
    print("Kommandozentrale läuft: %s  (beenden mit Strg+C)" % url, flush=True)
    if oeffnen:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        server.server_close()
    return 0
