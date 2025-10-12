# 🏪 상업 시설 데이터 분석 & 날씨 마케팅

RAG 기반 상업 시설 데이터 분석 및 실시간 날씨 기반 마케팅 전략 제공 챗봇

## ✨ 주요 기능

### 1. 📊 RAG 기반 데이터 분석
- 86,903개 상업 시설 데이터 분석
- 매출, 고객 정보, 업종 분석
- 대화형 AI 챗봇

### 2. 🌤️ 실시간 날씨 기반 마케팅
- OpenWeatherMap API 실시간 날씨 조회
- 날씨 기반 맞춤 마케팅 전략 제안
- 원클릭 날씨 모드 전환

### 3. 🤖 고급 RAG 기술
- History-Aware Retriever
- Query Rewriting
- Multi-Chain Architecture
- External Context Injection
- 샘플링 모드 (빠른 테스트)

## 🛠️ 기술 스택

- **AI 모델**: Google Gemini 2.5 Flash
- **프레임워크**: Streamlit
- **RAG**: LangChain
- **벡터 DB**: Chroma
- **임베딩**: HuggingFace Sentence Transformers
- **날씨 API**: OpenWeatherMap

## 🚀 로컬 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/zalcoach.git
cd zalcoach
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일 생성:
```
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

### 5. 실행
```bash
streamlit run gemini_rag.py
```

## 📝 사용 방법

1. **데이터 로드**: 사이드바에서 "데이터 로드" 클릭 (빠른 모드 권장)
2. **일반 분석**: 질문 입력
3. **날씨 기반 분석**: 
   - 지역 선택
   - "날씨 확인" 클릭
   - 날씨 기반 질문 입력

## 🎯 질문 예시

**일반 데이터 분석:**
- "서울 성동구 중식당 매출은?"
- "재방문율이 높은 업종은?"
- "배달 매출 비율이 높은 지역은?"

**날씨 기반 마케팅:**
- "이 날씨에 잘 팔릴 메뉴는?"
- "현재 기온에 맞는 프로모션은?"
- "비 오는 날 추천할 전략은?"

## 📊 데이터 출처

- 상업 시설 운영 데이터 (86,903개 레코드)
- 매출, 고객, 업종 정보 포함
- 2023-2024년 데이터

## 🔐 보안

- API 키는 `.env` 파일 또는 Streamlit Secrets로 관리
- `.gitignore`로 민감 정보 보호
- 환경변수를 통한 안전한 키 관리

## 📄 라이선스

MIT License

## 👤 제작자

Zalcoach - 2025

## 🙏 감사 인사

- LangChain
- Google Gemini
- OpenWeatherMap
- Streamlit

