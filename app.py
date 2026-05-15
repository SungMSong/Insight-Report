import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# 1. 페이지 초기 설정
st.set_page_config(page_title="CVRMS 리포트 분석", layout="wide", initial_sidebar_state="expanded")
st.title("🏭 CVRMS 리포트 분석 시스템")
st.caption("한솔제지 신탄진공장 설비 계통 및 전력 절감 품질 비교 대시보드")

# 2. API 키 및 모델 확인 구역
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Secrets에 GOOGLE_API_KEY를 등록해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

@st.cache_resource
def get_available_model():
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    for name in available_models:
        if 'gemini-1.5-flash' in name: return name
    for name in available_models:
        if 'gemini-1.5-pro' in name: return name
    return available_models if available_models else None

selected_model_name = get_available_model()

if not selected_model_name:
    st.error("사용 가능한 Gemini 모델을 찾을 수 없습니다. API 키 설정을 확인해주세요.")
    st.stop()

model = genai.GenerativeModel(model_name=selected_model_name)

# 3. 사이드바 다중 이미지 업로드 레이아웃
st.sidebar.header("📸 리포트 이미지 업로드")
current_file = st.sidebar.file_uploader("🔴 현재 분석 리포트", type=["png", "jpg", "jpeg"], key="curr_img")
past_file = st.sidebar.file_uploader("🔵 과거 비교 리포트", type=["png", "jpg", "jpeg"], key="past_img")

if current_file and past_file:
    current_image = Image.open(current_file)
    past_image = Image.open(past_file)
    
    if st.button("🚀 두 리포트 데이터 비교 분석 시작", use_container_width=True):
        with st.spinner(f"AI가 두 이미지의 데이터를 정밀 비교 분석 중입니다... ({selected_model_name})"):
            try:
                # 4. 규격화된 JSON 데이터 추출을 위한 전용 프롬프트
                prompt = """
제공된 두 장의 CVRMS 전력 리포트 이미지(첫 번째: 현재 리포트, 두 번째: 과거 리포트)를 정밀 대조하여 분석 데이터를 JSON 형식으로 반환해라.

반드시 아래의 JSON 스키마 규격으로만 답변을 반환해야 하며, 다른 텍스트 설명은 제외해라:
{
  "current": {
    "date": "현재 날짜",
    "saving_krw": 현재_절감요금_숫자,
    "saving_kwh": 현재_절감량_숫자,
    "cvrf_rate": 현재_절감률_숫자,
    "tap": 현재_탭전환_숫자,
    "total_kwh": 현재_전체사용량_숫자,
    "pf_avg": 현재_평균역률_숫자,
    "excluded": 현재_제외장비_숫자
  },
  "past": {
    "date": "과거 날짜",
    "saving_krw": 과거_절감요금_숫자,
    "saving_kwh": 과거_절감량_숫자,
    "cvrf_rate": 과거_절감률_숫자,
    "tap": 과거_탭전환_숫자,
    "total_kwh": 과거_전체사용량_숫자,
    "pf_avg": 과거_평균역률_숫자,
    "excluded": 과거_제외장비_숫자
  },
  "ai_analysis": "두 시점의 데이터를 비교하여 마크다운 형식으로 종합 진단 요약 내용"
}
"""
                response = model.generate_content(
                    [prompt, current_image, past_image],
                    generation_config={"response_mime_type": "application/json"}
                )
                
                data = json.loads(response.text)
                st.success("✅ CVRMS 분석 및 데이터 연동 완료!")
                
                # 5. 상단 대시보드 지표 카드 출력
                st.markdown("### 📊 주요 운영 지표 비교")
                m1, m2, m3, m4, m5 = st.columns(5)
                
                with m1:
                    krw_delta = data["current"]["saving_krw"] - data["past"]["saving_krw"]
                    sign = "+" if krw_delta > 0 else ""
                    st.metric(
                        label="일간 절감 요금", 
                        value=f"{data['current']['saving_krw']:,} 원", 
                        delta=f"{sign}{krw_delta:,} 원"
                    )
                with m2:
                    kwh_delta = data["current"]["saving_kwh"] - data["past"]["saving_kwh"]
                    st.metric(
                        label="일간 절감량", 
                        value=f"{data['current']['saving_kwh']:.3f} kWh", 
                        delta=f"{kwh_delta:+.3f} kWh"
                    )
                with m3:
                    total_delta = data["current"]["total_kwh"] - data["past"]["total_kwh"]
                    t_sign = "+" if total_delta > 0 else ""
                    st.metric(
                        label="일간 전체 사용 전력량", 
                        value=f"{data['current']['total_kwh']:,} kWh" if isinstance(data['current']['total_kwh'], int) else f"{data['current']['total_kwh']:,.3f} kWh", 
                        delta=f"{t_sign}{total_delta:,.3f} kWh"
                    )
                with m4:
                    cvrf_delta = data["current"]["cvrf_rate"] - data["past"]["cvrf_rate"]
                    st.metric(
                        label="일간 절감률 (CVRf)", 
                        value=f"{data['current']['cvrf_rate']}%", 
                        delta=f"{cvrf_delta:+.3f}%"
                    )
                with m5:
                    tap_delta = data["current"]["tap"] - data["past"]["tap"]
                    st.metric(
                        label="Tap 전환 횟수", 
                        value=f"{data['current']['tap']} 회", 
                        delta=f"{tap_delta:+} 회"
                    )

                st.divider()

                # 6. 중단 비교 차트 시각화 구성
                c_chart1, c_chart2, c_chart3 = st.columns(3)

                with c_chart1:
                    st.markdown("#### ⚡ 일간 절감량 비교")
                    chart_data1 = pd.DataFrame([data["past"]["saving_kwh"], data["current"]["saving_kwh"]], index=["과거", "현재"], columns=["절감량(kWh)"])
                    st.bar_chart(chart_data1, use_container_width=True)

                with c_chart2:
                    st.markdown("#### 🔋 일간 전체 사용 전력량 비교")
                    chart_data2 = pd.DataFrame([data["past"]["total_kwh"], data["current"]["total_kwh"]], index=["과거", "현재"], columns=["전체 사용량(kWh)"])
                    st.bar_chart(chart_data2, use_container_width=True)

                with c_chart3:
                    st.markdown("#### 📉 계통 품질 역률 비교")
                    chart_data3 = pd.DataFrame([data["past"]["pf_avg"], data["current"]["pf_avg"]], index=["과거", "현재"], columns=["평균 역률(%)"])
                    st.bar_chart(chart_data3, use_container_width=True)

                st.divider()

                # 7. 하단 AI 종합 리포트 출력
                st.markdown("#### 🤖 AI 계통 및 에너지 절감 실적 진단 리포트")
                st.info(data["ai_analysis"])

                st.divider()

                # 8. 원본 이미지 대조 접기 메뉴
                with st.expander("🔍 업로드된 원본 리포트 이미지 대조 보기"):
                    img_col1, img_col2 = st.columns(2)
                    with img_col1:
                        st.image(current_image, caption=f"현재 리포트 ({data['current']['date']})", use_container_width=True)
                    with img_col2:
                        st.image(past_image, caption=f"과거 리포트 ({data['past']['date']})", use_container_width=True)

            except Exception as e:
                st.error(f"데이터 연동 중 오류가 발생했습니다: {e}")

else:
    st.info("💡 왼쪽 사이드바에서 '현재 리포트'와 '과거 비교 리포트' 이미지를 모두 업로드하면 대시보드가 활성화됩니다.")
