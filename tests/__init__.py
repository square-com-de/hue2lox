"""Automated Hue2Lox tests; run from the repository root."""

import sys
from pathlib import Path

# Match the application module search path used inside the container.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
