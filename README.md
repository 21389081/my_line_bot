# LINE Bot 盤點查詢與管理系統

這是一個基於 Python 與 Flask 框架打造的 LINE 聊天機器人 (LINE Bot) 專案。
本系統的主要功能是讓使用者能夠直接在 LINE 聊天室中，隨時隨地對 Supabase 雲端資料庫進行**庫存與盤點資料的查詢、新增與刪除**。

## 🚀 系統功能 (Features)

目前機器人支援四大核心指令，幫助您輕鬆管理資料庫：

- **模糊查詢**：傳送「`查詢 [品項名稱]`」，例如：`查詢 行動電源`，系統將回傳任何名稱中包含「行動電源」的所有產品盤點狀況。
- **查詢全部**：傳送「`查詢全部`」，系統將列出資料庫中所有的盤點清單。
- **新增資料**：傳送「`新增 [品項名稱] [庫存數量] [實際盤點] [(可選)備註]`」，例如：`新增 行動電源(白) 20 18 遺失兩顆`，系統將自動計算出「盤差」並寫入資料庫。
- **刪除資料**：傳送「`刪除 [品項名稱]`」，例如：`刪除 行動電源(白)`，系統將會前往資料庫進行精確配對並將該品項刪除。

**其他特色：**
- **直覺式排版**：回傳訊息經過重新設計，針對手機螢幕採取「垂直卡片」式條列佈局，確保盤點數據一目了然。
- **防呆與錯誤提示**：輸入錯誤指令、遺漏欄位或輸入非數字的內容時，系統會引導正確格式並提示錯誤。若查詢結果超出 LINE 單則訊息字數限制 (4000字)，也會主動截斷並提示。

---

## ⚙️ 系統架構與模組設計 (Architecture)

本系統採模組化設計，將職責妥善拆分以利後續的維護與擴充。主要劃分為以下三個核心檔案：

### 1. `app.py` (伺服器與 LINE 平台連接點)
- 負責載入環境變數（LINE 與 Supabase 金鑰）。
- 開啟 Flask Webhook 伺服器並提供 `/callback` 路由。
- 負責驗證來自 LINE 平台的訊息簽章 (Signature)，確保安全性。
- 接收到有效文字訊息後，將文字轉交給 `message_handler.py` 進行解析，最後將處理結果透過 LINE Reply API 傳送回使用者的手機上。

### 2. `message_handler.py` (中央訊息處理與商業邏輯)
- **意圖解析 (Intent Parsing)**：判斷使用者傳來的文字是屬於「查詢」、「新增」還是「刪除」指令，並將指令後的參數（如數量、品項名稱）切割提取出來。
- **防呆機制**：判斷字串與數字格式是否正確，若不正確則回傳對應的警告文案。
- **排版處理**：將從資料庫模組取回的生硬資料（Dictionary）透過迴圈整理，加上 Emoji 與分隔線，轉化成友善閱讀的文字格式。

### 3. `database.py` (資料庫 CRUD 操作層)
- 與 Supabase 建立連線。
- 提供三個核心的方法讓 `message_handler.py` 呼叫：
  - `search_items(keyword)`：執行 LIKE 模糊比對。
  - `add_item(name, stock, actual, remarks)`：將傳入的數值組成字典並寫入 `test` 資料表，自動計算 `actual - stock` 作為盤差。
  - `delete_item(name)`：執行精確比對並刪除指定的品項資料。

---

## 📚 本地開發與啟動指南

1. **配置環境**：確保您有安裝所需的套件（包含 `flask`, `line-bot-sdk`, `supabase`, `python-dotenv` 等）。
2. **設定 `.env`**：在專案根目錄必須擁有包含 LINE 與 Supabase 四把金鑰的環境設定檔：
   ```env
   LINE_CHANNEL_SECRET=您的Secret
   LINE_CHANNEL_ACCESS_TOKEN=您的Token
   SUPABASE_URL=您的專案URL
   SUPABASE_KEY=強烈建議使用您的 Service_Role Key 確保可以直接寫入資料與避開 RLS 限制
   ```
3. **資料庫設定提醒**：Supabase 中 `test` 資料表的 `id` 欄位必須設定為「Identity（自動遞增）」，否則新增資料會失敗。
4. **啟動伺服器**：
   ```bash
   python app.py
   # 或者是使用 Flask CLI:
   flask run
   ```
5. **準備公開 Webhook** (例如串接 ngrok)：由於 LINE 只能把訊息推入給一個公開的 https 網址，在本地開發測試時，需使用如 ngrok 工具將您的本機 Port 5000 變成臨時公開網址，並回填到 LINE Developer Console 中。
