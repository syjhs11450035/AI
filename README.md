# JCZ AI 中樞

`main.py` 是專案入口。直接執行會優先啟動 GUI；如果 GUI 啟動失敗，會自動退回終端模式。

## 執行

```powershell
python main.py
```

終端模式：

```powershell
python main.py --cli
```

## 離線優先規則

此專案是為「沒有網路時也能工作」準備的。

- 一般對話使用本地模型。
- 寫程式、除錯、原型生成也使用本地模型。
- 專家模式用來決定本地模型的工作方式。
- 只有按下「訓練」或在終端模式使用「訓練」指令時，才會使用聯網 AI。
- 聯網訓練可以選擇 `gemini` 或 `groq`。
- Google 搜尋只會在訓練時勾選後使用。

## 專案接管

GUI 支援：

- 加入單一檔案
- 加入資料夾
- 接管整個專案
- 在專案根目錄執行終端指令

終端頁會在目前接管的專案根目錄執行本機指令，適合離線時檢查依賴、跑測試、建立索引或整理資料。

終端模式也支援相同能力：

```text
接管
加入檔案
加入資料夾
終端
```

## 打包

依照目前裝置打包：

```powershell
python build.py
```

打包後的檔案會輸出到 `dist/<系統>/JCZ_AI_Hub`。在 Windows 上預設使用 `--noconsole`，不會跳出額外的終端視窗。

需要除錯、想看終端輸出時：

```powershell
python build.py --console
```

## 資料位置

使用者內容會儲存在應用程式目錄旁：

```text
ai-data/
  conversations/
  outputs/
  logs/
  cache/
```

## 專案結構

```text
main.py
build.py
main/
  app.py
  gui.py
  cli.py
  ai_client.py
  config.py
  models.py
  project_context.py
  storage.py
  api-key/
  json/
  temp/
```

`main/api-key/` 不會進入 git。你可以用 `.env` 或 `main/api-key/api_keys.json` 提供金鑰：

```json
{
  "GEMINI_API_KEY": "你的金鑰",
  "GROQ_API_KEY": "你的金鑰",
  "SERPAPI_API_KEY": "你的金鑰"
}
```

## 專家模式

- 生成原型代碼
- 檢查邏輯死鎖
- 提出創新想法
- 生產環境代碼
- 分析調試錯誤
- 優化提示詞

## 原型能力

此應用會列出文字轉語音、生成音樂、圖片生成與編輯、語音對話、影片生成、Google 搜尋資料、Google 地圖資料、圖片分析、低延遲回應、影片分析、語音轉文字、Gemini 聊天與高思考模式等能力。

只有在設定 API 金鑰後，訓練功能才會使用聯網 AI。沒有金鑰時，應用會保持離線並回傳本地原型回覆。
