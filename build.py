from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path


APP_NAME = "JCZ_AI_Hub"
ROOT = Path(__file__).resolve().parent


def pyinstaller_command(console: bool = False) -> list[str]:
    system = platform.system().lower()
    suffix = ".exe" if system == "windows" else ""
    data_separator = ";" if system == "windows" else ":"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "main.py",
        "--name",
        APP_NAME,
        "--onefile",
        "--clean",
        "--distpath",
        str(ROOT / "dist" / system),
        "--workpath",
        str(ROOT / "build" / system),
        "--specpath",
        str(ROOT / "build" / system),
        "--add-data",
        f"main{data_separator}main",
    ]
    if not console:
        command.append("--noconsole" if system == "windows" else "--windowed")
    if system == "windows":
        command.extend(["--target-architecture", "x86_64"])
    print(f"輸出位置：{ROOT / 'dist' / system / (APP_NAME + suffix)}")
    return command


def build(console: bool = False) -> int:
    command = pyinstaller_command(console=console)
    print("執行打包：", " ".join(command))
    return subprocess.call(command, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="依照目前裝置打包 JCZ AI 中樞。")
    parser.add_argument("--console", action="store_true", help="打包後顯示終端視窗，方便除錯")
    args = parser.parse_args()
    return build(console=args.console)


if __name__ == "__main__":
    raise SystemExit(main())
