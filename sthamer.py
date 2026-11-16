"""Einstiegspunkt: python sthamer.py <befehl>  (setup, serve, mcp, status, ...)."""
import sys

sys.dont_write_bytecode = True  # geänderten Code nie durch eine veraltete .pyc-Datei ersetzen lassen

if sys.version_info < (3, 9):
    sys.stderr.write(
        "Dieses Programm braucht Python 3.9 oder neuer. "
        "Gefunden: %d.%d. Bitte Python neu installieren (siehe docs/INSTALL_*.md).\n"
        % sys.version_info[:2]
    )
    sys.exit(1)

from sthamer_sys.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
