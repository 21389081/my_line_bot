# LINE Bot 盤點查詢系統

這是一個基於 Python 與 Flask 框架打造的 LINE 聊天機器人 (LINE Bot) 專案。
本系統的主要功能是讓使用者能夠直接在 LINE 聊天室中，隨時隨地從 Supabase 雲端資料庫查詢最新的**庫存與盤點資料**。

## 🚀 系統功能 (Features)

- **模糊查詢**：傳送「`查詢 [品項名稱]`」，例如：`查詢 行動電源`，系統將回傳任何名稱中包含「行動電源」的所有產品盤點狀況。
- **查詢全部**：傳送「`查詢全部`」，系統將列出資料庫中所有的盤點清單。
- **直覺式排版**：回傳訊息經過重新設計，針對手機螢幕採取「垂直卡片」式條列佈局，確保盤點數字一目了然。
- **防呆與錯誤提示**：輸入錯誤指令時會引導正確格式；若查詢結果超出 LINE 單則訊息字數限制 (4000字)，也會主動截斷並提示。

---

## ⚙️ 系統運行原理 (Architecture & Principles)

這個應用程式的核心是一個 **Webhook 伺服器**。整個資訊流 (Data Flow) 的運作機制如下：

1. **User 發送訊息（LINE APP）**：使用者在手機對著您的 LINE Bot 傳送文字「查詢 行動電源」。
2. **LINE Platform 推播給伺服器**：LINE 收到訊息後，會把這個事件包裝成 JSON，使用 `POST` 請求推播 (Webhook) 到這個 Python 系統所開啟的 `/callback` 網址。
3. **安全驗證**：Flask 接收到請求，程式首先會提取 `X-Line-Signature`，計算並驗證這個訊息是否真的是由 LINE 官方發送的。
4. **解析與過濾**：通過驗證後，我們自定義的 Python 處理函式 (`handle_message`) 會接手，把「查詢 行動電源」拆解，提取出關鍵字 `"行動電源"`。
5. **資料庫連線 (Supabase)**：系統呼叫 `supabase-py` 套件，向後台庫存資料庫中名為 `test` 的表單發起「讀取全部資料」的 API 請求。
6. **Python 邏輯運算**：拿到所有資料後，利用 Python 的 `for` 迴圈進行字串比對，篩選出符合關鍵字的產品，進一步將數據格式化為整齊的卡片字串。
7. **回傳給使用者**：透過 `linebot` SDK，呼叫 LINE 提供的 `Reply API`，將剛才組裝完成的盤點表字串傳回給使用者。


---

## 💻 `app.py` 程式邏輯深度解析

`app.py` 整支程式依照職責可以劃分為以下三大區塊：

### 1. 環境設定與初始化 (Initialization)
- **環境變數載入 (`load_dotenv`)**：使用 `dotenv` 套件將 `.env` 文件裡的敏感資訊（如 `LINE_CHANNEL_SECRET`、`SUPABASE_KEY`）安全載入記憶體。
- **實體化 (Instantiation)**：
  - 建立 `Flask` 應用程式實體。
  - 透過 `create_client(...)` 建立 `supabase` 資料庫操作物件。
  - 設定 `WebhookHandler` (負責驗證請求) 以及 `Configuration` (處理主動跟 LINE API 的溝通邏輯)。

### 2. 伺服器接收端點 (Webhook Endpoint: `/callback`)
- **裝飾器 (`@app.route`)**：告訴 Flask 當收到來自 `/callback` 路徑的 `POST` 請求時要觸發這個函式。
- **簽章驗證邏輯 (`handler.handle(body, signature)`)**：把請求的原始內文 (`body`) 與 HTTP 標頭裡的簽章 (`signature`) 交由 `line-bot-sdk` 自動查驗。若偽造或設定錯誤，會觸發 `InvalidSignatureError`，我們將拋出 http 狀態 400 來拒絕請求。

### 3. 使用者訊息處理邏輯 (Message Handler)
- **事件監聽器 (`@handler.add`)**：表示每當上面那層驗證成功，並且發現事件種類是「收到純文字訊息 (TextMessageContent)」時，就進入這個函式。
- **字串處理邏輯**：使用 Python 內建的方法如 `.strip()` 移除多餘空白，用 `.startswith()` 判斷前綴，並以 `.split(" ", 1)` 精準將指令與關鍵字分開。
- **資料庫互動與迴圈過濾**：
  - 呼叫 `supabase.table("test").select("*").execute()` 一口氣抓下當前庫存表。
  - 將資料寫入 `results` 陣列前，透過 `if not keyword or keyword in item_name` 來達成有輸入就過濾，沒輸入就全拿的靈活判斷。
- **組成 Reply API Request**：最終透過 `line_bot_api.reply_message_with_http_info()` 將結果塞進 `TextMessage` 物件，藉由專屬的 `reply_token` (回覆權杖) 原路退回給發言的使用者。

---

## 📚 本地開發與啟動指南

1. **配置環境**：確保您有設定 `requirements.txt` 指定的相應套件（包含 `flask`, `line-bot-sdk`, `supabase`）。
2. **設定 `.env`**：在專案根目錄必須擁有包含 LINE 與 Supabase 四把金鑰的環境設定檔。
3. **啟動伺服器**：
   ```bash
   python app.py
   # 或者是使用 Flask CLI:
   flask run
   ```
4. **準備公開 Webhook** (例如串接 ngrok)：由於 LINE 只能把訊息推入給一個公開的 https 網址，在本地開發測試時，需使用如 ngrok 工具將您的本機 Port 5000 變成臨時公開網址，並回填到 LINE Developer Console 中。
