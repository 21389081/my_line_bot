import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 初始化時自動載入 .env
load_dotenv()
def get_supabase_client() -> Client:
    """初始化並回傳 Supabase 客戶端連線"""
    url = os.getenv("SUPABASE_URL") or ""
    key = os.getenv("SUPABASE_KEY") or ""
    return create_client(url, key)

# 建立一個全域的 supabase 實例供檔案內的函式使用
supabase_client = get_supabase_client()

def search_items(keyword: str) -> list[dict]:
    """
    與資料庫溝通，根據關鍵字搜尋相符的商品。
    如果 keyword 為空字串，則回傳所有商品。
    """
    try:
        # 向 Supabase 發送請求
        if keyword:
            # 在資料庫端執行模糊比對 (LIKE)，只回傳符合條件的資料
            # 由於欄位名稱包含特殊符號「[]」，需要加上雙引號 '"欄位"' 供 Supabase 辨識為單一欄位
            response = supabase_client.table("test").select("*").like('"品項名稱[規格]"', f"%{keyword}%").execute()
        else:
            # 如果是「查詢全部」(keyword 為空)，則直接取回所有資料
            response = supabase_client.table("test").select("*").execute()
            
        return response.data  # type: ignore
    except Exception as e:
        # 當資料庫發生連線/查詢錯誤時，將錯誤拋出讓外層處理
        raise Exception(f"資料庫查詢失敗: {str(e)}")
