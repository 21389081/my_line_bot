from database import search_items, add_item, delete_item

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
    reply_text = "⚠️ 無效的輸入！\n目前機器人僅支援以下指令：\n👉 「查詢全部」\n👉 「查詢 [品項名稱]」\n👉 「新增 [品項名稱] [庫存數量] [實際盤點] [(可選)備註]」\n👉 「刪除 [品項名稱]」\n(注意中間需有半形空格)"
    
    is_search = False
    is_add = False
    is_delete = False
    
    keyword = ""
    add_data = {}
    delete_name = ""

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
    elif user_message.startswith("新增 "):
        parts = user_message.split(" ")
        # 過濾多餘空白，確保使用者多打空白也不會出錯
        parts = [p for p in parts if p.strip()]
        
        if len(parts) >= 4:
            try:
                name = parts[1]
                stock = int(parts[2])
                actual = int(parts[3])
                # 若有備註，將剩餘的部份重新組裝
                remarks = " ".join(parts[4:]) if len(parts) > 4 else ""
                
                add_data = {
                    "name": name,
                    "stock": stock,
                    "actual": actual,
                    "remarks": remarks
                }
                is_add = True
            except ValueError:
                reply_text = "⚠️ 數字格式錯誤！\n請確定「庫存數量」與「實際盤點」都是整數。\n例如：新增 行動電源 20 18"
        else:
            reply_text = "⚠️ 新增指令格式錯誤！\n請依照：新增 [品項名稱] [庫存數量] [實際盤點] \n例如：新增 行動電源 20 18"
            
    elif user_message.startswith("刪除 "):
        delete_name = user_message.split(" ", 1)[1].strip()
        if delete_name:
            is_delete = True
        else:
            reply_text = "⚠️ 請輸入想要刪除的品項名稱！\n例如：刪除 行動電源"
            
    elif user_message == "讀取excel":
        reply_text = "⚠️ 系統指令已升級！\n請使用新指令：\n「查詢全部」或「查詢 [品項名稱]」\n例如：查詢 行動電源"
        
    # 2. 商業邏輯調用 (Business Logic & Services)
    if is_search:
        try:
            # 呼叫資料庫取得資料
            results = search_items(keyword)
            # 將資料拋給排版方法
            reply_text = format_search_results(results, keyword)
        except Exception as e:
            reply_text = f"不好意思，小幫手遇到了一點問題：\n{str(e)}"
    elif is_add:
        try:
            add_item(add_data["name"], add_data["stock"], add_data["actual"], add_data["remarks"])
            reply_text = f"✅ 已成功新增品項：{add_data['name']}\n庫存：{add_data['stock']} / 盤點：{add_data['actual']}"
        except Exception as e:
            reply_text = f"新增失敗：\n{str(e)}"
    elif is_delete:
        try:
            results = delete_item(delete_name)
            if results:
                reply_text = f"✅ 已成功刪除品項：{delete_name} (共刪除 {len(results)} 筆資料)"
            else:
                reply_text = f"⚠️ 找不到品項「{delete_name}」，無法刪除。"
        except Exception as e:
            reply_text = f"刪除失敗：\n{str(e)}"
            
    return reply_text
