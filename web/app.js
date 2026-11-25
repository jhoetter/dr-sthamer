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
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
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
  shield: '<path d="M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6z"/><path d="m9 12 2 2 4-4"/>',
  clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
  chart: '<path d="M5 19V9M12 19V5M19 19v-7"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="2"/>',
  chevron: '<path d="m6 9 6 6 6-6"/>',
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
const fallNr = id => "#" + id; // Nummer eines To-dos (intern: Fall)
const plural = (n, one, many) => n + " " + (n === 1 ? one : many);

const TYPEN = {
  aufgabe: ["Interner Auftrag", "dot-blue"], kundenanfrage: ["Kundenanfrage", "dot-green"], verordnung: ["Verordnung", "dot-orange"],
  berichtigung: ["Berichtigung", "dot-red"], intern: ["Intern", "dot-grey"], email: ["E-Mail", "dot-blue"],
};
const FALL_STATUS = { neu: ["Neu", ""], in_bearbeitung: ["In Bearbeitung", "progress"], gesendet: ["Gesendet", "done"] };
const ANWENDUNGEN = {
  tragbarer_feuerloescher: "Tragbarer Feuerlöscher", fahrbarer_feuerloescher: "Fahrbarer Feuerlöscher",
  stationaere_anlage: "Stationäre Löschanlage", feuerwehrfahrzeug: "Feuerwehrfahrzeug",
  uebung_training: "Übung und Training", lager_bestand: "Lagerbestand",
};
const EREIGNISSE = {
  postfach_abgerufen: "Postfach abgerufen", belegpruefung_abgewiesen: "Belegprüfung abgewiesen", fall_angelegt: "To-do angelegt", entwurf_angelegt: "Entwurf angelegt",
  entwurf_geaendert: "Entwurf geändert", gesendet: "Gesendet", notiz: "Notiz",
  zur_freigabe: "Zur Freigabe eingereicht", geplant: "Eingeplant", freigegeben: "Freigegeben", abgelehnt: "Abgelehnt",
  versand_gestoppt: "Versand gestoppt", uhr_vorgespult: "Übungsuhr vorgespult", einschaetzung: "Einschätzung festgehalten",
  postfach_verbunden: "E-Mail-Postfach verbunden", echte_mail_gesendet: "E-Mail gesendet", echte_mail_abgeholt: "E-Mails abgeholt",
};
const STUFEN = { pflichtfreigabe: "Pflichtfreigabe", eingriffsfenster: "Eingriffsfenster" };
const ES_LABEL = {
  betroffen: ["betroffen", "solid-orange"], nicht_betroffen: ["nicht betroffen", "solid-green"],
  mittelbar: ["mittelbar", "solid-blue"], unklar: ["unklar", "solid-grey"],
};
const esChip = es => { const [t, c] = ES_LABEL[es.ergebnis] || [es.ergebnis, "solid-grey"]; return chip(t, c); };
const AKTEURE = { mensch: ["Du", "mensch"], claude: ["Claude", "claude"], system: ["System", "system"] };

const chip = (text, cls) => h("span", { class: "chip " + (cls || "") }, text);
const typChip = t => { const [txt, cls] = TYPEN[t] || [t, "dot-grey"]; return chip(txt, cls); };
const statusIcon = st => h("span", { class: "status-icon " + ((FALL_STATUS[st] || [])[1] || "") });
const anwendung = id => ANWENDUNGEN[id] || id;
const faehig = name => !!(S && S.faehigkeiten && S.faehigkeiten[name]);

/* Übungsuhr: Zeiten der Übungswelt, nicht der Systemuhr */
const uhrText = () => (S && S.jetzt ? fmtDateShort(S.jetzt) + " · " + hhmm(S.jetzt) : "");
function restzeit(sendeAm) {
  if (!sendeAm || !S || !S.jetzt) return "";
  const min = Math.round((parseIso(sendeAm) - parseIso(S.jetzt)) / 60000);
  if (min <= 0) return "fällig";
  const std = Math.floor(min / 60);
  const rest = min % 60;
  return "in " + (std ? std + " Std." + (rest ? " " : "") : "") + (rest || !std ? rest + " Min." : "");
}

/* Protokolltext eines Ereignisses (für Fall und Protokoll) */
function eventText(e) {
  const d = e.details || {};
  let t = e.art === "gesendet" && d.automatisch ? "Automatisch gesendet" : (EREIGNISSE[e.art] || e.art);
  if (d.text) t += ": " + d.text;
  else if (d.grund) t += ": " + d.grund;
  else if (d.kunde_id) t += " · " + d.kunde_id + (d.ergebnis ? " · " + (ES_LABEL[d.ergebnis] || [d.ergebnis])[0] : "");
  else if (d.stunden) t += " um " + d.stunden + " Std." + (d.jetzt ? " (jetzt " + fmtTime(d.jetzt) + ")" : "");
  else if (d.an) t += " an " + d.an;
  if (d.stufe && STUFEN[d.stufe]) t += " · " + STUFEN[d.stufe];
  if (e.art === "geplant" && d.sende_am) t += " · Versand " + fmtTime(d.sende_am);
  return t;
}

