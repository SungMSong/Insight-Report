import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="전력 리포트 분석기", layout="wide")
st.title("⚡ 전력 리포트 AI 분석기")

# API 키 설정
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Secrets에 GOOGLE_API_KEY를 등록해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# [핵심 수정] 사용 가능한 최신 모델을 자동으로 찾는 로직
@st.cache_resource
def load_model():
    # 사용 가능한 모델 목록 중 이미지 분석(generateContent)이 가능한 모델 찾기
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # 가장 성능이 좋은 1.5 flash 또는 pro 모델 우선 선택
            if '1.5-flash' in m.name:
                return genai.GenerativeModel(m.name)
    # 못 찾을 경우 기본값
    return genai.GenerativeModel('gemini-1.5-flash')

model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.file_uploader("리포트 이미지를 업로드하세요.", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 리포트', use_column_width=True)
    
    if st.button("AI 분석 시작"):
        with st.spinner(f"분석 중입니다... (모델: {model.model_name})"):
            try:
                prompt = "이 전력 리포트 이미지에서 피크 전력, 역률 저하 구간, 특이사항을 한국어로 상세히 분석해줘."
                response = model.generate_content([prompt, image])
                
                st.success("분석 완료!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.info("API 키가 생성된 지 얼마 안 되었다면 1~2분 후 다시 시도해 보세요.")
