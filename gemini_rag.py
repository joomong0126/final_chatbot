import time
import os
import uuid
import warnings
from typing import Dict, List, Any, Optional
from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd
import requests
from datetime import datetime

# Deprecation 경고 무시
warnings.filterwarnings('ignore', category=DeprecationWarning)
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import streamlit as st

# 환경변수 로드 (인코딩 문제 처리)
try:
    load_dotenv(encoding='utf-8')
except:
    try:
        load_dotenv(encoding='utf-8-sig')
    except:
        try:
            load_dotenv(encoding='cp949')
        except:
            pass  # .env 없이도 계속 진행

# 페이지 설정
st.set_page_config(page_title="상업 시설 데이터 분석", page_icon="🏪", layout="wide")

# 세션 상태 초기화
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.vectorstore_q1 = None
    st.session_state.vectorstore_q2 = None
    st.session_state.vectorstore_q3 = None
    st.session_state.rag_chain_q1 = None
    st.session_state.rag_chain_q2 = None
    st.session_state.rag_chain_q3 = None
    st.session_state.weather_mode = False
    st.session_state.weather_data = None
    st.session_state.weather_info = None
    st.session_state.selected_region = None
    st.session_state.messages = []
    st.session_state.current_mode = "통합분석"

# CSV에서 지역 목록 읽기
@st.cache_data
def load_regions():
    """CSV에서 고유한 지역 목록을 추출합니다."""
    try:
        df = None
        for encoding in ['utf-8-sig', 'cp949', 'euc-kr', 'latin-1', 'utf-8']:
            try:
                df = pd.read_csv('file/merged_data.csv', encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            return []
        
        regions = df['MCT_SIGUNGU_NM'].dropna().unique().tolist()
        regions = sorted([r for r in regions if isinstance(r, str) and r.strip()])
        return regions
    except Exception as e:
        st.error(f"지역 목록 로드 오류: {e}")
        return []

# OpenWeatherMap API로 날씨 조회
def get_weather(city_name, api_key):
    """OpenWeatherMap API를 사용하여 날씨 정보를 가져옵니다."""
    city_mapping = {
        "서울": "Seoul", "부산": "Busan", "인천": "Incheon", 
        "대구": "Daegu", "대전": "Daejeon", "광주": "Gwangju",
        "울산": "Ulsan", "세종": "Sejong", "수원": "Suwon",
        "성남": "Seongnam", "고양": "Goyang", "용인": "Yongin",
    }
    
    city_key = city_name.split()[0] if ' ' in city_name else city_name
    english_city = city_mapping.get(city_key, "Seoul")
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{english_city},KR",
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"날씨 API 호출 오류: {e}")
        return None

# 날씨 정보 포맷팅
def format_weather_info(weather_data):
    """날씨 데이터를 읽기 쉽게 포맷팅합니다."""
    if not weather_data:
        return None
    
    try:
        main = weather_data['main']
        weather = weather_data['weather'][0]
        wind = weather_data['wind']
        
        info = {
            "도시": weather_data['name'],
            "날씨": weather['description'],
            "온도": f"{main['temp']:.1f}°C",
            "체감온도": f"{main['feels_like']:.1f}°C",
            "습도": f"{main['humidity']}%",
            "풍속": f"{wind['speed']} m/s",
        }
        return info
    except Exception as e:
        return None

def format_weather_context(weather_info):
    """날씨 정보를 프롬프트용 텍스트로 변환"""
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return f"""
🌤️ **실시간 날씨 정보** (OpenWeatherMap API 실제 데이터)

📍 **중요**: 아래는 OpenWeatherMap API에서 {current_time}에 조회한 **실제 실시간 날씨 데이터**입니다.
이것은 가상이나 시뮬레이션이 아닌, 현재 시점의 **실제 기상 정보**입니다.

📊 **실시간 기상 데이터**:
- 관측 지역: {weather_info['도시']}
- 현재 날씨: {weather_info['날씨']}
- 실제 온도: {weather_info['온도']} (체감온도: {weather_info['체감온도']})
- 현재 습도: {weather_info['습도']}
- 현재 풍속: {weather_info['풍속']}

⚠️ **답변 시 필수 사항**: 
- 이 실시간 날씨를 "가상" 또는 "시뮬레이션" 데이터라고 절대 언급하지 마세요
- OpenWeatherMap에서 방금 조회한 **실제 현재 날씨**임을 인지하고 답변하세요
- 이 실시간 날씨 정보를 바탕으로 현실적이고 실행 가능한 마케팅 전략을 제시하세요
"""

