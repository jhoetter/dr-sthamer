"use strict";
/* sthamer-sys Cockpit. Eine kleine App ohne Build und ohne externe Dateien.
   Alle Inhalte (auch Mailtexte) werden nur als Text eingefügt, nie als HTML. */

const TOKEN = document.querySelector("meta[name=sthamer-token]").content;
const app = document.getElementById("app");
const NS = "http://www.w3.org/2000/svg";

/* ---------- Helfer ---------- */
const ICONS = {
  inbox: '<path d="M3 13h4l2 3h6l2-3h4M5 5h14l2 8v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-6z"/>',
  cases: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M3 13h18"/>',
  send: '<path d="m21 3-9 18-2.5-7.5L3 11z"/><path d="m21 3-11.5 10.5"/>',
  book: '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11M9 8h6"/>',
  flask: '<path d="M9 3h6M10 3v6L4.5 18.5A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-2.5L14 9V3M7.5 15h9"/>',
  users: '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5M16 5.2a3 3 0 0 1 0 5.6M18 14.8c1.9.7 3 2.4 3 5.2"/>',
  list: '<path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4-4"/>',
  sync: '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8M4 13a8 8 0 0 0 14.3 4.9L20 16M4 4v4h4M20 20v-4h-4"/>',
  close: '<path d="M6 6l12 12M18 6 6 18"/>',
  clip: '<path d="m20 11-8.5 8.5a5 5 0 0 1-7-7L13 4a3.5 3.5 0 0 1 5 5l-8.5 8.5a2 2 0 0 1-3-3L14 7"/>',
  bot: '<rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9 16.5h6"/>',
  user: '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.5 3-6 7-6s7 2.5 7 6"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  building: '<rect x="5" y="3" width="14" height="18" rx="1.5"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>',
};

function icon(name, size) {
  const s = document.createElementNS(NS, "svg");
  s.setAttribute("class", "icon");
  s.setAttribute("width", size || 16);
  s.setAttribute("height", size || 16);
  s.setAttribute("viewBox", "0 0 24 24");
  s.setAttribute("aria-hidden", "true");
  s.innerHTML = ICONS[name] || ""; // nur feste Symbole aus dieser Datei
  return s;
}

const PROPS = new Set(["value", "checked", "disabled", "selected"]);
function h(tag, props, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (PROPS.has(k)) el[k] = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

const parseIso = s => {
  if (!s) return null;
  const d = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  return d ? new Date(+d[1], +d[2] - 1, +d[3]) : new Date(s);
};
const fmtDate = s => (s ? parseIso(s).toLocaleDateString("de-DE", { day: "numeric", month: "long", year: "numeric" }) : "–");
const fmtDateShort = s => (s ? parseIso(s).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }) : "–");
const fmtTime = s => (s ? parseIso(s).toLocaleString("de-DE", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "–");
const hhmm = s => (s ? parseIso(s).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }) : "");
const senderName = v => (v || "").replace(/<.*>/, "").trim() || v || "";
const senderMail = v => ((v || "").match(/<(.*)>/) || [, ""])[1];
const initials = v => senderName(v).split(/[\s.@-]+/).filter(Boolean).slice(0, 2).map(p => p[0].toUpperCase()).join("") || "?";
const fallNr = id => "F-" + String(id).padStart(4, "0");
const plural = (n, one, many) => n + " " + (n === 1 ? one : many);

const TYPEN = {
  aufgabe: ["Aufgabe", "dot-blue"], kundenanfrage: ["Kundenanfrage", "dot-green"], verordnung: ["Verordnung", "dot-orange"],
  berichtigung: ["Berichtigung", "dot-red"], intern: ["Intern", "dot-grey"],
};
const FALL_STATUS = { neu: ["Neu", ""], in_bearbeitung: ["In Bearbeitung", "progress"], gesendet: ["Gesendet", "done"] };
const ANWENDUNGEN = {
  tragbarer_feuerloescher: "Tragbarer Feuerlöscher", fahrbarer_feuerloescher: "Fahrbarer Feuerlöscher",
  stationaere_anlage: "Stationäre Löschanlage", feuerwehrfahrzeug: "Feuerwehrfahrzeug",
  uebung_training: "Übung und Training", lager_bestand: "Lagerbestand",
};
const EREIGNISSE = {
  postfach_abgerufen: "Postfach abgerufen", fall_angelegt: "Fall angelegt", entwurf_angelegt: "Entwurf angelegt",
  entwurf_geaendert: "Entwurf geändert", gesendet: "Gesendet", notiz: "Notiz",
};
const AKTEURE = { mensch: ["Du", "mensch"], claude: ["Claude", "claude"], system: ["System", "system"] };

const chip = (text, cls) => h("span", { class: "chip " + (cls || "") }, text);
const typChip = t => { const [txt, cls] = TYPEN[t] || [t, "dot-grey"]; return chip(txt, cls); };
const statusIcon = st => h("span", { class: "status-icon " + ((FALL_STATUS[st] || [])[1] || "") });
const anwendung = id => ANWENDUNGEN[id] || id;

async function api(pfad, body) {
  const opt = body === undefined ? {} : {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Sthamer-Token": TOKEN },
    body: JSON.stringify(body),
  };
  const r = await fetch("/api/" + pfad, opt);
  const d = await r.json().catch(() => ({ fehler: "Unerwartete Antwort." }));
  if (!r.ok) throw new Error(d.fehler || "Fehler " + r.status);
  return d;
}

let toastTimer = null;
function toast(text, error) {
  document.querySelectorAll(".toast").forEach(t => t.remove());
  document.body.append(h("div", { class: "toast" + (error ? " error" : ""), role: "status" }, text));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => document.querySelectorAll(".toast").forEach(t => t.remove()), error ? 7000 : 3500);
}

