"""Programmänderungen sofort wirksam machen, ohne etwas neu zu starten.

Wer den Code in `sthamer_sys/` ändert (die Person mit Claude im Bauauftrag), soll die Wirkung gleich im Cockpit und in
den Werkzeugen von Claude sehen. Cockpit und Werkzeug-Server prüfen dazu bei jedem Aufruf, ob eine Programmdatei neuer
ist, und laden `daten` und `domain` samt allem, was daran hängt, neu. Ist der neue Code kaputt (Tippfehler), bleibt der
alte aktiv, und der Fehler steht im Status (`code_fehler`), bis die Datei wieder stimmt.

Abschalten für Tests: Umgebungsvariable STHAMER_NACHLADEN=0.
"""
from __future__ import annotations

import importlib
import os
import sys
import threading
from typing import Dict, Optional, Tuple

from .paths import PKG_DIR

# Diese Module bleiben beim Nachladen stehen: sie enthalten die laufenden Schleifen (app, mcp_server) oder Zustand, der nicht
# verloren gehen darf (schutz: die Freischaltung der Menschen-Aktionen im Cockpit).
BEHALTEN = ("sthamer_sys.nachladen", "sthamer_sys.schutz", "sthamer_sys.app", "sthamer_sys.mcp_server", "sthamer_sys.cli", "sthamer_sys.paths")

_sperre = threading.Lock()


def _stand() -> int:
    try:
        return max(p.stat().st_mtime_ns for p in PKG_DIR.glob("*.py"))
    except (OSError, ValueError):
        return 0


_zustand: Dict[str, object] = {"geladen": _stand(), "fehler": None}


def fehler() -> Optional[str]:
    return _zustand["fehler"]  # type: ignore[return-value]


def geladen() -> int:
    return int(_zustand["geladen"])  # type: ignore[arg-type]


def pruefen(globs: dict, namen: Tuple[str, ...] = ("daten", "domain")) -> bool:
    """Lädt neu, wenn sich der Code geändert hat. Gibt True zurück, wenn neu geladen wurde."""
    if os.environ.get("STHAMER_NACHLADEN") == "0":
        return False
    aktuell = _stand()
    if aktuell == _zustand["geladen"]:
        return False
    with _sperre:
        if aktuell == _zustand["geladen"]:
            return False
        paket = sys.modules.get("sthamer_sys")
        gesichert = {n: m for n, m in sys.modules.items() if n.startswith("sthamer_sys.") and n not in BEHALTEN}
        for n in gesichert:
            del sys.modules[n]
            if paket is not None and hasattr(paket, n.split(".", 1)[1]):
                delattr(paket, n.split(".", 1)[1])  # sonst findet `from . import x` die alte Datei
        try:
            neu = {name: importlib.import_module("sthamer_sys." + name) for name in namen}
        except Exception as e:  # Tippfehler im neuen Code: alten Stand behalten
            for n in [k for k in sys.modules if k.startswith("sthamer_sys.") and k not in BEHALTEN]:
                del sys.modules[n]
            sys.modules.update(gesichert)
            _zustand["geladen"] = aktuell
            _zustand["fehler"] = "%s: %s" % (type(e).__name__, e)
            sys.stderr.write("Neuer Code hat einen Fehler, der alte bleibt aktiv: %s\n" % _zustand["fehler"])
            return False
        globs.update(neu)
        _zustand["geladen"] = aktuell
        _zustand["fehler"] = None
        sys.stderr.write("Code neu geladen.\n")
        return True