async function api(pfad, body) {
  const opt = body === undefined ? {} : {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Sthamer-Token": TOKEN },
    body: JSON.stringify(body),
  };
  const r = await fetch("/api/" + pfad, opt);
  const d = await r.json().catch(() => ({ fehler: "Unerwartete Antwort." }));
  if (!r.ok) {
    if (r.status === 403 && /Cockpit im Browser/.test(d.fehler || "")) { // veraltete Seite (Kommandozentrale wurde neu gestartet)
      toast("Die Seite war veraltet und wird neu geladen.", true);
      setTimeout(() => location.reload(), 900);
    }
    throw new Error(d.fehler || "Fehler " + r.status);
  }
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
    uhrMenu(),
    h("button", { class: "btn ghost", title: "Suchen und springen", onclick: openPalette }, icon("search"), "Suchen", h("span", { class: "kbd" }, "⌘K")),
    h("button", { class: "btn", onclick: openPostfach }, icon("sync"), "Postfach abrufen"));
}

function uhrMenu() {
  if (!faehig("fenster")) return null;
  const menu = h("div", { class: "menu", hidden: true }, h("div", { class: "menu-head" }, "Übungsuhr vorspulen"),
    [[1, "+1 Stunde"], [6, "+6 Stunden"], [24, "+1 Tag"]].map(([std, text]) => h("button", { onclick: async () => {
      menu.hidden = true;
      try {
        const res = await api("uhr", { stunden: std });
        toast(res.automatisch_gesendet > 0 ? plural(res.automatisch_gesendet, "Mail", "Mails") + " automatisch gesendet." : "Übungsuhr vorgespult.");
        await render(true);
      } catch (e) { toast(e.message, true); }
    } }, text)));
  const btn = h("button", { class: "btn ghost", title: "Übungsuhr", onclick: ev => { ev.stopPropagation(); menu.hidden = !menu.hidden; } },
    icon("clock"), h("span", { class: "uhr-text" }, uhrText()), icon("chevron", 12));
  return h("div", { class: "uhr" }, btn, menu);
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

const anhangName = a => (/berichtigung/i.test(a) ? "Berichtigung zur Verordnung (fiktiv)" : "Verordnung (EU) 2026/9001 (fiktiv)");
const attachLink = a => h("a", { class: "attach", href: href("verordnung", null, { text: a.split("/").pop() }), title: "Im Wortlaut lesen" }, icon("clip", 14), anhangName(a));

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
  ["Arbeitskorb", [
    ["eingang", "Eingang", "inbox", s => s.ungelesen, true], ["faelle", "To-dos", "cases", s => s.offene_aufgaben],
    ["freigaben", "Freigaben", "shield", s => s.zur_freigabe, true, "freigabe"], ["geplant", "Geplant", "clock", s => s.geplant, false, "fenster"],
    ["postausgang", "Postausgang", "send", s => s.gesendet], ["email", "E-Mail", "mail", null, false, "email"]]],
  ["Wissen", [["regelwerk", "Regelwerk", "book"], ["produkte", "Produkte", "flask", s => s.produkte], ["kunden", "Kunden", "users", s => s.kunden]]],
  ["Nachweis", [["protokoll", "Protokoll", "list"], ["bericht", "Bericht", "chart", null, false, "bericht"]]],
];
let S = null;
let mainEl = null;
const navEls = {};

