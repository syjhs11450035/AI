from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from ai_client import OnlineAI
from config import PATHS
from models import CAPABILITIES, EXPERT_MODES
from storage import save_json


class AIHubGUI:
    def __init__(self) -> None:
        self.ai = OnlineAI()
        self._set_process_dpi_awareness()
        self.root = tk.Tk()
        self.root.title("JCZ AI Hub")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self._scale_tk_for_dpi()
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

    def _build(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self.root, padding=12)
        sidebar.grid(row=0, column=0, sticky="ns")

        ttk.Label(sidebar, text="JCZ AI Hub", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
        ttk.Label(sidebar, text="Mode").pack(anchor="w")
        self.mode = tk.StringVar(value="prototype")
        ttk.Combobox(sidebar, textvariable=self.mode, values=list(EXPERT_MODES), state="readonly", width=22).pack(fill="x")

        self.use_search = tk.BooleanVar(value=False)
        ttk.Checkbutton(sidebar, text="Use Google Search data", variable=self.use_search).pack(anchor="w", pady=12)

        self.status = tk.StringVar(value=f"Data: {PATHS.data_dir}")
        ttk.Label(sidebar, textvariable=self.status, wraplength=190).pack(anchor="w", pady=(16, 0))

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)

        chat = ttk.Frame(notebook, padding=12)
        notebook.add(chat, text="AI")
        chat.columnconfigure(0, weight=1)
        chat.rowconfigure(0, weight=1)

        self.output = tk.Text(chat, wrap="word", font=("Segoe UI", 11), height=20)
        self.output.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.prompt = ttk.Entry(chat)
        self.prompt.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(chat, text="Send", command=self._send).grid(row=1, column=1, padx=(8, 0), pady=(10, 0))
        self.prompt.bind("<Return>", lambda _event: self._send())

        models = ttk.Frame(notebook, padding=12)
        notebook.add(models, text="Models")
        columns = ("key", "title", "category", "status")
        tree = ttk.Treeview(models, columns=columns, show="headings")
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=160)
        tree.pack(fill="both", expand=True)
        for item in CAPABILITIES:
            tree.insert("", "end", values=(item.key, item.title, item.category, item.status))

        data = ttk.Frame(notebook, padding=12)
        notebook.add(data, text="Data")
        text = (
            f"Application directory:\n{PATHS.app_dir}\n\n"
            f"User content:\n{PATHS.data_dir}\n\n"
            f"Project modules:\n{PATHS.module_dir}\n\n"
            "API keys can be supplied by .env or main/api-key/api_keys.json."
        )
        ttk.Label(data, text=text, justify="left").pack(anchor="nw")

    def _send(self) -> None:
        prompt = self.prompt.get().strip()
        if not prompt:
            return
        self.prompt.delete(0, "end")
        self.output.insert("end", f"\nYou: {prompt}\nAI: working...\n")
        self.output.see("end")
        threading.Thread(target=self._run_ai, args=(prompt,), daemon=True).start()

    def _run_ai(self, prompt: str) -> None:
        try:
            response = self.ai.ask(prompt, mode=self.mode.get(), use_search=self.use_search.get())
            save_path = save_json("conversation", {"prompt": prompt, "mode": self.mode.get(), "response": response.__dict__})
            self.root.after(0, self._show_response, response.provider, response.text, save_path)
        except Exception as exc:
            self.root.after(0, lambda exc=exc: messagebox.showerror("AI error", str(exc)))

    def _show_response(self, provider: str, text: str, save_path) -> None:
        self.output.insert("end", f"\n[{provider}]\n{text}\n")
        self.output.see("end")
        self.status.set(f"Saved: {save_path}")


def run_gui() -> None:
    AIHubGUI().run()
