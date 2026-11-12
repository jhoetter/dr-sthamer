"""Welche Kontrolle gilt für eine Mail? Reine Regel, ohne Datenbank, gut zu lesen und zu testen.

Zwei Muster (Drill 3 und 4):
  pflichtfreigabe   Ein Mensch gibt den aktuellen Text ausdrücklich frei, erst dann kann er gesendet werden.
  eingriffsfenster  Die Mail wird für +24 Stunden eingeplant und geht automatisch raus, wenn niemand stoppt.

Claude meldet nur, OB der Text über eine Standardinformation hinausgeht (`rechtsaussage`). Die Stufe bestimmt diese Regel; die strengere gewinnt.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

PFLICHTFREIGABE = "pflichtfreigabe"
EINGRIFFSFENSTER = "eingriffsfenster"


def stufe_fuer(kunde: Optional[Dict[str, Any]], rechtsaussage: bool, fenster_aktiv: bool,
               geltungsbereich: Optional[List[str]] = None) -> Tuple[str, List[str]]:
    """Gibt (Stufe, Gründe) zurück. Gründe sind kurze Sätze, die das Cockpit dem Menschen zeigt."""
    gruende: List[str] = []
    if rechtsaussage:
        gruende.append("Der Text geht über eine Standardinformation hinaus (Rechtsauskunft, Auslegung, Zusage oder ein Produkt ist unklar).")
    if kunde:
        if kunde.get("seveso"):
            gruende.append("Seveso-Betrieb: besondere Auflagen, Fachprüfung nötig.")
        if kunde.get("key_account"):
            gruende.append("Key Account: Antwort immer mit Vier-Augen-Prinzip.")
        if kunde.get("segment") == "Flughafen":
            gruende.append("Flughafen: Ausnahmen und Bescheide möglich, nicht automatisch beantworten.")
        if kunde.get("ist_haendler"):
            gruende.append("Händler: Weitergabe an Endkunden ist zu klären.")
        if kunde.get("status") and kunde["status"] != "aktiv":
            gruende.append("Kunde ist nicht aktiv (%s)." % kunde["status"])
        if geltungsbereich and kunde.get("land") not in geltungsbereich:
            gruende.append("Kunde sitzt außerhalb des Geltungsbereichs (%s)." % kunde.get("land"))
        if kunde.get("ausnahme_ids"):
            gruende.append("Für den Kunden gilt eine Ausnahme.")
    if not fenster_aktiv:
        gruende.append("Das Eingriffsfenster ist noch nicht freigeschaltet: alles geht über Pflichtfreigabe.")
    return (PFLICHTFREIGABE if gruende else EINGRIFFSFENSTER), gruende
