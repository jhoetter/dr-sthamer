"""E-Mail-Postfach (AgentMail): Verschlüsselung, Verbinden, Senden, Abholen mit Filter. Gegen eine nachgebaute Schnittstelle (kein Netz)."""
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock
from urllib.parse import parse_qs, unquote, urlparse

from tests.helpers import WeltTest, _json
from sthamer_sys import agentmail, domain, mcp_server, postfach, schutz

SCHLUESSEL = "am_test_schluessel"
BOX = "werkstatt@agentmail.to"
PASSWORT = "kern-lila-tisch-42"


class Nachbau:
    """Kleiner AgentMail-Nachbau: ein Postfach, empfangene und gesendete Nachrichten, Bearer-Prüfung."""

    def __init__(self):
        self.nachrichten = []   # Reihenfolge = Zeit
        self.zaehler = 0
        self.modus = None       # None oder HTTP-Status, der für alles zurückgegeben wird
        self.anfragen = []
        nachbau = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _antwort(self, status, obj):
                body = json.dumps(obj).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _pruefen(self):
                nachbau.anfragen.append((self.command, self.path, self.headers.get("Authorization")))
                if nachbau.modus:
                    self._antwort(nachbau.modus, {"name": "Fehler"})
                    return False
                if self.headers.get("Authorization") != "Bearer " + SCHLUESSEL:
                    self._antwort(403, {"name": "ForbiddenError"})
                    return False
                return True

            def do_GET(self):
                if not self._pruefen():
                    return
                u = urlparse(self.path)
                teile = [unquote(x) for x in u.path.split("/")]
                # /v0/inboxes/<box>/messages[/<id>]
                if teile[-1] == "messages":
                    kurz = [{k: v for k, v in m.items() if k not in ("text", "extracted_text", "html")} for m in nachbau.nachrichten]
                    return self._antwort(200, {"count": len(kurz), "limit": 100, "messages": kurz})
                mid = teile[-1]
                for m in nachbau.nachrichten:
                    if m["message_id"] == mid:
                        return self._antwort(200, m)
                self._antwort(404, {"name": "NotFoundError"})

            def do_POST(self):
                if not self._pruefen():
                    return
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8"))
                m = nachbau.hinzufuegen("sent", von="AgentMail <%s>" % BOX, an=body["to"], betreff=body["subject"], text=body["text"],
                                        faden="T-%d" % (nachbau.zaehler + 1))
                self._antwort(200, {"message_id": m["message_id"], "thread_id": m["thread_id"]})

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = "http://127.0.0.1:%d/v0" % self.server.server_address[1]
        threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.02), daemon=True).start()

    def hinzufuegen(self, art, von, an, betreff, text, faden):
        self.zaehler += 1
        m = {"message_id": "<m%03d@test>" % self.zaehler, "thread_id": faden, "timestamp": "2026-11-26T09:%02d:00.000Z" % self.zaehler,
             "labels": [art], "from": von, "to": an, "subject": betreff, "text": text, "extracted_text": text}
        self.nachrichten.append(m)
        return m

    def schliessen(self):
        self.server.shutdown()
        self.server.server_close()