function buildShell() {
  const nav = h("nav", {});
  NAV.forEach(([label, items]) => {
    nav.append(h("div", { class: "nav-label" }, label));
    items.forEach(([key, text, ic, count, hot, cap]) => {
      const c = h("span", { class: "count" });
      const a = h("a", { class: "nav-item", href: "#/" + key, hidden: !!cap }, icon(ic), text, c);
      navEls[key] = { a, c, count, hot, cap };
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
    if (n.cap) n.a.hidden = !faehig(n.cap);
    const v = n.count && S ? n.count(S) : null;
    n.c.textContent = v ? String(v) : "";
    n.c.classList.toggle("hot", !!(n.hot && v));
  });
  const f = document.getElementById("foot-stand");
  if (f && S && S.heute) f.textContent = "Runde " + S.welle + " · Übungstag " + fmtDateShort((S.jetzt || S.heute).slice(0, 10));
  document.querySelectorAll(".uhr-text").forEach(n => { n.textContent = uhrText(); });
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
      ? h("a", { class: "btn", href: href("faelle", m.fall_id) }, icon("cases"), "To-do öffnen")
      : h("button", { class: "btn primary", onclick: async () => {
        try { const res = await api("fall", { nachricht_id: m.id }); toast("To-do " + fallNr(res.fall_id) + " angelegt."); go("faelle", res.fall_id); }
        catch (e) { toast(e.message, true); }
      } }, icon("cases"), "To-do anlegen");
    detail = h("div", { class: "detail" }, h("div", { class: "detail-grid" },
      h("div", { class: "thread" },
        h("h1", {}, m.betreff),
        h("div", { class: "chips", style: "margin: 10px 0 24px" }, typChip(m.typ), chip("Runde " + m.welle)),
        m.anhaenge.length ? h("div", { class: "attachments", style: "margin: 0 0 18px" }, h("span", { class: "muted small", style: "align-self: center" }, "Anhang:"), m.anhaenge.map(attachLink)) : null,
        messageBlock(m)),
      h("aside", { class: "props" },
        h("div", { class: "prop-group", style: "margin-top: 0" }, "Eigenschaften"),
        prop("Typ", typChip(m.typ)), prop("Runde", String(m.welle)), prop("Von", senderName(m.von)), prop("Empfangen", fmtTime(m.empfangen)),
        prop("Kunde", kundeLink(m.kunde_id)), prop("To-do", m.fall_id ? h("a", { href: href("faelle", m.fall_id) }, "To-do " + fallNr(m.fall_id)) : "noch keins"))));
  }
  const list = msgs.length ? rows : [emptyState("inbox", "Noch keine Nachrichten. Rufe das Postfach ab.", h("button", { class: "btn primary", onclick: openPostfach }, icon("sync"), "Postfach abrufen"))];
  return col(topbar(m ? ["Arbeitskorb", "Eingang", m.id] : ["Arbeitskorb", "Eingang"], action), splitView(list, detail, "inbox", "Wähle links eine Nachricht."));
}

async function viewFaelle(r) {
  const [fs, prods, kunden] = await Promise.all([api("faelle"), api("produkte"), api("kunden")]);
  const rows = [h("div", { class: "list-hint" }, "Ein To-do entsteht aus einer Mail, auf die jemand reagieren muss. Es ist erledigt, wenn die Antwort raus ist.")];
  const stand = f => {
    if (!f.offene_aufgaben) return "erledigt";
    if (f.status === "gesendet") return "Antwort ist raus, aber das To-do ist noch nicht abgehakt";
    return f.entwuerfe ? plural(f.entwuerfe, "Entwurf liegt vor", "Entwürfe liegen vor") : "noch kein Entwurf";
  };
  [[f => f.offene_aufgaben > 0, "Offen"], [f => !f.offene_aufgaben, "Erledigt"]].forEach(([test, label]) => {
    const items = fs.filter(test);
    if (!items.length) return;
    rows.push(h("div", { class: "group" }, label + " · " + items.length));
    items.forEach(f => rows.push(h("a", { class: "row" + (String(f.id) === r.id ? " active" : "") + (f.offene_aufgaben ? "" : " row-done"), href: href("faelle", f.id) },
      h("span", { class: "check" + (f.offene_aufgaben ? "" : " on") }), h("span", { class: "row-id" }, fallNr(f.id)),
      h("span", { class: "row-main" }, h("span", { class: "row-title" }, f.titel), h("span", { class: "row-sub" }, stand(f))))));
  });
  let detail = null;
  if (r.id && /^\d+$/.test(r.id)) {
    const f = await api("fall/" + r.id).catch(() => null);
    if (f) detail = fallDetail(f, prods, kunden);
  }
  const list = fs.length ? rows : [emptyState("cases", "Noch kein To-do. Ein To-do entsteht aus einer Mail im Eingang, auf die jemand reagieren muss: Claude legt es an, oder du mit dem Knopf „To-do anlegen“ in der Mail.", h("a", { class: "btn primary", href: "#/eingang" }, icon("inbox"), "Zum Eingang"))];
  return col(topbar(detail ? ["Arbeitskorb", "To-dos", fallNr(r.id)] : ["Arbeitskorb", "To-dos"]), splitView(list, detail, "cases", "Wähle links ein To-do."));
}

function fallDetail(f, prods, kunden) {
  const m = f.nachricht;
  const offen = f.aufgaben.filter(a => a.status === "offen").length;
  const prodName = id => (prods.find(p => p.id === id) || {}).name;
  const kundeName = id => (kunden.find(k => k.id === id) || {}).name;
  const auto = new Set(f.protokoll.filter(e => e.art === "gesendet" && e.details && e.details.automatisch).map(e => e.details.entwurf_id));
  return h("div", { class: "detail" }, h("div", { class: "detail-grid" },
    h("div", { class: "thread" },
      h("h1", {}, f.titel),
      h("p", { class: "lead" }, "To-do " + fallNr(f.id), m ? [" · entstanden aus der ", h("a", { href: href("eingang", m.id) }, "Mail im Eingang")] : null),
      m ? messageBlock(m) : null,
      h("div", { class: "section" }, h("div", { class: "section-head" }, "Was zu tun ist", h("span", { class: "meta" }, offen ? "offen" : "erledigt")),
        f.aufgaben.map(a => h("div", { class: "task" + (a.status === "erledigt" ? " done" : "") }, h("span", { class: "check" + (a.status === "erledigt" ? " on" : "") }), h("span", { class: "task-title" }, a.titel)))),
      h("div", { class: "section" }, h("div", { class: "section-head" }, "Entwürfe", h("span", { class: "meta" }, "Claude bereitet vor, du entscheidest")),
        f.entwuerfe.length ? f.entwuerfe.map(e => draftBlock(e, prodName, kundeName, { auto: auto.has(e.id) })) : h("p", { class: "muted" }, "Noch kein Entwurf. Bitte Claude in der Claude-App, einen vorzubereiten.")),
      h("div", { class: "section" }, h("div", { class: "section-head" }, "Protokoll", h("span", { class: "meta" }, plural(f.protokoll.length, "Eintrag", "Einträge"))),
        f.protokoll.slice().reverse().map(eventRow))),
    h("aside", { class: "props" },
      h("div", { class: "prop-group", style: "margin-top: 0" }, "Eigenschaften"),
      prop("Status", h("span", { class: "chips" }, h("span", { class: "check" + (offen ? "" : " on") }), offen ? "Offen" : "Erledigt")),
      prop("Antwort", f.status === "gesendet" ? "gesendet" : (f.entwuerfe.length ? "Entwurf liegt vor" : "noch kein Entwurf")),
      prop("Kunde", kundeLink(f.kunde_id, kundeName(f.kunde_id))),
      prop("Erstellt", fmtTime(f.erstellt)),
      prop("Entwürfe", String(f.entwuerfe.length)),
      m && m.anhaenge.length ? [h("div", { class: "prop-group" }, "Anhang"), h("div", { class: "chips" }, m.anhaenge.map(attachLink))] : null)));
}

function eventRow(e) {
  const [who, cls] = AKTEURE[e.akteur] || [e.akteur, "system"];
  return h("div", { class: "event" }, h("span", { class: "pt " + cls }), h("span", {}, h("strong", {}, who), " · ", eventText(e)), h("span", { class: "when" }, fmtTime(e.zeit)));
}

/* Belege als anklickbare Marken (Artikel, Produkt, Kunde, Nachricht) */
function belegChips(belege, prodName, kundeName) {
  return (belege || []).map(b => {
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
}

/* Entwurf mit Kontrollband. Die Oberfläche zeigt nur den Status aus der API; sie entwertet keine Freigabe und
   bricht keinen Termin von sich aus ab (das bauen die Teilnehmenden im Programm). */
function draftBlock(e, prodName, kundeName, opts) {
  opts = opts || {};
  const sent = e.status === "gesendet";
  const an = h("input", { value: e.an, disabled: sent, "aria-label": "An" });
  const betreff = h("input", { value: e.betreff, disabled: sent, "aria-label": "Betreff" });
  const text = h("textarea", { disabled: sent, "aria-label": "Text" });
  text.value = e.text;
  const fit = () => { text.style.height = "auto"; text.style.height = Math.max(text.scrollHeight + 2, 200) + "px"; };
  text.addEventListener("input", fit);
  requestAnimationFrame(fit);
  const dirty = () => an.value !== e.an || betreff.value !== e.betreff || text.value !== e.text;
  const saveIfDirty = async () => { if (dirty()) await api("entwurf/" + e.id, { an: an.value, betreff: betreff.value, text: text.value }); };
  const act = async (fn, msg) => {
    try { await fn(); if (msg) toast(msg); await render(true); } catch (x) { toast(x.message, true); }
  };

  const stufeChip = e.stufe ? chip(STUFEN[e.stufe] || e.stufe) : null;
  const band = (cls, ic, textNodes, ...right) => h("div", { class: "draft-notice " + cls }, icon(ic), h("span", {}, textNodes), h("span", { class: "right" }, right));
  let notice;
  if (sent) notice = band("sent", "check", opts.auto ? "Automatisch gesendet, nachdem das Eingriffsfenster abgelaufen war. Die Mail liegt im Postausgang; es ging nichts ins Netz." : "Gesendet. Die Mail liegt im Postausgang; es ging nichts ins Netz.", stufeChip);
  else if (e.status === "geplant") notice = band("plan", "clock", "Eingeplant: geht automatisch am " + fmtTime(e.sende_am) + " raus (" + restzeit(e.sende_am) + "). Bis dahin kannst du stoppen.", stufeChip);
  else if (e.status === "freigegeben") notice = band("sent", "check", "Freigegeben" + (e.freigabe_zeit ? " am " + fmtTime(e.freigabe_zeit) : "") + (e.freigabe_von ? " von " + (e.freigabe_von === "mensch" ? "dir" : e.freigabe_von) : "") + ". Jetzt kannst du senden.", stufeChip);
  else if (e.status === "zur_freigabe") notice = band("warn", "shield", "Wartet auf deine Freigabe.", stufeChip);
  else if (faehig("freigabe")) notice = band("", "bot", "Entwurf von Claude. Claude reicht ihn ein, dann entscheidet die Kontrolle.");
  else notice = band("", e.von === "claude" ? "bot" : "user", e.von === "claude" ? "Entwurf von Claude. Du prüfst, änderst und sendest. Claude kann nicht senden." : "Dein Entwurf.");

  const reasons = (e.stufe_gruende || []).length && !sent && e.status !== "entwurf"
    ? h("div", { class: "draft-reasons" }, h("div", { class: "evidence-title" }, "Warum diese Kontrolle"), h("ul", {}, e.stufe_gruende.map(g => h("li", {}, g)))) : null;
  const abgelehnt = e.status === "entwurf" && e.ablehnung ? h("div", { class: "draft-note" }, "Abgelehnt: " + e.ablehnung) : null;

  const ev = belegChips(e.belege, prodName, kundeName);
  const evidence = h("div", { class: "evidence" }, h("div", { class: "evidence-title" }, "Belege"),
    ev.length ? ev : h("span", { class: "muted small" }, "Keine Belege angegeben. Aussagen ohne Beleg solltest du nicht senden."));

  /* Knöpfe */
  const save = h("button", { class: "btn", onclick: () => act(async () => { await api("entwurf/" + e.id, { an: an.value, betreff: betreff.value, text: text.value }); }, "Gespeichert.") }, "Speichern");

  let armed = false;
  let timer = null;
  const cancel = h("button", { class: "btn ghost", style: "display:none" }, "Abbrechen");
  const send = h("button", { class: "btn primary" }, icon("send"), "Senden");
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
      await saveIfDirty(); // gesendet wird, was du siehst
      await api("senden/" + e.id, {});
      toast("Im Postausgang abgelegt.");
      await render(true);
    } catch (x) { disarm(); toast(x.message, true); }
  });

  const grund = h("input", { placeholder: "Begründung", "aria-label": "Begründung" });
  const rejectMsg = h("span", { class: "small muted" });
  const rejectGo = h("button", { class: "btn" }, "Ablehnen");
  const rejectBox = h("div", { class: "reject-row", hidden: true }, grund, rejectGo, rejectMsg);
  rejectGo.addEventListener("click", () => {
    if (!grund.value.trim()) { rejectMsg.textContent = "Bitte kurz begründen."; grund.focus(); return; }
    act(() => api("ablehnen/" + e.id, { grund: grund.value }), "Zurück an Claude.");
  });
  const rejectToggle = label => h("button", { class: "btn ghost", onclick: () => { rejectBox.hidden = !rejectBox.hidden; if (!rejectBox.hidden) grund.focus(); } }, label);
  const approve = h("button", { class: "btn primary", onclick: () => act(async () => { await saveIfDirty(); await api("freigeben/" + e.id, {}); }, "Freigegeben.") }, icon("check"), "Freigeben");
  const stop = h("button", { class: "btn", onclick: () => act(() => api("stoppen/" + e.id, {}), "Versand gestoppt. Der Entwurf liegt wieder bei dir.") }, icon("stop", 14), "Stoppen");

  let foot = null;
  if (!sent) {
    if (e.status === "zur_freigabe") foot = [h("span", { class: "hint" }, "Du gibst diesen Text frei."), rejectToggle("Ablehnen"), save, approve];
    else if (e.status === "freigegeben") foot = [h("span", { class: "hint" }, "Geht nur in den Ordner „postausgang“."), rejectToggle("Zurückziehen"), cancel, save, send];
    else if (e.status === "geplant") foot = [h("span", { class: "hint" }, "Die Übungsuhr kannst du oben vorspulen."), save, stop];
    else if (faehig("freigabe")) foot = [h("span", { class: "hint" }, "Ändern kannst du hier. Eingereicht wird über Claude."), save];
    else foot = [h("span", { class: "hint" }, "Gesendet wird nur in den Ordner „postausgang“."), cancel, save, send];
  }

  return h("div", { class: "draft" }, notice, abgelehnt, reasons,
    h("div", { class: "field" }, h("label", {}, "An"), an),
    h("div", { class: "field" }, h("label", {}, "Betreff"), betreff),
    text, evidence,
    foot ? h("div", { class: "draft-foot" }, foot) : null,
    foot && (e.status === "zur_freigabe" || e.status === "freigegeben") ? rejectBox : null);
}

