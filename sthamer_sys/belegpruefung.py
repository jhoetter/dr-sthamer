"""Belegprüfung (Drill 2): Jede Aussage braucht einen Beleg, der wirklich existiert.

Beim Speichern eines Entwurfs und beim Festhalten einer Einschätzung wird hier geprüft. Jede Funktion gibt eine
Liste von Problemen zurück (leer = in Ordnung). Ein Problem ist ein kurzer Satz, den der Mensch versteht.

DRILL 2 (Bauauftrag): Die Funktionen sind absichtlich noch leer. Teilnehmende legen mit Claude fest, was gelten soll,
zum Beispiel: zitierte Artikel gibt es im Regelwerk, zitierte Produkte und Kunden gibt es, eine betroffene Einschätzung
braucht Artikel UND Produkt als Beleg, und jedes Datum im Text ist eine Frist aus dem Regelwerk (nach Berichtigung).
"""
from __future__ import annotations

from typing import Any, Dict, List


def pruefe_entwurf(an: str, betreff: str, text: str, belege: List[Dict[str, str]]) -> List[str]:
    return []


def pruefe_einschaetzung(kunde_id: str, ergebnis: str, begruendung: str, belege: List[Dict[str, str]]) -> List[str]:
    return []
