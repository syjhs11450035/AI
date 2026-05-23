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
    Capability("audio_spark_tts", "Convert text to speech", "Audio", "prototype", "Turn this text into natural spoken audio."),
    Capability("music_note", "Generate music", "Audio", "prototype", "Create a short soundtrack, jingle, or loop from this idea."),
    Capability("database_auth", "Add database and auth", "App", "design", "Design Firebase Auth and Firestore persistence for this app."),
    Capability("image_edit_auto", "Create and edit images", "Image", "prototype", "Create or edit an image from this prompt."),
    Capability("live_voice", "Add voice conversations", "Audio", "prototype", "Design a real-time Gemini Live voice conversation."),
    Capability("movie", "Animate images into video", "Video", "prototype", "Animate this still image into a short video concept."),
    Capability("google_search", "Use Google Search data", "Search", "available with key", "Use live search results and cite sources."),
    Capability("google_maps", "Use Google Maps data", "Maps", "design", "Use Maps data for places, routes, or directions."),
    Capability("image", "Generate high-quality images", "Image", "prototype", "Generate a high quality image with this aspect and style."),
    Capability("spark", "Add Gemini intelligence", "Reasoning", "available with key", "Answer with Gemini intelligence."),
    Capability("voice_chat", "Add a Gemini chatbot", "Chat", "available with key", "Keep context and solve this multi-step request."),
    Capability("video_spark", "Generate video from text", "Video", "prototype", "Turn this text into a short video plan."),
    Capability("aspect_ratio", "Control image aspect ratios", "Image", "prototype", "Create image prompts for exact aspect ratios."),
    Capability("document_scanner", "Analyze images", "Vision", "prototype", "Extract, translate, or summarize image content."),
    Capability("bolt", "Add low-latency responses", "Speed", "available with key", "Use a fast response style for instant interaction."),
    Capability("video_library", "Analyze video content", "Video", "prototype", "Find key moments and summarize this video."),
    Capability("speech_to_text", "Transcribe audio", "Audio", "prototype", "Transcribe audio into clean text."),
    Capability("network_intelligence", "Enable high thinking", "Reasoning", "available with key", "Think carefully and solve complex tasks."),
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