/* Freigaben und Geplant: Liste der Entwürfe mit ihrer Kontrolle */
function queueDetail(e, prods, kunden) {
  const prodName = id => (prods.find(p => p.id === id) || {}).name;
  const kundeName = id => (kunden.find(k => k.id === id) || {}).name;
  return h("div", { class: "detail" }, h("div", { class: "detail-grid" },
    h("div", { class: "thread" },
      h("h1", {}, e.betreff),
      h("p", { class: "lead" }, fallNr(e.fall_id) + " · ", h("a", { href: href("faelle", e.fall_id) }, e.fall_titel)),
      draftBlock(e, prodName, kundeName)),
    h("aside", { class: "props" },
      h("div", { class: "prop-group", style: "margin-top: 0" }, "Eigenschaften"),
      prop("Status", e.status === "zur_freigabe" ? "Wartet auf Freigabe" : e.status === "freigegeben" ? "Freigegeben" : "Eingeplant"),
      prop("Kontrolle", STUFEN[e.stufe] || "–"),
      prop("Rechtsaussage", e.rechtsaussage ? "ja" : "nein"),
      prop("Kunde", kundeLink(e.kunde_id, e.kunde_name)),
      prop("To-do", h("a", { href: href("faelle", e.fall_id) }, "To-do " + fallNr(e.fall_id))),
      e.status === "geplant" ? [prop("Versand", fmtTime(e.sende_am)), prop("Restzeit", restzeit(e.sende_am))] : null,
      e.freigabe_zeit && e.status === "freigegeben" ? prop("Freigabe", fmtTime(e.freigabe_zeit)) : null)));
}