# CSV 데이터 로드 및 인덱싱 함수 (개별 파일용)
@st.cache_resource
def load_and_index_csv_individual(file_path, file_name, use_sample=False, sample_ratio=0.1):
    """개별 CSV 파일을 로드하고 벡터 스토어를 생성합니다."""
    csv_file_path = file_path
    
    try:
        documents = None
        used_encoding = None
        
        for encoding in ['utf-8-sig', 'cp949', 'euc-kr', 'latin-1', 'utf-8']:
            try:
                loader = CSVLoader(
                    file_path=csv_file_path,
                    encoding=encoding,
                    csv_args={'delimiter': ',',}
                )
                documents = loader.load()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if documents is None:
            raise Exception(f"{file_name}: 지원되는 인코딩으로 CSV 파일을 읽을 수 없습니다.")
        
        st.info(f"✅ {file_name} 인코딩: {used_encoding}")
        total_docs = len(documents)
        
        if use_sample:
            sample_size = int(total_docs * sample_ratio)
            documents = documents[::int(1/sample_ratio)][:sample_size]
            st.info(f"📊 {file_name} 샘플링: {len(documents):,}개 / {total_docs:,}개 레코드 사용")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ",", " ", ""]
        )
        splits = text_splitter.split_documents(documents)
        
        vectorstore = Chroma.from_documents(
            splits,
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        )
        
        return vectorstore, len(documents)
    
    except Exception as e:
        st.error(f"{file_name} 파일 로드 중 오류 발생: {e}")
        return None, 0

# 질문 분류 함수
def classify_question(question):
    """질문을 분석하여 어떤 데이터셋을 사용할지 결정합니다."""
    question_lower = question.lower()
    
    # 카페 관련 키워드
    cafe_keywords = ['카페', '커피', '음료', '디저트', '원두', '라떼', '아메리카노']
    
    # 재방문율 관련 키워드
    revisit_keywords = ['재방문', '재방문율', '충성도', '단골', '리텐션', '이탈', '재구매']
    
    # 요식업 관련 키워드
    restaurant_keywords = ['요식업', '식당', '음식점', '한식', '중식', '일식', '양식', '배달', '매출']
    
    # 키워드 매칭
    if any(keyword in question_lower for keyword in cafe_keywords):
        return "Q1", "카페업종"
    elif any(keyword in question_lower for keyword in revisit_keywords):
        return "Q2", "재방문율"
    elif any(keyword in question_lower for keyword in restaurant_keywords):
        return "Q3", "요식업"
    else:
        return "통합", "통합분석"

