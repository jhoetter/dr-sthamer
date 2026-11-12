#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sthamer-Systemcheck: prüft, ob dieses Gerät für den Workshop bereit ist.

Aufruf (im Ordner dr-sthamer):

    python check.py              alles prüfen
    python check.py --netz       nur Internet und Proxy prüfen
    python check.py --offline    ohne Internet prüfen
    python check.py --json       Ergebnis maschinenlesbar ausgeben
    python check.py --decode CODE   Support-Code lesen (für uns Dozenten)

Nur Python-Standardbibliothek, keine Pakete. Der Code unten verwendet
absichtlich keine neue Syntax (keine f-Strings, keine Typangaben), damit auch
eine zu alte Python-Version die deutsche Meldung am Anfang noch erreicht.
"""
import sys

if sys.version_info < (3, 6):
    print("Dieses Programm braucht Python 3.9 oder neuer. Hier läuft Python %d.%d."
          % (sys.version_info[0], sys.version_info[1]))
    print("Bitte Python 3 installieren (siehe docs/INSTALL_WINDOWS.md oder docs/INSTALL_MAC.md)")
    print("und mit 'python3 check.py' bzw. 'py check.py' erneut starten.")
    sys.exit(1)

import argparse
import concurrent.futures
import io
import json
import os
import platform
import re
import shutil
import socket
import ssl
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request

try:
    import queue
except ImportError:  # pragma: no cover
    import Queue as queue

MIN_PYTHON = (3, 9)
PORT = 3005
SERVICE_NAME = "sthamer-sys"
NET_TIMEOUT = 5

OK = "ok"
WARN = "warn"
FAIL = "fail"
SKIP = "skip"

# Feste Reihenfolge: Der Support-Code hat je Prüfung ein Zeichen.
CHECK_IDS = [
    "python", "os", "git", "git-repo", "pfad", "schreiben", "sqlite", "utf8",
    "port", "proxy",
    "net-github", "net-claude", "net-anthropic-api", "net-python", "net-git",
    "mcp-json", "mcp",
]
NET_IDS = [i for i in CHECK_IDS if i.startswith("net-")]

# (id, Host, Status bei Fehler)
NET_HOSTS = [
    ("net-github", "github.com", WARN),
    ("net-claude", "claude.ai", FAIL),
    ("net-anthropic-api", "api.anthropic.com", FAIL),
    ("net-python", "www.python.org", WARN),
    ("net-git", "git-scm.com", WARN),
]

TITEL = {
    "python": "Python", "os": "Betriebssystem", "git": "Git", "git-repo": "Git-Ordner",
    "pfad": "Ordner", "schreiben": "Schreibrechte", "sqlite": "Datenbank (SQLite)",
    "utf8": "Umlaute und Zeichensatz", "port": "Lokaler Server (Port %d)" % PORT,
    "proxy": "Proxy", "mcp-json": "Verbindung zu Claude (.mcp.json)",
    "mcp": "Werkzeuge für Claude (MCP)",
}
for _i, _h, _s in NET_HOSTS:
    TITEL[_i] = "Internet: %s" % _h

STATUS_ZEICHEN = {OK: "+", WARN: "~", FAIL: "X", SKIP: "."}
ZEICHEN_STATUS = dict((v, k) for k, v in STATUS_ZEICHEN.items())


class Ergebnis(object):
    """Ergebnis einer einzelnen Prüfung."""

    def __init__(self, id, status, titel, detail="", hinweis=""):
        self.id = id
        self.status = status
        self.titel = titel
        self.detail = detail
        self.hinweis = hinweis

    def as_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "titel": self.titel,
            "detail": self.detail,
            "hinweis": self.hinweis,
        }


def uebersprungen(id, titel, grund="übersprungen"):
    return Ergebnis(id, SKIP, titel, grund)


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------

def sichere_ausgabe(stream):
    """Sorgt dafür, dass nicht darstellbare Zeichen nie zum Absturz führen.

    Windows-Konsolen nutzen oft cp1252 oder cp850. Umlaute gehen dort, andere
    Zeichen würden sonst einen UnicodeEncodeError auslösen.
    """
    try:
        stream.reconfigure(errors="replace")
        return stream
    except Exception:
        pass
    puffer = getattr(stream, "buffer", None)
    if puffer is not None:
        try:
            return io.TextIOWrapper(
                puffer,
                encoding=getattr(stream, "encoding", None) or "ascii",
                errors="replace",
                line_buffering=True,
            )
        except Exception:
            pass
    return stream


def _aktiviere_windows_ansi():
    try:
        import ctypes
        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)
        modus = ctypes.c_uint32()
        if not kernel.GetConsoleMode(handle, ctypes.byref(modus)):
            return False
        return bool(kernel.SetConsoleMode(handle, modus.value | 0x0004))
    except Exception:
        return False


def farben_moeglich(stream, env=None, nt=None):
    env = os.environ if env is None else env
    if env.get("NO_COLOR"):
        return False
    try:
        if not stream.isatty():
            return False
    except Exception:
        return False
    if (os.name == "nt") if nt is None else nt:
        return _aktiviere_windows_ansi()
    return env.get("TERM", "") != "dumb"


# ---------------------------------------------------------------------------
# Einzelne Prüfungen (Abhängigkeiten sind injizierbar, damit sie testbar sind)
# ---------------------------------------------------------------------------

def windows_store_platzhalter(plattform, executable, which, getsize):
    """True, wenn 'python3' vermutlich nur der Microsoft-Store-Platzhalter ist."""
    if plattform != "win32":
        return False
    if "pythonsoftwarefoundation" in (executable or "").lower():
        return False  # echtes Store-Python läuft: der Alias ist dann in Ordnung
    pfad = which("python3")
    if not pfad or "windowsapps" not in pfad.lower():
        return False
    try:
        return getsize(pfad) == 0
    except OSError:
        return True


def pruefe_python(version_info=None, executable=None, plattform=None,
                  which=None, getsize=None):
    titel = "Python"
    vi = version_info or sys.version_info
    version = "%d.%d.%d" % (vi[0], vi[1], vi[2])
    if (vi[0], vi[1]) < MIN_PYTHON:
        return Ergebnis(
            "python", FAIL, titel, "Python %s ist zu alt (nötig: 3.9 oder neuer)." % version,
            "Installiere Python 3.12 (siehe Installationsanleitung) und starte danach "
            "den Check mit 'python check.py' bzw. 'py check.py' erneut.")
    stub = windows_store_platzhalter(
        plattform or sys.platform, executable or sys.executable,
        which or shutil.which, getsize or os.path.getsize)
    if stub:
        return Ergebnis(
            "python", WARN, titel,
            "Python %s läuft. Aber: 'python3' zeigt auf den Microsoft-Store-Platzhalter." % version,
            "Wenn 'python3' den Microsoft Store öffnet: schließe den Store und benutze "
            "'python' oder 'py' statt 'python3'.")
    return Ergebnis("python", OK, titel, "Python %s" % version)


def windows_name(system, release, version):
    if system != "Windows":
        return None
    try:
        bau = int(str(version).split(".")[2])
    except Exception:
        bau = 0
    if bau >= 22000:
        return "Windows 11"
    return "Windows %s" % (release or "?")


def os_kurz(system, release, version):
    """Kurzname für den Support-Code, ohne persönliche Angaben."""
    if system == "Windows":
        return "W11" if windows_name(system, release, version) == "Windows 11" else "W" + re.sub(r"\W", "", str(release))[:3]
    if system == "Darwin":
        return "MAC"
    if system == "Linux":
        return "LIN"
    return "OS"


def pruefe_os(system=None, release=None, version=None, maschine=None):
    system = system or platform.system()
    release = release if release is not None else platform.release()
    version = version if version is not None else platform.version()
    maschine = maschine or platform.machine()
    if system == "Windows":
        name = windows_name(system, release, version)
        if str(release) in ("7", "8", "8.1", "Vista", "XP"):
            return Ergebnis("os", WARN, "Betriebssystem", "%s (%s)" % (name, maschine),
                            "Dieses Windows ist sehr alt. Sag uns bitte vor dem Workshop Bescheid.")
        return Ergebnis("os", OK, "Betriebssystem", "%s (%s)" % (name, maschine))
    if system == "Darwin":
        return Ergebnis("os", OK, "Betriebssystem", "macOS %s (%s)" % (platform.mac_ver()[0] or release, maschine))
    return Ergebnis("os", OK, "Betriebssystem", "%s %s (%s)" % (system, release, maschine))


def pruefe_git(which=None, run=None):
    titel = "Git"
    which = which or shutil.which
    run = run or subprocess.run
    pfad = which("git")
    if not pfad:
        return Ergebnis(
            "git", WARN, titel, "Git wurde nicht gefunden.",
            "Ohne Git geht der ZIP-Weg. Die Claude-App braucht auf Windows aber meist Git: "
            "installiere Git (Anleitung) und öffne danach ein NEUES Terminal.")
    try:
        antwort = run([pfad, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      timeout=15, universal_newlines=True)
        text = (antwort.stdout or "").strip()
    except Exception as fehler:
        return Ergebnis("git", WARN, titel, "Git ist da, lässt sich aber nicht starten (%s)." % type(fehler).__name__,
                        "Auf dem Mac: Falls ein Fenster 'Befehlszeilentools' erscheint, bestätige die Installation.")
    if antwort.returncode != 0:
        return Ergebnis("git", WARN, titel, "Git meldet einen Fehler.",
                        "Auf dem Mac: Falls ein Fenster 'Befehlszeilentools' erscheint, bestätige die Installation.")
    return Ergebnis("git", OK, titel, text or "Git vorhanden")


def pruefe_git_repo(repo):
    if os.path.exists(os.path.join(repo, ".git")):
        return Ergebnis("git-repo", OK, "Git-Ordner", "Dieser Ordner ist ein geklontes Git-Repo.")
    return Ergebnis("git-repo", OK, "Git-Ordner",
                    "Kein Git-Repo (ZIP-Betrieb). Das ist erlaubt; Updates holen wir dann als neues ZIP.")


def pfad_probleme(repo, env=None, home=None, plattform=None):
    """Gibt eine Liste von Hinweisen zum Ordnerpfad zurück (ohne den Pfad selbst)."""
    env = os.environ if env is None else env
    home = home if home is not None else os.path.expanduser("~")
    plattform = plattform or sys.platform
    probleme = []
    klein = repo.lower().replace("\\", "/")
    onedrive_wurzeln = [env.get(k) for k in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer") if env.get(k)]
    in_onedrive = "onedrive" in klein
    for wurzel in onedrive_wurzeln:
        if klein.startswith(wurzel.lower().replace("\\", "/")):
            in_onedrive = True
    if in_onedrive:
        probleme.append("Der Ordner liegt in OneDrive. Das stört Git und Python (Dateien werden umgeleitet oder gesperrt).")
    rest = klein
    home_klein = home.lower().replace("\\", "/")
    if home_klein and klein.startswith(home_klein):
        rest = klein[len(home_klein):].lstrip("/")
    erste = rest.split("/")[0] if rest else ""
    if erste in ("desktop", "schreibtisch", "documents", "dokumente", "downloads"):
        probleme.append("Der Ordner liegt direkt in Schreibtisch, Dokumente oder Downloads. Diese Ordner werden oft umgeleitet.")
    if " " in repo:
        probleme.append("Der Pfad enthält ein Leerzeichen. Das geht meist, ist aber eine häufige Fehlerquelle.")
    if any(ord(c) > 127 for c in repo):
        probleme.append("Der Pfad enthält Sonderzeichen (z. B. Umlaute). Das geht meist, ist aber eine mögliche Fehlerquelle.")
    if plattform == "win32" and len(repo) > 120:
        probleme.append("Der Pfad ist sehr lang. Windows kann damit Probleme bekommen.")
    return probleme


def pruefe_pfad(repo, env=None, home=None, plattform=None):
    probleme = pfad_probleme(repo, env, home, plattform)
    if not probleme:
        return Ergebnis("pfad", OK, "Ordner", "Der Ordner liegt an einem guten Platz.")
    return Ergebnis(
        "pfad", WARN, "Ordner", " ".join(probleme),
        "Am besten liegt der Ordner direkt im Benutzerordner, z. B. C:\\Users\\<du>\\dr-sthamer "
        "(Mac: ~/dr-sthamer), nicht in OneDrive und nicht auf dem Schreibtisch.")


def pruefe_schreiben(repo):
    titel = "Schreibrechte"
    data = os.path.join(repo, ".data")
    angelegt = False
    try:
        if not os.path.isdir(data):
            os.makedirs(data)
            angelegt = True
        for ordner in (repo, data):
            datei = os.path.join(ordner, ".check-schreibtest-%d" % os.getpid())
            with open(datei, "w", encoding="utf-8") as f:
                f.write("test")
            os.remove(datei)
    except Exception as fehler:
        return Ergebnis("schreiben", FAIL, titel, "In diesem Ordner kann nicht geschrieben werden (%s)." % type(fehler).__name__,
                        "Klone oder entpacke das Repo in deinen Benutzerordner (nicht in einen geschützten Ordner wie C:\\Programme).")
    finally:
        if angelegt:
            try:
                os.rmdir(data)
            except OSError:
                pass
    return Ergebnis("schreiben", OK, titel, "Im Ordner und in .data kann geschrieben werden.")


def pruefe_sqlite(importer=None):
    titel = "Datenbank (SQLite)"
    try:
        sqlite3 = (importer or __import__)("sqlite3")
        verbindung = sqlite3.connect(":memory:")
        version = verbindung.execute("select sqlite_version()").fetchone()[0]
        verbindung.close()
    except Exception as fehler:
        return Ergebnis("sqlite", FAIL, titel, "Das SQLite-Modul von Python fehlt oder läuft nicht (%s)." % type(fehler).__name__,
                        "Installiere Python neu von python.org (nicht die abgespeckte Variante).")
    return Ergebnis("sqlite", OK, titel, "SQLite %s" % version)


def pruefe_utf8(tmp_ordner=None, stdout_encoding=None, preferred=None, utf8_modus=None):
    titel = "Umlaute und Zeichensatz"
    text = u"Prüfung äöüß Ä Ö Ü – µg/l ≥ 1,0 €\n"
    try:
        ordner = tmp_ordner or tempfile.mkdtemp(prefix="sthamer-check-")
        eigener = tmp_ordner is None
        try:
            pfad = os.path.join(ordner, "umlaute.txt")
            with open(pfad, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            with open(pfad, "r", encoding="utf-8") as f:
                zurueck = f.read()
        finally:
            if eigener:
                shutil.rmtree(ordner, ignore_errors=True)
    except Exception as fehler:
        return Ergebnis("utf8", FAIL, titel, "Eine Datei mit Umlauten lässt sich nicht schreiben und lesen (%s)." % type(fehler).__name__,
                        "Prüfe, ob der temporäre Ordner beschreibbar ist.")
    if zurueck != text:
        return Ergebnis("utf8", FAIL, titel, "Umlaute kommen aus einer Datei verändert zurück.",
                        "Setze die Umgebungsvariable PYTHONUTF8=1 und starte den Check erneut.")
    enc = (stdout_encoding if stdout_encoding is not None else getattr(sys.stdout, "encoding", None)) or "ascii"
    pref = preferred if preferred is not None else _preferred_encoding()
    modus = utf8_modus if utf8_modus is not None else bool(getattr(sys.flags, "utf8_mode", 0))
    try:
        u"äöüßÄÖÜ".encode(enc)
        konsole_ok = True
    except (UnicodeEncodeError, LookupError):
        konsole_ok = False
    if not konsole_ok:
        return Ergebnis("utf8", WARN, titel, "Die Konsole (%s) kann keine Umlaute anzeigen. Die Software selbst nutzt immer UTF-8." % enc,
                        "Starte mit 'set PYTHONUTF8=1' (Windows) oder 'export PYTHONUTF8=1' (Mac), wenn dich das stört.")
    zusatz = ""
    if not modus and pref.lower().replace("-", "") not in ("utf8",):
        zusatz = " Standard-Kodierung des Geräts: %s (unproblematisch, wir nutzen immer UTF-8)." % pref
    return Ergebnis("utf8", OK, titel, "Umlaute werden korrekt gespeichert und gelesen." + zusatz)


def _preferred_encoding():
    try:
        import locale
        return locale.getpreferredencoding(False) or "?"
    except Exception:
        return "?"


def _health_probe(port):
    antwort = urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
        "http://127.0.0.1:%d/api/health" % port, timeout=1.5)
    try:
        return json.loads(antwort.read().decode("utf-8"))
    finally:
        antwort.close()


def _binde(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
    finally:
        s.close()


def pruefe_port(port=PORT, binde=None, health=None):
    titel = "Lokaler Server (Port %d)" % port
    binde = binde or _binde
    health = health or _health_probe
    try:
        binde(0)
    except OSError as fehler:
        return Ergebnis("port", FAIL, titel, "Dieses Gerät erlaubt keinen lokalen Server (%s)." % type(fehler).__name__,
                        "Eine Firewall oder Sicherheitssoftware blockiert lokale Server. Sag der IT bzw. uns Bescheid.")
    try:
        binde(port)
    except OSError:
        try:
            antwort = health(port)
            if isinstance(antwort, dict) and antwort.get("service") == SERVICE_NAME:
                return Ergebnis("port", OK, titel, "Die Kommandozentrale läuft bereits auf diesem Port.")
        except Exception:
            pass
        return Ergebnis("port", WARN, titel, "Port %d ist von einem anderen Programm belegt." % port,
                        "Kein Problem: sthamer-sys sucht sich automatisch einen freien Port.")
    return Ergebnis("port", OK, titel, "Port %d ist frei." % port)


def _proxy_variablen(env):
    namen = []
    for name in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY"):
        if env.get(name) or env.get(name.lower()):
            namen.append(name)
    return namen


def pruefe_proxy(env=None, getproxies=None):
    env = os.environ if env is None else env
    getproxies = getproxies or urllib.request.getproxies
    namen = _proxy_variablen(env)
    try:
        system = sorted(k for k, v in getproxies().items() if v)
    except Exception:
        system = []
    if not namen and not system:
        return Ergebnis("proxy", OK, "Proxy", "Kein Proxy eingestellt.")
    teile = []
    if namen:
        teile.append("Umgebungsvariablen: " + ", ".join(namen))
    if system and not namen:
        teile.append("Systemeinstellung für: " + ", ".join(system))
    return Ergebnis("proxy", WARN, "Proxy", "Ein Proxy ist eingestellt (%s). Werte zeigen wir nicht an." % "; ".join(teile),
                    "Wenn Verbindungen scheitern, sag uns bitte Bescheid: Ein Firmen-Proxy kann Claude oder GitHub bremsen.")


def klassifiziere_netzfehler(fehler, plattform=None):
    """Ordnet einen Netzwerkfehler einer Ursache zu. Gibt (code, Text) zurück."""
    plattform = plattform or sys.platform
    if isinstance(fehler, urllib.error.URLError) and not isinstance(fehler, urllib.error.HTTPError):
        grund = fehler.reason
        if isinstance(grund, BaseException):
            return klassifiziere_netzfehler(grund, plattform)
        return "netz", "Keine Verbindung (%s)." % grund
    if isinstance(fehler, socket.gaierror):
        return "dns", ("Der Name der Seite konnte nicht aufgelöst werden. Bist du mit dem Gäste-WLAN verbunden? "
                       "Manche Gäste-WLANs verlangen zuerst eine Anmeldung im Browser.")
    if isinstance(fehler, socket.timeout) or isinstance(fehler, TimeoutError):
        return "timeout", "Keine Antwort in %d Sekunden. Das WLAN ist langsam oder blockiert diese Seite." % NET_TIMEOUT
    zertifikat = getattr(ssl, "SSLCertVerificationError", ssl.SSLError)
    if isinstance(fehler, (zertifikat, ssl.SSLError)):
        text = ("Das Sicherheitszertifikat wurde nicht akzeptiert. Häufige Ursachen: die Anmeldeseite des Gäste-WLANs "
                "(Captive Portal) oder eine Firmen-Prüfung des Datenverkehrs (TLS-Inspektion/Proxy). "
                "Öffne einen Browser und melde dich im WLAN an.")
        if plattform == "darwin":
            text += " Mac mit Python von python.org: starte einmal 'Install Certificates.command' (siehe INSTALL_MAC.md)."
        return "tls", text
    if isinstance(fehler, ConnectionRefusedError):
        return "abgelehnt", "Die Verbindung wurde abgelehnt. Wahrscheinlich blockiert eine Firewall diese Seite."
    if isinstance(fehler, (ConnectionResetError, ConnectionAbortedError)):
        return "zurueckgesetzt", "Die Verbindung wurde mittendrin getrennt. Meist blockiert eine Firewall oder ein Filter diese Seite."
    if isinstance(fehler, OSError):
        return "netz", "Keine Verbindung (Fehlercode %s)." % (fehler.errno if fehler.errno is not None else "?")
    return "netz", "Unbekannter Netzwerkfehler (%s)." % type(fehler).__name__


def _oeffne_url(url, timeout):
    anfrage = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "sthamer-check/1.0"})
    antwort = urllib.request.urlopen(anfrage, timeout=timeout)
    try:
        return antwort.getcode()
    finally:
        antwort.close()


def pruefe_netz(id, host, schweregrad, oeffnen=None, timeout=NET_TIMEOUT, plattform=None):
    titel = "Internet: %s" % host
    oeffnen = oeffnen or _oeffne_url
    try:
        oeffnen("https://%s/" % host, timeout)
    except urllib.error.HTTPError as antwort:
        if antwort.code == 407:
            return Ergebnis(id, schweregrad, titel, "Ein Proxy verlangt eine Anmeldung (Fehler 407).",
                            "Sag uns bitte Bescheid: Hier ist eine Freigabe durch die IT nötig.")
        return Ergebnis(id, OK, titel, "Erreichbar (Antwort %d)." % antwort.code)
    except Exception as fehler:
        code, text = klassifiziere_netzfehler(fehler, plattform)
        return Ergebnis(id, schweregrad, titel, text,
                        "Wenn es im Browser geht, aber hier nicht: Notiere den Support-Code und sag uns Bescheid.")
    return Ergebnis(id, OK, titel, "Erreichbar.")


def pruefe_netz_alle(oeffnen=None, hosts=None, plattform=None):
    hosts = hosts or NET_HOSTS
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(hosts)) as pool:
        futures = [pool.submit(pruefe_netz, i, h, s, oeffnen, NET_TIMEOUT, plattform) for i, h, s in hosts]
        return [f.result() for f in futures]


def pruefe_mcp_json(repo):
    titel = "Verbindung zu Claude (.mcp.json)"
    pfad = os.path.join(repo, ".mcp.json")
    if not os.path.exists(pfad):
        return Ergebnis("mcp-json", SKIP, titel, "Noch nicht eingerichtet (kommt beim Setup).")
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            daten = json.load(f)
        server = daten.get("mcpServers", {})
        if not server:
            raise ValueError("keine Server")
        fehlend = []
        for name, eintrag in server.items():
            kommando = eintrag.get("command", "")
            if not (os.path.isfile(kommando) or shutil.which(kommando)):
                fehlend.append(name)
    except Exception:
        return Ergebnis("mcp-json", FAIL, titel, "Die Datei .mcp.json ist beschädigt.",
                        "Führe 'python sthamer.py setup' erneut aus.")
    if fehlend:
        return Ergebnis("mcp-json", FAIL, titel, "Der in .mcp.json eingetragene Python-Pfad existiert nicht mehr.",
                        "Führe 'python sthamer.py setup' erneut aus (nach einem Umzug des Ordners oder einem Python-Update nötig).")
    return Ergebnis("mcp-json", OK, titel, "Eintrag vorhanden, Python-Pfad existiert.")


def mcp_handshake(befehl, cwd, timeout=10, popen=None):
    """Startet den MCP-Server, sendet 'initialize' und gibt die Antwort zurück.

    Rückgabe: (antwort_dict_oder_None, fehlertext_oder_None)
    """
    popen = popen or subprocess.Popen
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    try:
        prozess = popen(befehl, cwd=cwd, env=env, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except Exception as fehler:
        return None, "Der Server lässt sich nicht starten (%s)." % type(fehler).__name__
    zeilen = queue.Queue()

    def lesen():
        try:
            for zeile in iter(prozess.stdout.readline, b""):
                zeilen.put(zeile)
        except Exception:
            pass
        zeilen.put(None)

    leser = threading.Thread(target=lesen)
    leser.daemon = True
    leser.start()
    anfrage = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
               "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                          "clientInfo": {"name": "sthamer-check", "version": "1"}}}
    antwort, fehler = None, None
    try:
        prozess.stdin.write((json.dumps(anfrage) + "\n").encode("utf-8"))
        prozess.stdin.flush()
        ende = time.time() + timeout
        while True:
            rest = ende - time.time()
            if rest <= 0:
                fehler = "Keine Antwort in %d Sekunden." % timeout
                break
            try:
                zeile = zeilen.get(timeout=rest)
            except queue.Empty:
                fehler = "Keine Antwort in %d Sekunden." % timeout
                break
            if zeile is None:
                fehler = "Der Server hat sich sofort beendet."
                break
            try:
                nachricht = json.loads(zeile.decode("utf-8"))
            except ValueError:
                continue
            if isinstance(nachricht, dict) and nachricht.get("id") == 1:
                antwort = nachricht
                break
    except Exception as ausnahme:
        fehler = "Fehler bei der Kommunikation (%s)." % type(ausnahme).__name__
    finally:
        try:
            prozess.stdin.close()
        except Exception:
            pass
        try:
            prozess.wait(timeout=3)
        except Exception:
            try:
                prozess.kill()
                prozess.wait(timeout=3)
            except Exception:
                pass
        leser.join(2)
        try:
            prozess.stdout.close()
        except Exception:
            pass
    return antwort, fehler


def pruefe_mcp(repo, python=None, popen=None, timeout=10):
    titel = "Werkzeuge für Claude (MCP)"
    skript = os.path.join(repo, "sthamer.py")
    if not os.path.isfile(skript):
        return uebersprungen("mcp", titel, "sthamer.py ist noch nicht vorhanden.")
    antwort, fehler = mcp_handshake([python or sys.executable, skript, "mcp"], repo, timeout, popen)
    name = None
    if antwort:
        name = ((antwort.get("result") or {}).get("serverInfo") or {}).get("name")
    if name == SERVICE_NAME:
        return Ergebnis("mcp", OK, titel, "Der MCP-Server startet und meldet sich korrekt.")
    ohne_setup = not os.path.exists(os.path.join(repo, ".data", "sthamer.db"))
    detail = fehler or "Die Antwort enthält nicht den erwarteten Namen."
    if ohne_setup:
        return Ergebnis("mcp", WARN, titel, detail + " (Das Setup ist noch nicht gelaufen.)",
                        "Führe zuerst 'python sthamer.py setup' aus und danach den Check erneut.")
    return Ergebnis("mcp", FAIL, titel, detail,
                    "Der Rückfall ist die Kommandozeile ('python sthamer.py status'). Sag uns bitte Bescheid.")


# ---------------------------------------------------------------------------
# Zusammenstellung, Support-Code, Ausgabe
# ---------------------------------------------------------------------------

def sortiere(ergebnisse):
    nach_id = dict((e.id, e) for e in ergebnisse)
    return [nach_id[i] for i in CHECK_IDS if i in nach_id]


def fuehre_aus(repo, netz=True, lokal=True, oeffnen=None, plattform=None):
    """Führt die gewählten Prüfungen aus und gibt die Ergebnisliste in fester Reihenfolge zurück."""
    ergebnisse = []
    if lokal:
        ergebnisse += [
            pruefe_python(), pruefe_os(), pruefe_git(), pruefe_git_repo(repo),
            pruefe_pfad(repo), pruefe_schreiben(repo), pruefe_sqlite(), pruefe_utf8(),
            pruefe_port(),
        ]
    ergebnisse.append(pruefe_proxy())
    if netz:
        ergebnisse += pruefe_netz_alle(oeffnen, plattform=plattform)
    if lokal:
        ergebnisse += [pruefe_mcp_json(repo), pruefe_mcp(repo)]
    gesehen = set(e.id for e in ergebnisse)
    for i in CHECK_IDS:
        if i not in gesehen:
            ergebnisse.append(uebersprungen(i, TITEL.get(i, i)))
    return sortiere(ergebnisse)


def support_code(ergebnisse, system=None, release=None, version=None, version_info=None):
    system = system or platform.system()
    release = release if release is not None else platform.release()
    version = version if version is not None else platform.version()
    vi = version_info or sys.version_info
    nach_id = dict((e.id, e) for e in ergebnisse)
    zeichen = "".join(STATUS_ZEICHEN[nach_id[i].status] if i in nach_id else "." for i in CHECK_IDS)
    kern = "STH-%s-PY%d%d-%s" % (os_kurz(system, release, version), vi[0], vi[1], zeichen)
    return kern + "-" + _pruefsumme(kern)


def _pruefsumme(kern):
    return "%02X" % (sum(ord(c) * (n + 1) for n, c in enumerate(kern)) % 256)


def dekodiere(code):
    """Liest einen Support-Code. Gibt (Kopf, [(id, status)]) zurück oder wirft ValueError."""
    treffer = re.match(r"^(STH-([A-Z0-9]+)-PY(\d+)-([+~X.]+))-([0-9A-F]{2})$", code.strip().upper())
    if not treffer:
        raise ValueError("Das ist kein gültiger Support-Code.")
    if _pruefsumme(treffer.group(1)) != treffer.group(5):
        raise ValueError("Die Prüfsumme stimmt nicht. Hat sich ein Zeichen eingeschlichen?")
    zeichen = treffer.group(4)
    if len(zeichen) != len(CHECK_IDS):
        raise ValueError("Der Code hat eine andere Länge, als diese Version erwartet.")
    liste = [(i, ZEICHEN_STATUS[z]) for i, z in zip(CHECK_IDS, zeichen)]
    kopf = "%s Python %s.%s" % (treffer.group(2), treffer.group(3)[0], treffer.group(3)[1:])
    return kopf, liste


def zusammenfassung(ergebnisse):
    zaehler = {OK: 0, WARN: 0, FAIL: 0, SKIP: 0}
    for e in ergebnisse:
        zaehler[e.status] += 1
    return zaehler


def gesamturteil(zaehler):
    if zaehler[FAIL]:
        return FAIL, "Es gibt Fehler. Bitte lies die roten Zeilen und die Hinweise darunter."
    if zaehler[WARN]:
        return WARN, "Fast alles gut. Die Warnungen sind meist kein Hindernis – lies sie kurz durch."
    return OK, "Alles grün. Dieses Gerät ist bereit."


_LABEL = {OK: "  OK    ", WARN: " ACHTUNG", FAIL: " FEHLER ", SKIP: "  --    "}
_FARBE = {OK: "\033[32m", WARN: "\033[33m", FAIL: "\033[31m", SKIP: "\033[90m"}


def drucke(ergebnisse, out, farbig=False):
    def farbe(status, text):
        return _FARBE[status] + text + "\033[0m" if farbig else text

    out.write("Sthamer-Systemcheck\n")
    out.write("===================\n")
    for e in ergebnisse:
        out.write("%s %s\n" % (farbe(e.status, _LABEL[e.status]), e.titel))
        if e.detail:
            out.write("           %s\n" % e.detail)
        if e.hinweis and e.status in (WARN, FAIL):
            out.write("           Was tun? %s\n" % e.hinweis)
    zaehler = zusammenfassung(ergebnisse)
    status, text = gesamturteil(zaehler)
    out.write("\n")
    out.write("%s\n" % farbe(status, text))
    out.write("(%d in Ordnung, %d Warnungen, %d Fehler, %d übersprungen)\n"
              % (zaehler[OK], zaehler[WARN], zaehler[FAIL], zaehler[SKIP]))
    out.write("\nSupport-Code (bei Problemen bitte vorlesen oder abtippen):\n  %s\n" % support_code(ergebnisse))


def json_bericht(ergebnisse):
    zaehler = zusammenfassung(ergebnisse)
    status, text = gesamturteil(zaehler)
    return {
        "version": 1,
        "ok": zaehler[FAIL] == 0,
        "gesamt": status,
        "zusammenfassung": text,
        "zaehler": zaehler,
        "python": "%d.%d.%d" % tuple(sys.version_info[:3]),
        "system": os_kurz(platform.system(), platform.release(), platform.version()),
        "support_code": support_code(ergebnisse),
        "pruefungen": [e.as_dict() for e in ergebnisse],
    }


def main(argv=None, out=None, repo=None):
    parser = argparse.ArgumentParser(description="Sthamer-Systemcheck: ist dieses Gerät bereit für den Workshop?")
    gruppe = parser.add_mutually_exclusive_group()
    gruppe.add_argument("--netz", action="store_true", help="nur Internet und Proxy prüfen")
    gruppe.add_argument("--offline", action="store_true", help="Internet nicht prüfen")
    parser.add_argument("--json", action="store_true", help="Ergebnis als JSON ausgeben")
    parser.add_argument("--decode", metavar="CODE", help="einen Support-Code lesen")
    args = parser.parse_args(argv)

    out = sichere_ausgabe(out or sys.stdout)

    if args.decode:
        try:
            kopf, liste = dekodiere(args.decode)
        except ValueError as fehler:
            out.write("%s\n" % fehler)
            return 2
        out.write("%s\n" % kopf)
        for i, status in liste:
            out.write("  %-20s %s\n" % (i, status))
        return 0

    repo = repo or os.path.dirname(os.path.abspath(__file__))
    ergebnisse = fuehre_aus(repo, netz=not args.offline, lokal=not args.netz)
    if args.json:
        out.write(json.dumps(json_bericht(ergebnisse), ensure_ascii=True, indent=2) + "\n")
    else:
        drucke(ergebnisse, out, farbig=farben_moeglich(out))
    return 1 if zusammenfassung(ergebnisse)[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