async function viewQueue(r, kind) {
  const [es, prods, kunden] = await Promise.all([api("entwuerfe"), api("produkte"), api("kunden")]);
  const frei = kind === "freigaben";
  const items = es.filter(e => (frei ? e.status === "zur_freigabe" || e.status === "freigegeben" : e.status === "geplant"));
  if (!frei) items.sort((a, b) => String(a.sende_am).localeCompare(String(b.sende_am)));
  const row = e => h("a", { class: "row" + (String(e.id) === r.id ? " active" : ""), href: href(kind, e.id) },
    h("span", { class: "status-icon " + (e.status === "zur_freigabe" ? "review" : e.status === "freigegeben" ? "done" : "scheduled") }),
    h("span", { class: "row-id" }, fallNr(e.fall_id)),
    h("span", { class: "row-main" }, h("span", { class: "row-title" }, e.betreff), h("span", { class: "row-sub" }, "an " + (e.kunde_name || e.an) + (e.stufe ? " · " + STUFEN[e.stufe] : ""))),
    frei ? null : h("span", { class: "countdown" }, restzeit(e.sende_am)));
  const rows = [];
  if (frei) {
    [["zur_freigabe", "Wartet auf Freigabe"], ["freigegeben", "Freigegeben, noch nicht gesendet"]].forEach(([st, label]) => {
      const g = items.filter(e => e.status === st);
      if (g.length) { rows.push(h("div", { class: "group" }, label)); g.forEach(e => rows.push(row(e))); }
    });
  } else if (items.length) { rows.push(h("div", { class: "group" }, "Eingeplant")); items.forEach(e => rows.push(row(e))); }
  const sel = items.find(e => String(e.id) === r.id);
  const label = frei ? "Freigaben" : "Geplant";
  const list = items.length ? rows : [emptyState(frei ? "shield" : "clock", frei ? "Nichts wartet auf deine Freigabe." : "Nichts eingeplant. Mails im Eingriffsfenster erscheinen hier.")];
  return col(topbar(sel ? ["Arbeitskorb", label, fallNr(sel.fall_id)] : ["Arbeitskorb", label]),
    splitView(list, sel ? queueDetail(sel, prods, kunden) : null, frei ? "shield" : "clock", frei ? "Wähle links einen Entwurf zur Freigabe." : "Wähle links eine eingeplante Mail."));
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

/* ---------- E-Mail (echtes Postfach, optional) ---------- */
async function viewEmail() {
  const p = await api("postfach");
  const body = [];
  body.push(h("h1", {}, "E-Mail"));
  if (!p.verbunden) {
    body.push(h("p", { class: "lead" }, "Das gemeinsame Workshop-Postfach ist für echte E-Mails da: Du kannst an jede Adresse schreiben, und Mails vom Dozenten kommen in deinen Eingang. Alles andere im Cockpit funktioniert auch ohne."));
    if (!p.verfuegbar) {
      body.push(h("p", { class: "muted" }, "Für diesen Workshop ist kein Postfach eingerichtet."));
    } else {
      const pw = h("input", { type: "password", placeholder: "Passwort vom Dozenten", autocomplete: "off", "aria-label": "Passwort vom Dozenten" });
      const err = h("div", { class: "err" });
      const run = async () => {
        try { await api("postfach/verbinden", { passwort: pw.value }); toast("Postfach verbunden."); await render(true); }
        catch (e) { err.textContent = e.message; }
      };
      pw.addEventListener("keydown", ev => { if (ev.key === "Enter") run(); });
      body.push(h("div", { class: "mailform" }, h("label", {}, "Passwort"), pw, err,
        h("div", { class: "actions" }, h("button", { class: "btn primary", onclick: run }, "Verbinden"))));
      setTimeout(() => pw.focus(), 30);
    }
  } else {
    body.push(h("p", { class: "lead" }, "Verbunden mit ", h("strong", {}, p.postfach), ". Es ist ein gemeinsames Postfach: Du siehst hier nur deine eigenen Mails und die neuen vom Dozenten. Du kannst Claude auch bitten, Mails abzuholen oder zu senden (jede Sendung bestätigst du in der App)."));
    const abholen = h("button", { class: "btn", onclick: async () => {
      try {
        const res = await api("postfach/abholen", {});
        toast(res.neu ? plural(res.neu, "neue Mail", "neue Mails") + " im Eingang." : "Keine neuen Mails.");
        await render(true);
      } catch (e) { toast(e.message, true); }
    } }, icon("sync"), "Neue E-Mails abholen");
    body.push(h("div", { class: "actions-row" }, abholen, h("a", { class: "btn ghost", href: "#/eingang" }, "Zum Eingang")));
    const an = h("input", { placeholder: "name@firma.de", autocomplete: "off", "aria-label": "An" });
    const betreff = h("input", { placeholder: "Betreff", autocomplete: "off", "aria-label": "Betreff" });
    const text = h("textarea", { "aria-label": "Text", rows: 7 });
    const err = h("div", { class: "err" });
    const senden = h("button", { class: "btn primary", onclick: async () => {
      err.textContent = "";
      senden.disabled = true;
      try { await api("postfach/senden", { an: an.value, betreff: betreff.value, text: text.value }); toast("E-Mail an " + an.value.trim() + " gesendet."); await render(true); }
      catch (e) { err.textContent = e.message; senden.disabled = false; }
    } }, icon("send"), "Senden");
    body.push(h("h2", {}, "Neue E-Mail"),
      h("div", { class: "mailform" }, h("label", {}, "An"), an, h("label", {}, "Betreff"), betreff, h("label", {}, "Text"), text, err,
        h("div", { class: "actions" }, senden)));
    body.push(h("h2", {}, "Von dir gesendet"));
    body.push(p.gesendet_liste.length
      ? h("div", { class: "mailsent" }, p.gesendet_liste.map(m => h("div", { class: "mailsent-row" },
        h("div", {}, h("strong", {}, m.betreff), h("span", { class: "muted small" }, " · an " + m.an + " · " + fmtTime(m.gesendet))),
        h("div", { class: "message-text" }, m.text))))
      : h("p", { class: "muted" }, "Noch nichts gesendet."));
  }
  return col(topbar(["Arbeitskorb", "E-Mail"]), h("div", { class: "detail" }, h("div", { class: "thread" }, body)));
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
  const label = n => (n.toLowerCase().includes("berichtigung") ? "Berichtigung" : "Verordnung");
  const tbl = (heads, rows) => h("table", {}, h("thead", {}, h("tr", {}, heads.map(t => h("th", {}, t)))), h("tbody", {}, rows));
  return col(topbar(["Wissen", "Regelwerk"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, rw.titel || rw.id),
    h("p", { class: "lead" }, "Fiktive Verordnung, für den Workshop erfunden, kein geltendes Recht. Hier stehen die Fristen auf einen Blick."),
    h("div", { class: "actions-row" }, d.verfuegbar.map(n => h("a", { class: "btn" + (n === d.haupttext ? " primary" : ""), href: href("verordnung", null, { text: n }) }, icon("book"), label(n) + " im Wortlaut lesen"))),
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
  )));
}

