# -*- coding: utf-8 -*-
"""Tests für check.py (Systemcheck). Keine echten Netzwerkaufrufe, nur unittest."""
import ast
import getpass
import io
import json
import os
import re
import shutil
import socket
import ssl
import sys
import tempfile
import textwrap
import unittest
import urllib.error

RAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIN not in sys.path:
    sys.path.insert(0, RAIN)

import check  # noqa: E402


def http_fehler(code):
    return urllib.error.HTTPError("https://example.invalid/", code, "x", {}, io.BytesIO(b""))


class PythonVersion(unittest.TestCase):
    def test_zu_alt_ist_fehler(self):
        e = check.pruefe_python(version_info=(3, 8, 10), plattform="linux", which=lambda n: None)
        self.assertEqual(e.status, check.FAIL)
        self.assertIn("3.9", e.detail)

    def test_mindestversion_ist_ok(self):
        e = check.pruefe_python(version_info=(3, 9, 6), plattform="linux", which=lambda n: None)
        self.assertEqual(e.status, check.OK)

    def test_neue_version_ist_ok(self):
        e = check.pruefe_python(version_info=(3, 13, 0), plattform="darwin", which=lambda n: None)
        self.assertEqual(e.status, check.OK)

    def test_store_platzhalter_warnt(self):
        e = check.pruefe_python(
            version_info=(3, 12, 1), executable="C:\\Python312\\python.exe", plattform="win32",
            which=lambda n: "C:\\Users\\a\\AppData\\Local\\Microsoft\\WindowsApps\\python3.exe",
            getsize=lambda p: 0)
        self.assertEqual(e.status, check.WARN)
        self.assertIn("Store", e.detail)
        self.assertIn("py", e.hinweis)

    def test_echtes_store_python_ist_ok(self):
        e = check.pruefe_python(
            version_info=(3, 12, 1),
            executable="C:\\Users\\a\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.12_x\\python.exe",
            plattform="win32",
            which=lambda n: "C:\\Users\\a\\AppData\\Local\\Microsoft\\WindowsApps\\python3.exe",
            getsize=lambda p: 0)
        self.assertEqual(e.status, check.OK)

    def test_python3_ausserhalb_windowsapps_ist_ok(self):
        e = check.pruefe_python(
            version_info=(3, 12, 1), executable="C:\\Python312\\python.exe", plattform="win32",
            which=lambda n: "C:\\Python312\\python3.exe", getsize=lambda p: 100)
        self.assertEqual(e.status, check.OK)


class Betriebssystem(unittest.TestCase):
    def test_windows_11_wird_erkannt(self):
        e = check.pruefe_os("Windows", "10", "10.0.22631", "AMD64")
        self.assertIn("Windows 11", e.detail)

    def test_windows_10(self):
        e = check.pruefe_os("Windows", "10", "10.0.19045", "AMD64")
        self.assertIn("Windows 10", e.detail)
        self.assertEqual(e.status, check.OK)

    def test_sehr_altes_windows_warnt(self):
        e = check.pruefe_os("Windows", "7", "6.1.7601", "AMD64")
        self.assertEqual(e.status, check.WARN)


