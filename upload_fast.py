import pandas as pd
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import time
import math

# 환경변수 로드
load_dotenv()

def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # 서비스 키 사용 (더 많은 권한)
    
    if not url or not key:
        print("❌ 환경변수를 확인하세요:")
        print("   SUPABASE_URL")
        print("   SUPABASE_SERVICE_ROLE_KEY")
        return None
    
    return create_client(url, key)

def get_column_mapping(table_name):
    """테이블별 컬럼 매핑 정의"""
    if table_name == "cafe_data":
        return {
            '가맹점명': 'franchise_name', '업종': 'business_type', '가맹점지역': 'franchise_region',
            '상권': 'commercial_area', '남성비중': 'male_ratio', '여성비중': 'female_ratio',
            '성비차이': 'gender_difference', '연령집중도': 'age_concentration', '주요고객층': 'main_customer_group',
            '충성도지수': 'loyalty_index', '상권유형': 'commercial_area_type', '고객유형': 'customer_type'
        }
    elif table_name == "revisit_data":
        return {
            '가맹점구분번호': 'franchise_id', '가맹점주소': 'franchise_address', '가맹점명': 'franchise_name',
            '브랜드구분코드': 'brand_code', '가맹점지역': 'franchise_region', '업종': 'business_type',
            '상권': 'commercial_area', '개설일': 'opening_date', '폐업일': 'closing_date',
            '기준년월': 'base_year_month', 'MCT_OPE_MS_CN': 'mct_ope_ms_cn', '월간매출액': 'monthly_sales',
            '월간이용건수': 'monthly_usage_count', '월간이용고객수': 'monthly_customer_count',
            '월평균객단가': 'monthly_avg_price', '평균결제비율': 'avg_payment_ratio', '배달매출비율': 'delivery_sales_ratio',
            '동종업종매출비율_1개월': 'same_industry_sales_ratio_1m', '동종업종이용비율_1개월': 'same_industry_usage_ratio_1m',
            '동종업종매출점유율_12개월': 'same_industry_sales_share_12m', '상권매출점유율_12개월': 'commercial_area_sales_share_12m',
            '동종업종평균매출비율_12개월': 'same_industry_avg_sales_ratio_12m', '상권평균매출비율_12개월': 'commercial_area_avg_sales_ratio_12m',
            '남성20대이하비율': 'male_under20_ratio', '남성30대비율': 'male_30s_ratio', '남성40대비율': 'male_40s_ratio',
            '남성50대비율': 'male_50s_ratio', '남성60대이상비율': 'male_over60_ratio',
            '여성20대이하비율': 'female_under20_ratio', '여성30대비율': 'female_30s_ratio', '여성40대비율': 'female_40s_ratio',
            '여성50대비율': 'female_50s_ratio', '여성60대이상비율': 'female_over60_ratio',
            '재방문고객비율': 'revisit_customer_ratio', '신규고객비율': 'new_customer_ratio',
            '거주이용고객비율': 'residential_customer_ratio', '직장이용고객비율': 'workplace_customer_ratio',
            '유동인구이용고객비율': 'floating_population_customer_ratio', '업종평균재방문률': 'industry_avg_revisit_rate',
            '상권평균재방문률': 'commercial_area_avg_revisit_rate', '재방문률변화': 'revisit_rate_change',
            '재방문률_3개월평균': 'revisit_rate_3m_avg', '업종대비차이': 'industry_comparison_diff',
            '재방문률_등급': 'revisit_rate_grade'
        }
    elif table_name == "restaurant_data":
        return {
            '가맹점구분번호': 'franchise_id', '가맹점주소': 'franchise_address', '가맹점명': 'franchise_name',
            '브랜드구분코드': 'brand_code', '가맹점지역': 'franchise_region', '업종': 'business_type',
            '상권': 'commercial_area', '개설일': 'opening_date', '폐업일': 'closing_date',
            '기준년월': 'base_year_month', 'MCT_OPE_MS_CN': 'mct_ope_ms_cn', '월간매출액': 'monthly_sales',
            '월간이용건수': 'monthly_usage_count', '월간이용고객수': 'monthly_customer_count',
            '월평균객단가': 'monthly_avg_price', '평균결제비율': 'avg_payment_ratio', '배달매출비율': 'delivery_sales_ratio',
            '동종업종매출비율_1개월': 'same_industry_sales_ratio_1m', '동종업종이용비율_1개월': 'same_industry_usage_ratio_1m',
            '동종업종매출점유율_12개월': 'same_industry_sales_share_12m', '상권매출점유율_12개월': 'commercial_area_sales_share_12m',
            '동종업종평균매출비율_12개월': 'same_industry_avg_sales_ratio_12m', '상권평균매출비율_12개월': 'commercial_area_avg_sales_ratio_12m',
            '남성20대이하비율': 'male_under20_ratio', '남성30대비율': 'male_30s_ratio', '남성40대비율': 'male_40s_ratio',
            '남성50대비율': 'male_50s_ratio', '남성60대이상비율': 'male_over60_ratio',
            '여성20대이하비율': 'female_under20_ratio', '여성30대비율': 'female_30s_ratio', '여성40대비율': 'female_40s_ratio',
            '여성50대비율': 'female_50s_ratio', '여성60대이상비율': 'female_over60_ratio',
            '재방문고객비율': 'revisit_customer_ratio', '신규고객비율': 'new_customer_ratio',
            '거주이용고객비율': 'residential_customer_ratio', '직장이용고객비율': 'workplace_customer_ratio',
            '유동인구이용고객비율': 'floating_population_customer_ratio', '월간매출액_rank': 'monthly_sales_rank',
            '월간매출액_score': 'monthly_sales_score', '월간이용건수_rank': 'monthly_usage_count_rank',
            '월간이용건수_score': 'monthly_usage_count_score', '월간이용고객수_rank': 'monthly_customer_count_rank',
            '월간이용고객수_score': 'monthly_customer_count_score', '월평균객단가_rank': 'monthly_avg_price_rank',
            '월평균객단가_score': 'monthly_avg_price_score', '평균결제비율_rank': 'avg_payment_ratio_rank',
            '평균결제비율_score': 'avg_payment_ratio_score', '재방문고객비율_num': 'revisit_customer_ratio_num',
            '신규고객비율_num': 'new_customer_ratio_num', '거주이용고객비율_num': 'residential_customer_ratio_num',
            '직장이용고객비율_num': 'workplace_customer_ratio_num', '유동인구이용고객비율_num': 'floating_population_customer_ratio_num',
            '남성20대이하비율_num': 'male_under20_ratio_num', '남성30대비율_num': 'male_30s_ratio_num',
            '남성40대비율_num': 'male_40s_ratio_num', '남성50대비율_num': 'male_50s_ratio_num',
            '남성60대이상비율_num': 'male_over60_ratio_num', '여성20대이하비율_num': 'female_under20_ratio_num',
            '여성30대비율_num': 'female_30s_ratio_num', '여성40대비율_num': 'female_40s_ratio_num',
            '여성50대비율_num': 'female_50s_ratio_num', '여성60대이상비율_num': 'female_over60_ratio_num',
            '업종평균재방문률': 'industry_avg_revisit_rate', '상권평균재방문률': 'commercial_area_avg_revisit_rate',
            '업종평균매출': 'industry_avg_sales', '재방문률_업종차이': 'revisit_rate_industry_diff',
            '매출_업종차이': 'sales_industry_diff', '직장비율_과다': 'workplace_ratio_excess',
            '신규고객비중': 'new_customer_weight', '매출효율': 'sales_efficiency',
            '재방문률등급': 'revisit_rate_grade'
        }
    return {}