/* ---------- Verordnung im Wortlaut (Leseseite wie ein Amtsblatt, deutlich als fiktiv markiert) ---------- */
async function viewVerordnung(r) {
  const d = await api("regelwerk");
  if (!d.verfuegbar.length) return col(topbar(["Wissen", "Regelwerk"]), emptyState("book", "Noch keine Verordnung im Postfach. Rufe das Postfach ab.", h("button", { class: "btn primary", onclick: openPostfach }, icon("sync"), "Postfach abrufen")));
  const sel = r.q.text && d.verfuegbar.includes(r.q.text) ? r.q.text : d.haupttext;
  const label = n => (n.toLowerCase().includes("berichtigung") ? "Berichtigung" : "Verordnung");
  return col(topbar(["Wissen", "Regelwerk", label(sel) + " im Wortlaut"], h("a", { class: "btn", href: "#/regelwerk" }, icon("list"), "Fristen auf einen Blick")),
    h("div", { class: "page" }, h("div", { class: "page-inner" },
      d.verfuegbar.length > 1 ? h("div", { class: "tabs", style: "margin-top: 0" }, d.verfuegbar.map(n => h("a", { class: "tab" + (n === sel ? " on" : ""), href: href("verordnung", null, { text: n }) }, label(n)))) : null,
      h("div", { class: "paper" },
        h("div", { class: "paper-mark" }, "FIKTIV"),
        h("div", { class: "paper-head" }, h("span", {}, "★ Amtsblatt der Europäischen Union · Übungsfassung"), h("span", {}, "erfunden für den Workshop")),
        markdown(d.texte[sel] || "")))));
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
  const [ks, es] = await Promise.all([api("kunden"), api("einschaetzungen")]);
  const eMap = {};
  es.forEach(x => { eMap[x.kunde_id] = x; });
  const rows = k => h("tr", { class: "click", onclick: () => { location.hash = panelHref("k", k.id); } },
    h("td", { class: "faint mono" }, k.id), h("td", {}, k.name), h("td", {}, k.segment), h("td", {}, k.land),
    h("td", {}, h("span", { class: "chips" }, k.seveso ? chip("Seveso") : null, k.key_account ? chip("Key Account", "solid-blue") : null, k.ist_haendler ? chip("Händler") : null, k.status !== "aktiv" ? chip(k.status, "solid-orange") : null)),
    h("td", {}, eMap[k.id] ? esChip(eMap[k.id]) : h("span", { class: "faint" }, "–")));
  return col(topbar(["Wissen", "Kunden"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, "Kunden"), h("p", { class: "lead" }, plural(ks.length, "Kunde", "Kunden") + " aus dem Kundenstamm, mit allen Lieferungen und Anlagen."),
    tableWithSearch("Kunde suchen …", ks, k => k.segment, rows, ["ID", "Kunde", "Segment", "Land", "Merkmale", "Einschätzung"]))));
}

