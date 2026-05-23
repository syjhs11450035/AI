from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from config import GEMINI_API_KEY, GROQ_API_KEY, SERPAPI_API_KEY
from models import EXPERT_MODES, capability_summary


@dataclass
class AIResponse:
    text: str
    provider: str
    online: bool


class OnlineAI:
    def __init__(self) -> None:
        self.gemini_key = GEMINI_API_KEY
        self.groq_key = GROQ_API_KEY
        self.serpapi_key = SERPAPI_API_KEY

    def available(self) -> bool:
        return bool(self.gemini_key or self.groq_key)

    def ask(self, prompt: str, mode: str = "prototype", use_search: bool = False) -> AIResponse:
        context = self._search(prompt) if use_search else ""
        system_prompt = self._system_prompt(mode, context)
        if self.gemini_key:
            try:
                return AIResponse(self._gemini(prompt, system_prompt), "Gemini", True)
            except Exception as exc:
                return AIResponse(f"Gemini failed: {exc}\n\n{self._offline(prompt, mode)}", "Offline fallback", False)
        if self.groq_key:
            try:
                return AIResponse(self._groq(prompt, system_prompt), "Groq", True)
            except Exception as exc:
                return AIResponse(f"Groq failed: {exc}\n\n{self._offline(prompt, mode)}", "Offline fallback", False)
        return AIResponse(self._offline(prompt, mode), "Offline prototype", False)

    def _system_prompt(self, mode: str, context: str) -> str:
        mode_name = EXPERT_MODES.get(mode, EXPERT_MODES["prototype"])
        return (
            "You are a practical AI product engineer. Reply in Traditional Chinese unless asked otherwise.\n"
            f"Current mode: {mode_name}.\n"
            "Only training and live knowledge should use online AI. Keep user files under ai-data.\n"
            "Available model features:\n"
            f"{capability_summary()}\n"
            f"{context}"
        )

    def _gemini(self, prompt: str, system_prompt: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={self.gemini_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser request:\n{prompt}"}]}],
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
            return "\nSearch requested, but SERPAPI_API_KEY is not configured.\n"
        params = urllib.parse.urlencode({"engine": "google", "q": query, "num": 5, "api_key": self.serpapi_key})
        with urllib.request.urlopen(f"https://serpapi.com/search.json?{params}", timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        snippets = []
        for item in data.get("organic_results", [])[:5]:
            snippets.append(f"- {item.get('title', '')}: {item.get('snippet', '')} ({item.get('link', '')})")
        return "\nLive search context:\n" + "\n".join(snippets) + "\n"

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

    def _offline(self, prompt: str, mode: str) -> str:
        mode_name = EXPERT_MODES.get(mode, EXPERT_MODES["prototype"])
        return (
            f"[{mode_name}] Offline prototype response\n\n"
            "No GEMINI_API_KEY or GROQ_API_KEY is configured, so online AI training is disabled.\n"
            "Use this local planning skeleton first:\n"
            "1. Target feature\n"
            "2. Input data\n"
            "3. Expected output\n"
            "4. Risks and tests\n\n"
            f"User input: {prompt}"
        )
