from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import PATHS


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def save_json(name: str, payload: dict[str, Any], folder: Path | None = None) -> Path:
    target_dir = folder or PATHS.conversations_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{name}-{timestamp()}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def append_log(message: str) -> None:
    PATHS.logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = PATHS.logs_dir / "app.log"
    log_file.write_text(
        (log_file.read_text(encoding="utf-8") if log_file.exists() else "") + message + "\n",
        encoding="utf-8",
    )
