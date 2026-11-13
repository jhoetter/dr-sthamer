import json
import threading
import unittest
from http.client import HTTPConnection

from tests.helpers import WeltTest
from sthamer_sys import app, domain


class AppTest(WeltTest):
    def setUp(self):
        super().setUp()
        domain.welle_freischalten(1)
        self.srv = app.Server(("127.0.0.1", 0))
        self.srv.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        super().tearDown()

    def anfrage(self, methode, pfad, body=None, header=None):
        c = HTTPConnection("127.0.0.1", self.srv.port, timeout=10)
        h = {"Host": "127.0.0.1:%d" % self.srv.port}
        h.update(header or {})
        c.request(methode, pfad, body=json.dumps(body).encode("utf-8") if body is not None else None, headers=h)
        r = c.getresponse()
        data = r.read()
        c.close()
        return r.status, data

    def post(self, pfad, body, token=True, **header):
        h = {"Content-Type": "application/json"}
        if token:
            h["X-Sthamer-Token"] = self.srv.token
        h.update(header)
        return self.anfrage("POST", pfad, body, h)

    def test_health_und_index_mit_token(self):
        s, d = self.anfrage("GET", "/api/health")
        self.assertEqual((s, json.loads(d)["service"]), (200, "sthamer-sys"))
        s, d = self.anfrage("GET", "/")
        self.assertEqual(s, 200)
        self.assertIn(self.srv.token.encode(), d)
        self.assertNotIn(b"{{TOKEN}}", d)

    def test_fremde_hosts_und_pfade_werden_abgelehnt(self):
        self.assertEqual(self.anfrage("GET", "/api/health", header={"Host": "evil.example.com"})[0], 403)
        self.assertEqual(self.anfrage("GET", "/../sthamer.py")[0], 404)
        self.assertEqual(self.anfrage("GET", "/%2e%2e/sthamer.py")[0], 404)
        self.assertEqual(self.anfrage("GET", "/api/gibtsnicht")[0], 404)

    def test_aktionen_brauchen_token_und_json(self):
        self.assertEqual(self.post("/api/fall", {"nachricht_id": "MSG-1-01"}, token=False)[0], 403)
        self.assertEqual(self.post("/api/fall", {"nachricht_id": "MSG-1-01"}, Origin="http://evil.example.com")[0], 403)
        s, _ = self.anfrage("POST", "/api/fall", {"nachricht_id": "MSG-1-01"},
                            {"X-Sthamer-Token": self.srv.token, "Content-Type": "text/plain"})
        self.assertEqual(s, 415)
        self.assertEqual(domain.faelle(), [])

    def test_ablauf_fall_entwurf_senden(self):
        s, d = self.post("/api/fall", {"nachricht_id": "MSG-1-02"})
        fid = json.loads(d)["fall_id"]
        eid = domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "Antwort", "Text", [], "claude")["entwurf_id"]
        self.assertEqual(self.post("/api/entwurf/%d" % eid, {"text": "Geändert"})[0], 200)
        s, d = self.post("/api/senden/%d" % eid, {})
        self.assertEqual(s, 200)
        s, d = self.post("/api/senden/%d" % eid, {})
        self.assertEqual(s, 400)
        self.assertIn("schon gesendet", json.loads(d)["fehler"])
        s, d = self.anfrage("GET", "/api/postausgang")
        self.assertEqual(json.loads(d)[0]["text"], "Geändert")

    def test_runde_2_mit_code_ueber_die_oberflaeche(self):
        self.assertEqual(self.post("/api/welle", {"welle": 2, "code": "falsch"})[0], 400)
        self.assertEqual(self.post("/api/welle", {"welle": 2, "code": "testcode"})[0], 200)
        s, d = self.anfrage("GET", "/api/nachrichten")
        self.assertEqual(len(json.loads(d)), 4)

    def test_ungueltige_eingaben_geben_400_nicht_500(self):
        self.assertEqual(self.post("/api/welle", {})[0], 400)
        self.assertEqual(self.post("/api/entwurf/9999", {"text": "x"})[0], 400)
        self.assertEqual(self.post("/api/unbekannt", {})[0], 400)


if __name__ == "__main__":
    unittest.main()
