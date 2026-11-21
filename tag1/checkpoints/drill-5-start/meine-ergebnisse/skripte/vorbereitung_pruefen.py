# -*- coding: utf-8 -*-
"""Prüft die Vorbereitungsnotizen: Verweise (Wikilinks) lösen auf, Gliederung nach Vorlage,
verbotene Wörter (Urteile, Gesundheit, Familie, Gehalt). Nur lesen."""
import os
import re

NB = "notizbuch"
VORB = os.path.join(NB, "Vorbereitung")

namen = set()
for pfad, _o, dateien in os.walk(NB):
    for d in dateien:
        if d.endswith(".md"):
            namen.add(d[:-3])

verboten = ["krank", "blutdruck", "arzt", "kinder", "familie", "trennung", "schläft", "schlaf",
            "gesundheit", "überlastet", "belastung", "gehalt", "bonus", "beförderung",
            "abmahnung", "erreicht", "verfehlt", "note", "teilzeit", "ruhestand", "bewerbung",
            "motivation", "fels", "zuverlässig"]
kopf = ["## 1. Gesprächseinstieg", "## 2. Rückblick: Ziele 2026", "## 3. Zusammenarbeit und Arbeitssituation",
        "## 4. Offene Zusagen", "## 5. Entwicklung und Weiterbildung",
        "## 6. Ziele 2027 (Entwurf, gemeinsam festlegen)", "## 7. Vereinbarungen"]

for d in sorted(os.listdir(VORB)):
    if not d.endswith(".md"):
        continue
    with open(os.path.join(VORB, d), encoding="utf-8-sig") as f:
        text = f.read()
    print("Datei:", d)
    links = re.findall(r"\[\[([^\]]+)\]\]", text)
    kaputt = sorted(set(l for l in links if l not in namen))
    print("  Verweise: %d, davon unbekannt: %s" % (len(links), kaputt if kaputt else "keine"))
    fehlt = [k for k in kopf if k not in text]
    print("  Gliederung vollständig:", "ja" if not fehlt else "NEIN, fehlt: %s" % fehlt)
    reihenfolge = [text.find(k) for k in kopf]
    print("  Reihenfolge stimmt:", reihenfolge == sorted(reihenfolge))
    low = text.lower()
    treffer = []
    for w in verboten:
        for m in re.finditer(r"\b" + re.escape(w), low):
            ctx = text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
            treffer.append((w, ctx))
    print("  Verbotene/prüfbare Wörter:", "keine" if not treffer else "")
    for w, ctx in treffer:
        print("    [%s] …%s…" % (w, ctx))
    zeilen_ohne_link = []
    for z in text.splitlines():
        if z.startswith(("- ", "|", "1.", "2.", "3.", "4.", "5.")) and "[[" not in z and z.strip() not in ("- [ ]",):
            if not z.startswith("|---") and not z.startswith("| Ziel") and not z.startswith("| Monat"):
                zeilen_ohne_link.append(z[:90])
    print("  Zeilen ohne Verweis: %d" % len(zeilen_ohne_link))
    for z in zeilen_ohne_link:
        print("    ", z)
