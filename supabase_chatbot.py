import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Supabase 기반 마케팅 분석 챗봇",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase 클라이언트 초기화
@st.cache_resource
def init_supabase():
    """Supabase 클라이언트 초기화"""
    try:
        # 환경변수 또는 하드코딩된 값 사용
        url = os.getenv("SUPABASE_URL") or "https://kqzdrorzgsmqavxdaeos.supabase.co"
        key = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtxemRyb3J6Z3NtcWF2eGRhZW9zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1NjU4MDMsImV4cCI6MjA3NjE0MTgwM30.3Rbz6Yp7KLzybtIe93yy37LVfxRObx4XuPHavqqz468"
        
        if not url or not key:
            st.error("❌ Supabase 설정을 확인하세요.")
            return None
        
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Supabase 연결 실패: {e}")
        return None

# 데이터 조회 함수
@st.cache_data(ttl=600)  # 10분 캐시로 연장
def query_supabase_data(table_name, filters=None, limit=None):
    """Supabase에서 데이터 조회"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()
    
    try:
        query = supabase.table(table_name).select("*")
        
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        
        # limit이 None이면 전체 데이터 조회, 있으면 제한
        if limit:
            result = query.limit(limit).execute()
        else:
            result = query.execute()
            
        return pd.DataFrame(result.data)
    
    except Exception as e:
        st.error(f"❌ 데이터 조회 실패 ({table_name}): {e}")
        return pd.DataFrame()

# 질문 분류 및 데이터 조회
def get_relevant_data(question):
    """질문에 따라 관련 데이터 조회"""
    question_lower = question.lower()
    
    # 키워드 기반 테이블 선택
    if any(keyword in question_lower for keyword in ['카페', '커피', '음료', '디저트', '원두', '라떼', '아메리카노']):
        table_name = "cafe_data"
        data_type = "카페업종"
    elif any(keyword in question_lower for keyword in ['재방문', '재방문율', '충성도', '단골', '리텐션', '이탈', '재구매']):
        table_name = "revisit_data"
        data_type = "재방문율"
    elif any(keyword in question_lower for keyword in ['요식업', '식당', '음식점', '한식', '중식', '일식', '양식', '배달', '매출']):
        table_name = "restaurant_data"
        data_type = "요식업"
    else:
        # 기본값으로 카페 데이터 사용
        table_name = "cafe_data"
        data_type = "통합분석"
    
    # 데이터 조회 (전체 데이터 활용)
    if table_name == "revisit_data":
        # 재방문율 데이터 - 더 많은 샘플로 정확한 분석
        df = query_supabase_data(table_name, limit=10000)
    elif table_name == "restaurant_data":
        # 요식업 데이터 - 더 많은 샘플로 정확한 분석
        df = query_supabase_data(table_name, limit=8000)
    else:
        # 카페 데이터는 전체 조회
        df = query_supabase_data(table_name)
    
    return df, data_type, table_name

# AI 응답 생성
def generate_ai_response(question, data_df, data_type):
    """AI를 사용하여 데이터 기반 응답 생성"""
    
    if data_df.empty:
        return "❌ 데이터를 조회할 수 없습니다. Supabase 연결과 테이블을 확인하세요."
    
    # 데이터를 텍스트로 변환 (더 많은 데이터로 정확한 분석)
    data_sample = data_df.head(15).to_string(max_cols=12, max_colwidth=50)
    
    # 분석 유형별 시스템 프롬프트
    if data_type == "카페업종":
        system_prompt = f"""당신은 카페업종 전문 마케팅 컨설턴트입니다.
        
다음 카페 데이터를 분석하여 질문에 답변하세요:

{data_sample}

**데이터 설명:**
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

답변 형식 (반드시 모든 섹션을 완성하세요):
## 1. 📊 데이터 분석
구체적인 수치와 패턴을 제시하세요.

## 2. 🎯 핵심 인사이트  
주요 발견사항과 특징을 분석하세요.

## 3. 💡 마케팅 전략
실행 가능한 구체적 전략을 제안하세요.

## 4. 📈 실행 방안
단계별 실행 계획을 제시하세요.

## 5. 📋 결론 및 요약
핵심 포인트를 정리하세요.

**중요: 답변을 중간에 끊지 말고 모든 섹션을 완성해주세요.**
"""
    
    elif data_type == "재방문율":
        system_prompt = f"""당신은 고객 재방문율 개선 전문 컨설턴트입니다.
        
다음 재방문율 데이터를 분석하여 질문에 답변하세요:

{data_sample}

**데이터 설명:**
- 재방문고객비율: 재방문 고객 비율
- 신규고객비율: 신규 고객 비율
- 월간매출액: 월 매출 수준
- 월간이용건수/고객수: 이용 빈도
- 업종평균재방문률: 업종 평균 대비 비교
- 재방문률등급: 재방문율 등급
- 충성도 관련 지표들

답변 형식 (반드시 모든 섹션을 완성하세요):
## 1. 🔍 현황 분석
현재 재방문율과 문제점을 진단하세요.