/* ---------- Routing: der Zustand steht in der Adresse ---------- */
function parseRoute() {
  const raw = location.hash.replace(/^#\/?/, "");
  const [path, qs = ""] = raw.split("?");
  const [view = "eingang", id = ""] = path.split("/");
  const q = Object.fromEntries(new URLSearchParams(qs));
  return { view: view || "eingang", id: id ? decodeURIComponent(id) : null, q };
}
function href(view, id, q) {
  const qs = q && Object.keys(q).length ? "?" + new URLSearchParams(q) : "";
  return "#/" + view + (id ? "/" + encodeURIComponent(id) : "") + qs;
}
function go(view, id, q) { location.hash = href(view, id, q); }
/* Adresse der aktuellen Ansicht mit geöffnetem Seitenpanel (key: "p" Produkt, "k" Kunde) */
function panelHref(key, id) {
  const r = parseRoute();
  const q = Object.assign({}, r.q);
  delete q.p; delete q.k;
  q[key] = id;
  return href(r.view, r.id, q);
}
function closePanelHref() {
  const r = parseRoute();
  const q = Object.assign({}, r.q);
  delete q.p; delete q.k;
  return href(r.view, r.id, q);
}
function closePanel() { location.hash = closePanelHref(); }

/* ---------- Bausteine ---------- */
const col = (...kids) => h("div", { class: "col" }, kids);

function topbar(crumbs, ...actions) {
  return h("div", { class: "topbar" },
    h("div", { class: "crumbs" }, crumbs.map((c, i) => [i ? h("span", { class: "sep" }, "›") : null, i === crumbs.length - 1 ? h("strong", {}, c) : h("span", {}, c)])),
    h("div", { class: "spacer" }),
    actions,
    h("button", { class: "btn ghost", title: "Suchen und springen", onclick: openPalette }, icon("search"), "Suchen", h("span", { class: "kbd" }, "⌘K")),
    h("button", { class: "btn", onclick: openPostfach }, icon("sync"), "Postfach abrufen"));
}

function emptyState(iconName, text, ...buttons) {
  return h("div", { class: "empty" }, h("div", { class: "glyph" }, icon(iconName, 22)), h("p", {}, text), buttons.length ? h("div", { class: "btns" }, buttons) : null);
}

function splitView(listChildren, detail, emptyIcon, emptyText) {
  return h("div", { class: "split" + (detail ? " has-detail" : "") },
    h("div", { class: "list" }, listChildren),
    detail || h("div", { class: "detail" }, emptyState(emptyIcon || "inbox", emptyText || "Wähle links einen Eintrag.")));
}

function groupBy(items, keyFn) {
  const m = new Map();
  items.forEach(i => { const k = keyFn(i); if (!m.has(k)) m.set(k, []); m.get(k).push(i); });
  return m;
}

const prop = (label, ...value) => h("div", { class: "prop" }, h("span", {}, label), h("span", {}, value));
const kundeLink = (id, name) => (id ? h("a", { href: panelHref("k", id) }, name || id) : "–");
const fact = (label, value, sub) => h("div", { class: "fact" }, h("div", { class: "fact-label" }, label), h("div", { class: "fact-value" }, value), h("div", { class: "fact-sub" }, sub || " "));

/* Mailtext lesbar machen: harte Zeilenumbrüche im Absatz entfernen, Listen und Fettdruck zeigen, Grußformeln behalten. */
function mailText(text) {
  const out = h("div", { class: "message-text" });
  text.replace(/\r/g, "").split(/\n\s*\n/).forEach(chunk => {
    const lines = chunk.split("\n").filter(l => l.trim() !== "");
    if (!lines.length) return;
    const isItem = l => /^\s*(?:[-*]|\d+\.)\s+/.test(l);
    if (isItem(lines[0])) {
      const items = [];
      lines.forEach(l => { if (isItem(l)) items.push(l.replace(/^\s*(?:[-*]|\d+\.)\s+/, "")); else items[items.length - 1] += " " + l.trim(); });
      const ordered = /^\s*\d+\./.test(lines[0]);
      out.append(h(ordered ? "ol" : "ul", {}, items.map(i => h("li", {}, inline(i)))));
    } else if (lines.slice(0, -1).every(l => l.length < 46) && lines.length > 1) {
      out.append(h("p", { class: "keep" }, lines.map((l, i) => [i ? h("br") : null, inline(l)])));
    } else {
      out.append(h("p", {}, inline(lines.map(l => l.trim()).join(" "))));
    }
  });
  return out;
}

function messageBlock(m) {
  return h("div", { class: "message" },
    h("div", { class: "avatar" }, initials(m.von)),
    h("div", { class: "message-body" },
      h("div", { class: "message-head" }, h("span", {}, h("strong", {}, senderName(m.von)), " ", h("span", { class: "faint small" }, senderMail(m.von))), h("span", { class: "when" }, fmtTime(m.empfangen))),
      mailText(m.text)));
}

const attachLink = a => h("a", { class: "attach", href: href("regelwerk", null, { text: a.split("/").pop() }) }, icon("clip", 14), a.split("/").pop());

/* Sehr kleiner Markdown-Leser für den Verordnungstext (nur Text, nie HTML). */
function inline(text) {
  return text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/).filter(Boolean).map(part => {
    if (part.startsWith("**")) return h("strong", {}, part.slice(2, -2));
    if (part.startsWith("*") && part.length > 2) return h("em", {}, part.slice(1, -1));
    return part;
  });
}
function markdown(text) {
  const out = h("div", { class: "reading" });
  text.replace(/\r/g, "").split(/\n\s*\n/).forEach(chunk => {
    const lines = chunk.split("\n").filter(l => l.trim() !== "");
    if (!lines.length) return;
    const hd = /^(#{1,3})\s+(.*)$/.exec(lines[0]);
    if (hd) { out.append(h("h" + hd[1].length, {}, inline(hd[2]))); lines.shift(); if (!lines.length) return; }
    if (/^---+$/.test(lines[0])) { out.append(h("hr")); return; }
    if (lines.every(l => l.startsWith(">"))) out.append(h("blockquote", {}, h("p", {}, inline(lines.map(l => l.replace(/^>\s?/, "")).join(" ")))));
    else if (lines.every(l => /^[-*]\s+/.test(l))) out.append(h("ul", {}, lines.map(l => h("li", {}, inline(l.replace(/^[-*]\s+/, ""))))));
    else out.append(h("p", {}, inline(lines.join(" "))));
  });
  return out;
}

/* ---------- Gerüst ---------- */
const NAV = [
  ["Arbeitskorb", [["eingang", "Eingang", "inbox", s => s.ungelesen, true], ["faelle", "Fälle", "cases", s => s.faelle_offen], ["postausgang", "Postausgang", "send", s => s.gesendet]]],
  ["Wissen", [["regelwerk", "Regelwerk", "book"], ["produkte", "Produkte", "flask", s => s.produkte], ["kunden", "Kunden", "users", s => s.kunden]]],
  ["Nachweis", [["protokoll", "Protokoll", "list"]]],
];
let S = null;
let mainEl = null;
const navEls = {};

function buildShell() {
  const nav = h("nav", {});
  NAV.forEach(([label, items]) => {
    nav.append(h("div", { class: "nav-label" }, label));
    items.forEach(([key, text, ic, count, hot]) => {
      const c = h("span", { class: "count" });
      const a = h("a", { class: "nav-item", href: "#/" + key }, icon(ic), text, c);
      navEls[key] = { a, c, count, hot };
      nav.append(a);
    });
  });
  const brand = h("div", { class: "brand" }, h("a", { href: "#/eingang", title: "Dr. Sthamer" }, h("img", { src: "logo-sthamer.png", alt: "Dr. Sthamer – Foam fights fire" })));
  const partner = h("img", { src: "logo-itmp.svg", alt: "ITMP SG" });
  partner.addEventListener("error", () => partner.remove());
  const foot = h("div", { class: "sidebar-foot" },
    h("div", { class: "foot-line" }, h("span", { class: "dot" }), h("span", { id: "foot-stand" }, "…")),
    h("div", { class: "foot-note" }, "Übungsdaten: alles erfunden."),
    h("div", { class: "partner" }, h("span", {}, "Workshop von"), partner, h("strong", { class: "muted" }, "ITMP SG")));
  mainEl = h("div", { class: "main" });
  app.replaceChildren(h("div", { class: "shell" }, h("aside", { class: "sidebar" }, brand, nav, foot), mainEl));
}

async function refreshStatus() {
  try { S = await api("status"); } catch (e) { S = S || {}; }
  Object.values(navEls).forEach(n => {
    const v = n.count && S ? n.count(S) : null;
    n.c.textContent = v ? String(v) : "";
    n.c.classList.toggle("hot", !!(n.hot && v));
  });
  const f = document.getElementById("foot-stand");
  if (f && S && S.heute) f.textContent = "Runde " + S.welle + " · Übungstag " + fmtDateShort(S.heute);
}

/* ---------- Ansichten ---------- */
async function viewEingang(r) {
  const m = r.id ? await api("nachricht/" + encodeURIComponent(r.id)).catch(() => null) : null; // markiert als gelesen
  const msgs = await api("nachrichten");
  const rows = [];
  groupBy(msgs, x => x.welle).forEach((items, welle) => {
    rows.push(h("div", { class: "group" }, "Runde " + welle));
    items.forEach(x => {
      const unread = !x.gelesen && x.id !== r.id;
      rows.push(h("a", { class: "row" + (x.id === r.id ? " active" : "") + (unread ? " unread" : ""), href: href("eingang", x.id) },
        h("span", { class: "unread-dot" + (unread ? "" : " off") }),
        h("span", { class: "row-main" }, h("span", { class: "row-title" }, x.betreff), h("span", { class: "row-sub" }, senderName(x.von) + " · " + (TYPEN[x.typ] || [x.typ])[0])),
        h("span", { class: "row-sub" }, hhmm(x.empfangen))));
    });
  });
  let detail = null;
  let action = null;
  if (m) {
    action = m.fall_id
      ? h("a", { class: "btn", href: href("faelle", m.fall_id) }, icon("cases"), "Fall öffnen")
      : h("button", { class: "btn primary", onclick: async () => {
        try { const res = await api("fall", { nachricht_id: m.id }); toast("Fall " + fallNr(res.fall_id) + " angelegt."); go("faelle", res.fall_id); }
        catch (e) { toast(e.message, true); }
      } }, icon("cases"), "Fall anlegen");
    detail = h("div", { class: "detail" }, h("div", { class: "detail-grid" },
      h("div", { class: "thread" },
        h("h1", {}, m.betreff),
        h("div", { class: "chips", style: "margin: 10px 0 24px" }, typChip(m.typ), chip("Runde " + m.welle)),
        messageBlock(m),
        m.anhaenge.length ? h("div", { class: "attachments" }, m.anhaenge.map(attachLink)) : null),
      h("aside", { class: "props" },
        h("div", { class: "prop-group", style: "margin-top: 0" }, "Eigenschaften"),
        prop("Typ", typChip(m.typ)), prop("Runde", String(m.welle)), prop("Von", senderName(m.von)), prop("Empfangen", fmtTime(m.empfangen)),
        prop("Kunde", kundeLink(m.kunde_id)), prop("Fall", m.fall_id ? h("a", { href: href("faelle", m.fall_id) }, fallNr(m.fall_id)) : "noch keiner"))));
  }
  const list = msgs.length ? rows : [emptyState("inbox", "Noch keine Nachrichten. Rufe das Postfach ab.", h("button", { class: "btn primary", onclick: openPostfach }, icon("sync"), "Postfach abrufen"))];
  return col(topbar(m ? ["Arbeitskorb", "Eingang", m.id] : ["Arbeitskorb", "Eingang"], action), splitView(list, detail, "inbox", "Wähle links eine Nachricht."));
}

async function viewFaelle(r) {
  const [fs, prods, kunden] = await Promise.all([api("faelle"), api("produkte"), api("kunden")]);
  const rows = [];
  [["in_bearbeitung", "In Bearbeitung"], ["neu", "Neu"], ["gesendet", "Gesendet"]].forEach(([st, label]) => {
    const items = fs.filter(f => f.status === st);
    if (!items.length) return;
    rows.push(h("div", { class: "group" }, label));
    items.forEach(f => rows.push(h("a", { class: "row" + (String(f.id) === r.id ? " active" : ""), href: href("faelle", f.id) },
      statusIcon(f.status), h("span", { class: "row-id" }, fallNr(f.id)),
      h("span", { class: "row-main" }, h("span", { class: "row-title" }, f.titel), h("span", { class: "row-sub" }, plural(f.offene_aufgaben, "offene Aufgabe", "offene Aufgaben") + " · " + plural(f.entwuerfe, "Entwurf", "Entwürfe"))))));
  });
  let detail = null;
  if (r.id && /^\d+$/.test(r.id)) {
    const f = await api("fall/" + r.id).catch(() => null);
    if (f) detail = fallDetail(f, prods, kunden);
  }
  const list = fs.length ? rows : [emptyState("cases", "Noch kein Fall. Lege im Eingang aus einer Nachricht einen an.", h("a", { class: "btn primary", href: "#/eingang" }, icon("inbox"), "Zum Eingang"))];
  return col(topbar(detail ? ["Arbeitskorb", "Fälle", fallNr(r.id)] : ["Arbeitskorb", "Fälle"]), splitView(list, detail, "cases", "Wähle links einen Fall."));
}

function fallDetail(f, prods, kunden) {
  const m = f.nachricht;
  const offen = f.aufgaben.filter(a => a.status === "offen").length;
  const prodName = id => (prods.find(p => p.id === id) || {}).name;
  const kundeName = id => (kunden.find(k => k.id === id) || {}).name;
  const st = FALL_STATUS[f.status] || [f.status, ""];
  return h("div", { class: "detail" }, h("div", { class: "detail-grid" },
    h("div", { class: "thread" },
      h("h1", {}, f.titel),
      h("p", { class: "lead" }, fallNr(f.id), m ? [" · aus Nachricht ", h("a", { href: href("eingang", m.id) }, m.id)] : null),
      m ? messageBlock(m) : null,
      h("div", { class: "section" }, h("div", { class: "section-head" }, "Aufgaben", h("span", { class: "meta" }, offen ? plural(offen, "offen", "offen") : "alle erledigt")),
        f.aufgaben.map(a => h("div", { class: "task" + (a.status === "erledigt" ? " done" : "") }, h("span", { class: "check" + (a.status === "erledigt" ? " on" : "") }), h("span", { class: "task-title" }, a.titel)))),
      h("div", { class: "section" }, h("div", { class: "section-head" }, "Entwürfe", h("span", { class: "meta" }, "Claude bereitet vor, du entscheidest")),
        f.entwuerfe.length ? f.entwuerfe.map(e => draftBlock(e, prodName, kundeName)) : h("p", { class: "muted" }, "Noch kein Entwurf. Bitte Claude in der Claude-App, einen vorzubereiten.")),
      h("div", { class: "section" }, h("div", { class: "section-head" }, "Protokoll", h("span", { class: "meta" }, plural(f.protokoll.length, "Eintrag", "Einträge"))),
        f.protokoll.slice().reverse().map(eventRow))),
    h("aside", { class: "props" },
      h("div", { class: "prop-group", style: "margin-top: 0" }, "Eigenschaften"),
      prop("Status", h("span", { class: "chips" }, statusIcon(f.status), st[0])),
      prop("Kunde", kundeLink(f.kunde_id, kundeName(f.kunde_id))),
      prop("Erstellt", fmtTime(f.erstellt)),
      prop("Aufgaben", f.aufgaben.length - offen + " von " + f.aufgaben.length + " erledigt"),
      prop("Entwürfe", String(f.entwuerfe.length)),
      m && m.anhaenge.length ? [h("div", { class: "prop-group" }, "Anhang"), h("div", { class: "chips" }, m.anhaenge.map(attachLink))] : null)));
}

function eventRow(e) {
  const [who, cls] = AKTEURE[e.akteur] || [e.akteur, "system"];
  const extra = e.details && e.details.text ? ": " + e.details.text : (e.details && e.details.an ? " an " + e.details.an : "");
  return h("div", { class: "event" }, h("span", { class: "pt " + cls }), h("span", {}, h("strong", {}, who), " · ", (EREIGNISSE[e.art] || e.art) + extra), h("span", { class: "when" }, fmtTime(e.zeit)));
}

function draftBlock(e, prodName, kundeName) {
  const sent = e.status !== "entwurf";
  const an = h("input", { value: e.an, disabled: sent, "aria-label": "An" });
  const betreff = h("input", { value: e.betreff, disabled: sent, "aria-label": "Betreff" });
  const text = h("textarea", { disabled: sent, "aria-label": "Text" });
  text.value = e.text;
  const fit = () => { text.style.height = "auto"; text.style.height = Math.max(text.scrollHeight + 2, 200) + "px"; };
  text.addEventListener("input", fit);
  requestAnimationFrame(fit);
  const notice = sent
    ? h("div", { class: "draft-notice sent" }, icon("check"), "Gesendet. Die Mail liegt im Postausgang; es ging nichts ins Netz.")
    : h("div", { class: "draft-notice" }, icon(e.von === "claude" ? "bot" : "user"), e.von === "claude" ? "Entwurf von Claude. Du prüfst, änderst und sendest. Claude kann nicht senden." : "Dein Entwurf.");

  const ev = (e.belege || []).map(b => {
    const label = b.typ === "produkt" ? b.ref + (prodName(b.ref) ? " · " + prodName(b.ref) : "")
      : b.typ === "kunde" ? b.ref + (kundeName(b.ref) ? " · " + kundeName(b.ref) : "") : b.ref;
    const ic = b.typ === "artikel" || b.typ === "datenblatt" ? "book" : b.typ === "produkt" ? "flask" : b.typ === "kunde" ? "building" : "clip";
    const content = [icon(ic, 13), label, b.hinweis ? h("span", { class: "hint-text" }, "– " + b.hinweis) : null];
    if (b.typ === "produkt") return h("a", { href: panelHref("p", b.ref) }, content);
    if (b.typ === "kunde") return h("a", { href: panelHref("k", b.ref) }, content);
    if (b.typ === "artikel") return h("a", { href: href("regelwerk") }, content);
    if (b.typ === "nachricht") return h("a", { href: href("eingang", b.ref) }, content);
    return h("span", { class: "ev" }, content);
  });
  const evidence = h("div", { class: "evidence" }, h("div", { class: "evidence-title" }, "Belege"),
    ev.length ? ev : h("span", { class: "muted small" }, "Keine Belege angegeben. Aussagen ohne Beleg solltest du nicht senden."));

  const save = h("button", { class: "btn", disabled: sent, onclick: async () => {
    try { await api("entwurf/" + e.id, { an: an.value, betreff: betreff.value, text: text.value }); toast("Gespeichert."); await render(true); }
    catch (x) { toast(x.message, true); }
  } }, "Speichern");

  let armed = false;
  let timer = null;
  const cancel = h("button", { class: "btn ghost", style: "display:none" }, "Abbrechen");
  const send = h("button", { class: "btn primary", disabled: sent }, icon("send"), "Senden");
  const disarm = () => {
    armed = false; clearTimeout(timer);
    send.replaceChildren(icon("send"), "Senden"); send.classList.remove("danger"); send.classList.add("primary"); cancel.style.display = "none";
  };
  cancel.addEventListener("click", disarm);
  send.addEventListener("click", async () => {
    if (!armed) {
      armed = true; send.replaceChildren(icon("send"), "Wirklich senden?"); send.classList.remove("primary"); send.classList.add("danger"); cancel.style.display = "";
      timer = setTimeout(disarm, 7000);
      return;
    }
    try {
      await api("entwurf/" + e.id, { an: an.value, betreff: betreff.value, text: text.value }); // gesendet wird, was du siehst
      await api("senden/" + e.id, {});
      toast("Im Postausgang abgelegt.");
      await render(true);
    } catch (x) { disarm(); toast(x.message, true); }
  });

  return h("div", { class: "draft" }, notice,
    h("div", { class: "field" }, h("label", {}, "An"), an),
    h("div", { class: "field" }, h("label", {}, "Betreff"), betreff),
    text, evidence,
    sent ? null : h("div", { class: "draft-foot" }, h("span", { class: "hint" }, "Gesendet wird nur in den Ordner „postausgang“."), cancel, save, send));
}

async function viewPostausgang(r) {
  const ps = await api("postausgang");
  const rows = ps.map(p => h("a", { class: "row" + (String(p.id) === r.id ? " active" : ""), href: href("postausgang", p.id) },
    h("span", { class: "status-icon done" }),
    h("span", { class: "row-main" }, h("span", { class: "row-title" }, p.betreff), h("span", { class: "row-sub" }, "an " + p.an)),
    h("span", { class: "row-sub" }, hhmm(p.gesendet))));
  const sel = ps.find(p => String(p.id) === r.id);
  const detail = sel ? h("div", { class: "detail" }, h("div", { class: "thread" },
    h("h1", {}, sel.betreff),
    h("div", { class: "chips", style: "margin: 10px 0 24px" }, chip("Gesendet", "solid-green"), chip(fmtTime(sel.gesendet))),
    h("div", { class: "message" }, h("div", { class: "avatar" }, initials(sel.an)),
      h("div", { class: "message-body" }, h("div", { class: "message-head" }, h("span", {}, "An ", h("strong", {}, sel.an))), h("div", { class: "message-text" }, sel.text))),
    sel.datei ? h("p", { class: "muted small", style: "margin-top: 28px" }, "Gespeichert als " + sel.datei + " im Ordner „postausgang“.") : null)) : null;
  const list = ps.length ? rows : [emptyState("send", "Noch nichts gesendet. Gesendete Mails erscheinen hier und als Datei im Ordner „postausgang“.")];
  return col(topbar(["Arbeitskorb", "Postausgang"]), splitView(list, detail, "send", "Wähle links eine gesendete Mail."));
}

async function viewRegelwerk(r) {
  const d = await api("regelwerk");
  if (!d.verfuegbar.length) return col(topbar(["Wissen", "Regelwerk"]), emptyState("book", "Noch keine Verordnung im Postfach. Rufe das Postfach ab.", h("button", { class: "btn primary", onclick: openPostfach }, icon("sync"), "Postfach abrufen")));
  const rw = d.regelwerk;
  const ber = rw.berichtigung;
  const geaendert = {};
  ((ber && ber.aenderungen) || []).forEach(a => { geaendert[a.anwendung + "|" + a.feld] = a; });
  const cell = (a, feld) => {
    const c = geaendert[a.id + "|" + feld];
    if (c) return h("span", { class: "changed" }, fmtDateShort(c.neu), h("span", { class: "chip solid-orange", title: "vorher " + c.alt }, "berichtigt"));
    return a[feld] ? fmtDateShort(a[feld]) : h("span", { class: "faint" }, "–");
  };
  const sel = r.q.text && d.verfuegbar.includes(r.q.text) ? r.q.text : d.haupttext;
  const label = n => (n.toLowerCase().includes("berichtigung") ? "Berichtigung" : "Verordnung");
  const tbl = (heads, rows) => h("table", {}, h("thead", {}, h("tr", {}, heads.map(t => h("th", {}, t)))), h("tbody", {}, rows));
  return col(topbar(["Wissen", "Regelwerk"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, rw.titel || rw.id),
    h("p", { class: "lead" }, "Fiktiver Übungstext, kein geltendes Recht."),
    h("div", { class: "facts" },
      fact("Grenzwert", rw.grenzwert_mg_l + " mg/l", String(rw.grenzwert_regel || "").replace(/_/g, " ")),
      fact("In Kraft ab", fmtDateShort(rw.inkrafttreten), "veröffentlicht " + fmtDateShort(rw.veroeffentlicht)),
      fact("Kunden informieren bis", fmtDateShort(rw.informationspflicht_bis), rw.informationspflicht_artikel || ""),
      fact("Geltungsbereich", (rw.geltungsbereich_laender || []).join(" · "), "CH, GB, NO außerhalb")),
    ber ? h("p", { class: "lead", style: "margin: 18px 0 0" }, chip("Berichtigung liegt vor", "solid-orange"), "  Geänderte Fristen sind in der Tabelle markiert.") : null,
    h("div", { class: "section" }, h("div", { class: "section-head" }, "Fristen je Anwendung"),
      tbl(["Anwendung", "Kennzeichnung ab", "Inverkehrbringen verboten ab", "Verwendung verboten ab", "Bestandsmeldung bis"],
        rw.anwendungen.map(a => h("tr", {}, h("td", {}, h("div", {}, a.name), h("div", { class: "faint small" }, a.artikel)),
          h("td", {}, cell(a, "kennzeichnung_ab")), h("td", {}, cell(a, "inverkehrbringen_verbot_ab")), h("td", {}, cell(a, "verwendung_verbot_ab")), h("td", {}, cell(a, "bestandsmeldung_bis")))))),
    (rw.ausnahmen || []).length ? h("div", { class: "section" }, h("div", { class: "section-head" }, "Ausnahmen"),
      tbl(["Ausnahme", "Gilt für", "Bis", "Bedingung"], rw.ausnahmen.map(x => h("tr", {},
        h("td", {}, h("div", {}, x.beschreibung), h("div", { class: "faint small" }, x.artikel)),
        h("td", {}, (x.gilt_fuer_segmente || []).join(", ") + ((x.gilt_fuer_anwendungen || []).length ? " · " + x.gilt_fuer_anwendungen.map(anwendung).join(", ") : "")),
        h("td", { class: "mono" }, fmtDateShort(x.befristet_bis)), h("td", { class: "muted" }, x.bedingung || "–"))))) : null,
    h("div", { class: "tabs" }, d.verfuegbar.map(n => h("a", { class: "tab" + (n === sel ? " on" : ""), href: href("regelwerk", null, { text: n }) }, label(n)))),
    markdown(d.texte[sel] || ""))));
}

