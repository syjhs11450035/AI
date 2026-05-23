from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ai_client import OnlineAI
from config import PATHS
from models import CAPABILITIES, EXPERT_MODES, LOCAL_MODELS
from project_context import ProjectContext
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


FONT = "Microsoft JhengHei UI"


class AIHubGUI:
    def __init__(self) -> None:
        self.ai = OnlineAI()
        self.project = ProjectContext()
        self._set_process_dpi_awareness()
        self.root = tk.Tk()
        self.root.title("JCZ AI 中樞")
        self.root.geometry("1240x780")
        self.root.minsize(1040, 680)
        self.root.configure(bg=COLORS["bg"])
        self._scale_tk_for_dpi()
        self._configure_style()

        self.mode = tk.StringVar(value="prototype")
        self.local_model = tk.StringVar(value=LOCAL_MODELS["offline-fast"])
        self.online_provider = tk.StringVar(value="gemini")
        self.use_search = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value=f"就緒 - 一般對話與程式碼皆使用本地模型。資料位置：{PATHS.data_dir}")
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
            font=(FONT, 10),
        )
        style.configure(
            "Hub.Treeview.Heading",
            background=COLORS["panel_soft"],
            foreground=COLORS["text"],
            borderwidth=0,
            font=(FONT, 10, "bold"),
        )
        style.map("Hub.Treeview", background=[("selected", COLORS["accent"])])

    def _build(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_workspace()
        self._select_view("chat")

    def _build_sidebar(self) -> None:
        sidebar = tk.Frame(self.root, bg=COLORS["panel"], width=280)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        tk.Label(sidebar, text="JCZ AI 中樞", bg=COLORS["panel"], fg=COLORS["text"], font=(FONT, 19, "bold")).pack(
            anchor="w", padx=22, pady=(24, 2)
        )
        tk.Label(sidebar, text="離線優先工作台", bg=COLORS["panel"], fg=COLORS["muted"], font=(FONT, 10)).pack(
            anchor="w", padx=22, pady=(0, 22)
        )

        for key, label in (
            ("chat", "AI 工作室"),
            ("project", "專案上下文"),
            ("terminal", "終端"),
            ("models", "模型能力"),
            ("data", "資料庫"),
        ):
            button = tk.Button(
                sidebar,
                text=label,
                command=lambda view=key: self._select_view(view),
                anchor="w",
                bd=0,
                relief="flat",
                padx=18,
                pady=11,
                cursor="hand2",
                font=(FONT, 11, "bold"),
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                activebackground=COLORS["panel_soft"],
                activeforeground=COLORS["text"],
            )
            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = button

        self._separator(sidebar)
        self._label(sidebar, "專家模式").pack(anchor="w", padx=22, pady=(0, 8))
        for key, label in EXPERT_MODES.items():
            self._radio(sidebar, label, key, self.mode).pack(fill="x", padx=18, pady=3)

        self._separator(sidebar)
        self._label(sidebar, "本地模型").pack(anchor="w", padx=22, pady=(0, 8))
        local_menu = tk.OptionMenu(sidebar, self.local_model, *LOCAL_MODELS.values())
        self._style_option_menu(local_menu)
        local_menu.pack(fill="x", padx=18, pady=(0, 10))

        self._label(sidebar, "聯網訓練模型").pack(anchor="w", padx=22, pady=(8, 8))
        provider_menu = tk.OptionMenu(sidebar, self.online_provider, "gemini", "groq")
        self._style_option_menu(provider_menu)
        provider_menu.pack(fill="x", padx=18)

        tk.Checkbutton(
            sidebar,
            text="訓練時使用 Google 搜尋",
            variable=self.use_search,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            selectcolor=COLORS["input"],
            activebackground=COLORS["panel"],
            activeforeground=COLORS["text"],
            font=(FONT, 10),
        ).pack(anchor="w", padx=20, pady=14)

        availability = "可進行聯網訓練" if self.ai.available() else "尚未設定聯網金鑰"
        color = COLORS["ok"] if self.ai.available() else COLORS["muted"]
        tk.Label(sidebar, text=availability, bg=COLORS["panel"], fg=color, font=(FONT, 10, "bold")).pack(
            side="bottom", anchor="w", padx=22, pady=(0, 24)
        )

    def _build_workspace(self) -> None:
        workspace = tk.Frame(self.root, bg=COLORS["bg"])
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(1, weight=1)

        header = tk.Frame(workspace, bg=COLORS["bg"])
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 12))
        header.columnconfigure(0, weight=1)
        tk.Label(header, text="AI 工作室", bg=COLORS["bg"], fg=COLORS["text"], font=(FONT, 22, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(header, textvariable=self.status, bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT, 10)).grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )

        body = tk.Frame(workspace, bg=COLORS["bg"])
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self.frames["chat"] = self._create_chat_view(body)
        self.frames["project"] = self._create_project_view(body)
        self.frames["terminal"] = self._create_terminal_view(body)
        self.frames["models"] = self._create_models_view(body)
        self.frames["data"] = self._create_data_view(body)

    def _create_chat_view(self, parent: tk.Frame) -> tk.Frame:
        frame = self._view_frame(parent)
        toolbar = self._panel(frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        toolbar.columnconfigure(0, weight=1)
        tk.Label(
            toolbar,
            text="送出＝本地模型；訓練＝Groq/Gemini 聯網 AI。",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=(FONT, 12, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=14)
        tk.Button(toolbar, text="加入檔案", command=self._add_file, **self._small_button()).grid(row=0, column=1, padx=4)
        tk.Button(toolbar, text="加入資料夾", command=self._add_folder, **self._small_button()).grid(row=0, column=2, padx=4)
        tk.Button(toolbar, text="接管專案", command=self._take_over_project, **self._small_button()).grid(row=0, column=3, padx=(4, 12))

        self.output = self._text(frame)
        self.output.grid(row=1, column=0, sticky="nsew")
        self.output.insert("end", "歡迎使用。一般對話與寫程式都會使用本地模型；只有按下訓練才會連網。\n")

        input_bar = tk.Frame(frame, bg=COLORS["bg"])
        input_bar.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        input_bar.columnconfigure(0, weight=1)
        self.prompt = tk.Entry(
            input_bar,
            bd=0,
            bg=COLORS["input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            font=(FONT, 12),
            relief="flat",
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
        )
        self.prompt.grid(row=0, column=0, sticky="ew", ipady=13)
        self.prompt.bind("<Return>", lambda _event: self._send_local())
        tk.Button(input_bar, text="送出", command=self._send_local, **self._primary_button()).grid(row=0, column=1, padx=(10, 0))
        tk.Button(input_bar, text="訓練", command=self._train_online, **self._train_button()).grid(row=0, column=2, padx=(10, 0))
        return frame

    def _create_project_view(self, parent: tk.Frame) -> tk.Frame:
        frame = self._view_frame(parent)
        toolbar = self._panel(frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        tk.Button(toolbar, text="加入檔案", command=self._add_file, **self._small_button()).pack(side="left", padx=8, pady=10)
        tk.Button(toolbar, text="加入資料夾", command=self._add_folder, **self._small_button()).pack(side="left", padx=4, pady=10)
        tk.Button(toolbar, text="接管整個專案", command=self._take_over_project, **self._small_button()).pack(side="left", padx=4, pady=10)
        tk.Button(toolbar, text="重新整理摘要", command=self._refresh_project_text, **self._small_button()).pack(side="left", padx=4, pady=10)

        self.project_text = self._text(frame)
        self.project_text.grid(row=1, column=0, sticky="nsew")
        self._refresh_project_text()
        return frame

    def _create_terminal_view(self, parent: tk.Frame) -> tk.Frame:
        frame = self._view_frame(parent)
        self.terminal_output = self._text(frame)
        self.terminal_output.grid(row=0, column=0, sticky="nsew")
        self.terminal_output.insert("end", f"終端工作目錄：{self.project.root}\n")

        bar = tk.Frame(frame, bg=COLORS["bg"])
        bar.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        bar.columnconfigure(0, weight=1)
        self.terminal_command = tk.Entry(
            bar,
            bd=0,
            bg=COLORS["input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            font=("Consolas", 11),
            relief="flat",
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
        )
        self.terminal_command.grid(row=0, column=0, sticky="ew", ipady=12)
        self.terminal_command.bind("<Return>", lambda _event: self._run_terminal())
        tk.Button(bar, text="執行", command=self._run_terminal, **self._primary_button()).grid(row=0, column=1, padx=(10, 0))
        return frame

    def _create_models_view(self, parent: tk.Frame) -> tk.Frame:
        frame = self._view_frame(parent)
        tk.Label(frame, text="原型能力清單", bg=COLORS["bg"], fg=COLORS["text"], font=(FONT, 15, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
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
        frame = self._view_frame(parent)
        entries = (
            ("應用程式目錄", PATHS.app_dir),
            ("使用者內容", PATHS.data_dir),
            ("專案模組", PATHS.module_dir),
            ("API 金鑰資料夾", PATHS.api_key_dir),
        )
        for index, (label, value) in enumerate(entries):
            row = self._panel(frame)
            row.grid(row=index, column=0, sticky="ew", pady=6)
            row.columnconfigure(1, weight=1)
            tk.Label(row, text=label, bg=COLORS["panel"], fg=COLORS["muted"], font=(FONT, 10, "bold")).grid(
                row=0, column=0, sticky="w", padx=16, pady=14
            )
            tk.Label(row, text=str(value), bg=COLORS["panel"], fg=COLORS["text"], font=("Consolas", 10)).grid(
                row=0, column=1, sticky="w", padx=16, pady=14
            )
        return frame

    def _send_local(self) -> None:
        prompt = self.prompt.get().strip()
        if not prompt:
            return
        self.prompt.delete(0, "end")
        self.output.insert("end", f"\n你\n{prompt}\n\nAI（本地）\n思考中...\n")
        self.status.set("本地模型思考中...")
        threading.Thread(target=self._run_local, args=(prompt,), daemon=True).start()

    def _train_online(self) -> None:
        prompt = self.prompt.get().strip()
        if not prompt:
            return
        self.prompt.delete(0, "end")
        provider = self.online_provider.get()
        self.output.insert("end", f"\n你\n{prompt}\n\n訓練（{provider}）\n連線訓練中...\n")
        self.status.set(f"正在使用 {provider} 進行聯網訓練...")
        threading.Thread(target=self._run_training, args=(prompt, provider), daemon=True).start()

    def _run_local(self, prompt: str) -> None:
        response = self.ai.ask(
            prompt,
            mode=self.mode.get(),
            local_model=self._local_model_key(),
            project_context=self.project.summary(max_files=8),
        )
        save_path = save_json("本地對話", {"prompt": prompt, "mode": self.mode.get(), "response": response.__dict__})
        self.root.after(0, self._show_response, response.provider, response.text, save_path)

    def _run_training(self, prompt: str, provider: str) -> None:
        response = self.ai.train(
            prompt,
            mode=self.mode.get(),
            provider=provider,
            use_search=self.use_search.get(),
            project_context=self.project.summary(max_files=8),
        )
        save_path = save_json("訓練", {"prompt": prompt, "mode": self.mode.get(), "provider": provider, "response": response.__dict__})
        self.root.after(0, self._show_response, response.provider, response.text, save_path)

    def _show_response(self, provider: str, text: str, save_path) -> None:
        self.output.insert("end", f"\n[{provider}]\n{text}\n")
        self.output.see("end")
        self.status.set(f"已儲存 - {save_path}")

    def _local_model_key(self) -> str:
        selected = self.local_model.get()
        for key, label in LOCAL_MODELS.items():
            if label == selected:
                return key
        return "offline-fast"

    def _add_file(self) -> None:
        file_path = filedialog.askopenfilename(title="選擇要加入的檔案")
        if file_path:
            self._project_message(self.project.add_file(file_path))

    def _add_folder(self) -> None:
        folder = filedialog.askdirectory(title="選擇要加入的資料夾")
        if folder:
            self._project_message(self.project.add_folder(folder))

    def _take_over_project(self) -> None:
        folder = filedialog.askdirectory(title="選擇要接管的專案根目錄")
        if folder:
            self._project_message(self.project.take_over(folder))

    def _project_message(self, message: str) -> None:
        self.status.set(message.replace("\n", " "))
        if hasattr(self, "project_text"):
            self._refresh_project_text()
        if hasattr(self, "terminal_output"):
            self.terminal_output.insert("end", f"\n{message}\n終端工作目錄：{self.project.root}\n")

    def _refresh_project_text(self) -> None:
        if not hasattr(self, "project_text"):
            return
        self.project_text.delete("1.0", "end")
        self.project_text.insert("end", self.project.summary(max_files=30, max_chars_per_file=1200))

    def _run_terminal(self) -> None:
        command = self.terminal_command.get().strip()
        self.terminal_command.delete(0, "end")
        self.terminal_output.insert("end", f"\n$ {command}\n執行中...\n")
        self.status.set("終端指令執行中...")
        threading.Thread(target=self._run_terminal_thread, args=(command,), daemon=True).start()

    def _run_terminal_thread(self, command: str) -> None:
        result = self.project.run_terminal(command)
        self.root.after(0, self._show_terminal_result, result)

    def _show_terminal_result(self, result: str) -> None:
        self.terminal_output.insert("end", f"{result}\n")
        self.terminal_output.see("end")
        self.status.set("終端指令完成。")

    def _select_view(self, name: str) -> None:
        for key, frame in self.frames.items():
            if key == name:
                frame.tkraise()
            else:
                frame.lower()
        for key, button in self.nav_buttons.items():
            active = key == name
            button.configure(bg=COLORS["accent"] if active else COLORS["panel"], fg="white" if active else COLORS["muted"])

    def _view_frame(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        return frame

    def _panel(self, parent: tk.Frame) -> tk.Frame:
        return tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)

    def _text(self, parent: tk.Frame) -> tk.Text:
        return tk.Text(
            parent,
            wrap="word",
            bd=0,
            padx=18,
            pady=18,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            selectbackground=COLORS["accent"],
            font=(FONT, 11),
            relief="flat",
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
        )

    def _label(self, parent: tk.Frame, text: str) -> tk.Label:
        return tk.Label(parent, text=text, bg=COLORS["panel"], fg=COLORS["muted"], font=(FONT, 9, "bold"))

    def _radio(self, parent: tk.Frame, text: str, value: str, variable: tk.StringVar) -> tk.Radiobutton:
        return tk.Radiobutton(
            parent,
            text=text,
            value=value,
            variable=variable,
            indicatoron=False,
            bd=0,
            padx=10,
            pady=8,
            selectcolor=COLORS["accent"],
            bg=COLORS["panel_soft"],
            fg=COLORS["text"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text"],
            font=(FONT, 9),
        )

    def _style_option_menu(self, menu: tk.OptionMenu) -> None:
        menu.configure(
            bd=0,
            bg=COLORS["panel_soft"],
            fg=COLORS["text"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text"],
            highlightthickness=0,
            font=(FONT, 10),
        )
        menu["menu"].configure(bg=COLORS["panel_soft"], fg=COLORS["text"], activebackground=COLORS["accent"])

    def _primary_button(self) -> dict:
        return {
            "bd": 0,
            "padx": 24,
            "pady": 12,
            "cursor": "hand2",
            "bg": COLORS["accent"],
            "fg": "white",
            "activebackground": COLORS["accent_hover"],
            "activeforeground": "white",
            "font": (FONT, 11, "bold"),
        }

    def _train_button(self) -> dict:
        return {
            "bd": 0,
            "padx": 24,
            "pady": 12,
            "cursor": "hand2",
            "bg": COLORS["ok"],
            "fg": "white",
            "activebackground": "#238636",
            "activeforeground": "white",
            "font": (FONT, 11, "bold"),
        }

    def _small_button(self) -> dict:
        return {
            "bd": 0,
            "padx": 12,
            "pady": 8,
            "cursor": "hand2",
            "bg": COLORS["panel_soft"],
            "fg": COLORS["text"],
            "activebackground": COLORS["accent_hover"],
            "activeforeground": COLORS["text"],
            "font": (FONT, 10, "bold"),
        }

    def _separator(self, parent: tk.Frame) -> None:
        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=16)


def run_gui() -> None:
    AIHubGUI().run()
