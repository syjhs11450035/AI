from __future__ import annotations

import traceback

from cli import run_cli


def run_app(prefer_gui: bool = True) -> int:
    if prefer_gui:
        try:
            from gui import run_gui

            run_gui()
            return 0
        except Exception:
            print("GUI 啟動失敗，改用終端模式。")
            print(traceback.format_exc())
    return run_cli()
