from __future__ import annotations

from ai_client import OnlineAI
from config import PATHS
from models import CAPABILITIES, EXPERT_MODES
from storage import save_json


def run_cli() -> int:
    ai = OnlineAI()
    print("JCZ AI 中樞 - 終端模式")
    print(f"資料目錄：{PATHS.data_dir}")
    print("指令：提問、模型、路徑、離開")
    while True:
        command = input("\n> ").strip().lower()
        if command in {"q", "quit", "exit", "離開"}:
            return 0
        if command in {"paths", "路徑"}:
            print(f"應用程式：{PATHS.app_dir}")
            print(f"使用者資料：{PATHS.data_dir}")
            print(f"模組目錄：{PATHS.module_dir}")
            continue
        if command in {"models", "模型"}:
            for item in CAPABILITIES:
                print(f"- {item.key}: {item.title}（{item.status}）")
            continue
        if command not in {"ask", "提問"}:
            print("可用指令：提問、模型、路徑、離開")
            continue

        mode_keys = list(EXPERT_MODES)
        print("模式：")
        for index, key in enumerate(mode_keys, start=1):
            print(f"  {index}. {EXPERT_MODES[key]}")
        mode_input = input("請選擇模式編號：").strip()
        if mode_input.isdigit() and 1 <= int(mode_input) <= len(mode_keys):
            mode = mode_keys[int(mode_input) - 1]
        else:
            mode = "prototype"
        use_search = input("是否使用 Google 搜尋資料？（是/否）：").strip().lower() in {"是", "y", "yes"}
        prompt = input("請輸入需求：").strip()
        if not prompt:
            print("沒有輸入內容。")
            continue
        response = ai.ask(prompt, mode=mode, use_search=use_search)
        print(f"\n[{response.provider}]\n{response.text}")
        path = save_json("對話", {"mode": mode, "prompt": prompt, "response": response.__dict__})
        print(f"\n已儲存：{path}")
