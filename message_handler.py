from database import search_items

def format_search_results(results: list[dict], keyword: str) -> str:
    """
    負責將資料庫傳回來的原始資料 (Array of Dictionaries)
    排版成具備 Emoji、分隔線、且符合受眾閱讀習慣的字串結構。
    """
    if not results:
        return f"查無包含『{keyword}』的相關資料。"
        
    reply_text = f"【搜尋結果：{keyword if keyword else '全部內容'}】\n"
    reply_text += "==================\n"
    
    for item in results:
        name = item.get('品項名稱[規格]', '未知品項')
        stock = item.get('庫存數量', 0)
        actual = item.get('實際盤點', 0)
        diff = item.get('盤差', 0)
        remarks = item.get('備注', '')
        
        if remarks is None:
            remarks = ""
            
        reply_text += f"📦 品項：{name}\n"
        reply_text += f"📊 庫存數量：{stock}\n"
        reply_text += f"✅ 實際盤點：{actual}\n"
        reply_text += f"⚠️ 盤差：{diff}\n"
        
        if str(remarks).strip():
            reply_text += f"📝 備註：{remarks}\n"
            
        reply_text += "----------------------\n"
    
    # 預防 LINE 限制的防呆處理
    if len(reply_text) > 4000:
        reply_text = reply_text[:4000] + "\n\n⚠️ 結果太多，超出 LINE 顯示限制，請輸入更精確的關鍵字！"
        
    return reply_text


def handle_text_message(user_message: str) -> str:
    """
    負責解析使用者的輸入文字，呼叫對應的商業邏輯模組，
    並決定最後要拋給 app.py 傳送回 LINE 的一段話。
    """
    user_message = user_message.strip()
    
    # 預設兜底回覆文案
    reply_text = "⚠️ 無效的輸入！\n目前機器人僅支援以下指令：\n👉 「查詢全部」\n👉 「查詢 [品項名稱]」(注意中間需有半形空格)"
    
    is_search = False
    keyword = ""

    # 1. 意圖解析 (Intent Parsing)
    if user_message == "查詢全部":
        keyword = ""
        is_search = True
    elif user_message.startswith("查詢 "):
        keyword = user_message.split(" ", 1)[1].strip()
        if keyword:
            is_search = True
        else:
            reply_text = "⚠️ 請輸入想要查詢的品項名稱關鍵字！\n例如：查詢 行動電源"
        
    # 2. 商業邏輯調用 (Business Logic & Services)
    if is_search:
        try:
            # 呼叫資料庫取得資料
            results = search_items(keyword)
            # 將資料拋給排版方法
            reply_text = format_search_results(results, keyword)
        except Exception as e:
            reply_text = f"不好意思，小幫手遇到了一點問題：\n{str(e)}"
            
    return reply_text
