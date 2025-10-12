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
    st.session_state.vectorstore = None
    st.session_state.rag_chain = None
    st.session_state.rag_chain_weather = None
    st.session_state.weather_mode = False
    st.session_state.weather_data = None
    st.session_state.weather_info = None
    st.session_state.selected_region = None
    st.session_state.messages = []

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

# CSV 데이터 로드 및 인덱싱 함수
@st.cache_resource
def load_and_index_csv(use_sample=False, sample_ratio=0.1):
    """CSV 파일을 로드하고 벡터 스토어를 생성합니다."""
    csv_file_path = "file/merged_data.csv"
    
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
            raise Exception("지원되는 인코딩으로 CSV 파일을 읽을 수 없습니다.")
        
        st.info(f"✅ 인코딩: {used_encoding}")
        total_docs = len(documents)
        
        if use_sample:
            sample_size = int(total_docs * sample_ratio)
            documents = documents[::int(1/sample_ratio)][:sample_size]
            st.info(f"📊 샘플링 모드: {len(documents):,}개 / {total_docs:,}개 레코드 사용")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ",", " ", ""]
        )
        splits = text_splitter.split_documents(documents)
        
        st.info(f"📝 총 {len(splits):,}개의 청크 생성 중...")
        
        vectorstore = Chroma.from_documents(
            splits,
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        )
        
        return vectorstore, len(documents)
    
    except Exception as e:
        st.error(f"CSV 파일 로드 중 오류 발생: {e}")
        return None, 0

# RAG 체인 생성 함수
def create_rag_chain(vectorstore, include_weather=False, weather_context=""):
    """RAG 체인을 생성합니다."""
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
    
    contextualize_q_system_prompt = """이전 대화 내용과 최신 사용자 질문이 있을 때, 이 질문이 이전 대화 내용과 관련이 있을 수 있습니다. 
이런 경우, 대화 내용을 알 필요 없이 독립적으로 이해할 수 있는 질문으로 바꾸세요. 
질문에 답할 필요는 없고, 필요하다면 그저 다시 구성하거나 그대로 두세요."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    history_aware_retriever = create_history_aware_retriever(
        chat, retriever, contextualize_q_prompt
    )
    
    # 날씨 포함 여부에 따라 시스템 프롬프트 변경
    if include_weather:
        qa_system_prompt = f"""당신은 날씨 기반 상업 시설 마케팅 전문가입니다.

{weather_context}

위 날씨 정보와 아래 데이터를 함께 고려하여 답변하세요.

**📢 실시간 날씨 데이터 확인 필수**:
- 위 날씨 정보는 OpenWeatherMap API에서 방금 조회한 **실제 실시간 기상 데이터**입니다
- 이것은 가상, 시뮬레이션, 예시, 가정의 데이터가 **절대 아닙니다**
- 현재 시점의 **실제 날씨 상황**을 정확히 반영한 데이터입니다
- 답변에서 "가상", "시뮬레이션", "예시"라는 표현을 **절대 사용하지 마세요**
- 이 실시간 날씨를 기반으로 **현실적인 마케팅 전략**을 제시하세요

**⚠️ 중요 지시사항**:
- 답변을 끝까지 완전히 작성하세요
- 절대 중간에 끊지 마세요
- 모든 섹션을 빠짐없이 작성하세요
- 답변 마지막에 자연스러운 마무리 문장을 추가하세요

데이터 컬럼 설명:
- ENCODED_MCT: 상점 ID (암호화)
- TA_YM: 기준 년월
- MCT_OPE_MS_CN: 운영 개월 수
- RC_M1_SAA: 최근 1개월 매출액
- MCT_BSE_AR: 상점 주소
- MCT_NM: 상점명
- HPSN_MCT_ZCD_NM: 업종 대분류
- HPSN_MCT_BZN_CD_NM: 업종 소분류
- M12_MAL_XX_RAT: 12개월 남성 연령대별 비율
- M12_FME_XX_RAT: 12개월 여성 연령대별 비율
- DLV_SAA_RAT: 배달 매출 비율
- MCT_UE_CLN_REU_RAT: 재방문 고객 비율
- MCT_UE_CLN_NEW_RAT: 신규 고객 비율