def clean_and_map_dataframe(df, table_name):
    column_mapping = get_column_mapping(table_name)
    mapped_df = pd.DataFrame()
    
    numeric_columns = {
        'cafe_data': ['male_ratio', 'female_ratio', 'gender_difference', 'age_concentration', 'loyalty_index'],
        'revisit_data': ['opening_date', 'closing_date', 'base_year_month', 'delivery_sales_ratio', 
                        'same_industry_sales_ratio_1m', 'same_industry_usage_ratio_1m', 'same_industry_sales_share_12m',
                        'commercial_area_sales_share_12m', 'same_industry_avg_sales_ratio_12m', 'commercial_area_avg_sales_ratio_12m',
                        'male_under20_ratio', 'male_30s_ratio', 'male_40s_ratio', 'male_50s_ratio', 'male_over60_ratio',
                        'female_under20_ratio', 'female_30s_ratio', 'female_40s_ratio', 'female_50s_ratio', 'female_over60_ratio',
                        'revisit_customer_ratio', 'new_customer_ratio', 'residential_customer_ratio', 'workplace_customer_ratio',
                        'floating_population_customer_ratio', 'industry_avg_revisit_rate', 'commercial_area_avg_revisit_rate',
                        'revisit_rate_change', 'revisit_rate_3m_avg', 'industry_comparison_diff'],
        'restaurant_data': ['opening_date', 'closing_date', 'base_year_month', 'delivery_sales_ratio',
                           'same_industry_sales_ratio_1m', 'same_industry_usage_ratio_1m', 'same_industry_sales_share_12m',
                           'commercial_area_sales_share_12m', 'same_industry_avg_sales_ratio_12m', 'commercial_area_avg_sales_ratio_12m',
                           'male_under20_ratio', 'male_30s_ratio', 'male_40s_ratio', 'male_50s_ratio', 'male_over60_ratio',
                           'female_under20_ratio', 'female_30s_ratio', 'female_40s_ratio', 'female_50s_ratio', 'female_over60_ratio',
                           'revisit_customer_ratio', 'new_customer_ratio', 'residential_customer_ratio', 'workplace_customer_ratio',
                           'floating_population_customer_ratio', 'monthly_sales_rank', 'monthly_sales_score',
                           'monthly_usage_count_rank', 'monthly_usage_count_score', 'monthly_customer_count_rank',
                           'monthly_customer_count_score', 'monthly_avg_price_rank', 'monthly_avg_price_score',
                           'avg_payment_ratio_rank', 'avg_payment_ratio_score', 'revisit_customer_ratio_num',
                           'new_customer_ratio_num', 'residential_customer_ratio_num', 'workplace_customer_ratio_num',
                           'floating_population_customer_ratio_num', 'male_under20_ratio_num', 'male_30s_ratio_num',
                           'male_40s_ratio_num', 'male_50s_ratio_num', 'male_over60_ratio_num', 'female_under20_ratio_num',
                           'female_30s_ratio_num', 'female_40s_ratio_num', 'female_50s_ratio_num', 'female_over60_ratio_num',
                           'industry_avg_revisit_rate', 'commercial_area_avg_revisit_rate', 'industry_avg_sales',
                           'revisit_rate_industry_diff', 'sales_industry_diff', 'workplace_ratio_excess',
                           'new_customer_weight', 'sales_efficiency']
    }
    
    table_numeric_cols = numeric_columns.get(table_name, [])
    
    for korean_col, english_col in column_mapping.items():
        if korean_col in df.columns:
            series = df[korean_col].copy()
            
            if english_col in table_numeric_cols:
                series = series.replace(['', ' ', 'nan', 'NaN', 'null', 'NULL'], None)
                try:
                    series = pd.to_numeric(series, errors='coerce')
                    series = series.replace([float('inf'), float('-inf')], None)
                    series = series.where(pd.notnull(series), None)
                except:
                    series = None
            else:
                series = series.fillna('')
                series = series.astype(str).str[:500]
            
            mapped_df[english_col] = series
        else:
            print(f"⚠️ 컬럼을 찾을 수 없음: {korean_col}")
    
    print(f"📋 매핑된 컬럼 수: {len(mapped_df.columns)}")
    return mapped_df

