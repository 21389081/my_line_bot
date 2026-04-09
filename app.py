import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from supabase import create_client, Client

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# 讀取 .env 檔案
load_dotenv()

# 從環境變數中取得私密資訊
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

app = Flask(__name__)

supabase: Client = create_client(supabase_url, supabase_key)
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text.strip()

    # 預設：當輸入不符合任何已知指令時的回覆
    reply_text = "⚠️ 無效的輸入！\n目前機器人僅支援以下指令：\n👉 「查詢全部」\n👉 「查詢 [關鍵字]」(注意中間需有半形空格)"
    
    keyword = None
    is_search = False

    if user_message == "查詢全部":
        keyword = ""
        is_search = True
    elif user_message.startswith("查詢 "):
        keyword = user_message.split(" ", 1)[1].strip()
        if keyword:
            is_search = True
        else:
            reply_text = "⚠️ 請輸入想要查詢的關鍵字！\n例如：查詢 人事"
    elif user_message == "讀取excel":
        reply_text = "⚠️ 系統指令已升級！\n請使用新指令：\n「查詢全部」或「查詢 [關鍵字]」\n例如：查詢 人事"
        
    if is_search:
        try:
            results = []
            # 從 Supabase 取得資料
            response = supabase.table("projects").select("*").execute()
            all_data = response.data
            header = ["單位分類", "專案名稱", "機密狀態"]
            
            # 逐列檢查
            for item in all_data:
                row = [item.get('department', ''), item.get('project_name', ''), item.get('secret_status', '')]
                if not keyword or any(keyword in col for col in row):
                    results.append(row)
            
            # 組織回傳文字
            if results:
                reply_text = f"【搜尋結果：{keyword if keyword else '全部內容'}】\n"
                reply_text += " | ".join(header) + "\n"
                reply_text += "-" * 22 + "\n"
                
                for row in results:
                    reply_text += " | ".join(row) + "\n"
            else:
                reply_text = f"查無包含『{keyword}』的相關資料。"
                
        except Exception as e:
            reply_text = f"讀取資料庫失敗：{str(e)}"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    app.run()