class Git(unittest.TestCase):
    def test_git_fehlt_ist_warnung_mit_zip_hinweis(self):
        e = check.pruefe_git(which=lambda n: None)
        self.assertEqual(e.status, check.WARN)
        self.assertIn("ZIP", e.hinweis)

    def test_git_vorhanden(self):
        class Antwort(object):
            returncode = 0
            stdout = "git version 2.45.0\n"
        e = check.pruefe_git(which=lambda n: "/usr/bin/git", run=lambda *a, **k: Antwort())
        self.assertEqual(e.status, check.OK)
        self.assertIn("2.45.0", e.detail)

    def test_git_for_windows_ohne_git_bash_ist_warnung(self):
        class Antwort(object):
            returncode = 0
            stdout = "git version 2.45.0.windows.1"
        git = "C:/Program Files/Git/cmd/git.exe"
        e = check.pruefe_git(which=lambda n: git if n == "git" else None, run=lambda *a, **k: Antwort(),
                             plattform="win32", existiert=lambda p: False)
        self.assertEqual(e.status, check.WARN)
        self.assertIn("Git Bash", e.detail)
        ok = check.pruefe_git(which=lambda n: git if n == "git" else None, run=lambda *a, **k: Antwort(),
                              plattform="win32", existiert=lambda p: p.replace("\\", "/") == "C:/Program Files/Git/bin/bash.exe")
        self.assertEqual(ok.status, check.OK)

    def test_netzlaufwerk_ist_pfad_warnung(self):
        probleme = check.pfad_probleme("\\\\server\\freigabe\\dr-sthamer", env={}, home="C:/Users/x", plattform="win32")
        self.assertTrue(any("Netzlaufwerk" in p for p in probleme), probleme)

    def test_git_startet_nicht(self):
        def kaputt(*a, **k):
            raise OSError("kaputt")
        e = check.pruefe_git(which=lambda n: "/usr/bin/git", run=kaputt)
        self.assertEqual(e.status, check.WARN)

    def test_ohne_git_ordner_ist_zip_betrieb_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            e = check.pruefe_git_repo(tmp)
            self.assertEqual(e.status, check.OK)
            self.assertIn("ZIP", e.detail)
            os.mkdir(os.path.join(tmp, ".git"))
            self.assertIn("geklont", check.pruefe_git_repo(tmp).detail)


class Pfad(unittest.TestCase):
    HOME = "C:\\Users\\mira"

    def test_guter_pfad(self):
        self.assertEqual(check.pfad_probleme("C:\\Users\\mira\\dr-sthamer", {}, self.HOME, "win32"), [])
        self.assertEqual(check.pruefe_pfad("C:\\Users\\mira\\dr-sthamer", {}, self.HOME, "win32").status, check.OK)

    def test_onedrive_im_pfad(self):
        p = check.pfad_probleme("C:\\Users\\mira\\OneDrive - Firma\\dr-sthamer", {}, self.HOME, "win32")
        self.assertTrue(any("OneDrive" in t for t in p))

    def test_onedrive_ueber_umgebungsvariable(self):
        env = {"OneDrive": "D:\\Sync"}
        p = check.pfad_probleme("D:\\Sync\\Projekte\\dr-sthamer", env, self.HOME, "win32")
        self.assertTrue(any("OneDrive" in t for t in p))

    def test_leerzeichen(self):
        p = check.pfad_probleme("C:\\Users\\mira\\Meine Ordner\\dr-sthamer", {}, self.HOME, "win32")
        self.assertTrue(any("Leerzeichen" in t for t in p))

    def test_umlaut(self):
        p = check.pfad_probleme("C:\\Users\\mira\\Übung\\dr-sthamer", {}, self.HOME, "win32")
        self.assertTrue(any("Sonderzeichen" in t for t in p))

    def test_schreibtisch_und_dokumente(self):
        for ordner in ("Desktop", "Schreibtisch", "Documents", "Dokumente"):
            p = check.pfad_probleme("C:\\Users\\mira\\%s\\dr-sthamer" % ordner, {}, self.HOME, "win32")
            self.assertTrue(any("Schreibtisch" in t for t in p), ordner)

    def test_mac_pfad_in_desktop(self):
        p = check.pfad_probleme("/Users/mira/Desktop/dr-sthamer", {}, "/Users/mira", "darwin")
        self.assertTrue(p)

    def test_warnung_nennt_den_pfad_nicht(self):
        e = check.pruefe_pfad("C:\\Users\\mira\\OneDrive\\dr-sthamer", {}, self.HOME, "win32")
        self.assertEqual(e.status, check.WARN)
        self.assertNotIn("mira", e.detail + e.hinweis.replace("<du>", ""))


