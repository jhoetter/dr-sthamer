"""Stammdaten aus data/ lesen (schreibgeschützt). Nur Standardbibliothek."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .paths import data_dir

_cache: Dict[str, Any] = {}


def _lesen_json(name: str) -> Any:
    pfad = data_dir() / name
    key = "%s|%s|%s" % (pfad, pfad.stat().st_mtime_ns if pfad.exists() else 0, name)
    if key not in _cache:
        with open(pfad, "r", encoding="utf-8") as f:
            _cache[key] = json.load(f)
    return _cache[key]


def leeren() -> None:
    _cache.clear()


def welt() -> Dict[str, Any]:
    return _lesen_json("welt.json")


def regelwerk() -> Dict[str, Any]:
    return _lesen_json("regelwerk.json")


def produkte() -> List[Dict[str, Any]]:
    return _lesen_json("produkte.json")


def kunden() -> List[Dict[str, Any]]:
    return _lesen_json("kunden.json")


def lieferungen() -> List[Dict[str, Any]]:
    return _lesen_json("lieferungen.json")


def wellen() -> Dict[str, Any]:
    """Wellen-Konfiguration: {"1": {"titel": ..., "code_sha256": null|hex}, ...}"""
    pfad = data_dir() / "wellen.json"
    if not pfad.exists():
        return {}
    return _lesen_json("wellen.json")


def produkt(produkt_id: str) -> Optional[Dict[str, Any]]:
    for p in produkte():
        if p["id"] == produkt_id:
            return p
    return None


def kunde(kunde_id: str) -> Optional[Dict[str, Any]]:
    for k in kunden():
        if k["id"] == kunde_id:
            return k
    return None


def verordnung_text(name: str = "vo-fiktiv-2026-9001.md") -> str:
    """Nur Dateien aus data/regulation/ (kein beliebiger Pfad)."""
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError("Ungültiger Dateiname.")
    pfad = data_dir() / "regulation" / name
    if not pfad.is_file():
        raise FileNotFoundError("Unbekannter Text: %s" % name)
    return _normalisieren(pfad.read_text(encoding="utf-8"))


def verordnungen() -> List[str]:
    ordner = data_dir() / "regulation"
    if not ordner.is_dir():
        return []
    return sorted(p.name for p in ordner.glob("*.md"))


def _normalisieren(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _parse_nachricht(pfad: Path) -> Dict[str, Any]:
    text = _normalisieren(pfad.read_text(encoding="utf-8")).lstrip("﻿")
    if not text.startswith("---\n"):
        raise ValueError("%s: Kopfzeilen fehlen" % pfad.name)
    kopf, _, rest = text[4:].partition("\n---\n")
    felder: Dict[str, str] = {}
    for zeile in kopf.split("\n"):
        if not zeile.strip() or ":" not in zeile:
            continue
        k, _, v = zeile.partition(":")
        felder[k.strip()] = v.strip()
    anhaenge = [a.strip() for a in felder.get("anhaenge", "").split(",") if a.strip()]
    return {
        "id": felder["id"],
        "welle": int(felder["welle"]),
        "typ": felder["typ"],
        "von": felder["von"],
        "betreff": felder["betreff"],
        "empfangen": felder["empfangen"],
        "kunde_id": felder.get("kunde_id") or None,
        "anhaenge": anhaenge,
        "text": rest.strip("\n"),
    }


def nachrichten_alle() -> List[Dict[str, Any]]:
    ordner = data_dir() / "eingang"
    if not ordner.is_dir():
        return []
    out = [_parse_nachricht(p) for p in sorted(ordner.glob("*.md"))]
    out.sort(key=lambda m: (m["welle"], m["empfangen"], m["id"]))
    return out


def interne_domain() -> str:
    return welt().get("interne_domain", "sthamer-uebung.example.com")


def erlaubte_empfaenger() -> Dict[str, str]:
    """E-Mail-Adresse (klein) -> Beschreibung. Nur bekannte Kontakte dürfen Entwürfe erhalten."""
    out: Dict[str, str] = {}
    for k in kunden():
        mail = (k.get("ansprechpartner") or {}).get("email")
        if mail:
            out[mail.lower()] = "%s (%s)" % (k["name"], k["id"])
    return out