async function viewProtokoll() {
  const es = await api("protokoll");
  const body = es.length
    ? h("table", {}, h("thead", {}, h("tr", {}, ["Zeit", "Wer", "Was", "To-do"].map(t => h("th", {}, t)))),
      h("tbody", {}, es.map(e => {
        const [who, cls] = AKTEURE[e.akteur] || [e.akteur, "system"];
        return h("tr", {}, h("td", { class: "muted mono", style: "white-space:nowrap" }, fmtTime(e.zeit)),
          h("td", {}, h("span", { class: "event", style: "padding:0" }, h("span", { class: "pt " + cls }), h("strong", {}, who))),
          h("td", {}, eventText(e)),
          h("td", {}, e.fall_id ? h("a", { href: href("faelle", e.fall_id) }, fallNr(e.fall_id)) : h("span", { class: "faint" }, "–")));
      })))
    : emptyState("list", "Noch nichts protokolliert. Jeder Schritt von dir und von Claude erscheint hier.");
  return col(topbar(["Nachweis", "Protokoll"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, "Protokoll"), h("p", { class: "lead" }, "Was Claude vorbereitet hat und was du entschieden hast, mit Zeit und Urheber."), body)));
}

/* Bericht: zeigt ALLE Zahlen aus bericht() (auch eigene Kennzahlen der Teilnehmenden), nichts wird hier neu gerechnet. */
const BERICHT_LABELS = {
  einschaetzungen: ["Kunden und Betroffenheit", { betroffen: "Betroffen", nicht_betroffen: "Nicht betroffen", mittelbar: "Mittelbar", unklar: "Unklar", ohne_einschaetzung: "Ohne Einschätzung", aktive_kunden: "Aktive Kunden" }],
  entwuerfe: ["Entwürfe", { gesamt: "Gesamt", von_claude: "Von Claude", offen: "Noch offen" }],
  versand: ["Versand", { gesendet: "Gesendet", mit_pflichtfreigabe: "Mit Pflichtfreigabe", automatisch_nach_fenster: "Automatisch nach Fenster", direkt_vom_menschen: "Direkt vom Menschen" }],
  kontrolle: ["Kontrolle", { freigegeben: "Freigegeben", abgelehnt: "Abgelehnt", gestoppt: "Gestoppt", gestoppt_vom_menschen: "Gestoppt vom Menschen", gestoppt_von_claude: "Gestoppt von Claude", wartet_auf_freigabe: "Wartet auf Freigabe", eingeplant: "Eingeplant" }],
  frist: ["Frist", { informationspflicht_bis: "Kunden informieren bis", tage_bis: "Tage bis zur Frist" }],
};
const humanize = k => { const t = String(k).replace(/_/g, " "); return t.charAt(0).toUpperCase() + t.slice(1); };
function berichtWert(v, key) {
  if (v === null || v === undefined) return "–";
  if (typeof v === "object") return JSON.stringify(v);
  if (/^\d{4}-\d{2}-\d{2}$/.test(String(v)) && /bis|am|ab/.test(key)) return fmtDateShort(String(v));
  return String(v).replace(/^(\d+)\.(\d+)$/, "$1,$2");
}
async function viewBericht() {
  const d = await api("bericht");
  const z = d.zahlen || {};
  const sections = Object.keys(z).filter(k => k !== "stand" && k !== "grenze").map(k => {
    const [titel, labels] = BERICHT_LABELS[k] || [humanize(k), {}];
    const v = z[k];
    const entries = v !== null && typeof v === "object" ? Object.entries(v) : [[k, v]];
    return h("div", { class: "section" }, h("div", { class: "section-head" }, titel),
      h("div", { class: "facts compact" }, entries.map(([ek, ev]) => fact(labels[ek] || humanize(ek), berichtWert(ev, ek)))));
  });
  return col(topbar(["Nachweis", "Bericht"]), h("div", { class: "page" }, h("div", { class: "page-inner" },
    h("h1", {}, "Bericht an die Geschäftsführung"),
    h("p", { class: "lead" }, "Zahlen aus Protokoll und Entwürfen" + (z.stand ? ", Stand " + fmtTime(z.stand) : "") + ". Darunter steht dein Bericht."),
    sections,
    h("div", { class: "section" }, h("div", { class: "section-head" }, "Dein Bericht"),
      d.text ? markdown(d.text) : emptyState("chart", "Noch kein Bericht. Bitte Claude, einen Entwurf als bericht.md zu schreiben.")),
    z.grenze ? h("p", { class: "muted small", style: "margin-top: 32px" }, z.grenze) : null)));
}

