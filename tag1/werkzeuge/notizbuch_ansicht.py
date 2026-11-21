#!/usr/bin/env python3
"""Notizbuch-Ansicht: macht aus dem Obsidian-Notizbuch eine einzige HTML-Datei.

Ersatz, wenn Obsidian nicht installiert ist. Nur Python-Standardbibliothek (ab 3.9).
Die Notizen werden nur gelesen, nie verändert.

Aufruf (im Ordner tag1):
    python werkzeuge/notizbuch_ansicht.py
    python werkzeuge/notizbuch_ansicht.py --oeffnen
    python werkzeuge/notizbuch_ansicht.py --notizbuch notizbuch --ziel meine-ergebnisse/notizbuch.html

Ergebnis: meine-ergebnisse/notizbuch.html – im Browser öffnen. Wikilinks [[...]] sind
klickbar, rechts stehen die Rückverweise, oben links gibt es eine Volltextsuche.
Neue Notizen (z. B. unter notizbuch/Vorbereitung/) erscheinen nach erneutem Aufruf.
"""

import argparse
import html
import json
import os
import re
import sys
import webbrowser
from datetime import datetime

HIER = os.path.dirname(os.path.abspath(__file__))
TAG1 = os.path.dirname(HIER)

WIKILINK = re.compile(r"\[\[([^\[\]]+?)\]\]")


# --------------------------------------------------------------------------- Einlesen

def lies_notizen(wurzel):
    notizen = []
    for ordner, unterordner, dateien in os.walk(wurzel):
        unterordner[:] = sorted(d for d in unterordner if not d.startswith("."))
        for name in sorted(dateien):
            if not name.lower().endswith(".md"):
                continue
            pfad = os.path.join(ordner, name)
            rel = os.path.relpath(pfad, wurzel).replace(os.sep, "/")
            with open(pfad, encoding="utf-8-sig") as f:
                text = f.read().replace("\r\n", "\n")
            kopf, rumpf = trenne_frontmatter(text)
            notizen.append({
                "pfad": rel,
                "titel": name[:-3],
                "ordner": os.path.dirname(rel),
                "kopf": kopf,
                "rumpf": rumpf,
            })
    return notizen


def trenne_frontmatter(text):
    if not text.startswith("---\n"):
        return [], text
    ende = text.find("\n---", 4)
    if ende < 0:
        return [], text
    kopfzeilen = text[4:ende].split("\n")
    rest = text[ende + 4:]
    if rest.startswith("\n"):
        rest = rest[1:]
    kopf = []
    for zeile in kopfzeilen:
        if ":" in zeile and not zeile.startswith(" "):
            k, v = zeile.split(":", 1)
            kopf.append([k.strip(), v.strip()])
    return kopf, rest


# --------------------------------------------------------------------------- Verweise

def baue_index(notizen):
    index = {}
    for i, n in enumerate(notizen):
        index.setdefault(n["titel"].lower(), i)
        index.setdefault(n["pfad"][:-3].lower(), i)
    return index


def ziel_von(inhalt):
    ziel = inhalt.split("|", 1)[0]
    ziel = ziel.split("#", 1)[0].strip()
    if ziel.lower().endswith(".md"):
        ziel = ziel[:-3]
    return ziel


def finde(index, ziel):
    z = ziel.lower()
    if z in index:
        return index[z]
    z = z.split("/")[-1]
    return index.get(z)


# --------------------------------------------------------------------------- Markdown