function tableWithSearch(placeholder, items, segOf, rowFn, headers) {
  let q = "";
  let seg = "";
  const tbody = h("tbody", {});
  const segs = [...new Set(items.map(segOf))].sort();
  const segBox = h("div", { class: "seg" });
  const draw = () => {
    segBox.replaceChildren(h("button", { class: seg === "" ? "on" : "", onclick: () => { seg = ""; draw(); } }, "Alle"),
      ...segs.map(s => h("button", { class: seg === s ? "on" : "", onclick: () => { seg = s; draw(); } }, s)));
    const shown = items.filter(i => (!seg || segOf(i) === seg) && (!q || JSON.stringify(i).toLowerCase().includes(q)));
    tbody.replaceChildren(...(shown.length ? shown.map(rowFn) : [h("tr", {}, h("td", { colspan: headers.length, class: "muted" }, "Nichts gefunden."))]));
  };
  const input = h("input", { placeholder: placeholder, "aria-label": placeholder });
  input.addEventListener("input", () => { q = input.value.trim().toLowerCase(); draw(); });
  draw();
  return h("div", {}, h("div", { class: "toolbar" }, h("label", { class: "search" }, icon("search", 15), input), segBox),
    h("table", {}, h("thead", {}, h("tr", {}, headers.map(t => h("th", {}, t)))), tbody));
}

