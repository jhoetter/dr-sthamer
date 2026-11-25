"""Erzeugt aus der fiktiven Verordnung (Markdown) ein PDF im Stil eines Amtsblatts, deutlich als FIKTIV markiert.

Nur für Lehrende, einmal vor dem Workshop (braucht Google Chrome oder Chromium auf dem Rechner; die Teilnehmenden brauchen
das nicht, das fertige PDF liegt im Repository):

    python3 scripts/verordnung_pdf.py

Ergebnis: web/verordnung-eu-2026-9001-fiktiv.pdf (das Cockpit zeigt es unter Regelwerk, „Als PDF“).
"""
from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUELLE = ROOT / "data" / "regulation" / "vo-fiktiv-2026-9001.md"
ZIEL = ROOT / "web" / "verordnung-eu-2026-9001-fiktiv.pdf"

CHROME = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser", "chrome",
]

CSS = """
@page { size: A4; margin: 22mm 20mm 20mm 20mm; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.6pt; line-height: 1.45; color: #111; }
.kopf { display: flex; justify-content: space-between; align-items: center; border-bottom: 2.5px solid #1b3a8a; padding-bottom: 6px; margin-bottom: 4px; }
.kopf .eu { font-family: Arial, sans-serif; font-size: 9pt; color: #1b3a8a; font-weight: 700; letter-spacing: .04em; }
.kopf .serie { font-family: Arial, sans-serif; font-size: 8.5pt; color: #444; }
.stern { display: inline-block; width: 26px; height: 18px; background: #1b3a8a; color: #ffcc00; font-size: 9px; text-align: center; line-height: 18px; margin-right: 8px; vertical-align: middle; }
.unterkopf { font-family: Arial, sans-serif; font-size: 8pt; color: #555; display: flex; justify-content: space-between; margin-bottom: 18px; }
.hinweis { border: 2px solid #c0272d; background: #fff4f3; color: #8b1a1f; font-family: Arial, sans-serif; font-size: 9.5pt; padding: 8px 12px; margin: 0 0 18px; }
h1 { font-size: 13.5pt; text-align: center; text-transform: none; margin: 4px 0 6px; letter-spacing: .02em; }
.datum, .titel, .amtsblatt { text-align: center; margin: 2px 0; }
.titel { font-weight: 700; margin-top: 6px; }
.amtsblatt { font-style: italic; color: #333; margin-bottom: 14px; }
h2 { font-size: 11pt; text-align: center; margin: 18px 0 8px; }
p { margin: 0 0 7px; text-align: justify; }
ul { margin: 2px 0 8px 22px; padding: 0; }
li { margin: 0 0 2px; }
.wasserzeichen { position: fixed; top: 42%; left: -10%; width: 120%; text-align: center; transform: rotate(-32deg); font-family: Arial, sans-serif;
  font-size: 92pt; font-weight: 800; color: rgba(192, 39, 45, .09); letter-spacing: .08em; z-index: -1; }
.fuss { margin-top: 22px; border-top: 1px solid #999; padding-top: 6px; font-family: Arial, sans-serif; font-size: 8pt; color: #555; }
"""


def inline(text: str) -> str:
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    return t


def umwandeln(md: str) -> str:
    """Kleiner Markdown-Wandler für genau diesen Text: Überschriften, Absätze, Listen, Hinweisblock."""
    zeilen = md.splitlines()
    teile, absatz, liste, hinweis = [], [], [], []

    def absatz_schliessen():
        if absatz:
            teile.append("<p>%s</p>" % inline(" ".join(absatz)))
            absatz.clear()

    def liste_schliessen():
        if liste:
            teile.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(x) for x in liste))
            liste.clear()

    def hinweis_schliessen():
        if hinweis:
            teile.append('<div class="hinweis">%s</div>' % inline(" ".join(hinweis)))
            hinweis.clear()

    kopf_bloecke = 0
    for z in zeilen:
        s = z.strip()
        if s.startswith("> "):
            absatz_schliessen(); liste_schliessen()
            hinweis.append(s[2:])
            continue
        hinweis_schliessen()
        if not s:
            absatz_schliessen(); liste_schliessen()
            continue
        if s.startswith("# "):
            absatz_schliessen(); liste_schliessen()
            teile.append("<h1>%s</h1>" % inline(s[2:]))
            continue
        if s.startswith("## "):
            absatz_schliessen(); liste_schliessen()
            teile.append("<h2>%s</h2>" % inline(s[3:]))
            continue
        if s.startswith("- "):
            absatz_schliessen()
            liste.append(s[2:])
            continue
        absatz.append(s)
    absatz_schliessen(); liste_schliessen(); hinweis_schliessen()
    rumpf = "\n".join(teile)
    # Datum, Titel und Amtsblatt-Zeile unter der Hauptüberschrift zentrieren (die ersten drei Absätze nach dem Hinweis)
    zaehler = {"n": 0}

    def zentrieren(m):
        zaehler["n"] += 1
        klasse = {1: "datum", 2: "titel", 3: "amtsblatt"}.get(zaehler["n"])
        return '<p class="%s">%s</p>' % (klasse, m.group(1)) if klasse else m.group(0)

    kopf, _, rest = rumpf.partition("<h2>")
    kopf = re.sub(r"<p>(.*?)</p>", zentrieren, kopf)
    return kopf + ("<h2>" + rest if rest else "")


def main() -> int:
    chrome = next((c for c in CHROME if Path(c).exists() or shutil.which(c)), None)
    if not chrome:
        print("Chrome oder Chromium nicht gefunden.", file=sys.stderr)
        return 1
    rumpf = umwandeln(QUELLE.read_text(encoding="utf-8"))
    seite = """<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Verordnung (EU) 2026/9001 (FIKTIV)</title><style>%s</style></head><body>
<div class="wasserzeichen">FIKTIV</div>
<div class="kopf"><div class="eu"><span class="stern">★</span>AMTSBLATT DER EUROPÄISCHEN UNION · ÜBUNGSFASSUNG</div><div class="serie">L 9001 · 10.3.2027</div></div>
<div class="unterkopf"><span>Deutsche Ausgabe</span><span>Erfunden für den Workshop Dr. Sthamer × ITMP SG · kein geltendes Recht</span></div>
%s
<div class="fuss">Fiktiver Übungstext. Alle Zahlen, Fristen und Ausnahmen sind für den Workshop erfunden und haben keine Rechtswirkung. Kein Rechtsrat.</div>
</body></html>""" % (CSS, rumpf)
    with tempfile.TemporaryDirectory() as tmp:
        datei = Path(tmp) / "verordnung.html"
        datei.write_text(seite, encoding="utf-8")
        r = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=3000",
                            "--print-to-pdf=%s" % ZIEL, datei.as_uri()], capture_output=True, timeout=120)
    if not ZIEL.is_file() or ZIEL.stat().st_size < 5000:
        print("PDF wurde nicht erzeugt: %s" % r.stderr.decode("utf-8", "replace")[-400:], file=sys.stderr)
        return 1
    print("Fertig: %s (%d KB)" % (ZIEL, ZIEL.stat().st_size // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
