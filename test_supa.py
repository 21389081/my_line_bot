import os
from dotenv import load_dotenv
from supabase import create_client, Client
## supabase 測試
load_dotenv()
supabase_url = os.getenv('SUPABASE_URL') or ""
supabase_key = os.getenv('SUPABASE_KEY') or ""
supabase: Client = create_client(supabase_url, supabase_key)

try:
    res = supabase.table("test").select("*").like('"品項名稱[規格]"', "%公仔%").execute()
    print("SUCCESS with quotes:", len(res.data))
except Exception as e:
    print("ERROR with quotes:", e)

try:
    res = supabase.table("test").select("*").like('品項名稱[規格]', "%公仔%").execute()
    print("SUCCESS without quotes:", len(res.data))
except Exception as e:
    print("ERROR without quotes:", e)