class Schreiben(unittest.TestCase):
    def test_schreibbar_und_raeumt_auf(self):
        with tempfile.TemporaryDirectory() as tmp:
            e = check.pruefe_schreiben(tmp)
            self.assertEqual(e.status, check.OK)
            self.assertEqual(os.listdir(tmp), [])

    def test_vorhandenes_data_bleibt(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, ".data"))
            check.pruefe_schreiben(tmp)
            self.assertTrue(os.path.isdir(os.path.join(tmp, ".data")))

    def test_nicht_vorhandener_ordner_ist_fehler(self):
        with tempfile.TemporaryDirectory() as tmp:
            e = check.pruefe_schreiben(os.path.join(tmp, "gibt-es-nicht", "x"))
            self.assertIn(e.status, (check.FAIL, check.OK))  # makedirs legt ggf. an
        # Datei statt Ordner: sicher ein Fehler
        with tempfile.NamedTemporaryFile() as f:
            e = check.pruefe_schreiben(f.name)
            self.assertEqual(e.status, check.FAIL)


class Sqlite(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(check.pruefe_sqlite().status, check.OK)

    def test_fehlendes_modul(self):
        def importer(name):
            raise ImportError(name)
        self.assertEqual(check.pruefe_sqlite(importer).status, check.FAIL)


class Zeichensatz(unittest.TestCase):
    def test_ok(self):
        e = check.pruefe_utf8(stdout_encoding="utf-8", preferred="UTF-8", utf8_modus=False)
        self.assertEqual(e.status, check.OK)

    def test_konsole_ohne_umlaute_warnt(self):
        e = check.pruefe_utf8(stdout_encoding="ascii", preferred="cp1252", utf8_modus=False)
        self.assertEqual(e.status, check.WARN)

    def test_cp1252_konsole_ist_ok(self):
        e = check.pruefe_utf8(stdout_encoding="cp1252", preferred="cp1252", utf8_modus=False)
        self.assertEqual(e.status, check.OK)
        self.assertIn("cp1252", e.detail)


class Port(unittest.TestCase):
    def test_frei(self):
        e = check.pruefe_port(3005, binde=lambda p: None, health=lambda p: None)
        self.assertEqual(e.status, check.OK)

    def test_belegt_durch_fremdes_programm(self):
        def binde(p):
            if p == 3005:
                raise OSError("belegt")
        e = check.pruefe_port(3005, binde=binde, health=lambda p: (_ for _ in ()).throw(OSError("keine Antwort")))
        self.assertEqual(e.status, check.WARN)

    def test_belegt_durch_unsere_kommandozentrale(self):
        def binde(p):
            if p == 3005:
                raise OSError("belegt")
        e = check.pruefe_port(3005, binde=binde, health=lambda p: {"ok": True, "service": "sthamer-sys"})
        self.assertEqual(e.status, check.OK)
        self.assertIn("läuft bereits", e.detail)

    def test_kein_lokaler_server_moeglich(self):
        def binde(p):
            raise OSError("verboten")
        e = check.pruefe_port(3005, binde=binde)
        self.assertEqual(e.status, check.FAIL)

    def test_echter_bindeversuch_funktioniert(self):
        # Port 0 = irgendein freier Port: das echte _binde darf nicht scheitern
        check._binde(0)


class Proxy(unittest.TestCase):
    def test_kein_proxy(self):
        self.assertEqual(check.pruefe_proxy({}, lambda: {}).status, check.OK)

    def test_proxy_wird_gemeldet_aber_nie_mit_wert(self):
        env = {"HTTPS_PROXY": "http://benutzer:geheim@proxy.example.com:8080"}
        e = check.pruefe_proxy(env, lambda: {})
        self.assertEqual(e.status, check.WARN)
        self.assertIn("HTTPS_PROXY", e.detail)
        for verboten in ("geheim", "benutzer", "proxy.example.com", "8080"):
            self.assertNotIn(verboten, e.detail + e.hinweis)

    def test_systemproxy(self):
        e = check.pruefe_proxy({}, lambda: {"https": "http://secret.example:1"})
        self.assertEqual(e.status, check.WARN)
        self.assertNotIn("secret", e.detail)


class Netzfehler(unittest.TestCase):
    def code(self, fehler, plattform="win32"):
        return check.klassifiziere_netzfehler(fehler, plattform)[0]

    def test_dns(self):
        self.assertEqual(self.code(socket.gaierror(-2, "Name unknown")), "dns")

    def test_dns_in_urlerror_verpackt(self):
        self.assertEqual(self.code(urllib.error.URLError(socket.gaierror(-2, "x"))), "dns")

    def test_timeout(self):
        self.assertEqual(self.code(socket.timeout("timed out")), "timeout")
        self.assertEqual(self.code(urllib.error.URLError(socket.timeout("timed out"))), "timeout")

    def test_zertifikat(self):
        fehler = getattr(ssl, "SSLCertVerificationError", ssl.SSLError)("certificate verify failed")
        code, text = check.klassifiziere_netzfehler(urllib.error.URLError(fehler), "win32")
        self.assertEqual(code, "tls")
        self.assertIn("Gäste-WLAN", text)
        self.assertIn("TLS-Inspektion", text)
        self.assertNotIn("Install Certificates", text)

    def test_zertifikat_mac_nennt_install_certificates(self):
        fehler = getattr(ssl, "SSLCertVerificationError", ssl.SSLError)("certificate verify failed")
        _, text = check.klassifiziere_netzfehler(fehler, "darwin")
        self.assertIn("Install Certificates.command", text)

    def test_abgelehnt(self):
        self.assertEqual(self.code(ConnectionRefusedError(111, "refused")), "abgelehnt")

    def test_zurueckgesetzt(self):
        self.assertEqual(self.code(ConnectionResetError(104, "reset")), "zurueckgesetzt")

    def test_sonstiger_oserror(self):
        code, text = check.klassifiziere_netzfehler(OSError(101, "unreachable"))
        self.assertEqual(code, "netz")
        self.assertIn("101", text)


class NetzPruefung(unittest.TestCase):
    def test_erreichbar(self):
        e = check.pruefe_netz("net-claude", "claude.ai", check.FAIL, oeffnen=lambda u, t: 200)
        self.assertEqual(e.status, check.OK)

    def test_http_fehlerantwort_zaehlt_als_erreichbar(self):
        def oeffnen(u, t):
            raise http_fehler(403)
        e = check.pruefe_netz("net-claude", "claude.ai", check.FAIL, oeffnen=oeffnen)
        self.assertEqual(e.status, check.OK)
        self.assertIn("403", e.detail)

    def test_proxy_anmeldung_ist_fehler(self):
        def oeffnen(u, t):
            raise http_fehler(407)
        e = check.pruefe_netz("net-claude", "claude.ai", check.FAIL, oeffnen=oeffnen)
        self.assertEqual(e.status, check.FAIL)
        self.assertIn("407", e.detail)

    def test_schweregrad_wird_uebernommen(self):
        def oeffnen(u, t):
            raise socket.gaierror(-2, "x")
        self.assertEqual(check.pruefe_netz("net-git", "git-scm.com", check.WARN, oeffnen=oeffnen).status, check.WARN)
        self.assertEqual(check.pruefe_netz("net-claude", "claude.ai", check.FAIL, oeffnen=oeffnen).status, check.FAIL)

    def test_alle_hosts_je_eigene_zeile_in_fester_reihenfolge(self):
        gefragt = []

        def oeffnen(url, timeout):
            gefragt.append(url)
            if "claude.ai" in url:
                raise socket.timeout("timed out")
            return 200

        ergebnisse = check.pruefe_netz_alle(oeffnen=oeffnen)
        self.assertEqual([e.id for e in ergebnisse], check.NET_IDS)
        status = dict((e.id, e.status) for e in ergebnisse)
        self.assertEqual(status["net-claude"], check.FAIL)
        self.assertEqual(status["net-github"], check.OK)
        self.assertEqual(len(gefragt), 5)
        self.assertTrue(all(u.startswith("https://") for u in gefragt))

    def test_diese_hosts_werden_geprueft(self):
        hosts = [h for _, h, _ in check.NET_HOSTS]
        for erwartet in ("github.com", "claude.ai", "api.anthropic.com", "www.python.org", "git-scm.com"):
            self.assertIn(erwartet, hosts)


class McpJson(unittest.TestCase):
    def test_fehlt_ist_uebersprungen(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check.pruefe_mcp_json(tmp).status, check.SKIP)

    def test_gueltiger_pfad(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, ".mcp.json"), "w", encoding="utf-8") as f:
                json.dump({"mcpServers": {"sthamer": {"command": sys.executable, "args": ["x"]}}}, f)
            self.assertEqual(check.pruefe_mcp_json(tmp).status, check.OK)

    def test_veralteter_pfad(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, ".mcp.json"), "w", encoding="utf-8") as f:
                json.dump({"mcpServers": {"sthamer": {"command": "/gibt/es/nicht/python"}}}, f)
            e = check.pruefe_mcp_json(tmp)
            self.assertEqual(e.status, check.FAIL)
            self.assertNotIn("/gibt/es/nicht", e.detail)

    def test_kaputte_datei(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, ".mcp.json"), "w", encoding="utf-8") as f:
                f.write("{kaputt")
            self.assertEqual(check.pruefe_mcp_json(tmp).status, check.FAIL)