답변 형식 (모든 섹션 필수):

## 1. 🌤️ 날씨 고려사항
현재 날씨가 고객 행동에 미치는 영향을 분석하세요.

## 2. 📊 데이터 근거
구체적인 수치와 데이터를 제시하세요.

## 3. 💡 실행 가능한 마케팅 전략
### 전략 1: [전략명]
- 실행 방법:
- 예상 효과:

### 전략 2: [전략명]
- 실행 방법:
- 예상 효과:

### 전략 3: [전략명]
- 실행 방법:
- 예상 효과:

## 4. 마무리
핵심 내용을 요약하고 마무리하세요.

{{context}}"""
    else:
        qa_system_prompt = """당신은 상업 시설 데이터 분석 전문가입니다. 
주어진 데이터를 바탕으로 상점의 매출, 고객 특성, 운영 현황 등에 대해 분석하고 답변하세요.

**⚠️ 중요 지시사항**:
- 답변을 끝까지 완전히 작성하세요
- 절대 중간에 끊지 마세요
- 모든 섹션을 빠짐없이 작성하세요
- 답변 마지막에 자연스러운 마무리 문장을 추가하세요

데이터 컬럼 설명:
- ENCODED_MCT: 상점 ID (암호화)
- TA_YM: 기준 년월
- MCT_OPE_MS_CN: 운영 개월 수
- RC_M1_SAA: 최근 1개월 매출액
- MCT_BSE_AR: 상점 주소
- MCT_NM: 상점명
- HPSN_MCT_ZCD_NM: 업종 대분류
- HPSN_MCT_BZN_CD_NM: 업종 소분류
- M12_MAL_XX_RAT: 12개월 남성 연령대별 비율
- M12_FME_XX_RAT: 12개월 여성 연령대별 비율
- DLV_SAA_RAT: 배달 매출 비율
- MCT_UE_CLN_REU_RAT: 재방문 고객 비율
- MCT_UE_CLN_NEW_RAT: 신규 고객 비율

답변 형식 (모든 섹션 필수):

## 1. 📍 핵심 답변
명확하고 간결하게 핵심을 설명하세요.

## 2. 📊 데이터 근거
구체적인 수치와 데이터를 제시하세요.

## 3. 💡 인사이트
추가 해석과 시사점을 제공하세요.

## 4. 마무리
핵심 내용을 요약하고 마무리하세요.

