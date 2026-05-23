from __future__ import annotations

from ai_client import OnlineAI
from config import PATHS
from models import CAPABILITIES, EXPERT_MODES
from storage import save_json


def run_cli() -> int:
    ai = OnlineAI()
    print("JCZ AI Hub - terminal mode")
    print(f"Data directory: {PATHS.data_dir}")
    print("Commands: ask, models, paths, quit")
    while True:
        command = input("\n> ").strip().lower()
        if command in {"q", "quit", "exit"}:
            return 0
        if command == "paths":
            print(f"app: {PATHS.app_dir}")
            print(f"data: {PATHS.data_dir}")
            print(f"modules: {PATHS.module_dir}")
            continue
        if command == "models":
            for item in CAPABILITIES:
                print(f"- {item.key}: {item.title} ({item.status})")
            continue
        if command != "ask":
            print("Use: ask, models, paths, quit")
            continue

        print("Modes:", ", ".join(EXPERT_MODES))
        mode = input("mode: ").strip() or "prototype"
        use_search = input("use Google Search data? y/N: ").strip().lower() == "y"
        prompt = input("prompt: ").strip()
        if not prompt:
            print("Empty prompt.")
            continue
        response = ai.ask(prompt, mode=mode, use_search=use_search)
        print(f"\n[{response.provider}]\n{response.text}")
        path = save_json("conversation", {"mode": mode, "prompt": prompt, "response": response.__dict__})
        print(f"\nSaved: {path}")