def inline(text, index, notizen):
    platz = []

    def merke(s):
        platz.append(s)
        return "\x00%d\x00" % (len(platz) - 1)

    text = re.sub(r"`([^`]+)`", lambda m: merke("<code>%s</code>" % html.escape(m.group(1))), text)

    def wl(m):
        inhalt = m.group(1)
        ziel = ziel_von(inhalt)
        anzeige = inhalt.split("|", 1)[1] if "|" in inhalt else inhalt
        i = finde(index, ziel)
        if i is None:
            return merke('<span class="kaputt" title="Notiz nicht gefunden">%s</span>' % html.escape(anzeige))
        return merke('<a class="wl" href="#/%s">%s</a>' % (html.escape(quote(notizen[i]["pfad"])), html.escape(anzeige)))

    text = WIKILINK.sub(wl, text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  lambda m: merke('<a href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(m.group(2)), html.escape(m.group(1)))),
                  text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: platz[int(m.group(1))], text)


def quote(s):
    from urllib.parse import quote as q
    return q(s, safe="")


def zellen(zeile):
    z = zeile.strip()
    if z.startswith("|"):
        z = z[1:]
    if z.endswith("|"):
        z = z[:-1]
    return [c.strip() for c in z.split("|")]


LISTE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


def markdown(text, index, notizen):
    zeilen = text.split("\n")
    aus = []
    i = 0
    absatz = []

    def absatz_ende():
        if absatz:
            aus.append("<p>%s</p>" % "<br>".join(inline(z, index, notizen) for z in absatz))
            del absatz[:]

    while i < len(zeilen):
        z = zeilen[i]
        s = z.strip()
        if s.startswith("```"):
            absatz_ende()
            code = []
            i += 1
            while i < len(zeilen) and not zeilen[i].strip().startswith("```"):
                code.append(zeilen[i])
                i += 1
            aus.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code)))
            i += 1
            continue
        if not s:
            absatz_ende()
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            absatz_ende()
            n = len(m.group(1))
            aus.append("<h%d>%s</h%d>" % (n, inline(m.group(2), index, notizen), n))
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            absatz_ende()
            aus.append("<hr>")
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(zeilen) and re.match(r"^\s*\|?\s*:?-{2,}", zeilen[i + 1]):
            absatz_ende()
            kopf = zellen(z)
            i += 2
            rumpf = []
            while i < len(zeilen) and zeilen[i].strip().startswith("|"):
                rumpf.append(zellen(zeilen[i]))
                i += 1
            t = ["<table><thead><tr>"]
            t += ["<th>%s</th>" % inline(c, index, notizen) for c in kopf]
            t.append("</tr></thead><tbody>")
            for r in rumpf:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c, index, notizen) for c in r) + "</tr>")
            t.append("</tbody></table>")
            aus.append("<div class='tab'>%s</div>" % "".join(t))
            continue
        if s.startswith(">"):
            absatz_ende()
            zitat = []
            while i < len(zeilen) and zeilen[i].strip().startswith(">"):
                zitat.append(zeilen[i].strip()[1:].lstrip())
                i += 1
            aus.append("<blockquote>%s</blockquote>" % markdown("\n".join(zitat), index, notizen))
            continue
        if LISTE.match(z):
            absatz_ende()
            block = []
            while i < len(zeilen) and zeilen[i].strip() and (LISTE.match(zeilen[i]) or zeilen[i].startswith("  ")):
                block.append(zeilen[i])
                i += 1
            aus.append(liste(block, index, notizen))
            continue
        absatz.append(s)
        i += 1
    absatz_ende()
    return "\n".join(aus)


def liste(block, index, notizen):
    eintraege = []
    for z in block:
        m = LISTE.match(z)
        if m:
            tiefe = len(m.group(1).replace("\t", "    ")) // 2
            eintraege.append([tiefe, m.group(2)[0].isdigit(), m.group(3)])
        elif eintraege:
            eintraege[-1][2] += " " + z.strip()
    aus = []
    stapel = []
    for tiefe, nummer, inhalt in eintraege:
        while stapel and stapel[-1][0] > tiefe:
            aus.append("</li></%s>" % stapel.pop()[1])
        if not stapel or stapel[-1][0] < tiefe:
            tag = "ol" if nummer else "ul"
            stapel.append((tiefe, tag))
            aus.append("<%s>" % tag)
        else:
            aus.append("</li>")
        m = re.match(r"^\[([ xX])\]\s*(.*)$", inhalt)
        if m:
            erledigt = m.group(1).lower() == "x"
            aus.append('<li class="aufgabe%s"><span class="box">%s</span> %s' % (
                " erledigt" if erledigt else "", "&#10003;" if erledigt else "", inline(m.group(2), index, notizen)))
        else:
            aus.append("<li>%s" % inline(inhalt, index, notizen))
    while stapel:
        aus.append("</li></%s>" % stapel.pop()[1])
    return "".join(aus)