async function viewProdukte() {
  const ps = await api("produkte");
  const rows = p => h("tr", { class: "click", onclick: () => { location.hash = panelHref("p", p.id); } },
    h("td", { class: "faint mono" }, p.id), h("td", {}, p.name), h("td", {}, p.schaumart), h("td", { class: "muted" }, p.basis),
    h("td", { class: "mono" }, p.pfas_wert === null ? h("span", { class: "faint" }, "kein Messwert") : p.pfas_wert + " " + p.pfas_einheit),
    h("td", { class: "muted mono" }, "v" + p.sdb_version + " · " + fmtDateShort(p.sdb_datum)),
    h("td", {}, p.status === "aktiv" ? h("span", { class: "muted" }, "aktiv") : chip(p.status, "solid-orange")));
  return col(topbar(["Wissen", "Produkte"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, "Produkte"), h("p", { class: "lead" }, plural(ps.length, "Produkt", "Produkte") + " mit Fluorgehalt, Datenblatt-Stand und Nachfolger."),
    tableWithSearch("Produkt suchen …", ps, p => p.schaumart, rows, ["ID", "Produkt", "Schaumart", "Basis", "PFAS-Messwert", "Sicherheitsdatenblatt", "Status"]))));
}

async function viewKunden() {
  const ks = await api("kunden");
  const rows = k => h("tr", { class: "click", onclick: () => { location.hash = panelHref("k", k.id); } },
    h("td", { class: "faint mono" }, k.id), h("td", {}, k.name), h("td", {}, k.segment), h("td", {}, k.land),
    h("td", {}, h("span", { class: "chips" }, k.seveso ? chip("Seveso") : null, k.key_account ? chip("Key Account", "solid-blue") : null, k.ist_haendler ? chip("Händler") : null, k.status !== "aktiv" ? chip(k.status, "solid-orange") : null)));
  return col(topbar(["Wissen", "Kunden"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, "Kunden"), h("p", { class: "lead" }, plural(ks.length, "Kunde", "Kunden") + " aus dem Kundenstamm, mit allen Lieferungen und Anlagen."),
    tableWithSearch("Kunde suchen …", ks, k => k.segment, rows, ["ID", "Kunde", "Segment", "Land", "Merkmale"]))));
}