def upload_csv_to_supabase(csv_file, table_name, supabase_client):
    start_time = time.time()
    print(f"\n🚀 {csv_file} → {table_name} 고속 업로드 시작")
    print(f"📂 파일 읽는 중...")
    
    df = None
    for encoding in ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']:
        try:
            df = pd.read_csv(csv_file, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        print(f"❌ {csv_file} 파일을 읽을 수 없습니다.")
        return False
    
    print(f"✅ 원본 데이터: {len(df):,}행 × {len(df.columns)}열")
    print(f"🔄 데이터 매핑 중...")
    df = clean_and_map_dataframe(df, table_name)
    print(f"✅ 매핑 완료: {len(df):,}행 × {len(df.columns)}열")
    
    try:
        supabase_client.table(table_name).delete().neq('id', 0).execute()
        print(f"🗑️ 기존 {table_name} 데이터 삭제 완료")
    except Exception as e:
        print(f"ℹ️ {table_name} 테이블이 비어있거나 존재하지 않음: {e}")
    
    batch_size = 1000
    total_rows = len(df)
    successful_uploads = 0
    
    print(f"📤 {batch_size}개씩 고속 업로드 시작...")
    
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i+batch_size]
        data = batch.to_dict('records')
        
        cleaned_data = []
        for record in data:
            cleaned_record = {}
            for key, value in record.items():
                if pd.isna(value) or (isinstance(value, float) and (value != value or value in [float('inf'), float('-inf')])):
                    cleaned_record[key] = None
                else:
                    cleaned_record[key] = value
            cleaned_data.append(cleaned_record)
        
        data = cleaned_data
        
        try:
            result = supabase_client.table(table_name).insert(data).execute()
            successful_uploads += len(data)
            progress = (i + len(data)) / total_rows * 100
            elapsed_time = time.time() - start_time
            print(f"   배치 {i//batch_size + 1}/{math.ceil(total_rows/batch_size)}: {len(data):,}개 완료 | 진행률: {progress:.1f}% | 경과시간: {int(elapsed_time // 60)}분 {int(elapsed_time % 60)}초")
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ 배치 {i//batch_size + 1} 업로드 실패: {e}")
            break
    
    end_time = time.time()
    total_elapsed_time = end_time - start_time
    print(f"✅ {table_name} 업로드 완료!")
    print(f"   📊 성공: {successful_uploads:,}/{total_rows:,}개")
    print(f"   ⏱️ 소요시간: {int(total_elapsed_time // 60)}분 {int(total_elapsed_time % 60)}초")
    return successful_uploads == total_rows

def main():
    print("=" * 60)
    print("🚀 CSV → Supabase 업로드 시작 (컬럼명 매핑)")
    print("=" * 60)
    
    supabase = init_supabase()
    if not supabase:
        return
    
    files_to_upload = [
        ("file/Q1_data.csv", "cafe_data"),
        ("file/Q2_data.csv", "revisit_data"), 
        ("file/Q3_data.csv", "restaurant_data")
    ]
    
    success_count = 0
    main_start_time = time.time()
    
    for csv_file, table_name in files_to_upload:
        if os.path.exists(csv_file):
            if upload_csv_to_supabase(csv_file, table_name, supabase):
                success_count += 1
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {csv_file}")
    
    print("\n" + "=" * 70)
    print(f"🎉 전체 업로드 완료: {success_count}/{len(files_to_upload)}개 성공")
    print(f"⏱️ 총 소요시간: {int((time.time() - main_start_time) // 60)}분 {int((time.time() - main_start_time) % 60)}초")
    print("=" * 70)
    
    if success_count == len(files_to_upload):
        print("✅ 모든 데이터가 성공적으로 업로드되었습니다!")
        print("🚀 이제 streamlit run supabase_chatbot.py로 챗봇을 실행하세요!")
    else:
        print("⚠️ 일부 파일 업로드에 실패했습니다. 환경변수와 Supabase 설정을 확인하세요.")

if __name__ == "__main__":
    main()