# 전문화된 RAG 체인 생성 함수
def create_specialized_rag_chain(vectorstore, analysis_type):
    """특화된 RAG 체인을 생성합니다."""
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    
    api_key = os.getenv("GOOGLE_API_KEY")
    chat = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        max_output_tokens=8192,  # 완전한 응답을 위해 최대로 증가
        api_key=api_key
    )
    
    # 분석 유형별 시스템 프롬프트
    if analysis_type == "카페업종":
        system_prompt = """당신은 카페업종 전문 마케팅 컨설턴트입니다.

Q1_data.csv 데이터를 기반으로 카페 관련 질문에 답변하세요.

**데이터 컬럼 설명**:
- 가맹점명: 카페 이름
- 업종: 카페
- 가맹점지역: 위치 정보
- 상권: 상권 유형
- 남성비중/여성비중: 고객 성별 분포
- 연령집중도: 특정 연령대 집중 정도
- 주요고객층: 주력 고객 연령대
- 충성도지수: 고객 충성도 수치
- 상권유형: 거주상권/직장상권/유동인구상권
- 고객유형: 충성형/신규형

**답변 형식**:
## 1. 📊 카페 데이터 분석
구체적인 수치와 데이터를 제시하세요.

## 2. 🎯 타겟 고객 특성
주요 고객층과 특성을 분석하세요.

## 3. 💡 마케팅 전략 제안
### 전략 1: [전략명]
- 실행 방법:
- 예상 효과:
- 데이터 근거:

### 전략 2: [전략명]
- 실행 방법:
- 예상 효과:
- 데이터 근거:

## 4. 📈 성과 예측
예상되는 개선 효과를 제시하세요.

{context}"""

    elif analysis_type == "재방문율":
        system_prompt = """당신은 고객 재방문율 개선 전문 컨설턴트입니다.

Q2_data.csv 데이터를 기반으로 재방문율 관련 질문에 답변하세요.

**데이터 컬럼 설명**:
- 재방문고객비율: 재방문 고객 비율
- 신규고객비율: 신규 고객 비율
- 월간매출액: 월 매출 수준
- 월간이용건수/고객수: 이용 빈도
- 업종평균재방문률: 업종 평균 대비 비교
- 재방문률등급: 재방문율 등급 (High/Mid/Low)
- 충성도 관련 지표들

**답변 형식**:
## 1. 🔍 재방문율 현황 분석
현재 재방문율과 문제점을 진단하세요.

## 2. 📊 업종 평균 대비 분석
업종 평균과 비교한 상대적 위치를 분석하세요.

## 3. 💡 재방문율 개선 전략
### 전략 1: [전략명]
- 실행 방법:
- 예상 효과:
- 데이터 근거:

### 전략 2: [전략명]
- 실행 방법:
- 예상 효과:
- 데이터 근거:

## 4. 🎯 단계별 실행 계획
구체적인 실행 로드맵을 제시하세요.

{context}"""

    elif analysis_type == "요식업":
        system_prompt = """당신은 요식업 전문 마케팅 컨설턴트입니다.

Q3_data.csv 데이터를 기반으로 요식업 관련 질문에 답변하세요.

**데이터 컬럼 설명**:
- 업종: 한식, 중식, 일식, 양식 등
- 월간매출액: 매출 수준
- 배달매출비율: 배달 의존도
- 월평균객단가: 평균 객단가
- 연령대별 고객 비율
- 거주/직장/유동인구 이용 비율
- 동종업종 대비 성과 지표

**답변 형식**:
## 1. 🍽️ 요식업 현황 분석
매출, 고객층, 운영 현황을 분석하세요.

## 2. 📊 경쟁력 분석
동종업종 대비 강점과 약점을 분석하세요.

## 3. 💡 매출 증대 전략
### 전략 1: [전략명]
- 실행 방법:
- 예상 효과:
- 데이터 근거:

### 전략 2: [전략명]
- 실행 방법:
- 예상 효과:
- 데이터 근거:

## 4. 🚀 성장 방안
장기적인 성장 전략을 제시하세요.

{context}"""

    else:  # 통합분석
        system_prompt = """당신은 종합 마케팅 전략 컨설턴트입니다.

세 개의 데이터셋(Q1: 카페, Q2: 재방문율, Q3: 요식업)을 종합적으로 분석하여 답변하세요.

**답변 형식**:
## 1. 📊 종합 데이터 분석
관련 데이터를 종합적으로 분석하세요.

## 2. 💡 통합 마케팅 전략
여러 관점에서의 종합적인 전략을 제시하세요.

## 3. 🎯 실행 우선순위
중요도에 따른 실행 순서를 제안하세요.

{context}"""

    contextualize_q_system_prompt = """이전 대화 내용과 최신 사용자 질문이 있을 때, 이 질문이 이전 대화 내용과 관련이 있을 수 있습니다. 
이런 경우, 대화 내용을 알 필요 없이 독립적으로 이해할 수 있는 질문으로 바꾸세요."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    history_aware_retriever = create_history_aware_retriever(
        chat, retriever, contextualize_q_prompt
    )
    
    # 전문화된 시스템 프롬프트 사용 (이미 위에서 정의됨)
    qa_system_prompt = system_prompt
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain

# 사이드바 (간소화)
with st.sidebar:
    st.header("⚙️ 설정")
    
    st.markdown("### 📊 데이터 로딩")
    use_sample = st.checkbox(
        "빠른 테스트 모드 (10% 샘플링)", 
        value=True,
        help="첫 실행 시 권장 (4-6분)"
    )
    
    if use_sample:
        st.info("⚡ 빠른 모드: 4-6분 소요")
    else:
        st.warning("⏳ 전체 모드: 55-80분 소요")
    
    if st.button("🔄 전체 데이터 로드", type="primary", use_container_width=True):
        with st.spinner("데이터 인덱싱 중... ☕"):
            # Q1 데이터 로드 (카페)
            vectorstore_q1, doc_count_q1 = load_and_index_csv_individual(
                "file/Q1_data.csv", "Q1_data(카페)", use_sample, 0.1
            )
            if vectorstore_q1:
                st.session_state.vectorstore_q1 = vectorstore_q1
                st.session_state.rag_chain_q1 = create_specialized_rag_chain(vectorstore_q1, "카페업종")
            
            # Q2 데이터 로드 (재방문율)
            vectorstore_q2, doc_count_q2 = load_and_index_csv_individual(
                "file/Q2_data.csv", "Q2_data(재방문율)", use_sample, 0.1
            )
            if vectorstore_q2:
                st.session_state.vectorstore_q2 = vectorstore_q2
                st.session_state.rag_chain_q2 = create_specialized_rag_chain(vectorstore_q2, "재방문율")
            
            # Q3 데이터 로드 (요식업)
            vectorstore_q3, doc_count_q3 = load_and_index_csv_individual(
                "file/Q3_data.csv", "Q3_data(요식업)", use_sample, 0.1
            )
            if vectorstore_q3:
                st.session_state.vectorstore_q3 = vectorstore_q3
                st.session_state.rag_chain_q3 = create_specialized_rag_chain(vectorstore_q3, "요식업")
            
            if all([vectorstore_q1, vectorstore_q2, vectorstore_q3]):
                st.success(f"✅ 전체 로딩 완료!")
                st.success(f"Q1: {doc_count_q1:,}개 | Q2: {doc_count_q2:,}개 | Q3: {doc_count_q3:,}개")
                st.balloons()
    
    st.markdown("---")
    
    # 분석 모드 선택
    st.markdown("### 🎯 분석 모드")
    analysis_mode = st.selectbox(
        "분석 유형 선택",
        ["자동 감지", "카페업종", "재방문율", "요식업", "통합분석"],
        help="질문에 따라 자동으로 감지하거나 수동으로 선택"
    )
    
    st.markdown("""
    ### 💡 질문 예시
    
    **🍵 카페업종:**
    - "성수동 카페들의 고객 특성은?"
    - "충성도가 높은 카페의 공통점은?"
    - "여성 고객이 많은 카페 마케팅 전략은?"
    
    **🔄 재방문율:**
    - "재방문율이 낮은 매장 개선 방안은?"
    - "고객 충성도를 높이는 방법은?"
    - "단골 고객 확보 전략은?"
    
    **🍽️ 요식업:**
    - "배달 매출 비중이 높은 업종은?"
    - "객단가 개선 방안은?"
    - "한식당 경쟁력 강화 방법은?"
    """)

# 메인 컨텐츠
st.title("🏪 마케팅 전략 분석 챗봇")
st.markdown("### 📊 카페 · 재방문율 · 요식업 전문 분석")

# 데이터 로드 체크
if not all([st.session_state.rag_chain_q1, st.session_state.rag_chain_q2, st.session_state.rag_chain_q3]):
    st.warning("⚠️ 먼저 사이드바에서 **'전체 데이터 로드'** 버튼을 클릭해주세요!")
    st.stop()


# 현재 모드 표시
st.info(f"🎯 **현재 분석 모드**: {st.session_state.current_mode}")

st.markdown("---")

# 채팅 영역
st.markdown("### 💬 질문하기")

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력
MAX_MESSAGES = 12

if prompt := st.chat_input("마케팅 전략에 대해 질문하세요..."):
    # 메시지 제한
    if len(st.session_state.messages) >= MAX_MESSAGES:
        del st.session_state.messages[0]
        del st.session_state.messages[0]
    
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 응답
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 질문 분류 (자동 감지 모드일 때)
            if analysis_mode == "자동 감지":
                dataset_type, analysis_type = classify_question(prompt)
                st.session_state.current_mode = analysis_type
            else:
                analysis_type = analysis_mode
                if analysis_type == "카페업종":
                    dataset_type = "Q1"
                elif analysis_type == "재방문율":
                    dataset_type = "Q2"
                elif analysis_type == "요식업":
                    dataset_type = "Q3"
                else:
                    dataset_type = "통합"
            
            # 해당하는 RAG 체인 선택
            if dataset_type == "Q1":
                chain = st.session_state.rag_chain_q1
                st.info(f"🍵 **카페업종 데이터**로 분석 중...")
            elif dataset_type == "Q2":
                chain = st.session_state.rag_chain_q2
                st.info(f"🔄 **재방문율 데이터**로 분석 중...")
            elif dataset_type == "Q3":
                chain = st.session_state.rag_chain_q3
                st.info(f"🍽️ **요식업 데이터**로 분석 중...")
            else:
                # 통합 분석 - 가장 관련성 높은 체인 사용
                chain = st.session_state.rag_chain_q1  # 기본값
                st.info(f"📊 **통합 분석** 중...")
            
            # RAG 실행
            result = chain.invoke({
                "input": prompt,
                "chat_history": st.session_state.messages
            })
            
            # 응답 텍스트 추출
            answer_text = result.get("answer", "")
            
            # 응답 완전성 검증
            is_complete = (
                len(answer_text) > 100 and  # 최소 길이 체크
                (answer_text.endswith(('.', '!', '?', '다', '요', '니다', '습니다', '세요')) or
                 "마무리" in answer_text or
                 "요약" in answer_text)
            )
            
            if not is_complete and len(answer_text) > 50:
                st.warning("⚠️ 응답이 불완전할 수 있습니다. 더 구체적으로 질문하거나 다시 시도해주세요.")
            
            # 참고 데이터 표시
            with st.expander("📚 참고 데이터"):
                for i, doc in enumerate(result["context"], 1):
                    st.markdown(f"**데이터 {i}:**")
                    st.text(doc.page_content[:400])
                    st.markdown("---")
            
            # 타이핑 효과로 응답 표시
            for chunk in answer_text.split(" "):
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 메시지 저장
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
        
        except Exception as e:
            error_message = f"❌ 오류가 발생했습니다: {str(e)}"
            st.error(error_message)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_message}
            )

# 푸터
st.markdown("---")
st.caption("💡 Tip: 질문 유형에 따라 자동으로 적절한 데이터셋을 선택하여 분석합니다.")
