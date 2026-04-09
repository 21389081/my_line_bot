-- 建立 projects 資料表
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    department TEXT NOT NULL,
    project_name TEXT NOT NULL,
    secret_status TEXT NOT NULL
);

-- 設定 RLS (Row Level Security) 政策
-- 啟用 RLS
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- 允許任何人讀取資料 (如果希望公開讀取的話)
CREATE POLICY "允許公開讀取專案資料"
ON public.projects FOR SELECT
USING (true);

-- 插入測試資料 (與原本 CSV 相同)
-- 單位分類, 專案名稱, 機密狀態
INSERT INTO public.projects (department, project_name, secret_status) VALUES
('人事部', '2026企業招募計畫', '一般'),
('人事部', '高階主管薪資調整', '機密'),
('IT部', '基礎伺服器架構升級', '一般'),
('IT部', '全年度資安系統演練', '極機密'),
('財務部', 'Q1季度財報統整與查驗', '機密'),
('行銷部', '春季新產品全球發表會', '一般'),
('業務部', '海外經銷商拓展計畫', '一般');
