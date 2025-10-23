# 🚀 Supabase 설정 가이드

이 가이드는 Supabase 클라우드 데이터베이스를 설정하고 CSV 데이터를 업로드하는 방법을 설명합니다.

## 📋 목차
1. [Supabase 프로젝트 생성](#1-supabase-프로젝트-생성)
2. [환경변수 설정](#2-환경변수-설정)
3. [데이터베이스 테이블 생성](#3-데이터베이스-테이블-생성)
4. [CSV 데이터 업로드](#4-csv-데이터-업로드)
5. [챗봇 실행](#5-챗봇-실행)

## 1. Supabase 프로젝트 생성

### 1.1 계정 생성
1. [Supabase 웹사이트](https://supabase.com) 방문
2. "Start your project" 클릭
3. GitHub 계정으로 로그인 (권장)

### 1.2 새 프로젝트 생성
1. "New Project" 클릭
2. 프로젝트 정보 입력:
   - **Name**: `zalcoach-marketing`
   - **Database Password**: 강력한 비밀번호 설정
   - **Region**: `Northeast Asia (Seoul)` 선택 (한국 사용자)
3. "Create new project" 클릭
4. 프로젝트 생성 완료까지 2-3분 대기

### 1.3 API 키 확인
프로젝트 대시보드에서:
1. **Settings** → **API** 메뉴 이동
2. 다음 정보 복사:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public**: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`
   - **service_role**: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`

## 2. 환경변수 설정

### 2.1 .env 파일 생성
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력:

```env
# Supabase 설정
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Google AI 설정
GOOGLE_API_KEY=your_google_api_key_here

# OpenWeather API (선택사항)
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### 2.2 Google API 키 발급
1. [Google AI Studio](https://aistudio.google.com/) 방문
2. "Get API key" 클릭
3. API 키 생성 후 `.env` 파일에 추가

## 3. 데이터베이스 테이블 생성

### 3.1 SQL Editor 접근
1. Supabase 대시보드에서 **SQL Editor** 메뉴 클릭
2. "New query" 버튼 클릭

### 3.2 테이블 생성 SQL 실행
`create_tables.sql` 파일의 내용을 복사하여 SQL Editor에 붙여넣고 실행:

```sql
-- cafe_data 테이블
CREATE TABLE IF NOT EXISTS public.cafe_data (
    id SERIAL PRIMARY KEY,
    franchise_name VARCHAR(70),
    business_type VARCHAR(52),
    -- ... 나머지 컬럼들
);

-- revisit_data 테이블
CREATE TABLE IF NOT EXISTS public.revisit_data (
    -- ... 테이블 정의
);

-- restaurant_data 테이블  
CREATE TABLE IF NOT EXISTS public.restaurant_data (
    -- ... 테이블 정의
);
```

### 3.3 테이블 생성 확인
1. **Table Editor** 메뉴에서 생성된 테이블 확인:
   - `cafe_data` (카페업종 데이터)
   - `revisit_data` (재방문율 데이터)
   - `restaurant_data` (요식업 데이터)

## 4. CSV 데이터 업로드

### 4.1 CSV 파일 준비
다음 파일들이 `file/` 디렉토리에 있는지 확인:
- `Q1_data.csv` (카페업종 데이터)
- `Q2_data.csv` (재방문율 데이터)  
- `Q3_data.csv` (요식업 데이터)

### 4.2 데이터 업로드 실행
터미널에서 다음 명령어 실행:

```bash
# 고속 업로드 (권장)
python upload_fast.py

# 또는 일반 업로드
python upload_to_supabase_fixed.py
```

### 4.3 업로드 진행 상황
```
🚀 CSV → Supabase 업로드 시작
📂 파일 읽는 중...
✅ 원본 데이터: 7,052행 × 13열
🔄 데이터 매핑 중...
✅ 매핑 완료: 7,052행 × 12열
📤 1,000개씩 고속 업로드 시작...
   배치 1/8: 1,000개 완료 | 진행률: 14.2%
   배치 2/8: 1,000개 완료 | 진행률: 28.4%
   ...
✅ cafe_data 업로드 완료!
```

### 4.4 업로드 확인
Supabase 대시보드의 **Table Editor**에서:
1. `cafe_data`: 7,052개 레코드
2. `revisit_data`: 1,960,290개 레코드
3. `restaurant_data`: 86,590개 레코드

## 5. 챗봇 실행

### 5.1 의존성 설치
```bash
pip install -r requirements.txt
```

### 5.2 Streamlit 앱 실행
```bash
streamlit run supabase_chatbot.py
```

### 5.3 브라우저 접속
- **로컬 URL**: http://localhost:8501
- **네트워크 URL**: http://your-ip:8501

## 🔧 문제 해결

### 연결 오류
```
❌ Supabase 연결 실패: Invalid API key
```
**해결방법**: `.env` 파일의 API 키 확인

### 테이블 없음 오류
```
❌ Could not find the table 'cafe_data'
```
**해결방법**: `create_tables.sql` 다시 실행

### 업로드 실패
```
❌ 배치 업로드 실패: JSON serialization error
```
**해결방법**: `upload_fast.py` 사용 (NaN 값 처리 개선)

### 디스크 공간 부족
```
error: file write error: No space left on device
```
**해결방법**: 
1. 불필요한 파일 삭제
2. CSV 파일을 `.gitignore`에 추가
3. Git LFS 사용 고려

## 📊 성능 최적화

### 캐싱 설정
```python
@st.cache_data(ttl=600)  # 10분 캐시
def query_supabase_data(table_name, limit=None):
    # ...
```

### 샘플링 설정
```python
# 대용량 데이터 샘플링
if table_name == "revisit_data":
    df = query_supabase_data(table_name, limit=10000)
elif table_name == "restaurant_data":
    df = query_supabase_data(table_name, limit=8000)
```

### AI 응답 최적화
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    timeout=60,
    max_tokens=4000
)
```

## 🔒 보안 설정

### Row Level Security (RLS)
```sql
-- RLS 활성화
ALTER TABLE public.cafe_data ENABLE ROW LEVEL SECURITY;

-- 읽기 정책
CREATE POLICY "Enable read access for all users" 
ON public.cafe_data FOR SELECT USING (true);

-- 쓰기 정책
CREATE POLICY "Enable insert for authenticated users only" 
ON public.cafe_data FOR INSERT WITH CHECK (true);
```

### 환경변수 보안
- `.env` 파일을 `.gitignore`에 추가
- 프로덕션에서는 환경변수 직접 설정
- Service Role 키는 서버 사이드에서만 사용

## 📞 지원

문제가 발생하면:
1. [Supabase 문서](https://supabase.com/docs) 확인
2. [GitHub Issues](https://github.com/your-repo/issues) 생성
3. 로그 파일 첨부하여 문의

---

**🎉 설정 완료 후 205만개 실제 데이터 기반 AI 마케팅 분석을 시작하세요!**