FAKE_SERVER_OK = textwrap.dedent('''
    import sys, json
    print("Hinweis: das ist keine JSON-Zeile", flush=True)
    zeile = sys.stdin.readline()
    anfrage = json.loads(zeile)
    antwort = {"jsonrpc": "2.0", "id": anfrage["id"],
               "result": {"protocolVersion": "2024-11-05", "capabilities": {},
                          "serverInfo": {"name": "sthamer-sys", "version": "0"}}}
    print(json.dumps(antwort), flush=True)
    sys.stdin.read()
''')

FAKE_SERVER_FALSCH = FAKE_SERVER_OK.replace("sthamer-sys", "anderer-server")
FAKE_SERVER_STIRBT = "import sys\nsys.exit(3)\n"
FAKE_SERVER_HAENGT = "import time\ntime.sleep(60)\n"


class McpHandshake(unittest.TestCase):
    def repo_mit_server(self, code, mit_db=False):
        tmp = tempfile.mkdtemp(prefix="sthamer-test-")
        self.addCleanup(shutil.rmtree, tmp, True)
        with open(os.path.join(tmp, "sthamer.py"), "w", encoding="utf-8") as f:
            f.write(code)
        if mit_db:
            os.mkdir(os.path.join(tmp, ".data"))
            open(os.path.join(tmp, ".data", "sthamer.db"), "w").close()
        return tmp

    def test_ohne_sthamer_py_uebersprungen(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check.pruefe_mcp(tmp).status, check.SKIP)

    def test_server_antwortet_richtig(self):
        repo = self.repo_mit_server(FAKE_SERVER_OK)
        self.assertEqual(check.pruefe_mcp(repo, timeout=15).status, check.OK)

    def test_falscher_servername_nach_setup_ist_fehler(self):
        repo = self.repo_mit_server(FAKE_SERVER_FALSCH, mit_db=True)
        self.assertEqual(check.pruefe_mcp(repo, timeout=15).status, check.FAIL)

    def test_falscher_servername_vor_setup_ist_warnung(self):
        repo = self.repo_mit_server(FAKE_SERVER_FALSCH)
        self.assertEqual(check.pruefe_mcp(repo, timeout=15).status, check.WARN)

    def test_server_beendet_sich_sofort(self):
        repo = self.repo_mit_server(FAKE_SERVER_STIRBT, mit_db=True)
        e = check.pruefe_mcp(repo, timeout=15)
        self.assertEqual(e.status, check.FAIL)
        self.assertIn("beendet", e.detail)

    def test_haengender_server_wird_nach_timeout_beendet(self):
        repo = self.repo_mit_server(FAKE_SERVER_HAENGT, mit_db=True)
        e = check.pruefe_mcp(repo, timeout=1)
        self.assertEqual(e.status, check.FAIL)
        self.assertIn("Keine Antwort", e.detail)

    def test_server_startet_nicht(self):
        def popen(*a, **k):
            raise OSError("nicht gefunden")
        antwort, fehler = check.mcp_handshake(["gibt-es-nicht"], ".", 1, popen=popen)
        self.assertIsNone(antwort)
        self.assertIn("lässt sich nicht starten", fehler)


