"use strict";
// Cockpit-Oberfläche. Alle Inhalte (auch Mailtexte) werden nur als Text eingefügt, nie als HTML.
const TOKEN = document.querySelector("meta[name=sthamer-token]").content;
const $inhalt = document.getElementById("inhalt");
const $nav = document.getElementById("nav");
const ANSICHTEN = [
  ["eingang", "Eingang"], ["faelle", "Fälle"], ["regelwerk", "Regelwerk"], ["produkte", "Produkte"],
  ["kunden", "Kunden"], ["postausgang", "Postausgang"], ["protokoll", "Protokoll"],
];

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

function h(tag, props, ...kinder) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined && v !== false) el.setAttribute(k, v === true ? "" : v);
  }
  for (const kind of kinder.flat()) {
    if (kind === null || kind === undefined || kind === false) continue;
    el.append(kind.nodeType ? kind : document.createTextNode(String(kind)));
  }
  return el;
}

function meldung(text, fehler) {
  const m = h("div", { class: "meldung" + (fehler ? " fehler" : "") }, text);
  $inhalt.prepend(m);
  setTimeout(() => m.remove(), 6000);
}

function tabelle(spalten, zeilen, beiKlick) {
  return h("table", {},
    h("thead", {}, h("tr", {}, spalten.map(s => h("th", {}, s[0])))),
    h("tbody", {}, zeilen.map(z => {
      const tr = h("tr", beiKlick ? { style: "cursor:pointer", onclick: () => beiKlick(z) } : {},
        spalten.map(s => h("td", {}, s[1](z))));
      return tr;
    })));
}

function zweiSpaltig(liste, detail) {
  $inhalt.className = "";
  $inhalt.replaceChildren(h("div", { class: "liste" }, liste), h("div", { class: "detail", id: "detail" }, detail));
}
function einSpaltig(...kinder) {
  $inhalt.className = "einspaltig";
  $inhalt.replaceChildren(h("div", { class: "detail" }, kinder));
}
function zeigeDetail(...kinder) {
  document.getElementById("detail").replaceChildren(...kinder.flat().filter(Boolean));
}

// ---------------------------------------------------------------- Ansichten
async function ansichtEingang(auswahl) {
  const msgs = await api("nachrichten");
  const liste = msgs.length ? msgs.map(m => h("button", { class: "zeile", onclick: () => ansichtEingang(m.id) },
    h("div", {}, m.betreff), h("div", { class: "klein" }, m.von + " · Runde " + m.welle + (m.fall_id ? " · Fall F-" + String(m.fall_id).padStart(4, "0") : "")))) :
    [h("div", { class: "zeile" }, "Noch keine Nachrichten. Oben „Postfach abrufen“.")];
  zweiSpaltig(liste, h("p", { class: "leise" }, "Nachricht links auswählen."));
  if (!auswahl) return;
  const m = await api("nachricht/" + encodeURIComponent(auswahl));
  zeigeDetail(
    h("h2", {}, m.betreff),
    h("div", { class: "leise" }, "Von " + m.von + " · " + m.empfangen),
    m.anhaenge.length ? h("div", { class: "leise" }, "Anhang: " + m.anhaenge.join(", ")) : null,
    h("pre", { class: "text" }, m.text),
    h("div", { class: "leiste" }, m.fall_id
      ? h("button", { class: "knopf leer", onclick: () => { location.hash = "#/faelle/" + m.fall_id; } }, "Fall öffnen")
      : h("button", { class: "knopf", onclick: async () => {
          try { const r = await api("fall", { nachricht_id: m.id }); location.hash = "#/faelle/" + r.fall_id; }
          catch (e) { meldung(e.message, true); }
        } }, "Fall anlegen")));
}

function fallNr(id) { return "F-" + String(id).padStart(4, "0"); }

async function ansichtFaelle(auswahl) {
  const fs = await api("faelle");
  const liste = fs.length ? fs.map(f => h("button", { class: "zeile" + (String(f.id) === auswahl ? " aktiv" : ""), onclick: () => { location.hash = "#/faelle/" + f.id; } },
    h("div", {}, fallNr(f.id) + " · " + f.titel),
    h("div", { class: "klein" }, f.status + " · offene Aufgaben: " + f.offene_aufgaben + " · Entwürfe: " + f.entwuerfe))) :
    [h("div", { class: "zeile" }, "Noch keine Fälle. Im Eingang „Fall anlegen“.")];
  zweiSpaltig(liste, h("p", { class: "leise" }, "Fall links auswählen."));
  if (!auswahl) return;
  const f = await api("fall/" + auswahl);
  zeigeDetail(
    h("h2", {}, fallNr(f.id) + " · " + f.titel),
    h("div", { class: "leise" }, "Status: " + f.status),
    h("h3", {}, "Nachricht"),
    f.nachricht ? h("pre", { class: "text" }, f.nachricht.text) : null,
    h("h3", {}, "Aufgaben"),
    f.aufgaben.map(a => h("div", {}, (a.status === "erledigt" ? "✓ " : "○ ") + a.titel)),
    h("h3", {}, "Entwürfe"),
    f.entwuerfe.length ? f.entwuerfe.map(e => blockEntwurf(e, f)) : h("p", { class: "leise" }, "Noch kein Entwurf. Bitte Claude, einen vorzubereiten."),
    h("h3", {}, "Protokoll"),
    tabelle([["Zeit", z => z.zeit.replace("T", " ")], ["Wer", z => z.akteur], ["Was", z => z.art + (z.details && z.details.text ? ": " + z.details.text : "")]],
      f.protokoll.slice().reverse()));
}