## 2. 📊 문제점 진단
업종 평균과 비교한 상대적 위치를 분석하세요.

## 3. 💡 개선 전략
재방문율 향상을 위한 구체적 방안을 제시하세요.

## 4. 🎯 실행 계획
단계별 실행 로드맵을 제시하세요.

## 5. 📋 결론 및 요약
핵심 포인트를 정리하세요.

**중요: 답변을 중간에 끊지 말고 모든 섹션을 완성해주세요.**
"""
    
    else:  # 요식업 또는 통합
        system_prompt = f"""당신은 요식업 전문 마케팅 컨설턴트입니다.
        
다음 요식업 데이터를 분석하여 질문에 답변하세요:

{data_sample}

**데이터 설명:**
- 업종: 한식, 중식, 일식, 양식 등
- 월간매출액: 매출 수준
- 배달매출비율: 배달 의존도
- 월평균객단가: 평균 객단가
- 연령대별 고객 비율
- 거주/직장/유동인구 이용 비율
- 동종업종 대비 성과 지표

답변 형식 (반드시 모든 섹션을 완성하세요):
## 1. 🍽️ 현황 분석
매출, 고객층, 운영 현황을 분석하세요.

## 2. 📊 경쟁력 진단
동종업종 대비 강점과 약점을 분석하세요.

## 3. 💡 성장 전략
매출 증대를 위한 구체적 방안을 제시하세요.

## 4. 🚀 실행 방안
장기적인 성장 전략을 제시하세요.

## 5. 📋 결론 및 요약
핵심 포인트를 정리하세요.

**중요: 답변을 중간에 끊지 말고 모든 섹션을 완성해주세요.**
"""
    
    # AI 모델 초기화
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "❌ GOOGLE_API_KEY 설정을 확인하세요."
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            api_key=api_key,
            timeout=60,  # 60초로 타임아웃 연장
            max_tokens=4000  # 응답 길이 제한 해제로 완전한 답변
        )
        
        # 메시지 생성
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question)
        ]
        
        # AI 응답 생성
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        return f"❌ AI 응답 생성 실패: {str(e)}"

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.title("🏪 Supabase 기반 마케팅 분석 챗봇")
    st.markdown("### 📊 실시간 데이터 기반 분석")
    
    # 사이드바
    with st.sidebar:
        st.markdown("## 📋 시스템 정보")
        
        # 데이터 통계
        st.markdown("### 📊 데이터 현황")
        supabase = init_supabase()
        if supabase:
            try:
                tables_info = [
                    ("cafe_data", "🍵 카페업종"),
                    ("revisit_data", "🔄 재방문율"),
                    ("restaurant_data", "🍽️ 요식업")
                ]
                
                for table_name, display_name in tables_info:
                    try:
                        # COUNT 쿼리로 실제 레코드 수 조회
                        result = supabase.table(table_name).select("*", count="exact").execute()
                        count = result.count
                        st.metric(display_name, f"{count:,}개")
                    except Exception as e:
                        st.metric(display_name, "연결 안됨")
            except:
                st.warning("데이터 통계를 불러올 수 없습니다.")
        
        st.markdown("---")
        
        st.markdown("### 💡 사용 안내")
        st.info("📝 **직접 질문을 입력하세요**\n\n카페, 재방문율, 요식업 관련 마케팅 전략에 대해 자유롭게 질문해주세요. AI가 실제 데이터를 기반으로 상세한 분석과 제안을 제공합니다.")
    
    # 메인 채팅 영역
    st.markdown("### 💬 질문하기")
    
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 기존 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 채팅 입력
    if prompt := st.chat_input("마케팅 전략에 대해 질문하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답
        with st.chat_message("assistant"):
            try:
                # 1단계: 데이터 조회
                with st.spinner("🔍 데이터 조회 중..."):
                    data_df, data_type, table_name = get_relevant_data(prompt)
                
                if not data_df.empty:
                    # 데이터 정보 표시
                    st.success(f"✅ **{data_type} 데이터** 조회 완료 ({len(data_df):,}개 레코드)")
                    
                    # 2단계: AI 분석
                    with st.spinner("🤖 AI 상세 분석 중... (최대 60초)"):
                        response = generate_ai_response(prompt, data_df, data_type)
                    
                    st.markdown(response)
                    
                    # 참고 데이터 표시
                    with st.expander("📚 참고 데이터 (상위 10개)"):
                        st.dataframe(data_df.head(10))
                    
                    # 메시지 저장
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                else:
                    error_msg = f"❌ {table_name} 테이블에서 데이터를 조회할 수 없습니다. 업로드를 확인하세요."
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
                    
            except Exception as e:
                error_msg = f"❌ 오류가 발생했습니다: {str(e)}"
                st.error(error_msg)
                st.info("💡 다시 시도하거나 더 간단한 질문을 해보세요.")
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
    
    # 푸터
    st.markdown("---")
    st.caption("💡 Tip: Supabase 클라우드 데이터베이스 기반으로 실시간 분석을 제공합니다.")

if __name__ == "__main__":
    main()
