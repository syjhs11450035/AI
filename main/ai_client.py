from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from config import GEMINI_API_KEY, GROQ_API_KEY, SERPAPI_API_KEY
from models import EXPERT_MODES, LOCAL_MODELS, capability_summary


@dataclass
class AIResponse:
    text: str
    provider: str
    online: bool


class OnlineAI:
    """離線優先的 AI 路由。

    ask() 永遠使用本地原型模型。
    train() 才會使用 Groq 或 Gemini 聯網訓練。
    """

    def __init__(self) -> None:
        self.gemini_key = GEMINI_API_KEY
        self.groq_key = GROQ_API_KEY
        self.serpapi_key = SERPAPI_API_KEY

    def available(self) -> bool:
        return bool(self.gemini_key or self.groq_key)

    def ask(
        self,
        prompt: str,
        mode: str = "prototype",
        local_model: str = "offline-fast",
        project_context: str = "",
    ) -> AIResponse:
        return AIResponse(
            text=self._local_response(prompt, mode, local_model, project_context),
            provider=LOCAL_MODELS.get(local_model, "本地模型"),
            online=False,
        )

    def train(
        self,
        prompt: str,
        mode: str = "prototype",
        provider: str = "gemini",
        use_search: bool = False,
        project_context: str = "",
    ) -> AIResponse:
        context = self._search(prompt) if use_search else ""
        if project_context:
            context += f"\n專案內容：\n{project_context}\n"
        system_prompt = self._system_prompt(mode, context)

        if provider == "groq":
            if not self.groq_key:
                return AIResponse("尚未設定 GROQ_API_KEY，無法使用 Groq 訓練。", "Groq", False)
            try:
                return AIResponse(self._groq(prompt, system_prompt), "Groq 訓練", True)
            except Exception as exc:
                return AIResponse(f"Groq 訓練失敗：{exc}", "Groq 訓練", False)

        if not self.gemini_key:
            return AIResponse("尚未設定 GEMINI_API_KEY，無法使用 Gemini 訓練。", "Gemini", False)
        try:
            return AIResponse(self._gemini(prompt, system_prompt), "Gemini 訓練", True)
        except Exception as exc:
            return AIResponse(f"Gemini 訓練失敗：{exc}", "Gemini 訓練", False)

    def _local_response(self, prompt: str, mode: str, local_model: str, project_context: str) -> str:
        mode_name = EXPERT_MODES.get(mode, EXPERT_MODES["prototype"])
        model_name = LOCAL_MODELS.get(local_model, "本地模型")
        context_note = "已載入專案上下文。" if project_context else "尚未載入專案上下文。"
        if mode == "production":
            body = "我會以可維護、可測試、可打包的方式規劃程式碼，並優先避免依賴網路。"
        elif mode == "debug":
            body = "我會先列出可能錯誤點，再給出本地可執行的檢查步驟。"
        elif mode == "deadlock":
            body = "我會從狀態、等待條件、資源鎖定與事件迴圈檢查邏輯死鎖。"
        elif mode == "ideas":
            body = "我會提出可離線使用、可逐步擴充的創新方向。"
        elif mode == "prompt":
            body = "我會把需求整理成更穩定、更明確、可重複使用的提示詞。"
        else:
            body = "我會先產生可運作的原型，再標出下一步可替換成本地真模型的位置。"
        return (
            f"[{model_name}｜{mode_name}]\n\n"
            "目前使用本地模式，沒有呼叫 Groq、Gemini 或搜尋服務。\n"
            f"{context_note}\n\n"
            f"{body}\n\n"
            "本地準備建議：\n"
            "1. 把需要離線工作的檔案或資料夾加入專案上下文。\n"
            "2. 使用終端頁先確認環境、依賴與測試指令。\n"
            "3. 只有需要訓練或更新知識時，再按訓練按鈕使用聯網 AI。\n\n"
            f"你的需求：{prompt}"
        )

    def _system_prompt(self, mode: str, context: str) -> str:
        mode_name = EXPERT_MODES.get(mode, EXPERT_MODES["prototype"])
        return (
            "你是一位務實的 AI 產品工程師。請使用繁體中文回答。\n"
            f"目前訓練模式：{mode_name}。\n"
            "這次呼叫是明確的訓練行為，可以使用聯網 AI。\n"
            "訓練目標是讓應用在沒有網路時也能準備好本地知識、提示詞與專案上下文。\n"
            "可用模型功能：\n"
            f"{capability_summary()}\n"
            f"{context}"
        )

    def _gemini(self, prompt: str, system_prompt: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={self.gemini_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n訓練資料或需求：\n{prompt}"}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048},
        }
        data = self._post_json(url, payload)
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _groq(self, prompt: str, system_prompt: str) -> str:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        headers = {"Authorization": f"Bearer {self.groq_key}"}
        data = self._post_json("https://api.groq.com/openai/v1/chat/completions", payload, headers)
        return data["choices"][0]["message"]["content"]

    def _search(self, query: str) -> str:
        if not self.serpapi_key:
            return "\n已要求搜尋，但尚未設定 SERPAPI_API_KEY。\n"
        params = urllib.parse.urlencode({"engine": "google", "q": query, "num": 5, "api_key": self.serpapi_key})
        with urllib.request.urlopen(f"https://serpapi.com/search.json?{params}", timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        snippets = []
        for item in data.get("organic_results", [])[:5]:
            snippets.append(f"- {item.get('title', '')}: {item.get('snippet', '')} ({item.get('link', '')})")
        return "\n即時搜尋內容：\n" + "\n".join(snippets) + "\n"

    def _post_json(self, url: str, payload: dict, headers: dict[str, str] | None = None) -> dict:
        body = json.dumps(payload).encode("utf-8")
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        request = urllib.request.Request(url, data=body, headers=request_headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
