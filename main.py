from __future__ import annotations

import argparse
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
MODULE_DIR = APP_DIR / "main"
sys.path.insert(0, str(MODULE_DIR))

from app import run_app  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JCZ AI 中樞")
    parser.add_argument("--cli", action="store_true", help="啟動終端模式")
    parser.add_argument("--gui", action="store_true", help="啟動圖形介面模式")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    prefer_gui = not args.cli
    return run_app(prefer_gui=prefer_gui)


if __name__ == "__main__":
    raise SystemExit(main())
