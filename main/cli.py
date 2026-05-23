from __future__ import annotations

from ai_client import OnlineAI
from config import PATHS
from models import CAPABILITIES, EXPERT_MODES, LOCAL_MODELS
from project_context import ProjectContext
from storage import save_json


def run_cli() -> int:
    ai = OnlineAI()
    project = ProjectContext()
    local_model = "offline-fast"
    provider = "gemini"
    print("JCZ AI 中樞 - 終端模式")
    print(f"資料目錄：{PATHS.data_dir}")
    print("一般對話與程式碼使用本地模型；只有「訓練」會使用聯網 AI。")
    print("指令：提問、訓練、模型、接管、加入檔案、加入資料夾、終端、路徑、離開")

    while True:
        command = input("\n> ").strip().lower()
        if command in {"q", "quit", "exit", "離開"}:
            return 0
        if command in {"paths", "路徑"}:
            print(f"應用程式：{PATHS.app_dir}")
            print(f"使用者資料：{PATHS.data_dir}")
            print(f"模組目錄：{PATHS.module_dir}")
            print(f"專案根目錄：{project.root}")
            continue
        if command in {"models", "模型"}:
            print("本地模型：")
            for key, name in LOCAL_MODELS.items():
                print(f"- {key}: {name}")
            print("能力：")
            for item in CAPABILITIES:
                print(f"- {item.key}: {item.title}（{item.status}）")
            continue
        if command in {"接管", "takeover"}:
            folder = input("專案根目錄：").strip()
            print(project.take_over(folder))
            continue
        if command in {"加入檔案", "file"}:
            file_path = input("檔案路徑：").strip()
            print(project.add_file(file_path))
            continue
        if command in {"加入資料夾", "folder"}:
            folder = input("資料夾路徑：").strip()
            print(project.add_folder(folder))
            continue
        if command in {"終端", "shell"}:
            shell_command = input("終端指令：").strip()
            print(project.run_terminal(shell_command))
            continue
        if command not in {"ask", "提問", "train", "訓練"}:
            print("可用指令：提問、訓練、模型、接管、加入檔案、加入資料夾、終端、路徑、離開")
            continue

        mode = choose_mode()
        if command in {"ask", "提問"}:
            local_model = choose_local_model(local_model)
            prompt = input("請輸入需求：").strip()
            if not prompt:
                print("沒有輸入內容。")
                continue
            response = ai.ask(prompt, mode=mode, local_model=local_model, project_context=project.summary(max_files=8))
            path = save_json("本地對話", {"mode": mode, "local_model": local_model, "prompt": prompt, "response": response.__dict__})
            print(f"\n[{response.provider}]\n{response.text}\n\n已儲存：{path}")
        else:
            provider = choose_provider(provider)
            use_search = input("是否使用 Google 搜尋資料？（是/否）：").strip().lower() in {"是", "y", "yes"}
            prompt = input("請輸入訓練需求：").strip()
            if not prompt:
                print("沒有輸入內容。")
                continue
            response = ai.train(prompt, mode=mode, provider=provider, use_search=use_search, project_context=project.summary(max_files=8))
            path = save_json("訓練", {"mode": mode, "provider": provider, "prompt": prompt, "response": response.__dict__})
            print(f"\n[{response.provider}]\n{response.text}\n\n已儲存：{path}")


def choose_mode() -> str:
    keys = list(EXPERT_MODES)
    print("模式：")
    for index, key in enumerate(keys, start=1):
        print(f"  {index}. {EXPERT_MODES[key]}")
    choice = input("請選擇模式編號：").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(keys):
        return keys[int(choice) - 1]
    return "prototype"


def choose_local_model(current: str) -> str:
    keys = list(LOCAL_MODELS)
    print("本地模型：")
    for index, key in enumerate(keys, start=1):
        print(f"  {index}. {LOCAL_MODELS[key]}")
    choice = input(f"請選擇本地模型編號（Enter 使用目前：{LOCAL_MODELS[current]}）：").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(keys):
        return keys[int(choice) - 1]
    return current


def choose_provider(current: str) -> str:
    choice = input(f"聯網訓練模型 gemini/groq（Enter 使用目前：{current}）：").strip().lower()
    if choice in {"gemini", "groq"}:
        return choice
    return current