async function viewProtokoll() {
  const es = await api("protokoll");
  const body = es.length
    ? h("table", {}, h("thead", {}, h("tr", {}, ["Zeit", "Wer", "Was", "Fall"].map(t => h("th", {}, t)))),
      h("tbody", {}, es.map(e => {
        const [who, cls] = AKTEURE[e.akteur] || [e.akteur, "system"];
        const extra = e.details && e.details.text ? ": " + e.details.text : (e.details && e.details.an ? " an " + e.details.an : "");
        return h("tr", {}, h("td", { class: "muted mono", style: "white-space:nowrap" }, fmtTime(e.zeit)),
          h("td", {}, h("span", { class: "event", style: "padding:0" }, h("span", { class: "pt " + cls }), h("strong", {}, who))),
          h("td", {}, EREIGNISSE[e.art] || e.art, extra ? h("span", { class: "muted" }, extra) : null),
          h("td", {}, e.fall_id ? h("a", { href: href("faelle", e.fall_id) }, fallNr(e.fall_id)) : h("span", { class: "faint" }, "–")));
      })))
    : emptyState("list", "Noch nichts protokolliert. Jeder Schritt von dir und von Claude erscheint hier.");
  return col(topbar(["Nachweis", "Protokoll"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, "Protokoll"), h("p", { class: "lead" }, "Was Claude vorbereitet hat und was du entschieden hast, mit Zeit und Urheber."), body)));
}

