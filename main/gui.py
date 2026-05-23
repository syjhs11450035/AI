from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from ai_client import OnlineAI
from config import PATHS
from models import CAPABILITIES, EXPERT_MODES
from storage import save_json


COLORS = {
    "bg": "#0d1117",
    "panel": "#151b23",
    "panel_soft": "#1c2330",
    "border": "#303744",
    "text": "#edf2f7",
    "muted": "#9aa4b2",
    "accent": "#2f81f7",
    "accent_hover": "#1f6feb",
    "ok": "#2ea043",
    "input": "#0f141c",
}


class AIHubGUI:
    def __init__(self) -> None:
        self.ai = OnlineAI()
        self._set_process_dpi_awareness()
        self.root = tk.Tk()
        self.root.title("JCZ AI 中樞")
        self.root.geometry("1180x760")
        self.root.minsize(980, 640)
        self.root.configure(bg=COLORS["bg"])
        self._scale_tk_for_dpi()
        self._configure_style()

        self.mode = tk.StringVar(value="prototype")
        self.use_search = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value=f"就緒 - 資料會儲存在 {PATHS.data_dir}")
        self.frames: dict[str, tk.Frame] = {}
        self.nav_buttons: dict[str, tk.Button] = {}

        self._build()

    def run(self) -> None:
        self.root.mainloop()

    def _set_process_dpi_awareness(self) -> None:
        try:
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    def _scale_tk_for_dpi(self) -> None:
        try:
            scaling = max(self.root.winfo_fpixels("1i") / 72, 1.0)
            self.root.tk.call("tk", "scaling", scaling)
        except Exception:
            pass

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Hub.Treeview",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["panel"],
            borderwidth=0,
            rowheight=32,
            font=("Microsoft JhengHei UI", 10),
        )
        style.configure(
            "Hub.Treeview.Heading",
            background=COLORS["panel_soft"],
            foreground=COLORS["text"],
            borderwidth=0,
            font=("Microsoft JhengHei UI", 10, "bold"),
        )
        style.map("Hub.Treeview", background=[("selected", COLORS["accent"])])

    def _build(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_workspace()
        self._select_view("chat")

    def _build_sidebar(self) -> None:
        sidebar = tk.Frame(self.root, bg=COLORS["panel"], width=260)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        tk.Label(
            sidebar,
            text="JCZ AI 中樞",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Microsoft JhengHei UI", 19, "bold"),
        ).pack(anchor="w", padx=22, pady=(24, 2))
        tk.Label(
            sidebar,
            text="聯網 AI 工作台",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Microsoft JhengHei UI", 10),
        ).pack(anchor="w", padx=22, pady=(0, 22))

        for key, label in (("chat", "AI 工作室"), ("models", "模型能力"), ("data", "資料庫")):
            button = tk.Button(
                sidebar,
                text=label,
                command=lambda view=key: self._select_view(view),
                anchor="w",
                bd=0,
                relief="flat",
                padx=18,
                pady=12,
                cursor="hand2",
                font=("Microsoft JhengHei UI", 11, "bold"),
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                activebackground=COLORS["panel_soft"],
                activeforeground=COLORS["text"],
            )
            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = button

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=18)

        tk.Label(
            sidebar,
            text="專家模式",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Microsoft JhengHei UI", 9, "bold"),
        ).pack(anchor="w", padx=22, pady=(0, 8))

        mode_box = tk.Frame(sidebar, bg=COLORS["panel"])
        mode_box.pack(fill="x", padx=18)
        for key, label in EXPERT_MODES.items():
            button = tk.Radiobutton(
                mode_box,
                text=label,
                value=key,
                variable=self.mode,
                indicatoron=False,
                bd=0,
                padx=10,
                pady=8,
                selectcolor=COLORS["accent"],
                bg=COLORS["panel_soft"],
                fg=COLORS["text"],
                activebackground=COLORS["accent_hover"],
                activeforeground=COLORS["text"],
                font=("Microsoft JhengHei UI", 9),
            )
            button.pack(fill="x", pady=3)

        search = tk.Checkbutton(
            sidebar,
            text="使用 Google 搜尋資料",
            variable=self.use_search,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            selectcolor=COLORS["input"],
            activebackground=COLORS["panel"],
            activeforeground=COLORS["text"],
            font=("Microsoft JhengHei UI", 10),
        )
        search.pack(anchor="w", padx=20, pady=18)

        availability = "已找到線上金鑰" if self.ai.available() else "離線原型模式"
        color = COLORS["ok"] if self.ai.available() else COLORS["muted"]
        tk.Label(
            sidebar,
            text=availability,
            bg=COLORS["panel"],
            fg=color,
            font=("Microsoft JhengHei UI", 10, "bold"),
        ).pack(side="bottom", anchor="w", padx=22, pady=(0, 24))

    def _build_workspace(self) -> None:
        workspace = tk.Frame(self.root, bg=COLORS["bg"])
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(1, weight=1)

        header = tk.Frame(workspace, bg=COLORS["bg"])
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 12))
        header.columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="AI 工作室",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Microsoft JhengHei UI", 22, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            textvariable=self.status,
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=("Microsoft JhengHei UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        body = tk.Frame(workspace, bg=COLORS["bg"])
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self.frames["chat"] = self._create_chat_view(body)
        self.frames["models"] = self._create_models_view(body)
        self.frames["data"] = self._create_data_view(body)

    def _create_chat_view(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        toolbar = tk.Frame(frame, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        toolbar.columnconfigure(0, weight=1)
        tk.Label(
            toolbar,
            text="提問、打樣、除錯，或把想法變成程式碼。",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Microsoft JhengHei UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=14)
        tk.Label(
            toolbar,
            text="按 Enter 送出",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Microsoft JhengHei UI", 10),
        ).grid(row=0, column=1, sticky="e", padx=16)

        self.output = tk.Text(
            frame,
            wrap="word",
            bd=0,
            padx=18,
            pady=18,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            selectbackground=COLORS["accent"],
            font=("Microsoft JhengHei UI", 11),
            relief="flat",
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
        )
        self.output.grid(row=1, column=0, sticky="nsew")
        self.output.insert("end", "歡迎使用。選擇模式、輸入需求，然後送出。\n")

        input_bar = tk.Frame(frame, bg=COLORS["bg"])
        input_bar.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        input_bar.columnconfigure(0, weight=1)
        self.prompt = tk.Entry(
            input_bar,
            bd=0,
            bg=COLORS["input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            font=("Microsoft JhengHei UI", 12),
            relief="flat",
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
        )
        self.prompt.grid(row=0, column=0, sticky="ew", ipady=13)
        self.prompt.bind("<Return>", lambda _event: self._send())
        tk.Button(
            input_bar,
            text="送出",
            command=self._send,
            bd=0,
            padx=24,
            pady=12,
            cursor="hand2",
            bg=COLORS["accent"],
            fg="white",
            activebackground=COLORS["accent_hover"],
            activeforeground="white",
            font=("Microsoft JhengHei UI", 11, "bold"),
        ).grid(row=0, column=1, padx=(10, 0))
        return frame

    def _create_models_view(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        tk.Label(
            frame,
            text="原型能力清單",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Microsoft JhengHei UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        columns = ("title", "category", "status")
        tree = ttk.Treeview(frame, columns=columns, show="headings", style="Hub.Treeview")
        tree.heading("title", text="功能")
        tree.heading("category", text="類型")
        tree.heading("status", text="狀態")
        tree.column("title", width=360)
        tree.column("category", width=160)
        tree.column("status", width=180)
        tree.grid(row=1, column=0, sticky="nsew")
        for item in CAPABILITIES:
            tree.insert("", "end", values=(item.title, item.category, item.status))
        return frame

    def _create_data_view(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)

        entries = (
            ("應用程式目錄", PATHS.app_dir),
            ("使用者內容", PATHS.data_dir),
            ("專案模組", PATHS.module_dir),
            ("API 金鑰資料夾", PATHS.api_key_dir),
        )
        for index, (label, value) in enumerate(entries):
            row = tk.Frame(frame, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
            row.grid(row=index, column=0, sticky="ew", pady=6)
            row.columnconfigure(1, weight=1)
            tk.Label(row, text=label, bg=COLORS["panel"], fg=COLORS["muted"], font=("Microsoft JhengHei UI", 10, "bold")).grid(
                row=0, column=0, sticky="w", padx=16, pady=14
            )
            tk.Label(row, text=str(value), bg=COLORS["panel"], fg=COLORS["text"], font=("Consolas", 10)).grid(
                row=0, column=1, sticky="w", padx=16, pady=14
            )
        return frame

    def _select_view(self, name: str) -> None:
        for key, frame in self.frames.items():
            if key == name:
                frame.tkraise()
            else:
                frame.lower()
        for key, button in self.nav_buttons.items():
            active = key == name
            button.configure(
                bg=COLORS["accent"] if active else COLORS["panel"],
                fg="white" if active else COLORS["muted"],
            )

    def _send(self) -> None:
        prompt = self.prompt.get().strip()
        if not prompt:
            return
        self.prompt.delete(0, "end")
        self.output.insert("end", f"\n你\n{prompt}\n\nAI\n思考中...\n")
        self.output.see("end")
        self.status.set("思考中...")
        threading.Thread(target=self._run_ai, args=(prompt,), daemon=True).start()

    def _run_ai(self, prompt: str) -> None:
        try:
            response = self.ai.ask(prompt, mode=self.mode.get(), use_search=self.use_search.get())
            save_path = save_json("對話", {"prompt": prompt, "mode": self.mode.get(), "response": response.__dict__})
            self.root.after(0, self._show_response, response.provider, response.text, save_path)
        except Exception as exc:
            self.root.after(0, lambda exc=exc: messagebox.showerror("AI 錯誤", str(exc)))

    def _show_response(self, provider: str, text: str, save_path) -> None:
        self.output.insert("end", f"\n[{provider}]\n{text}\n")
        self.output.see("end")
        self.status.set(f"已儲存 - {save_path}")


def run_gui() -> None:
    AIHubGUI().run()
