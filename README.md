# JCZ AI Hub

`main.py` is the entry point. Run it directly and it starts the GUI by default. If the GUI fails, it falls back to terminal mode.

## Run

```powershell
python main.py
```

Terminal mode:

```powershell
python main.py --cli
```

## Build

Build for the current device:

```powershell
python build.py
```

The packaged app is written to `dist/<system>/JCZ_AI_Hub`. On Windows the packaged app uses `--noconsole`, so it does not open an extra terminal window.

Debug build with a visible terminal:

```powershell
python build.py --console
```

## Data Layout

User content is stored beside the application:

```text
ai-data/
  conversations/
  outputs/
  logs/
  cache/
```

Project modules are organized under:

```text
main.py
main/
  app.py
  gui.py
  cli.py
  ai_client.py
  config.py
  models.py
  storage.py
  api-key/
  json/
  temp/
```

`main/api-key/` is ignored by git. You can provide keys with `.env` or `main/api-key/api_keys.json`:

```json
{
  "GEMINI_API_KEY": "your-key",
  "GROQ_API_KEY": "your-key",
  "SERPAPI_API_KEY": "your-key"
}
```

## Modes

- 生成原型代碼
- 檢查邏輯死鎖
- 提出創新想法
- 生產環境代碼
- 分析調試錯誤
- 優化提示詞

## Model Feature Prototypes

The app lists prototypes for text-to-speech, music, image generation/editing, voice conversation, video generation, Google Search data, Google Maps data, document/image analysis, low-latency responses, video analysis, speech-to-text, Gemini chat, and high-thinking workflows.

Live training and current-knowledge features use online AI only when API keys are configured. Without keys, the app stays offline and returns a local prototype response.
