from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from config import PATHS


TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
    ".html",
    ".css",
    ".js",
    ".ts",
}


@dataclass
class ProjectContext:
    root: Path = PATHS.app_dir
    files: list[Path] = field(default_factory=list)

    def take_over(self, folder: str | Path) -> str:
        self.root = Path(folder).resolve()
        self.files = self._scan_folder(self.root)
        return f"已接管專案：{self.root}\n已加入 {len(self.files)} 個文字檔。"

    def add_file(self, file_path: str | Path) -> str:
        path = Path(file_path).resolve()
        if path.is_file() and path not in self.files:
            self.files.append(path)
        return f"已加入檔案：{path}"

    def add_folder(self, folder: str | Path) -> str:
        folder_path = Path(folder).resolve()
        added = 0
        for path in self._scan_folder(folder_path):
            if path not in self.files:
                self.files.append(path)
                added += 1
        return f"已加入資料夾：{folder_path}\n新增 {added} 個文字檔。"

    def summary(self, max_files: int = 20, max_chars_per_file: int = 4000) -> str:
        parts = [f"專案根目錄：{self.root}", f"已加入檔案數：{len(self.files)}"]
        for path in self.files[:max_files]:
            parts.append(f"\n--- {path} ---")
            parts.append(self._read_text(path, max_chars_per_file))
        if len(self.files) > max_files:
            parts.append(f"\n尚有 {len(self.files) - max_files} 個檔案未放入摘要。")
        return "\n".join(parts)

    def list_files(self) -> str:
        if not self.files:
            return "尚未加入檔案。"
        return "\n".join(str(path) for path in self.files)

    def run_terminal(self, command: str, timeout: int = 60) -> str:
        if not command.strip():
            return "沒有輸入終端指令。"
        try:
            result = subprocess.run(
                command,
                cwd=self.root,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return f"指令逾時：{command}"
        output = result.stdout.strip()
        error = result.stderr.strip()
        sections = [f"$ {command}", f"結束代碼：{result.returncode}"]
        if output:
            sections.append(f"\n輸出：\n{output}")
        if error:
            sections.append(f"\n錯誤：\n{error}")
        return "\n".join(sections)

    def _scan_folder(self, folder: Path) -> list[Path]:
        if not folder.exists():
            return []
        files: list[Path] = []
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {".git", "__pycache__", "build", "dist", "ai-data"} for part in path.parts):
                continue
            if path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path.resolve())
        return files

    def _read_text(self, path: Path, max_chars: int) -> str:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"讀取失敗：{exc}"
        if len(text) > max_chars:
            return text[:max_chars] + "\n...（內容已截斷）"
        return text
