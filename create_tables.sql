-- Supabase 테이블 생성 SQL
-- 실행 방법: Supabase Dashboard → SQL Editor에서 실행

-- cafe_data 테이블
CREATE TABLE IF NOT EXISTS public.cafe_data (
    id SERIAL PRIMARY KEY,
    franchise_name VARCHAR(70),
    business_type VARCHAR(52),
    franchise_region VARCHAR(56),
    commercial_area VARCHAR(54),
    male_ratio DECIMAL,
    female_ratio DECIMAL,
    gender_difference DECIMAL,
    age_concentration DECIMAL,
    main_customer_group VARCHAR(59),
    loyalty_index DECIMAL,
    commercial_area_type VARCHAR(56),
    customer_type VARCHAR(53),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS (Row Level Security) 활성화
ALTER TABLE public.cafe_data ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽을 수 있도록 정책 생성
CREATE POLICY "Enable read access for all users" ON public.cafe_data
    FOR SELECT USING (true);

-- 인증된 사용자가 삽입할 수 있도록 정책 생성
CREATE POLICY "Enable insert for authenticated users only" ON public.cafe_data
    FOR INSERT WITH CHECK (true);

-- revisit_data 테이블
CREATE TABLE IF NOT EXISTS public.revisit_data (
    id SERIAL PRIMARY KEY,
    franchise_id VARCHAR(50),
    franchise_address VARCHAR(200),
    franchise_name VARCHAR(100),
    brand_code VARCHAR(50),
    franchise_region VARCHAR(100),
    business_type VARCHAR(100),
    commercial_area VARCHAR(100),
    opening_date INTEGER,
    closing_date INTEGER,
    base_year_month INTEGER,
    mct_ope_ms_cn VARCHAR(50),
    monthly_sales VARCHAR(50),
    monthly_usage_count VARCHAR(50),
    monthly_customer_count VARCHAR(50),
    monthly_avg_price VARCHAR(50),
    avg_payment_ratio VARCHAR(50),
    delivery_sales_ratio DECIMAL,
    same_industry_sales_ratio_1m DECIMAL,
    same_industry_usage_ratio_1m DECIMAL,
    same_industry_sales_share_12m DECIMAL,
    commercial_area_sales_share_12m DECIMAL,
    same_industry_avg_sales_ratio_12m DECIMAL,
    commercial_area_avg_sales_ratio_12m DECIMAL,
    male_under20_ratio DECIMAL,
    male_30s_ratio DECIMAL,
    male_40s_ratio DECIMAL,
    male_50s_ratio DECIMAL,
    male_over60_ratio DECIMAL,
    female_under20_ratio DECIMAL,
    female_30s_ratio DECIMAL,
    female_40s_ratio DECIMAL,
    female_50s_ratio DECIMAL,
    female_over60_ratio DECIMAL,
    revisit_customer_ratio DECIMAL,
    new_customer_ratio DECIMAL,
    residential_customer_ratio DECIMAL,
    workplace_customer_ratio DECIMAL,
    floating_population_customer_ratio DECIMAL,
    industry_avg_revisit_rate DECIMAL,
    commercial_area_avg_revisit_rate DECIMAL,
    revisit_rate_change DECIMAL,
    revisit_rate_3m_avg DECIMAL,
    industry_comparison_diff DECIMAL,
    revisit_rate_grade VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 활성화 및 정책 생성
ALTER TABLE public.revisit_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON public.revisit_data FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON public.revisit_data FOR INSERT WITH CHECK (true);

-- restaurant_data 테이블 (더 많은 컬럼 포함)
CREATE TABLE IF NOT EXISTS public.restaurant_data (
    id SERIAL PRIMARY KEY,
    franchise_id VARCHAR(50),
    franchise_address VARCHAR(200),
    franchise_name VARCHAR(100),
    brand_code VARCHAR(50),
    franchise_region VARCHAR(100),
    business_type VARCHAR(100),
    commercial_area VARCHAR(100),
    opening_date INTEGER,
    closing_date INTEGER,
    base_year_month INTEGER,
    mct_ope_ms_cn VARCHAR(50),
    monthly_sales VARCHAR(50),
    monthly_usage_count VARCHAR(50),
    monthly_customer_count VARCHAR(50),
    monthly_avg_price VARCHAR(50),
    avg_payment_ratio VARCHAR(50),
    delivery_sales_ratio DECIMAL,
    same_industry_sales_ratio_1m DECIMAL,
    same_industry_usage_ratio_1m DECIMAL,
    same_industry_sales_share_12m DECIMAL,
    commercial_area_sales_share_12m DECIMAL,
    same_industry_avg_sales_ratio_12m DECIMAL,
    commercial_area_avg_sales_ratio_12m DECIMAL,
    male_under20_ratio DECIMAL,
    male_30s_ratio DECIMAL,
    male_40s_ratio DECIMAL,
    male_50s_ratio DECIMAL,
    male_over60_ratio DECIMAL,
    female_under20_ratio DECIMAL,
    female_30s_ratio DECIMAL,
    female_40s_ratio DECIMAL,
    female_50s_ratio DECIMAL,
    female_over60_ratio DECIMAL,
    revisit_customer_ratio DECIMAL,
    new_customer_ratio DECIMAL,
    residential_customer_ratio DECIMAL,
    workplace_customer_ratio DECIMAL,
    floating_population_customer_ratio DECIMAL,
    monthly_sales_rank DECIMAL,
    monthly_sales_score DECIMAL,
    monthly_usage_count_rank DECIMAL,
    monthly_usage_count_score DECIMAL,
    monthly_customer_count_rank DECIMAL,
    monthly_customer_count_score DECIMAL,
    monthly_avg_price_rank DECIMAL,
    monthly_avg_price_score DECIMAL,
    avg_payment_ratio_rank DECIMAL,
    avg_payment_ratio_score DECIMAL,
    revisit_customer_ratio_num DECIMAL,
    new_customer_ratio_num DECIMAL,
    residential_customer_ratio_num DECIMAL,
    workplace_customer_ratio_num DECIMAL,
    floating_population_customer_ratio_num DECIMAL,
    male_under20_ratio_num DECIMAL,
    male_30s_ratio_num DECIMAL,
    male_40s_ratio_num DECIMAL,
    male_50s_ratio_num DECIMAL,
    male_over60_ratio_num DECIMAL,
    female_under20_ratio_num DECIMAL,
    female_30s_ratio_num DECIMAL,
    female_40s_ratio_num DECIMAL,
    female_50s_ratio_num DECIMAL,
    female_over60_ratio_num DECIMAL,
    industry_avg_revisit_rate DECIMAL,
    commercial_area_avg_revisit_rate DECIMAL,
    industry_avg_sales DECIMAL,
    revisit_rate_industry_diff DECIMAL,
    sales_industry_diff DECIMAL,
    workplace_ratio_excess DECIMAL,
    new_customer_weight DECIMAL,
    sales_efficiency DECIMAL,
    revisit_rate_grade VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 활성화 및 정책 생성
ALTER TABLE public.restaurant_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON public.restaurant_data FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON public.restaurant_data FOR INSERT WITH CHECK (true);