class SupportCode(unittest.TestCase):
    def ergebnisse(self):
        return [check.Ergebnis(i, check.OK, i, "Pfad C:\\Users\\mira\\dr-sthamer") for i in check.CHECK_IDS]

    def test_format(self):
        code = check.support_code(self.ergebnisse(), "Windows", "10", "10.0.22631", (3, 12, 1))
        self.assertRegex(code, r"^STH-W11-PY312-[+~X.]{%d}-[0-9A-F]{2}$" % len(check.CHECK_IDS))

    def test_enthaelt_keine_pfade_oder_benutzernamen(self):
        code = check.support_code(self.ergebnisse(), "Windows", "10", "10.0.19045", (3, 12, 1))
        for verboten in ("mira", "Users", "\\", "/", getpass.getuser().upper() if len(getpass.getuser()) > 3 else "#"):
            self.assertNotIn(verboten, code)

    def test_statuszeichen(self):
        erg = self.ergebnisse()
        erg[0].status = check.FAIL
        erg[1].status = check.WARN
        erg[2].status = check.SKIP
        code = check.support_code(erg, "Darwin", "24.6.0", "x", (3, 9, 6))
        zeichen = code.split("-")[3]
        self.assertEqual(zeichen[:3], "X~.")
        self.assertTrue(code.startswith("STH-MAC-PY39-"))

    def test_entschluesseln(self):
        erg = self.ergebnisse()
        erg[4].status = check.WARN
        erg[10].status = check.FAIL
        code = check.support_code(erg, "Linux", "6", "x", (3, 12, 0))
        kopf, liste = check.dekodiere(code)
        status = dict(liste)
        self.assertEqual(status["pfad"], check.WARN)
        self.assertEqual(status["net-github"], check.FAIL)
        self.assertEqual(status["python"], check.OK)

    def test_entschluesseln_ignoriert_gross_und_kleinschreibung(self):
        code = check.support_code(self.ergebnisse(), "Linux", "6", "x", (3, 12, 0))
        check.dekodiere(code.lower())

    def test_falsche_pruefsumme(self):
        code = check.support_code(self.ergebnisse(), "Linux", "6", "x", (3, 12, 0))
        kaputt = code[:-2] + ("00" if not code.endswith("00") else "01")
        with self.assertRaises(ValueError):
            check.dekodiere(kaputt)

    def test_unsinn(self):
        with self.assertRaises(ValueError):
            check.dekodiere("hallo")


