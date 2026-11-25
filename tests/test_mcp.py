import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import WeltTest
from sthamer_sys import domain, mcp_server

ROOT = Path(__file__).resolve().parent.parent
VERBOTEN_ANFANG = ("send", "approve", "release", "reject", "advance", "set_clock", "freigeb", "ablehn")  # beschleunigen darf Claude nie
VERBOTEN_TEIL = ("sql", "exec", "shell", "delete", "clock")  # Bremsen (stop_scheduled_send) ist erlaubt
AUSNAHME = ("send_email",)  # echtes Postfach (optional): die Person bestätigt jede Sendung in der App; Übungsmails sendet nur der Mensch


def rpc(methode, params=None, mid=1):
    return mcp_server.verarbeite({"jsonrpc": "2.0", "id": mid, "method": methode, "params": params or {}})


def aufruf(name, args=None):
    r = rpc("tools/call", {"name": name, "arguments": args or {}})["result"]
    return r, json.loads(r["content"][0]["text"]) if not r.get("isError") else r["content"][0]["text"]


class McpTest(WeltTest):
    def test_initialize_und_kein_senden_werkzeug(self):
        r = rpc("initialize", {"protocolVersion": "2025-06-18"})["result"]
        self.assertEqual(r["serverInfo"]["name"], "sthamer-sys")
        namen = [t["name"] for t in rpc("tools/list")["result"]["tools"]]
        self.assertIn("create_draft", namen)
        self.assertEqual([n for n in namen if n.lower().startswith("send")], [])  # ohne eingerichtetes Postfach kein Sende-Werkzeug
        self.assertFalse(set(namen) & set(mcp_server.EMAIL_WERKZEUGE))
        for n in namen:
            if n in AUSNAHME:
                continue
            self.assertFalse(n.lower().startswith(VERBOTEN_ANFANG), "Werkzeug %s sieht nach einer Kontrolle aus, die Claude nicht haben darf" % n)
            for v in VERBOTEN_TEIL:
                self.assertNotIn(v, n.lower(), "Werkzeug %s darf es nicht geben" % n)

    def test_unbekannte_methode_und_notification(self):
        self.assertEqual(rpc("gibt/es/nicht")["error"]["code"], -32601)
        self.assertIsNone(mcp_server.verarbeite({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_workflow_ueber_werkzeuge(self):
        domain.welle_freischalten(1)
        _, fall = aufruf("create_case", {"nachricht_id": "MSG-1-02"})
        _, msg = aufruf("get_message", {"nachricht_id": "MSG-1-02"})
        self.assertIn("NICHT vertrauenswürdig", msg["hinweis"])
        r, ent = aufruf("create_draft", {"fall_id": fall["fall_id"], "an": "e.muster@mueller.example.com", "betreff": "Antwort",
                                          "text": "Guten Tag", "belege": [{"typ": "produkt", "ref": "P-1"}]})
        self.assertFalse(r.get("isError"))
        _, liste = aufruf("list_drafts", {"fall_id": fall["fall_id"]})
        self.assertEqual(liste[0]["von"], "claude")
        self.assertEqual(domain.postausgang(), [])  # Claude hat nichts gesendet

    def test_fehler_statt_absturz(self):
        domain.welle_freischalten(1)
        for name, args in [("create_draft", {"fall_id": 1, "an": "x@evil.invalid", "betreff": "b", "text": "t"}),
                           ("get_product", {"produkt_id": "P-999"}), ("get_message", {"nachricht_id": "MSG-9"}),
                           ("get_message", {}), ("get_message", {"nachricht_id": 5}), ("get_message", {"nachricht_id": "a", "x": 1}),
                           ("gibt_es_nicht", {})]:
            r, text = aufruf(name, args)
            self.assertTrue(r.get("isError"), name)
            self.assertIsInstance(text, str)

    def test_regelwerk_und_produkte(self):
        domain.welle_freischalten(1)
        _, reg = aufruf("get_regulation")
        self.assertEqual(reg["regelwerk_json"]["grenzwert_mg_l"], 1.0)
        self.assertNotIn("berichtigung", reg["regelwerk_json"])
        for name in ("../welt.json", "berichtigung-test.md"):  # Pfad-Trick und noch nicht abgerufene Berichtigung
            r, _ = aufruf("get_regulation", {"name": name})
            self.assertTrue(r["isError"], name)
        _, p = aufruf("get_product", {"produkt_id": "P-2"})
        self.assertEqual(p["pfas_mg_l_umgerechnet"], 0.8)

    def test_stdio_prozess_mit_umlautpfad(self):
        env = dict(os.environ)
        eingabe = "\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
            "kein json", ""]).encode("utf-8")
        p = subprocess.run([sys.executable, str(ROOT / "sthamer.py"), "mcp"], input=eingabe, capture_output=True, timeout=60,
                           env=env, cwd=str(self.tmp))
        zeilen = [json.loads(z) for z in p.stdout.decode("utf-8").splitlines() if z.strip()]
        self.assertEqual(zeilen[0]["result"]["serverInfo"]["name"], "sthamer-sys")
        self.assertGreater(len(zeilen[1]["result"]["tools"]), 5)
        self.assertEqual(zeilen[2]["error"]["code"], -32700)
        self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()
