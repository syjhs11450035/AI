from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


def application_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


APP_DIR = application_dir()
MODULE_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "ai-data"


@dataclass(frozen=True)
class Paths:
    app_dir: Path = APP_DIR
    module_dir: Path = MODULE_DIR
    data_dir: Path = DATA_DIR
    conversations_dir: Path = DATA_DIR / "conversations"
    outputs_dir: Path = DATA_DIR / "outputs"
    logs_dir: Path = DATA_DIR / "logs"
    cache_dir: Path = DATA_DIR / "cache"
    api_key_dir: Path = MODULE_DIR / "api-key"
    json_dir: Path = MODULE_DIR / "json"
    temp_dir: Path = MODULE_DIR / "temp"

    def ensure(self) -> None:
        for path in (
            self.data_dir,
            self.conversations_dir,
            self.outputs_dir,
            self.logs_dir,
            self.cache_dir,
            self.api_key_dir,
            self.json_dir,
            self.temp_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


PATHS = Paths()


def load_dotenv() -> None:
    env_file = APP_DIR / ".env"
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def read_local_api_keys() -> dict[str, str]:
    key_file = PATHS.api_key_dir / "api_keys.json"
    if not key_file.exists():
        return {}
    try:
        data = json.loads(key_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {str(k): str(v) for k, v in data.items() if v}


load_dotenv()
PATHS.ensure()

LOCAL_KEYS = read_local_api_keys()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or LOCAL_KEYS.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or LOCAL_KEYS.get("GROQ_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY") or LOCAL_KEYS.get("SERPAPI_API_KEY", "")