const VIEWS = { eingang: viewEingang, faelle: viewFaelle, postausgang: viewPostausgang, regelwerk: viewRegelwerk, produkte: viewProdukte, kunden: viewKunden, protokoll: viewProtokoll };

/* ---------- Seitenpanel (Produkt, Kunde) ---------- */
async function renderPanel(r) {
  document.querySelectorAll(".scrim:not(.dlg):not(.pal), .panel").forEach(n => n.remove());
  const id = r.q.p || r.q.k;
  if (!id) return;
  let panel;
  try { panel = r.q.p ? await productPanel(r.q.p) : await customerPanel(r.q.k); }
  catch (e) { toast(e.message, true); return; }
  document.body.append(h("div", { class: "scrim", onclick: closePanel }), panel);
}

function panelShell(idText, ...body) {
  return h("aside", { class: "panel", role: "dialog", "aria-modal": "true" },
    h("div", { class: "panel-head" }, h("span", { class: "faint mono" }, idText), h("div", { class: "spacer" }),
      h("button", { class: "icon-btn", title: "Schließen (Esc)", onclick: closePanel }, icon("close"))),
    h("div", { class: "panel-body" }, body));
}
const kv = rows => h("dl", { class: "kv" }, rows.filter(Boolean).map(([k, v]) => [h("dt", {}, k), h("dd", {}, v)]));

