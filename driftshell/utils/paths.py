from pathlib import Path

DRIFT_DIR = Path.home() / ".drift"
DB_PATH = DRIFT_DIR / "drift.db"
SNAPSHOTS_DIR = DRIFT_DIR / "snapshots"
CONFIG_PATH = DRIFT_DIR / "config.toml"


def ensure_dirs() -> None:
    DRIFT_DIR.mkdir(exist_ok=True)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
