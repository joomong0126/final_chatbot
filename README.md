# 🏪 Supabase 기반 마케팅 분석 챗봇

실시간 클라우드 데이터베이스를 활용한 AI 마케팅 전략 분석 시스템

> **205만개 실제 데이터**를 기반으로 카페, 재방문율, 요식업 전문 분석 및 마케팅 전략을 제안합니다.

## ✨ 주요 기능

### 🔥 **핵심 특징**
- 📊 **205만개 실제 데이터** 기반 분석
- ☁️ **Supabase 클라우드 DB** 실시간 연동
- 🤖 **Google Gemini 2.5 Flash** AI 모델
- 🎯 **3개 전문 분야** 맞춤 분석

### 📈 **데이터셋**
| 분야 | 레코드 수 | 컬럼 수 | 설명 |
|------|-----------|---------|------|
| 🍵 **카페업종** | 7,052개 | 15개 | 고객 특성, 충성도, 상권 분석 |
| 🔄 **재방문율** | 1,960,290개 | 47개 | 고객 행동, 재방문 패턴 분석 |
| 🍽️ **요식업** | 86,590개 | 75개 | 매출, 성과, 경쟁력 분석 |

### 🎯 **AI 분석 기능**
- **데이터 기반 현황 분석**: 구체적 수치와 패턴 제시
- **핵심 인사이트 도출**: 주요 발견사항과 특징 분석  
- **맞춤형 마케팅 전략**: 실행 가능한 구체적 전략 제안
- **단계별 실행 방안**: 체계적인 실행 계획 수립
- **종합 결론 및 요약**: 핵심 포인트 정리

## 🚀 실행 방법

### **1. 환경 설정**
```bash
# 저장소 클론
git clone https://github.com/your-username/zalcoach.git
cd zalcoach

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 패키지 설치
pip install -r requirements.txt
```

### **2. 환경변수 설정**
`.env` 파일을 생성하고 다음 내용을 입력하세요:
```env
# Supabase 설정
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# AI 모델 설정
GOOGLE_API_KEY=your_google_api_key

# 기타 (선택사항)
OPENWEATHER_API_KEY=your_openweather_api_key
```

### **3. 데이터베이스 설정**
```bash
# 1. Supabase에서 테이블 생성
# create_tables.sql 파일의 내용을 Supabase SQL Editor에서 실행

# 2. 데이터 업로드 (CSV 파일이 있는 경우)
python upload_fast.py
```

### **4. 챗봇 실행**
```bash
streamlit run supabase_chatbot.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📁 프로젝트 구조

```
zalcoach/
├── 📱 supabase_chatbot.py      # 메인 Streamlit 챗봇 애플리케이션
├── 📊 upload_fast.py           # 고속 데이터 업로드 스크립트
├── 🗃️ create_tables.py         # 테이블 스키마 생성 스크립트
├── 📋 create_tables.sql        # SQL DDL 파일
├── 📖 SUPABASE_SETUP_GUIDE.md  # Supabase 설정 가이드
├── 📦 requirements.txt         # Python 패키지 의존성
├── 🔧 .env                     # 환경변수 (생성 필요)
├── 📚 README.md               # 프로젝트 문서
└── 📂 file/                   # 데이터 파일 (CSV)
    ├── Q1_data.csv            # 카페업종 데이터
    ├── Q2_data.csv            # 재방문율 데이터
    └── Q3_data.csv            # 요식업 데이터
```

## 🛠️ 기술 스택

### **Backend & Database**
- **Supabase**: PostgreSQL 기반 클라우드 데이터베이스
- **Python**: 데이터 처리 및 API 연동
- **Pandas**: 데이터 분석 및 조작

### **AI & ML**
- **Google Gemini 2.5 Flash**: 대화형 AI 모델
- **LangChain**: AI 체인 및 프롬프트 관리
- **Streamlit**: 웹 애플리케이션 프레임워크

### **Data Processing**
- **CSV Processing**: 대용량 데이터 처리
- **Real-time Querying**: 실시간 데이터 조회
- **Batch Processing**: 배치 데이터 업로드

## 📊 사용 예시

### **카페업종 분석**
```
질문: "성동구 카페들의 여성 고객 집중 현상을 분석해주세요"

AI 응답:
📊 데이터 분석
- 성동구 카페 중 85%가 여성 60대 이상 고객 비중 100%
- 충성도지수 평균 87.3점으로 업계 평균 대비 23% 높음

🎯 핵심 인사이트
- 지역 특성상 주거 밀집지역의 시니어 여성층 집중
- 높은 충성도로 안정적 매출 기반 확보

💡 마케팅 전략
- 시니어 친화적 메뉴 및 서비스 강화
- 건강 관련 음료 및 디저트 라인업 확대
...
```

## 🔧 고급 설정

### **성능 최적화**
- **캐싱**: 10분 데이터 캐시로 응답 속도 향상
- **샘플링**: 대용량 데이터 지능형 샘플링
- **배치 처리**: 1,000개 단위 배치 업로드

### **보안 설정**
- **환경변수**: 민감 정보 .env 파일 관리
- **RLS**: Supabase Row Level Security 적용
- **API 키**: 서비스 롤 키 사용

## 📈 성능 지표

- **응답 시간**: 평균 8-15초 (대용량 데이터 기준)
- **데이터 처리**: 최대 196만개 레코드 실시간 분석
- **정확도**: 실제 데이터 기반 구체적 수치 제공
- **완성도**: 5단계 구조화된 완전한 답변

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.

---

**Made with ❤️ using Supabase, Google Gemini, and Streamlit**