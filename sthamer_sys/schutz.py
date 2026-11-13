"""Menschen-Aktionen laufen nur im Cockpit.

Senden, Freigeben, Ablehnen, Übungsuhr vorspulen und spätere Runden abrufen sind Entscheidungen des Menschen. Das
Cockpit schaltet sie beim Start frei (`freischalten`); in jedem anderen Prozess, zum Beispiel einem Python-Skript, das
Claude startet, werfen die Funktionen einen Fehler. Das ist keine Sicherheitsgrenze gegen jemanden, der den Code absichtlich
ändert, sondern verhindert den versehentlichen Abkürzer: Ein Umgehen wäre eine bewusste, sichtbare Handlung.

Ausnahmen: Die Tests und die Akzeptanzprüfung setzen STHAMER_MENSCH=1, die Kommandozeile der Person (`welle`) schaltet selbst frei.
Diese Datei ist für Claude zum Bearbeiten gesperrt (.claude/settings.json).
"""
from __future__ import annotations

import os

_frei = False


def freischalten() -> None:
    global _frei
    _frei = True


def erlaubt() -> bool:
    return _frei or os.environ.get("STHAMER_MENSCH") == "1"


def pruefen(was: str) -> None:
    if not erlaubt():
        from .domain import FachFehler  # spät importieren: domain importiert dieses Modul
        raise FachFehler("%s kann nur der Mensch im Cockpit. In einem anderen Programm ist das gesperrt." % was)