class Ausgabe(unittest.TestCase):
    def cp1252_stream(self):
        roh = io.BytesIO()
        return roh, io.TextIOWrapper(roh, encoding="cp1252", errors="strict")

    def test_cp1252_stream_stuerzt_nicht_ab(self):
        roh, stream = self.cp1252_stream()
        with self.assertRaises(UnicodeEncodeError):
            stream.write(u"\u2192")
            stream.flush()
        roh, stream = self.cp1252_stream()
        sicher = check.sichere_ausgabe(stream)
        sicher.write(u"Prüfung äöüß \u2192 \u2265 \u00b5g/l\n")
        sicher.flush()
        text = roh.getvalue().decode("cp1252")
        self.assertIn(u"äöüß", text)

    def test_stream_ohne_reconfigure_bekommt_wrapper(self):
        roh = io.BytesIO()

        class Alt(object):
            encoding = "cp1252"
            buffer = roh

            def isatty(self):
                return False

        sicher = check.sichere_ausgabe(Alt())
        sicher.write(u"\u2192 äöü")
        sicher.flush()
        self.assertIn(u"äöü", roh.getvalue().decode("cp1252"))

    def test_stringio_bleibt_unveraendert(self):
        s = io.StringIO()
        self.assertIs(check.sichere_ausgabe(s), s)

    def test_keine_farben_ohne_terminal_oder_mit_no_color(self):
        self.assertFalse(check.farben_moeglich(io.StringIO(), {}, nt=False))

        class Tty(io.StringIO):
            def isatty(self):
                return True
        self.assertFalse(check.farben_moeglich(Tty(), {"NO_COLOR": "1"}, nt=False))
        self.assertTrue(check.farben_moeglich(Tty(), {"TERM": "xterm"}, nt=False))

    def test_komplettlauf_offline_mit_cp1252_konsole(self):
        with tempfile.TemporaryDirectory() as repo:
            roh, stream = self.cp1252_stream()
            rc = check.main(["--offline"], out=stream, repo=repo)
            stream.flush()
            text = roh.getvalue().decode("cp1252")
            self.assertIn(rc, (0, 1))
            self.assertIn("Sthamer-Systemcheck", text)
            self.assertIn("Support-Code", text)
            self.assertNotIn("Internet: github.com\n           Erreichbar", text)

    def test_json_ist_gueltig_und_enthaelt_keine_pfade(self):
        with tempfile.TemporaryDirectory() as repo:
            puffer = io.StringIO()
            rc = check.main(["--offline", "--json"], out=puffer, repo=repo)
            daten = json.loads(puffer.getvalue())
            self.assertIn(rc, (0, 1))
            self.assertEqual([p["id"] for p in daten["pruefungen"]], check.CHECK_IDS)
            self.assertRegex(daten["support_code"], r"^STH-")
            roh = puffer.getvalue()
            self.assertNotIn(repo, roh)
            self.assertNotIn(getpass.getuser(), roh) if len(getpass.getuser()) > 3 else None
            status = dict((p["id"], p["status"]) for p in daten["pruefungen"])
            for i in check.NET_IDS:
                self.assertEqual(status[i], check.SKIP)

    def test_netz_modus_ueberspringt_lokale_pruefungen(self):
        ergebnisse = check.fuehre_aus(tempfile.gettempdir(), netz=True, lokal=False,
                                      oeffnen=lambda u, t: 200)
        status = dict((e.id, e.status) for e in ergebnisse)
        self.assertEqual(status["python"], check.SKIP)
        self.assertEqual(status["net-claude"], check.OK)

    def test_exitcode_bei_fehler(self):
        with tempfile.TemporaryDirectory() as repo:
            alt = check.pruefe_python
            check.pruefe_python = lambda *a, **k: check.Ergebnis("python", check.FAIL, "Python", "zu alt")
            try:
                rc = check.main(["--offline"], out=io.StringIO(), repo=repo)
            finally:
                check.pruefe_python = alt
            self.assertEqual(rc, 1)

    def test_decode_option(self):
        ergebnisse = check.fuehre_aus(tempfile.gettempdir(), netz=False, lokal=False)
        code = check.support_code(ergebnisse)
        puffer = io.StringIO()
        self.assertEqual(check.main(["--decode", code], out=puffer), 0)
        self.assertIn("python", puffer.getvalue())
        self.assertEqual(check.main(["--decode", "Unsinn"], out=io.StringIO()), 2)

    def test_offline_und_netz_schliessen_sich_aus(self):
        with self.assertRaises(SystemExit):
            stderr, sys.stderr = sys.stderr, io.StringIO()
            try:
                check.main(["--offline", "--netz"], out=io.StringIO())
            finally:
                sys.stderr = stderr