function blockEntwurf(e, f) {
  const gesendet = e.status !== "entwurf";
  const an = h("input", { value: e.an, disabled: gesendet });
  const betreff = h("input", { value: e.betreff, disabled: gesendet });
  const text = h("textarea", { disabled: gesendet }); text.value = e.text;
  let bestaetigt = false;
  const senden = h("button", { class: "knopf" }, "Senden");
  senden.addEventListener("click", async () => {
    if (!bestaetigt) { bestaetigt = true; senden.textContent = "Wirklich senden? Noch einmal klicken"; senden.classList.add("gefahr"); return; }
    try { const r = await api("senden/" + e.id, {}); meldung("Im Postausgang abgelegt: " + r.datei); ansichtFaelle(String(f.id)); }
    catch (x) { meldung(x.message, true); }
  });
  const speichern = h("button", { class: "knopf leer" }, "Änderungen speichern");
  speichern.addEventListener("click", async () => {
    try { await api("entwurf/" + e.id, { an: an.value, betreff: betreff.value, text: text.value }); meldung("Gespeichert."); ansichtFaelle(String(f.id)); }
    catch (x) { meldung(x.message, true); }
  });
  return h("div", {},
    h("span", { class: "marke-chip" }, "Entwurf " + e.id + " · von " + e.von + " · " + (gesendet ? "gesendet" : "offen")),
    h("label", {}, "An"), an, h("label", {}, "Betreff"), betreff, h("label", {}, "Text"), text,
    e.belege.length ? h("div", {}, h("label", {}, "Belege"), h("ul", {}, e.belege.map(b => h("li", {}, b.typ + ": " + b.ref + (b.hinweis ? " – " + b.hinweis : ""))))) : h("p", { class: "leise" }, "Keine Belege angegeben."),
    gesendet ? null : h("div", { class: "leiste" }, speichern, senden));
}

async function ansichtRegelwerk() {
  const d = await api("regelwerk");
  const r = d.regelwerk;
  if (!d.verfuegbar.length) { einSpaltig(h("h2", {}, "Regelwerk"), h("p", { class: "leise" }, "Noch keine Verordnung im Postfach.")); return; }
  // Berichtigung (falls schon im Postfach) auf die Tabelle anwenden und markieren
  const geaendert = {};
  ((r.berichtigung && r.berichtigung.aenderungen) || []).forEach(a => { geaendert[a.anwendung + "|" + a.feld] = a; });
  const zelle = (a, feld) => {
    const c = geaendert[a.id + "|" + feld];
    return c ? h("span", {}, c.neu + " ", h("span", { class: "marke-chip chip-warn", title: "vorher " + c.alt }, "berichtigt")) : (a[feld] || "–");
  };
  const auswahl = h("select", {}, d.verfuegbar.map(n => h("option", { value: n, selected: n === d.haupttext }, n)));
  const pre = h("pre", { class: "text" }, d.texte[d.haupttext] || "");
  auswahl.addEventListener("change", () => { pre.textContent = d.texte[auswahl.value]; });
  einSpaltig(
    h("h2", {}, r.titel || r.id),
    h("div", { class: "leise" }, "Grenzwert: " + r.grenzwert_mg_l + " mg/l (" + String(r.grenzwert_regel).replace(/_/g, " ") + ") · Geltungsbereich: " + (r.geltungsbereich_laender || []).join(", ")),
    h("h3", {}, "Fristen je Anwendung"),
    tabelle([["Anwendung", a => a.name], ["Artikel", a => a.artikel], ["Inverkehrbringen verboten ab", a => zelle(a, "inverkehrbringen_verbot_ab")],
      ["Verwendung verboten ab", a => zelle(a, "verwendung_verbot_ab")], ["Bestandsmeldung bis", a => zelle(a, "bestandsmeldung_bis")], ["Kennzeichnung ab", a => zelle(a, "kennzeichnung_ab")]], r.anwendungen),
    h("h3", {}, "Volltext"), auswahl, pre);
}