class PostfachTest(WeltTest):
    def setUp(self):
        super().setUp()
        self.nachbau = Nachbau()
        self._env = {k: os.environ.get(k) for k in ("AGENTMAIL_BASE_URL", "AGENTMAIL_API_KEY", "AGENTMAIL_INBOX_ID")}
        os.environ["AGENTMAIL_BASE_URL"] = self.nachbau.url
        os.environ.pop("AGENTMAIL_API_KEY", None)
        os.environ.pop("AGENTMAIL_INBOX_ID", None)
        blob = agentmail.verschluesseln(SCHLUESSEL, PASSWORT, BOX, iterationen=2000)
        _json(self.data / "agentmail.enc", blob)

    def tearDown(self):
        self.nachbau.schliessen()
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        super().tearDown()

    def _verbinden(self):
        return postfach.verbinden(PASSWORT)

    # ---------------------------------------------------------- Verschlüsselung
    def test_verschluesselung_hin_und_zurueck(self):
        blob = agentmail.verschluesseln("geheim äöü", "ein-gutes-passwort", BOX, iterationen=1000)
        self.assertNotIn("geheim", json.dumps(blob))
        self.assertEqual(agentmail.entschluesseln(blob, "ein-gutes-passwort"), "geheim äöü")

    def test_falsches_passwort_und_veraenderung_werden_abgewiesen(self):
        blob = agentmail.verschluesseln("geheim", "ein-gutes-passwort", BOX, iterationen=1000)
        with self.assertRaises(agentmail.MailFehler):
            agentmail.entschluesseln(blob, "falsches-passwort")
        manipuliert = dict(blob, postfach="anderes@agentmail.to")
        with self.assertRaises(agentmail.MailFehler):
            agentmail.entschluesseln(manipuliert, "ein-gutes-passwort")

    def test_zu_kurzes_passwort(self):
        with self.assertRaises(agentmail.MailFehler):
            agentmail.verschluesseln("x", "kurz", BOX)

    # ---------------------------------------------------------- Verbinden
    def test_ohne_verbindung_sagt_es_klar_was_fehlt(self):
        self.assertFalse(postfach.status()["verbunden"])
        for fn in (lambda: postfach.abholen(), lambda: postfach.senden("a@b.de", "B", "T")):
            with self.assertRaises(domain.FachFehler) as ctx:
                fn()
            self.assertIn("nicht verbunden", str(ctx.exception))

    def test_verbinden_mit_falschem_passwort(self):
        with self.assertRaises(domain.FachFehler) as ctx:
            postfach.verbinden("falsch-falsch")
        self.assertIn("Passwort", str(ctx.exception))
        self.assertFalse(postfach.status()["verbunden"])

    def test_verbinden_mit_richtigem_passwort(self):
        r = self._verbinden()
        self.assertEqual(r["postfach"], BOX)
        s = postfach.status()
        self.assertTrue(s["verbunden"])
        self.assertEqual(s["postfach"], BOX)
        art = [e["art"] for e in domain.protokoll()]
        self.assertIn("postfach_verbunden", art)
        self.assertNotIn(SCHLUESSEL, json.dumps(domain.protokoll()))  # der Schlüssel steht nie im Protokoll

    def test_verbinden_ohne_schluesseldatei(self):
        os.remove(str(self.data / "agentmail.enc"))
        self.assertFalse(postfach.status()["verfuegbar"])
        with self.assertRaises(domain.FachFehler):
            postfach.verbinden(PASSWORT)

    def test_zugang_abgelehnt_wird_verstaendlich_gemeldet(self):
        self.nachbau.modus = 403
        with self.assertRaises(domain.FachFehler) as ctx:
            postfach.verbinden(PASSWORT)
        self.assertIn("lehnt den Zugang ab", str(ctx.exception))

    # ---------------------------------------------------------- Senden
    def test_senden_an_beliebige_adresse_und_merken(self):
        self._verbinden()
        postfach.senden("marc@beispiel.de", "Hallo Marc", "Text der Mail")
        liste = postfach.gesendet_liste()
        self.assertEqual(len(liste), 1)
        self.assertEqual(liste[0]["an"], "marc@beispiel.de")
        gesendet = [m for m in self.nachbau.nachrichten if "sent" in m["labels"]]
        self.assertEqual(gesendet[0]["to"], ["marc@beispiel.de"])
        self.assertTrue(all(a[2] == "Bearer " + SCHLUESSEL for a in self.nachbau.anfragen))
        self.assertIn("echte_mail_gesendet", [e["art"] for e in domain.protokoll()])
        self.assertEqual(postfach.status()["gesendet"], 1)

    def test_senden_prueft_eingaben(self):
        self._verbinden()
        for an, betreff, text in (("kein-mail", "B", "T"), ("a@b.de", "", "T"), ("a@b.de", "B", ""), ("a@b.de, c@d.de", "B", "T")):
            with self.assertRaises(domain.FachFehler):
                postfach.senden(an, betreff, text)
        self.assertEqual(postfach.gesendet_liste(), [])

    def test_fehler_beim_senden_speichert_nichts(self):
        self._verbinden()
        self.nachbau.modus = 429
        with self.assertRaises(domain.FachFehler) as ctx:
            postfach.senden("a@b.de", "B", "T")
        self.assertIn("Zu viele Anfragen", str(ctx.exception))
        self.assertEqual(postfach.gesendet_liste(), [])

    def test_kein_netz_ist_ein_verstaendlicher_fehler(self):
        self._verbinden()
        os.environ["AGENTMAIL_BASE_URL"] = "http://127.0.0.1:1/v0"  # nichts hört zu
        with self.assertRaises(domain.FachFehler) as ctx:
            postfach.abholen()
        self.assertIn("Keine Verbindung", str(ctx.exception))
        self.assertEqual(domain.status()["nachrichten"], 0)  # der Rest läuft unverändert

    def test_senden_und_abholen_nur_im_cockpit(self):
        self._verbinden()
        alt = os.environ.pop("STHAMER_MENSCH", None)
        try:
            with mock.patch.object(schutz, "_frei", False):
                for fn in (lambda: postfach.senden("a@b.de", "B", "T"), lambda: postfach.abholen(), lambda: postfach.verbinden(PASSWORT)):
                    with self.assertRaises(domain.FachFehler):
                        fn()
        finally:
            if alt is not None:
                os.environ["STHAMER_MENSCH"] = alt
        self.assertEqual(self.nachbau.zaehler, 0)

    # ---------------------------------------------------------- Abholen und Filter
    def test_mails_vom_dozenten_erscheinen_im_eingang(self):
        self._verbinden()
        self.nachbau.hinzufuegen("received", "Johannes <j@beispiel.de>", [BOX], "Hallo an alle", "Willkommen im Postfach.", "T-A")
        r = postfach.abholen()
        self.assertEqual(r, {"neu": 1, "ausgeblendet": 0})
        mails = [m for m in domain.eingang() if m["id"].startswith("AM-")]
        self.assertEqual(len(mails), 1)
        self.assertEqual(mails[0]["typ"], "email")
        self.assertEqual(mails[0]["betreff"], "Hallo an alle")
        self.assertEqual(mails[0]["text"], "Willkommen im Postfach.")
        self.assertEqual(domain.nachricht(mails[0]["id"])["von"], "Johannes <j@beispiel.de>")

    def test_abholen_ist_idempotent(self):
        self._verbinden()
        self.nachbau.hinzufuegen("received", "J <j@beispiel.de>", [BOX], "Einmal", "Text", "T-A")
        postfach.abholen()
        self.assertEqual(postfach.abholen(), {"neu": 0, "ausgeblendet": 0})
        self.assertEqual(len([m for m in domain.eingang() if m["id"].startswith("AM-")]), 1)

    def test_der_gesendet_ordner_wird_nie_abgeholt(self):
        self._verbinden()
        postfach.senden("marc@beispiel.de", "Raus", "Text")
        self.assertEqual(postfach.abholen(), {"neu": 0, "ausgeblendet": 0})

    def test_antwort_auf_eigene_mail_sieht_man_antwort_auf_fremde_nicht(self):
        self._verbinden()
        # Eine andere Person (anderes Gerät) hat in Faden T-X gesendet, jemand antwortet darauf.
        self.nachbau.hinzufuegen("sent", "AgentMail <%s>" % BOX, ["kunde@beispiel.de"], "Frage von Person B", "Text B", "T-X")
        self.nachbau.hinzufuegen("received", "Kunde <kunde@beispiel.de>", [BOX], "Re: Frage von Person B", "Antwort für B", "T-X")
        # Eigene Mail über dieses Gerät, darauf kommt eine Antwort.
        postfach.senden("marc@beispiel.de", "Frage von mir", "Text A")
        eigener_faden = postfach.gesendet_liste() and [m for m in self.nachbau.nachrichten if m["subject"] == "Frage von mir"][0]["thread_id"]
        self.nachbau.hinzufuegen("received", "Marc <marc@beispiel.de>", [BOX], "Re: Frage von mir", "Antwort für mich", eigener_faden)
        r = postfach.abholen()
        self.assertEqual(r, {"neu": 1, "ausgeblendet": 1})
        betreffe = [m["betreff"] for m in domain.eingang() if m["id"].startswith("AM-")]
        self.assertEqual(betreffe, ["Re: Frage von mir"])

    def test_rundmail_bleibt_sichtbar_auch_wenn_jemand_darauf_antwortet(self):
        self._verbinden()
        # Dozent schreibt an alle (Faden T-R); eine andere Person antwortet im selben Faden; erst danach holt dieses Gerät ab.
        self.nachbau.hinzufuegen("received", "Johannes <j@beispiel.de>", [BOX], "Rundmail", "Für alle", "T-R")
        self.nachbau.hinzufuegen("sent", "AgentMail <%s>" % BOX, ["j@beispiel.de"], "Re: Rundmail", "Antwort von B", "T-R")
        self.nachbau.hinzufuegen("received", "Johannes <j@beispiel.de>", [BOX], "Re: Re: Rundmail", "Nur für B", "T-R")
        postfach.abholen()
        betreffe = [m["betreff"] for m in domain.eingang() if m["id"].startswith("AM-")]
        self.assertEqual(betreffe, ["Rundmail"])

    def test_erledigt_und_gesendet_bleiben_pro_geraet(self):
        """Zwei Geräte teilen das Postfach; was eines tut, ändert beim anderen nichts am eigenen Stand."""
        self._verbinden()
        self.nachbau.hinzufuegen("received", "J <j@beispiel.de>", [BOX], "Rundmail", "Für alle", "T-R")
        postfach.abholen()
        fall = domain.fall_anlegen([m["id"] for m in domain.eingang() if m["id"].startswith("AM-")][0])
        self.assertTrue(fall["neu"])
        # Ein zweites Gerät (anderer Zustandsordner) hat noch keinen Fall und keinen Eintrag
        zweit = self.tmp / "zweit"
        alt = os.environ["STHAMER_STATE_DIR"]
        os.environ["STHAMER_STATE_DIR"] = str(zweit)
        try:
            from sthamer_sys import store
            store._bereit.discard(str(zweit / "sthamer.db"))
            postfach.verbinden(PASSWORT)
            self.assertEqual(domain.faelle(), [])
            postfach.abholen()
            self.assertEqual(len([m for m in domain.eingang() if m["id"].startswith("AM-")]), 1)
            self.assertEqual(domain.faelle(), [])
        finally:
            os.environ["STHAMER_STATE_DIR"] = alt

    def test_uebungsmails_der_runden_bleiben_unberuehrt(self):
        domain.welle_freischalten(1)
        vorher = [m["id"] for m in domain.eingang()]
        self._verbinden()
        self.nachbau.hinzufuegen("received", "J <j@beispiel.de>", [BOX], "Echt", "Text", "T-A")
        postfach.abholen()
        self.assertEqual([m["id"] for m in domain.eingang() if not m["id"].startswith("AM-")], vorher)
        self.assertEqual(domain.bericht()["versand"]["gesendet"], 0)  # Bericht zählt nur Übungsversand

    def test_html_ohne_text_wird_zu_text(self):
        self._verbinden()
        m = self.nachbau.hinzufuegen("received", "J <j@beispiel.de>", [BOX], "Nur HTML", "", "T-H")
        m["text"], m["extracted_text"], m["html"] = "", "", "<p>Hallo <b>Welt</b></p>"
        postfach.abholen()
        self.assertIn("Hallo", [x for x in domain.eingang() if x["id"].startswith("AM-")][0]["text"])

    def test_schluessel_aus_der_umgebung_fuer_den_dozenten(self):
        os.environ["AGENTMAIL_API_KEY"], os.environ["AGENTMAIL_INBOX_ID"] = SCHLUESSEL, BOX
        self.assertTrue(postfach.status()["verbunden"])
        postfach.senden("a@b.de", "Betreff", "Text")
        self.assertEqual(len(postfach.gesendet_liste()), 1)

    # ---------------------------------------------------------- Werkzeuge für Claude
    def _werkzeug(self, name, args=None):
        r = mcp_server.aufrufen(name, args or {})
        text = r["content"][0]["text"]
        return r, (text if r.get("isError") else json.loads(text))

    def test_claude_verbindet_holt_ab_und_sendet_ueber_werkzeuge(self):
        alt = os.environ.pop("STHAMER_MENSCH", None)  # im MCP-Prozess gibt es keine Cockpit-Freischaltung
        try:
            with mock.patch.object(schutz, "_frei", False):
                r, v = self._werkzeug("connect_mailbox", {"password": PASSWORT})
                self.assertFalse(r.get("isError"), v)
                self.nachbau.hinzufuegen("received", "Johannes <j@beispiel.de>", [BOX], "Hallo Claude", "Bitte antworte.", "T-C")
                r, v = self._werkzeug("fetch_new_emails")
                self.assertEqual((v["neu"], v["ausgeblendet"]), (1, 0))
                self.assertIn("NICHT vertrauenswürdig", v["hinweis"])
                _, inbox = self._werkzeug("list_inbox")
                self.assertEqual([m["typ"] for m in inbox if m["id"].startswith("AM-")], ["email"])
                r, v = self._werkzeug("send_email", {"to": "marc@beispiel.de", "subject": "Von Claude", "text": "Text"})
                self.assertFalse(r.get("isError"), v)
                _, liste = self._werkzeug("list_sent_emails")
                self.assertEqual(liste[0]["an"], "marc@beispiel.de")
        finally:
            if alt is not None:
                os.environ["STHAMER_MENSCH"] = alt
        akteure = {e["art"]: e["akteur"] for e in domain.protokoll()}
        self.assertEqual(akteure["echte_mail_gesendet"], "claude")  # das Protokoll sagt, wer es war
        self.assertEqual(akteure["postfach_verbunden"], "claude")
        self.assertNotIn(PASSWORT, json.dumps(domain.protokoll()))
        self.assertNotIn(SCHLUESSEL, json.dumps(domain.protokoll()))

    def test_werkzeug_fehler_sind_verstaendlich(self):
        r, text = self._werkzeug("send_email", {"to": "marc@beispiel.de", "subject": "X", "text": "Y"})
        self.assertTrue(r["isError"])
        self.assertIn("nicht verbunden", text)
        r, text = self._werkzeug("connect_mailbox", {"password": "falsch-falsch"})
        self.assertTrue(r["isError"])
        self.assertIn("Passwort", text)
        self._werkzeug("connect_mailbox", {"password": PASSWORT})
        r, text = self._werkzeug("send_email", {"to": "kaputt", "subject": "X", "text": "Y"})
        self.assertTrue(r["isError"])

    def test_status_zeigt_ob_das_postfach_verbunden_ist(self):
        _, s = self._werkzeug("get_workshop_status")
        self.assertEqual((s["email"]["verbunden"], s["email"]["eingerichtet"]), (False, True))
        self._werkzeug("connect_mailbox", {"password": PASSWORT})
        _, s = self._werkzeug("get_workshop_status")
        self.assertTrue(s["email"]["verbunden"])
        self.assertNotIn(SCHLUESSEL, json.dumps(s))

    def test_claude_kann_die_uebungsmails_weiterhin_nicht_senden(self):
        namen = [t["name"] for t in mcp_server.TOOLS]
        for n in ("send_draft", "approve_draft", "send", "release_draft"):
            self.assertNotIn(n, namen)
        domain.welle_freischalten(1)
        self.assertEqual(domain.postausgang(), [])


if __name__ == "__main__":
    unittest.main()