async function productPanel(id) {
  const [p, kunden] = await Promise.all([api("produkt/" + encodeURIComponent(id)), api("kunden")]);
  const nachfolger = p.nachfolger_id ? h("a", { href: panelHref("p", p.nachfolger_id) }, p.nachfolger_id) : h("span", { class: "faint" }, "keiner");
  const an = (p.geliefert_an || []).map(kid => { const k = kunden.find(x => x.id === kid); return h("a", { class: "attach", href: panelHref("k", kid) }, icon("building", 14), k ? k.name : kid); });
  return panelShell(p.id,
    h("h2", {}, p.name),
    h("div", { class: "chips", style: "margin-top: 8px" }, chip(p.schaumart), chip(p.basis), p.status === "aktiv" ? null : chip(p.status, "solid-orange")),
    kv([
      ["PFAS-Messwert", p.pfas_wert === null ? h("span", { class: "faint" }, "kein Messwert vorhanden") : h("strong", {}, p.pfas_wert + " " + p.pfas_einheit)],
      ["Deklariert fluorfrei", p.fluorfrei_deklariert ? "ja" : "nein"],
      ["Brandklassen", (p.brandklassen || []).join(", ") || "–"],
      ["Einsatzbereiche", (p.einsatzbereiche || []).join(", ") || "–"],
      ["Zumischrate", p.zumischrate_prozent != null ? String(p.zumischrate_prozent).replace(".", ",") + " %" : "–"],
      ["Sicherheitsdatenblatt", "Version " + p.sdb_version + " vom " + fmtDate(p.sdb_datum)],
      ["Technisches Datenblatt", p.tdb_version ? "Version " + p.tdb_version : "–"],
      ["Nachfolger", nachfolger],
      p.bemerkung ? ["Bemerkung", p.bemerkung] : null,
    ]),
    h("div", { class: "section" }, h("div", { class: "section-head" }, "Geliefert an", h("span", { class: "meta" }, plural(an.length, "Kunde", "Kunden"))),
      an.length ? h("div", { class: "attachments", style: "margin-top: 0" }, an) : h("p", { class: "muted" }, "An keinen Kunden.")));
}

async function customerPanel(id) {
  const [k, kunden] = await Promise.all([api("kunde/" + encodeURIComponent(id)), api("kunden")]);
  const ap = k.ansprechpartner || {};
  const end = (k.beliefert_endkunden || []).map(kid => h("a", { href: panelHref("k", kid) }, ((kunden.find(x => x.id === kid) || {}).name) || kid));
  return panelShell(k.id,
    h("h2", {}, k.name),
    h("div", { class: "chips", style: "margin-top: 8px" }, chip(k.segment), chip(k.land), k.seveso ? chip("Seveso") : null, k.key_account ? chip("Key Account", "solid-blue") : null, k.ist_haendler ? chip("Händler") : null, k.status !== "aktiv" ? chip(k.status, "solid-orange") : null),
    kv([
      ["Ansprechperson", ap.name ? ap.name + ", " + ap.rolle : "–"], ["E-Mail", ap.email || "–"], ["Sprache", (k.sprache || "").toUpperCase()],
      (k.ausnahme_ids || []).length ? ["Ausnahmen", k.ausnahme_ids.join(", ")] : null,
      end.length ? ["Beliefert", h("span", {}, end.map((a, i) => [i ? ", " : "", a]))] : null,
      k.bemerkung ? ["Bemerkung", k.bemerkung] : null,
    ]),
    h("div", { class: "section" }, h("div", { class: "section-head" }, "Lieferungen und Anlagen", h("span", { class: "meta" }, plural(k.lieferungen.length, "Lieferung", "Lieferungen"))),
      k.lieferungen.length ? h("table", {}, h("thead", {}, h("tr", {}, ["Produkt", "Anwendung", "Menge", "Zuletzt"].map(t => h("th", {}, t)))),
        h("tbody", {}, k.lieferungen.map(l => h("tr", {},
          h("td", {}, h("a", { href: panelHref("p", l.produkt_id) }, l.produkt_name || l.produkt_id), h("div", { class: "faint small" }, l.produkt_id + (l.pfas_wert === null ? " · kein Messwert" : " · " + l.pfas_wert + " " + l.pfas_einheit))),
          h("td", {}, anwendung(l.anwendung), l.anlage ? h("div", { class: "faint small" }, l.anlage) : null),
          h("td", { class: "mono" }, l.menge_l + " l"), h("td", { class: "muted mono" }, fmtDateShort(l.letzte_lieferung)))))) : h("p", { class: "muted" }, "Keine Lieferungen.")));
}

