"""Dashboard directory paths — single source of truth for local and Cloud."""

from pathlib import Path

# dashboard/paths.py → dashboard/
DASHBOARD_DIR = Path(__file__).resolve().parent
DATA_DIR = DASHBOARD_DIR / "data"