const VIEWS = {
  email: viewEmail, eingang: viewEingang, faelle: viewFaelle, freigaben: r => viewQueue(r, "freigaben"), geplant: r => viewQueue(r, "geplant"), postausgang: viewPostausgang,
  regelwerk: viewRegelwerk, verordnung: viewVerordnung, produkte: viewProdukte, kunden: viewKunden, protokoll: viewProtokoll, bericht: viewBericht,
};
/* Was erst mit einer späteren Runde freigeschaltet wird */
const GATE = { freigaben: ["freigabe", 2, "Arbeitskorb", "Freigaben", "shield"], geplant: ["fenster", 3, "Arbeitskorb", "Geplant", "clock"], bericht: ["bericht", 4, "Nachweis", "Bericht", "chart"] };

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
  const [k, kunden, ess, prods] = await Promise.all([api("kunde/" + encodeURIComponent(id)), api("kunden"), api("einschaetzungen"), api("produkte")]);
  const es = ess.find(x => x.kunde_id === k.id);
  const prodName = pid => (prods.find(p => p.id === pid) || {}).name;
  const kundeName = kid => (kunden.find(x => x.id === kid) || {}).name;
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
    es ? h("div", { class: "section" }, h("div", { class: "section-head" }, "Einschätzung von " + (es.von === "claude" ? "Claude" : es.von === "mensch" ? "dir" : es.von), h("span", { class: "meta" }, fmtTime(es.zeit))),
      h("div", { class: "chips" }, esChip(es), es.stichtag ? chip("Stichtag " + fmtDateShort(es.stichtag)) : null),
      h("p", { style: "margin: 10px 0 8px" }, es.begruendung),
      h("div", { class: "evidence", style: "padding: 0; border: 0" }, belegChips(es.belege, prodName, kundeName))) : null,
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
    ["Eingang", "Ansicht", () => go("eingang")], ["To-dos", "Ansicht", () => go("faelle")],
    faehig("freigabe") ? ["Freigaben", "Ansicht", () => go("freigaben")] : null, faehig("fenster") ? ["Geplant", "Ansicht", () => go("geplant")] : null,
    ["Postausgang", "Ansicht", () => go("postausgang")],
    ["Regelwerk", "Ansicht", () => go("regelwerk")], ["Produkte", "Ansicht", () => go("produkte")], ["Kunden", "Ansicht", () => go("kunden")], ["Protokoll", "Ansicht", () => go("protokoll")],
    faehig("bericht") ? ["Bericht", "Ansicht", () => go("bericht")] : null,
    ["Postfach abrufen", "Aktion", openPostfach],
  ].filter(Boolean).concat(fs.map(f => ["To-do " + fallNr(f.id) + " · " + f.titel, "To-do", () => go("faelle", f.id)]))
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
    Object.entries(navEls).forEach(([k, n]) => n.a.classList.toggle("active", k === (r.view === "verordnung" ? "regelwerk" : r.view)));
    await refreshStatus();
    let node;
    const gate = GATE[r.view];
    if (gate && !faehig(gate[0])) {
      node = col(topbar([gate[2], gate[3]]), emptyState(gate[4], "Das schaltet der Dozent mit Runde " + gate[1] + " frei."));
    } else {
      try { node = await (VIEWS[r.view] || viewEingang)(r); }
      catch (e) { node = col(topbar(["Fehler"]), emptyState("list", e.message)); }
    }
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
document.addEventListener("click", () => document.querySelectorAll(".uhr .menu").forEach(m => { m.hidden = true; }));
/* Übungsuhr und Restzeiten regelmäßig auffrischen, ohne Eingaben zu stören */
setInterval(async () => {
  await refreshStatus();
  const typing = document.activeElement && /^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName);
  if (parseRoute().view === "geplant" && !typing && !document.querySelector(".panel, .dialog, .palette")) render(true);
}, 30000);
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