/* ---------- Postfach-Dialog ---------- */
function closeDialog() { document.querySelectorAll(".scrim.dlg, .dialog").forEach(n => n.remove()); }
function openPostfach() {
  closeDialog();
  const next = S && S.naechste_welle;
  let body;
  if (!next) {
    body = h("div", { class: "dialog" }, h("h2", {}, "Postfach abrufen"), h("p", {}, "Alle Nachrichten sind abgerufen. Es kommt nichts mehr nach."),
      h("div", { class: "actions" }, h("button", { class: "btn", onclick: closeDialog }, "Schließen")));
  } else {
    const code = h("input", { placeholder: "Code", autocomplete: "off", "aria-label": "Code vom Dozenten" });
    const err = h("div", { class: "err" });
    const run = async () => {
      try { const res = await api("welle", { welle: next, code: code.value }); closeDialog(); toast(plural(res.neue_nachrichten, "neue Nachricht", "neue Nachrichten") + " abgerufen."); await render(true); }
      catch (e) { err.textContent = e.message; }
    };
    code.addEventListener("keydown", ev => { if (ev.key === "Enter") run(); });
    body = h("div", { class: "dialog" }, h("h2", {}, "Runde " + next + " abrufen"), h("p", {}, "Den Code sagt dir der Dozent."), code, err,
      h("div", { class: "actions" }, h("button", { class: "btn ghost", onclick: closeDialog }, "Abbrechen"), h("button", { class: "btn primary", onclick: run }, "Abrufen")));
    setTimeout(() => code.focus(), 30);
  }
  document.body.append(h("div", { class: "scrim dlg", style: "z-index:40", onclick: closeDialog }), body);
}

/* ---------- Befehlspalette (⌘K / Strg+K) ---------- */
function closePalette() { document.querySelectorAll(".scrim.pal, .palette").forEach(n => n.remove()); }
async function openPalette() {
  closePalette();
  const [fs, ps, ks] = await Promise.all([api("faelle"), api("produkte"), api("kunden")]);
  const items = [
    ["Eingang", "Ansicht", () => go("eingang")], ["Fälle", "Ansicht", () => go("faelle")], ["Postausgang", "Ansicht", () => go("postausgang")],
    ["Regelwerk", "Ansicht", () => go("regelwerk")], ["Produkte", "Ansicht", () => go("produkte")], ["Kunden", "Ansicht", () => go("kunden")], ["Protokoll", "Ansicht", () => go("protokoll")],
    ["Postfach abrufen", "Aktion", openPostfach],
  ].concat(fs.map(f => [fallNr(f.id) + " · " + f.titel, "Fall", () => go("faelle", f.id)]))
    .concat(ps.map(p => [p.id + " · " + p.name, "Produkt", () => go("produkte", null, { p: p.id })]))
    .concat(ks.map(k => [k.id + " · " + k.name, "Kunde", () => go("kunden", null, { k: k.id })]));
  const input = h("input", { placeholder: "Springen zu …", "aria-label": "Suchen" });
  const ul = h("ul", {});
  let sel = 0;
  let shown = [];
  const draw = () => {
    const q = input.value.trim().toLowerCase();
    shown = items.filter(i => !q || i[0].toLowerCase().includes(q)).slice(0, 40);
    sel = Math.min(sel, Math.max(shown.length - 1, 0));
    ul.replaceChildren(...(shown.length ? shown.map((i, n) => h("li", { class: n === sel ? "sel" : "", onclick: () => { closePalette(); i[2](); } }, i[0], h("span", { class: "kind" }, i[1]))) : [h("li", { class: "none" }, "Nichts gefunden.")]));
  };
  input.addEventListener("input", () => { sel = 0; draw(); });
  input.addEventListener("keydown", ev => {
    if (ev.key === "ArrowDown") { sel = Math.min(sel + 1, shown.length - 1); draw(); ev.preventDefault(); }
    else if (ev.key === "ArrowUp") { sel = Math.max(sel - 1, 0); draw(); ev.preventDefault(); }
    else if (ev.key === "Enter" && shown[sel]) { closePalette(); shown[sel][2](); }
  });
  draw();
  document.body.append(h("div", { class: "scrim pal", style: "z-index:40", onclick: closePalette }), h("div", { class: "palette" }, input, ul));
  input.focus();
}

/* ---------- Start ---------- */
let lastKey = null;
let rendering = Promise.resolve();
function render(force) {
  rendering = rendering.then(() => doRender(force)).catch(e => toast((e && e.message) || String(e), true));
  return rendering;
}
async function doRender(force) {
  const r = parseRoute();
  const key = r.view + "/" + (r.id || "") + "?" + (r.q.text || "");
  if (force || key !== lastKey) {
    const sameView = lastKey && lastKey.split("/")[0] === r.view;
    const listTop = sameView && mainEl.querySelector(".list") ? mainEl.querySelector(".list").scrollTop : 0;
    const threadTop = lastKey === key && mainEl.querySelector(".thread") ? mainEl.querySelector(".thread").scrollTop : 0;
    Object.entries(navEls).forEach(([k, n]) => n.a.classList.toggle("active", k === r.view));
    let node;
    try { node = await (VIEWS[r.view] || viewEingang)(r); }
    catch (e) { node = col(topbar(["Fehler"]), emptyState("list", e.message)); }
    mainEl.replaceChildren(node);
    const l2 = mainEl.querySelector(".list");
    if (l2 && listTop) l2.scrollTop = listTop;
    const t2 = mainEl.querySelector(".thread");
    if (t2 && threadTop) t2.scrollTop = threadTop;
    lastKey = key;
    await refreshStatus();
  }
  await renderPanel(r);
}

window.addEventListener("hashchange", () => render(false));
window.addEventListener("keydown", ev => {
  if ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === "k") { ev.preventDefault(); openPalette(); }
  else if (ev.key === "Escape") {
    if (document.querySelector(".palette")) closePalette();
    else if (document.querySelector(".dialog")) closeDialog();
    else if (document.querySelector(".panel")) closePanel();
  }
});
window.addEventListener("error", e => toast("Fehler: " + e.message, true));
window.addEventListener("unhandledrejection", e => toast("Fehler: " + ((e.reason && e.reason.message) || e.reason), true));

buildShell();
render(true);