class Quelltext(unittest.TestCase):
    """check.py muss auch von alten Python-Versionen noch gelesen werden können."""

    def test_keine_neue_syntax(self):
        with open(os.path.join(RAIN, "check.py"), encoding="utf-8") as f:
            baum = ast.parse(f.read())
        verboten = [getattr(ast, n) for n in ("JoinedStr", "AnnAssign", "NamedExpr", "Nonlocal", "YieldFrom", "Match")
                    if hasattr(ast, n)]
        for knoten in ast.walk(baum):
            self.assertNotIsInstance(knoten, tuple(verboten), getattr(knoten, "lineno", "?"))
            if isinstance(knoten, ast.FunctionDef):
                self.assertFalse(knoten.args.kwonlyargs, knoten.name)
                self.assertIsNone(knoten.returns, knoten.name)
                for arg in knoten.args.args:
                    self.assertIsNone(arg.annotation, knoten.name)
                self.assertFalse(getattr(knoten.args, "posonlyargs", []), knoten.name)

    def test_versionswaechter_steht_vor_den_importen(self):
        with open(os.path.join(RAIN, "check.py"), encoding="utf-8") as f:
            text = f.read()
        self.assertLess(text.index("sys.version_info < (3, 6)"), text.index("import argparse"))

    def test_kodierungszeile(self):
        with open(os.path.join(RAIN, "check.py"), "rb") as f:
            erste = f.read(200)
        self.assertIn(b"coding: utf-8", erste)


if __name__ == "__main__":
    unittest.main()
