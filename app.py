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

# [해결책] 사용 가능한 모델을 자동으로 찾는 함수
@st.cache_resource
def get_available_model():
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # 우선순위: gemini-1.5-flash -> gemini-1.5-pro -> 리스트의 첫 번째 모델
    for name in available_models:
        if 'gemini-1.5-flash' in name: return name
    for name in available_models:
        if 'gemini-1.5-pro' in name: return name
    return available_models[0] if available_models else None

selected_model_name = get_available_model()

if not selected_model_name:
    st.error("사용 가능한 Gemini 모델을 찾을 수 없습니다. API 키 설정을 확인해주세요.")
    st.stop()

model = genai.GenerativeModel(model_name=selected_model_name)

uploaded_file = st.file_uploader("리포트 이미지를 업로드하세요.", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 리포트', use_column_width=True)
    
    if st.button("AI 분석 시작"):
        with st.spinner(f"분석 중... (연결 모델: {selected_model_name})"):
            try:
                prompt = "이 전력 리포트 이미지에서 피크 전력, 역률 저하 구간, 특이사항을 한국어로 상세히 분석해줘."
                response = model.generate_content([prompt, image])
                
                st.success("✅ 분석 완료!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.info("API 키가 활성화되는 중일 수 있습니다. 1분 뒤 다시 시도해 보세요.")
