"""Portable package patch: use this bundled runtime only."""
from pathlib import Path
import sys

def setup_env():
    scripts = Path(__file__).resolve().parents[1]
    for path in (scripts, scripts / "vendor"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