async function ansichtProdukte() {
  const ps = await api("produkte");
  const filter = h("input", { placeholder: "Suchen …" });
  const tab = h("div", {});
  const zeichne = () => tab.replaceChildren(tabelle(
    [["ID", p => p.id], ["Name", p => p.name], ["Schaumart", p => p.schaumart], ["Basis", p => p.basis],
     ["PFAS", p => p.pfas_wert === null ? "kein Messwert" : p.pfas_wert + " " + p.pfas_einheit], ["SDB", p => p.sdb_version + " (" + p.sdb_datum + ")"], ["Status", p => p.status]],
    ps.filter(p => (p.name + p.id).toLowerCase().includes(filter.value.toLowerCase()))));
  filter.addEventListener("input", zeichne);
  $inhalt.className = "einspaltig";
  $inhalt.replaceChildren(h("div", { class: "filter" }, filter), h("div", { class: "detail" }, tab));
  zeichne();
}

async function ansichtKunden(auswahl) {
  const ks = await api("kunden");
  const liste = ks.map(k => h("button", { class: "zeile" + (k.id === auswahl ? " aktiv" : ""), onclick: () => { location.hash = "#/kunden/" + k.id; } },
    h("div", {}, k.name), h("div", { class: "klein" }, k.id + " · " + k.segment + " · " + k.land + (k.seveso ? " · Seveso" : "") + (k.key_account ? " · Key Account" : "") + (k.status !== "aktiv" ? " · " + k.status : ""))));
  zweiSpaltig(liste, h("p", { class: "leise" }, "Kunde links auswählen."));
  if (!auswahl) return;
  const k = await api("kunde/" + encodeURIComponent(auswahl));
  zeigeDetail(
    h("h2", {}, k.name), h("div", { class: "leise" }, k.id + " · " + k.segment + " · " + k.land + " · Sprache " + k.sprache),
    h("div", {}, "Ansprechperson: " + k.ansprechpartner.name + ", " + k.ansprechpartner.rolle + " <" + k.ansprechpartner.email + ">"),
    k.bemerkung ? h("div", { class: "leise" }, "Bemerkung: " + k.bemerkung) : null,
    h("h3", {}, "Lieferungen und Anlagen"),
    tabelle([["Produkt", l => l.produkt_id + " " + (l.produkt_name || "")], ["Anwendung", l => l.anwendung], ["Anlage", l => l.anlage || "–"],
      ["Menge (l)", l => l.menge_l], ["PFAS", l => l.pfas_wert === null ? "–" : l.pfas_wert + " " + l.pfas_einheit], ["Letzte Lieferung", l => l.letzte_lieferung]], k.lieferungen));
}

async function ansichtPostausgang() {
  const ps = await api("postausgang");
  einSpaltig(h("h2", {}, "Postausgang"), h("div", { class: "leise" }, "So sähe der Versand aus. Es geht nichts ins Netz; die Dateien liegen im Ordner „postausgang“."),
    ps.length ? ps.map(p => h("div", {}, h("h3", {}, p.gesendet.replace("T", " ") + " · an " + p.an), h("strong", {}, p.betreff), h("pre", { class: "text" }, p.text))) : h("p", { class: "leise" }, "Noch nichts gesendet."));
}

async function ansichtProtokoll() {
  const es = await api("protokoll");
  einSpaltig(h("h2", {}, "Protokoll"), tabelle([["Zeit", e => e.zeit.replace("T", " ")], ["Wer", e => e.akteur], ["Was", e => e.art], ["Fall", e => e.fall_id ? fallNr(e.fall_id) : ""],
    ["Details", e => JSON.stringify(e.details)]], es));
}

// ---------------------------------------------------------------- Routing
const ROUTEN = { eingang: ansichtEingang, faelle: ansichtFaelle, regelwerk: ansichtRegelwerk, produkte: ansichtProdukte, kunden: ansichtKunden, postausgang: ansichtPostausgang, protokoll: ansichtProtokoll };

async function stand() {
  try {
    const s = await api("status");
    document.getElementById("stand").textContent = "Runde " + s.welle + " · " + s.faelle + " Fälle · " + s.gesendet + " gesendet";
  } catch (e) { document.getElementById("stand").textContent = "keine Verbindung"; }
}

async function route() {
  const [, name = "eingang", arg] = location.hash.split("/");
  $nav.replaceChildren(...ANSICHTEN.map(([k, t]) => h("a", { href: "#/" + k, class: k === name ? "aktiv" : "" }, t)));
  try { await (ROUTEN[name] || ansichtEingang)(arg); } catch (e) { einSpaltig(h("div", { class: "meldung fehler" }, e.message)); }
  stand();
}

document.getElementById("abrufen").addEventListener("click", async () => {
  const s = await api("status");
  const nr = s.naechste_welle;
  if (!nr) { meldung("Es gibt keine weiteren Nachrichten."); return; }
  const code = document.getElementById("code").value;
  try { const r = await api("welle", { welle: nr, code }); document.getElementById("code").value = ""; meldung(r.neue_nachrichten + " neue Nachricht(en) abgerufen."); route(); }
  catch (e) { meldung(e.message, true); }
});
window.addEventListener("hashchange", route);
route();
