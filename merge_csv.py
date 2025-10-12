import pandas as pd
import os

print("=" * 80)
print("CSV 파일 분석 및 병합 시작")
print("=" * 80)

# 1. 각 CSV 파일 읽기
print("\n[1단계] CSV 파일 읽기 중...")
try:
    df1 = pd.read_csv('file/big_data_set1_f.csv', encoding='utf-8')
    print(f"✓ big_data_set1_f.csv 읽기 완료: {len(df1)}행")
except:
    df1 = pd.read_csv('file/big_data_set1_f.csv', encoding='cp949')
    print(f"✓ big_data_set1_f.csv 읽기 완료 (cp949 인코딩): {len(df1)}행")

try:
    df2 = pd.read_csv('file/big_data_set2_f.csv', encoding='utf-8')
    print(f"✓ big_data_set2_f.csv 읽기 완료: {len(df2)}행")
except:
    df2 = pd.read_csv('file/big_data_set2_f.csv', encoding='cp949')
    print(f"✓ big_data_set2_f.csv 읽기 완료 (cp949 인코딩): {len(df2)}행")

try:
    df3 = pd.read_csv('file/big_data_set3_f.csv', encoding='utf-8')
    print(f"✓ big_data_set3_f.csv 읽기 완료: {len(df3)}행")
except:
    df3 = pd.read_csv('file/big_data_set3_f.csv', encoding='cp949')
    print(f"✓ big_data_set3_f.csv 읽기 완료 (cp949 인코딩): {len(df3)}행")

# 2. 데이터 분석
print("\n" + "=" * 80)
print("[2단계] 데이터 구조 분석")
print("=" * 80)

print("\n📊 big_data_set1_f.csv (상점 기본 정보)")
print(f"   - 행 개수: {len(df1):,}")
print(f"   - 열 개수: {len(df1.columns)}")
print(f"   - 컬럼: {', '.join(df1.columns.tolist())}")
print(f"   - 고유 상점 수: {df1['ENCODED_MCT'].nunique():,}")

print("\n📊 big_data_set2_f.csv (매출/운영 정보)")
print(f"   - 행 개수: {len(df2):,}")
print(f"   - 열 개수: {len(df2.columns)}")
print(f"   - 컬럼: {', '.join(df2.columns.tolist())}")
print(f"   - 고유 상점 수: {df2['ENCODED_MCT'].nunique():,}")
if 'TA_YM' in df2.columns:
    print(f"   - 기간: {df2['TA_YM'].min()} ~ {df2['TA_YM'].max()}")

print("\n📊 big_data_set3_f.csv (고객 인구통계 정보)")
print(f"   - 행 개수: {len(df3):,}")
print(f"   - 열 개수: {len(df3.columns)}")
print(f"   - 컬럼: {', '.join(df3.columns.tolist())}")
print(f"   - 고유 상점 수: {df3['ENCODED_MCT'].nunique():,}")
if 'TA_YM' in df3.columns:
    print(f"   - 기간: {df3['TA_YM'].min()} ~ {df3['TA_YM'].max()}")

# 3. 데이터 병합
print("\n" + "=" * 80)
print("[3단계] 데이터 병합 중...")
print("=" * 80)

# df2와 df3을 먼저 병합 (ENCODED_MCT와 TA_YM 기준)
print("\n단계 1: big_data_set2와 big_data_set3 병합 (ENCODED_MCT + TA_YM 기준)")
df_merged_23 = pd.merge(df2, df3, on=['ENCODED_MCT', 'TA_YM'], how='outer')
print(f"   ✓ 병합 완료: {len(df_merged_23):,}행, {len(df_merged_23.columns)}열")

# df1을 병합 (ENCODED_MCT 기준)
print("\n단계 2: 상점 기본정보(big_data_set1) 병합 (ENCODED_MCT 기준)")
df_final = pd.merge(df_merged_23, df1, on='ENCODED_MCT', how='left')
print(f"   ✓ 최종 병합 완료: {len(df_final):,}행, {len(df_final.columns)}열")

# 4. 결과 저장
print("\n" + "=" * 80)
print("[4단계] 병합된 데이터 저장 중...")
print("=" * 80)

output_file = 'file/merged_data.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n✅ 병합 완료!")
print(f"   저장 위치: {output_file}")
print(f"   총 행 개수: {len(df_final):,}")
print(f"   총 열 개수: {len(df_final.columns)}")
print(f"   파일 크기: {os.path.getsize(output_file) / (1024*1024):.2f} MB")

# 5. 최종 데이터 미리보기
print("\n" + "=" * 80)
print("[5단계] 병합된 데이터 미리보기")
print("=" * 80)
print("\n첫 5행:")
print(df_final.head())

print("\n\n컬럼 목록:")
for i, col in enumerate(df_final.columns, 1):
    null_count = df_final[col].isnull().sum()
    null_pct = (null_count / len(df_final)) * 100
    print(f"   {i:2d}. {col:30s} - 결측치: {null_count:,} ({null_pct:.1f}%)")

print("\n" + "=" * 80)
print("✅ 모든 작업이 완료되었습니다!")
print("=" * 80)

