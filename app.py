import os
from flask import Flask, request, abort
from dotenv import load_dotenv

# 匯入 LINE Bot 所需的模組
from linebot.v3 import WebhookHandler  # type: ignore
from linebot.v3.exceptions import InvalidSignatureError  # type: ignore
from linebot.v3.messaging import (  # type: ignore
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent  # type: ignore

# 匯入由我們自行封裝好的「訊息處理中心」
from message_handler import handle_text_message

# 讀取環境變數 (例如：LINE 的金鑰)
load_dotenv()
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# 建立 Flask 與 LINE Webhook 必要物件
app = Flask(__name__)
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

# 負責接收 LINE 平台推播過來的 Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Check your channel secret/access token.")
        abort(400)

    return 'OK'


# 當收到「文字訊息」事件時，所執行的處理函式
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 1. 取得使用者的文字
    user_message = event.message.text
    
    # 2. 將字串交給「客服人員」去解析並產生結果回覆的文案
    reply_text = handle_text_message(user_message)
    
    # 3. 呼叫 LINE 的 API，把文案確實傳送到使用者手機上
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

# 主程式進入點
if __name__ == "__main__":
    app.run()