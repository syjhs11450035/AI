from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    key: str
    title: str
    category: str
    status: str
    prompt_hint: str


CAPABILITIES: list[Capability] = [
    Capability("audio_spark_tts", "文字轉語音", "音訊", "原型", "把文字轉成自然語音。"),
    Capability("music_note", "生成音樂", "音訊", "原型", "依照提示生成短配樂、音效或循環片段。"),
    Capability("database_auth", "資料庫與登入", "應用", "設計", "設計 Firebase Auth 與 Firestore 持久化。"),
    Capability("image_edit_auto", "建立與編輯圖片", "圖片", "原型", "依照文字提示建立或編輯圖片。"),
    Capability("live_voice", "語音對話", "音訊", "原型", "設計 Gemini Live 即時語音對話體驗。"),
    Capability("movie", "圖片轉動畫影片", "影片", "原型", "把靜態圖片規劃成短影片動畫。"),
    Capability("google_search", "使用 Google 搜尋資料", "搜尋", "需金鑰", "使用即時搜尋結果並附上來源。"),
    Capability("google_maps", "使用 Google 地圖資料", "地圖", "設計", "規劃地點、路線或方向資訊。"),
    Capability("image", "生成高品質圖片", "圖片", "原型", "依照比例、風格與用途生成圖片提示。"),
    Capability("spark", "Gemini 智慧", "推理", "需金鑰", "使用 Gemini 完成分析、改寫與生成。"),
    Capability("voice_chat", "Gemini 聊天機器人", "聊天", "需金鑰", "保留上下文並處理多步驟任務。"),
    Capability("video_spark", "文字生成影片", "影片", "原型", "把文字、腳本或商品描述轉成短影片方案。"),
    Capability("aspect_ratio", "控制圖片比例", "圖片", "原型", "產生符合指定長寬比的圖片提示。"),
    Capability("document_scanner", "分析圖片", "視覺", "原型", "擷取、翻譯或摘要收據、菜單、圖表等圖片內容。"),
    Capability("bolt", "低延遲回應", "速度", "需金鑰", "使用快速模型做即時補全或短對話。"),
    Capability("video_library", "分析影片內容", "影片", "原型", "找出長影片重點、摘要、卡片與亮點。"),
    Capability("speech_to_text", "語音轉文字", "音訊", "原型", "把音訊轉錄成乾淨文字。"),
    Capability("network_intelligence", "高思考模式", "推理", "需金鑰", "給複雜任務更多推理時間。"),
]


EXPERT_MODES: dict[str, str] = {
    "prototype": "生成原型代碼",
    "deadlock": "檢查邏輯死鎖",
    "ideas": "提出創新想法",
    "production": "生產環境代碼",
    "debug": "分析調試錯誤",
    "prompt": "優化提示詞",
}


def capability_summary() -> str:
    lines = []
    for item in CAPABILITIES:
        lines.append(f"- {item.title} [{item.category}] - {item.status}")
    return "\n".join(lines)
