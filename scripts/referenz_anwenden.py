"""Referenzlösungen der fünf Bauaufträge (nur Lehrende, Rettungsnetz und Test der Akzeptanzprüfung).

  python scripts/referenz_anwenden.py ORDNER [--bis N]

Verändert den Code in ORDNER (eine Kopie des Repos, nie das Original der Teilnehmenden ohne Rückfrage!).
Teilnehmende und Claude lesen und nutzen diese Datei nicht.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def ersetze(pfad: Path, alt: str, neu: str) -> None:
    text = pfad.read_text(encoding="utf-8")
    if alt not in text:
        raise SystemExit("Referenz passt nicht mehr auf %s: %r" % (pfad.name, alt[:60]))
    pfad.write_text(text.replace(alt, neu, 1), encoding="utf-8", newline="\n")


def drill1(root: Path) -> None:
    ersetze(root / "sthamer_sys" / "domain.py",
            "    # DRILL 1 (Bauauftrag): Die Aufgabe des Falls bleibt hier bewusst offen.\n    # Teilnehmende bauen, dass sie sich beim Senden selbst erledigt.\n",
            "    conn.execute(\"UPDATE aufgaben SET status = 'erledigt', erledigt = ? WHERE fall_id = ? AND status = 'offen'\", (jetzt, e[\"fall_id\"]))\n")


def drill2(root: Path) -> None:
    (root / "sthamer_sys" / "belegpruefung.py").write_text('''"""Belegprüfung (Referenzlösung)."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from . import daten


def _artikel_gibt_es(ref: str) -> bool:
    rw = daten.regelwerk()
    erlaubt = {a["artikel"] for a in rw["anwendungen"]} | {a["artikel"] for a in rw.get("ausnahmen", [])}
    erlaubt |= {"Art. 7 Abs. 3", "Art. 1 Abs. 3", "Art. 2 Nr. 6", rw.get("informationspflicht_artikel", "")}
    return ref in erlaubt


def _belege(belege: List[Dict[str, str]]) -> List[str]:
    probleme = []
    for b in belege:
        t, r = b["typ"], b["ref"]
        if t == "artikel" and not _artikel_gibt_es(r):
            probleme.append("Der Artikel %s gibt es im Regelwerk nicht." % r)
        elif t == "produkt" and not daten.produkt(r):
            probleme.append("Das Produkt %s gibt es nicht." % r)
        elif t == "kunde" and not daten.kunde(r):
            probleme.append("Den Kunden %s gibt es nicht." % r)
    return probleme


def _fristen() -> set:
    rw = daten.regelwerk()
    fr = set()
    for a in rw["anwendungen"]:
        fr |= {v for k, v in a.items() if isinstance(v, str) and re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", v)}
    for c in (rw.get("berichtigung") or {}).get("aenderungen", []):
        fr.add(c["neu"])
    for k in ("informationspflicht_bis", "inkrafttreten"):
        if rw.get(k):
            fr.add(rw[k])
    return fr


def pruefe_entwurf(an: str, betreff: str, text: str, belege: List[Dict[str, str]]) -> List[str]:
    probleme = _belege(belege)
    for d in re.findall(r"\\d{4}-\\d{2}-\\d{2}", text):
        if d not in _fristen():
            probleme.append("Das Datum %s ist keine Frist aus dem Regelwerk." % d)
    return probleme


def pruefe_einschaetzung(kunde_id: str, ergebnis: str, begruendung: str, belege: List[Dict[str, str]]) -> List[str]:
    probleme = _belege(belege)
    if ergebnis == "betroffen":
        typen = {b["typ"] for b in belege}
        if "artikel" not in typen or "produkt" not in typen:
            probleme.append("Eine Einschätzung „betroffen“ braucht Artikel und Produkt als Beleg.")
    return probleme
''', encoding="utf-8", newline="\n")


def drill3(root: Path) -> None:
    ersetze(root / "sthamer_sys" / "domain.py",
            "        # DRILL 3 (Bauauftrag): Wer einen freigegebenen Entwurf ändert, entwertet die Freigabe.\n"
            "        #   Heute bleibt der Status unverändert: Die Freigabe gilt für einen Text, den niemand freigegeben hat.\n",
            "        geaendert = (neu[\"an\"], neu[\"betreff\"], neu[\"text\"], neu[\"belege\"]) != (e[\"an\"], e[\"betreff\"], e[\"text\"], loads(e[\"belege\"], []))\n"
            "        if geaendert and e[\"status\"] == \"freigegeben\":\n"
            "            conn.execute(\"UPDATE entwuerfe SET status='zur_freigabe', freigabe_von=NULL, freigabe_zeit=NULL WHERE id=?\", (entwurf_id,))\n"
            "            ereignis(conn, akteur, \"freigabe_erloschen\", e[\"fall_id\"], {\"entwurf_id\": entwurf_id})\n")


def drill4(root: Path) -> None:
    ersetze(root / "sthamer_sys" / "domain.py",
            "        # DRILL 4 (Bauauftrag): Wer einen eingeplanten Entwurf ändert, bricht den Termin ab.\n"
            "        #   Heute geht die geänderte Mail trotzdem automatisch raus.\n",
            "        if geaendert and e[\"status\"] == \"geplant\":\n"
            "            conn.execute(\"UPDATE entwuerfe SET status='entwurf', sende_am=NULL WHERE id=?\", (entwurf_id,))\n"
            "            ereignis(conn, akteur, \"termin_abgebrochen\", e[\"fall_id\"], {\"entwurf_id\": entwurf_id})\n")


def drill5(root: Path) -> None:
    ersetze(root / "sthamer_sys" / "domain.py",
            "        \"grenze\": \"Alle Zahlen stammen",
            "        \"eigene_kennzahl\": {\"anteil_ohne_eingriff_prozent\": (round(100.0 * (auto + sum(1 for e in gesendet if e[\"stufe\"] == kontrollen.PFLICHTFREIGABE)) / len(gesendet)) if gesendet else 0)},\n"
            "        \"grenze\": \"Alle Zahlen stammen")
    (root / "bericht.md").write_text(
        "# Bericht an die Geschäftsführung (Probelauf)\n\n## Lage\nDie Informationspflicht gegenüber gewerblichen Abnehmern läuft bis zum 30.06.2027.\n\n"
        "## Zahlen\nAlle Zahlen stammen aus dem Protokoll des Systems.\n\n## Empfehlung\nStandardinformationen im Fenster laufen lassen, "
        "alles mit Rechtsauskunft nur mit Freigabe.\n\n## Grenze der Aussage\nErfundene Übungsdaten, kein Rechtsrat; die Zahlen zeigen, was das System festgehalten hat.\n"
        + "Dieser Absatz füllt den Bericht auf eine sinnvolle Länge auf, damit die Prüfung ihn als echten Bericht erkennt. " * 2,
        encoding="utf-8", newline="\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("ordner")
    p.add_argument("--bis", type=int, default=5)
    a = p.parse_args()
    root = Path(a.ordner).resolve()
    for n, f in enumerate((drill1, drill2, drill3, drill4, drill5), 1):
        if n <= a.bis:
            f(root)
    print("Referenz bis Drill %d angewendet in %s" % (a.bis, root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