{context}"""
    
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
    
    if st.button("🔄 데이터 로드", type="primary", use_container_width=True):
        with st.spinner("데이터 인덱싱 중... ☕"):
            vectorstore, doc_count = load_and_index_csv(use_sample=use_sample, sample_ratio=0.1)
            if vectorstore:
                st.session_state.vectorstore = vectorstore
                st.session_state.rag_chain = create_rag_chain(vectorstore, include_weather=False)
                st.success(f"✅ 완료! ({doc_count:,}개)")
                st.balloons()
    
    st.markdown("---")
    
    st.markdown("""
    ### 💡 사용 방법
    1. **데이터 로드** 클릭 (1회만)
    2. 질문 입력
    3. 날씨 고려 필요 시 "날씨 확인" 클릭
    
    ### 📝 질문 예시
    **일반 분석:**
    - "서울 성동구 중식당 매출은?"
    - "재방문율이 높은 업종은?"
    
    **날씨 기반:**
    - "이 날씨에 잘 팔릴 메뉴는?"
    - "현재 기온에 맞는 프로모션은?"
    """)

# 메인 컨텐츠
st.title("🏪 상업 시설 데이터 분석")

# 데이터 로드 체크
if st.session_state.rag_chain is None:
    st.warning("⚠️ 먼저 사이드바에서 **'데이터 로드'** 버튼을 클릭해주세요!")
    st.stop()

# 날씨 옵션 (상단)
st.markdown("### 🌤️ 날씨 기반 분석 (선택사항)")

col1, col2, col3 = st.columns([3, 2, 1])

with col1:
    regions = load_regions()
    if regions:
        selected_region = st.selectbox(
            "분석 지역",
            options=regions,
            index=0,
            label_visibility="collapsed"
        )

with col2:
    # API 키 자동 로드
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    if not weather_api_key:
        st.warning("⚠️ .env에 OPENWEATHER_API_KEY 필요")
    
    # 날씨 확인 버튼
    if st.button("🌤️ 날씨 확인", disabled=not weather_api_key, use_container_width=True):
        with st.spinner("날씨 조회 중..."):
            weather_data = get_weather(selected_region, weather_api_key)
            if weather_data:
                weather_info = format_weather_info(weather_data)
                if weather_info:
                    st.session_state.weather_mode = True
                    st.session_state.weather_info = weather_info
                    st.session_state.selected_region = selected_region
                    
                    # 날씨 기반 RAG 체인 생성
                    if st.session_state.vectorstore:
                        weather_context = format_weather_context(weather_info)
                        st.session_state.rag_chain_weather = create_rag_chain(
                            st.session_state.vectorstore,
                            include_weather=True,
                            weather_context=weather_context
                        )
                    st.success("✅ 날씨 모드 ON")
                    st.rerun()

with col3:
    if st.session_state.weather_mode:
        if st.button("❌ 끄기", use_container_width=True):
            st.session_state.weather_mode = False
            st.session_state.weather_info = None
            st.rerun()

# 현재 모드 표시
if st.session_state.weather_mode and st.session_state.weather_info:
    weather_info = st.session_state.weather_info
    st.success(
        f"🌤️ **날씨 기반 분석 모드 ON** | "
        f"{st.session_state.selected_region} - {weather_info['날씨']} {weather_info['온도']} "
        f"(습도: {weather_info['습도']}, 풍속: {weather_info['풍속']})"
    )
else:
    st.info("📊 **일반 데이터 분석 모드** | 날씨 정보 없이 순수 데이터 기반 분석")

st.markdown("---")

# 채팅 영역
st.markdown("### 💬 질문하기")

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력
MAX_MESSAGES = 12

if prompt := st.chat_input("데이터에 대해 질문하세요..."):
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
            # 날씨 모드일 때 실시간 날씨 자동 갱신
            if st.session_state.weather_mode:
                weather_api_key = os.getenv("OPENWEATHER_API_KEY")
                if weather_api_key and st.session_state.selected_region:
                    # 매 질문마다 최신 날씨 조회
                    with st.spinner("🌤️ 실시간 날씨 조회 중..."):
                        weather_data = get_weather(st.session_state.selected_region, weather_api_key)
                        if weather_data:
                            weather_info = format_weather_info(weather_data)
                            if weather_info:
                                # 최신 날씨로 업데이트
                                st.session_state.weather_info = weather_info
                                
                                # 날씨 체인 재생성 (최신 날씨 반영)
                                if st.session_state.vectorstore:
                                    weather_context = format_weather_context(weather_info)
                                    st.session_state.rag_chain_weather = create_rag_chain(
                                        st.session_state.vectorstore,
                                        include_weather=True,
                                        weather_context=weather_context
                                    )
                                    
                                # 현재 날씨 정보 표시
                                st.info(f"🌤️ 실시간 날씨 반영: {weather_info['날씨']} {weather_info['온도']}")
                
                chain = st.session_state.rag_chain_weather
            else:
                chain = st.session_state.rag_chain
            
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
st.caption("💡 Tip: 대화 내용이 많아지면 자동으로 오래된 메시지가 삭제됩니다.")