# --------------------------------------------------------------------------- Seite

def baue(notizen):
    index = baue_index(notizen)
    rueck = [set() for _ in notizen]
    kaputt = []
    for i, n in enumerate(notizen):
        for m in WIKILINK.finditer(n["rumpf"]):
            ziel = ziel_von(m.group(1))
            j = finde(index, ziel)
            if j is None:
                kaputt.append((n["pfad"], ziel))
            elif j != i:
                rueck[j].add(i)
    daten = []
    for i, n in enumerate(notizen):
        daten.append({
            "p": n["pfad"],
            "t": n["titel"],
            "o": n["ordner"],
            "k": n["kopf"],
            "h": markdown(n["rumpf"], index, notizen),
            "r": sorted(rueck[i], key=lambda j: notizen[j]["pfad"]),
            "x": re.sub(r"\s+", " ", n["titel"] + " " + n["rumpf"]).lower(),
        })
    return daten, kaputt


SEITE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Notizbuch</title>
<style>
:root{--bg:#fafaf8;--fl:#ffffff;--tx:#1d2125;--le:#5d6670;--li:#e2e4e6;--ak:#2251ff;--ak2:#e8edff;--rot:#b42318;}
@media (prefers-color-scheme: dark){:root{--bg:#15181b;--fl:#1d2125;--tx:#e6e8ea;--le:#9aa3ad;--li:#30363c;--ak:#7d9bff;--ak2:#26304d;--rot:#ff8a80;}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.55 -apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.app{display:grid;grid-template-columns:290px 1fr 250px;height:100vh}
nav,aside{overflow:auto;border-right:1px solid var(--li);padding:14px 12px;background:var(--fl)}
aside{border-right:0;border-left:1px solid var(--li)}
main{overflow:auto;padding:28px 40px 60px}
h1.kopf{font-size:15px;margin:0 0 10px}
#suche{width:100%;padding:7px 9px;border:1px solid var(--li);border-radius:6px;background:var(--bg);color:var(--tx);font:inherit}
.ord{margin-top:12px;font-size:12px;font-weight:600;color:var(--le);text-transform:uppercase;letter-spacing:.04em;cursor:pointer;user-select:none}
.ord::before{content:"\\25BE  "}.ord.zu::before{content:"\\25B8  "}
.ord.zu + ul{display:none}
nav ul{list-style:none;margin:4px 0 0;padding:0}
nav li a{display:block;padding:3px 8px;border-radius:5px;color:var(--tx);text-decoration:none;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
nav li a:hover{background:var(--ak2)}
nav li a.akt{background:var(--ak);color:#fff}
.treffer{font-size:12px;color:var(--le);margin-top:8px}
article{max-width:780px}
.pfad{font-size:12px;color:var(--le)}
.fm{font-size:12.5px;color:var(--le);border:1px solid var(--li);border-radius:6px;padding:6px 10px;margin:10px 0 18px;background:var(--fl)}
.fm span{display:inline-block;margin-right:14px}.fm b{font-weight:600}
article h1{font-size:26px;margin:6px 0 12px}
article h2{font-size:19px;margin:24px 0 8px}
article h3{font-size:16px;margin:18px 0 6px}
a{color:var(--ak)}
a.wl{text-decoration:none;border-bottom:1px solid currentColor}
.kaputt{color:var(--rot);border-bottom:1px dashed var(--rot)}
.tab{overflow-x:auto}
table{border-collapse:collapse;margin:10px 0;font-size:14px}
th,td{border:1px solid var(--li);padding:5px 9px;text-align:left;vertical-align:top}
th{background:var(--ak2)}
blockquote{margin:10px 0;padding:2px 14px;border-left:3px solid var(--li);color:var(--le)}
code{background:var(--ak2);padding:1px 4px;border-radius:4px;font-size:13px}
pre{background:var(--ak2);padding:10px;border-radius:6px;overflow:auto}
hr{border:0;border-top:1px solid var(--li);margin:20px 0}
li.aufgabe{list-style:none;margin-left:-20px}
.box{display:inline-block;width:14px;height:14px;border:1.5px solid var(--le);border-radius:3px;font-size:11px;line-height:12px;text-align:center;vertical-align:-2px}
li.erledigt{color:var(--le)}li.erledigt .box{background:var(--ak);border-color:var(--ak);color:#fff}
aside h2{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--le);margin:0 0 6px}
aside ul{list-style:none;padding:0;margin:0 0 16px;font-size:14px}
aside li{padding:2px 0}
.fuss{font-size:12px;color:var(--le);margin-top:14px}
@media (max-width:900px){.app{grid-template-columns:1fr;height:auto}nav{max-height:40vh;border-right:0;border-bottom:1px solid var(--li)}aside{border-left:0;border-top:1px solid var(--li)}main{padding:18px 16px 40px}}
</style>
</head>
<body>
<div class="app">
<nav>
  <h1 class="kopf">Notizbuch</h1>
  <input id="suche" type="search" placeholder="Suchen …" autocomplete="off">
  <div id="treffer" class="treffer"></div>
  <div id="baum"></div>
  <div class="fuss">Erzeugt __ERZEUGT__ · __ANZAHL__ Notizen<br>Neu erzeugen: <code>python werkzeuge/notizbuch_ansicht.py</code></div>
</nav>
<main><article id="notiz"></article></main>
<aside><h2>Verweise hierher</h2><ul id="rueck"></ul><h2>Verweise von hier</h2><ul id="vor"></ul></aside>
</div>
<script id="daten" type="application/json">__DATEN__</script>
<script>
(function(){
var N = JSON.parse(document.getElementById('daten').textContent);
var nachPfad = {}; N.forEach(function(n,i){ nachPfad[n.p]=i; });
var baum = document.getElementById('baum'), suche = document.getElementById('suche');
function esc(s){ return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }
function link(i){ return '<a href="#/'+encodeURIComponent(N[i].p)+'" data-i="'+i+'">'+esc(N[i].t)+'</a>'; }
function zeichneBaum(filter){
  var gruppen = {}, reihe = [];
  N.forEach(function(n,i){
    if (filter && n.x.indexOf(filter) < 0) return;
    var o = n.o || '(Hauptordner)';
    if (!gruppen[o]) { gruppen[o]=[]; reihe.push(o); }
    gruppen[o].push(i);
  });
  reihe.sort(function(a,b){ if(a==='(Hauptordner)') return -1; if(b==='(Hauptordner)') return 1; return a.localeCompare(b,'de'); });
  var h = '';
  reihe.forEach(function(o){
    h += '<div class="ord">'+esc(o)+' ('+gruppen[o].length+')</div><ul>';
    gruppen[o].forEach(function(i){ h += '<li>'+link(i)+'</li>'; });
    h += '</ul>';
  });
  baum.innerHTML = h || '<p class="treffer">Keine Treffer.</p>';
  var anz = 0; reihe.forEach(function(o){ anz += gruppen[o].length; });
  document.getElementById('treffer').textContent = filter ? anz+' Notizen enthalten „'+filter+'“' : '';
  markiere();
}
baum.addEventListener('click', function(e){ if (e.target.classList.contains('ord')) e.target.classList.toggle('zu'); });
suche.addEventListener('input', function(){ zeichneBaum(suche.value.trim().toLowerCase()); });
function aktuell(){
  var h = decodeURIComponent(location.hash.replace(/^#\\/?/,''));
  if (h in nachPfad) return nachPfad[h];
  return nachPfad['Start hier.md'] !== undefined ? nachPfad['Start hier.md'] : 0;
}
function markiere(){
  var i = aktuell();
  baum.querySelectorAll('a').forEach(function(a){ a.classList.toggle('akt', +a.dataset.i === i); });
}
function zeige(){
  var i = aktuell(), n = N[i];
  if (!n) return;
  var fm = n.k.length ? '<div class="fm">'+n.k.map(function(kv){return '<span><b>'+esc(kv[0])+':</b> '+esc(kv[1])+'</span>';}).join('')+'</div>' : '';
  document.getElementById('notiz').innerHTML = '<div class="pfad">'+esc(n.p)+'</div>'+fm+n.h;
  document.getElementById('rueck').innerHTML = n.r.length ? n.r.map(function(j){return '<li>'+link(j)+'</li>';}).join('') : '<li class="treffer">keine</li>';
  var vor = [], gesehen = {};
  document.querySelectorAll('#notiz a.wl').forEach(function(a){
    var p = decodeURIComponent(a.getAttribute('href').slice(2)); var j = nachPfad[p];
    if (j !== undefined && j !== i && !gesehen[j]) { gesehen[j]=1; vor.push(j); }
  });
  document.getElementById('vor').innerHTML = vor.length ? vor.map(function(j){return '<li>'+link(j)+'</li>';}).join('') : '<li class="treffer">keine</li>';
  document.title = n.t + ' – Notizbuch';
  document.querySelector('main').scrollTop = 0;
  markiere();
}
window.addEventListener('hashchange', zeige);
zeichneBaum(''); zeige();
})();
</script>
</body>
</html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Notizbuch als HTML-Seite mit klickbaren Wikilinks (Obsidian-Ersatz).")
    ap.add_argument("--notizbuch", default=os.path.join(TAG1, "notizbuch"), help="Ordner mit den Notizen (Standard: notizbuch)")
    ap.add_argument("--ziel", default=os.path.join(TAG1, "meine-ergebnisse", "notizbuch.html"), help="HTML-Datei (Standard: meine-ergebnisse/notizbuch.html)")
    ap.add_argument("--oeffnen", action="store_true", help="danach im Standardbrowser öffnen")
    a = ap.parse_args(argv)

    if not os.path.isdir(a.notizbuch):
        print("Ordner nicht gefunden: %s" % a.notizbuch)
        return 1
    notizen = lies_notizen(a.notizbuch)
    if not notizen:
        print("Keine Notizen (.md) gefunden in %s" % a.notizbuch)
        return 1
    daten, kaputt = baue(notizen)
    json_text = json.dumps(daten, ensure_ascii=False).replace("</", "<\\/")
    seite = (SEITE.replace("__DATEN__", json_text)
             .replace("__ANZAHL__", str(len(notizen)))
             .replace("__ERZEUGT__", datetime.now().strftime("%d.%m.%Y %H:%M")))
    os.makedirs(os.path.dirname(os.path.abspath(a.ziel)), exist_ok=True)
    with open(a.ziel, "w", encoding="utf-8", newline="\n") as f:
        f.write(seite)
    print("%d Notizen -> %s" % (len(notizen), os.path.abspath(a.ziel)))
    if kaputt:
        print("Hinweis: %d Wikilinks ohne passende Notiz:" % len(kaputt))
        for pfad, ziel in kaputt:
            print("  %s -> [[%s]]" % (pfad, ziel))
    if a.oeffnen:
        webbrowser.open("file:///" + os.path.abspath(a.ziel).replace(os.sep, "/").lstrip("/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
