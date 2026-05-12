import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="전력 리포트 분석기", layout="wide")
st.title("⚡ 전력 리포트 AI 분석기 (무료 버전)")

# API 키 설정
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Secrets에 GOOGLE_API_KEY를 등록해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 모델 설정 (가장 최신 모델 사용)
model = genai.GenerativeModel('gemini-1.5-pro')

uploaded_file = st.file_uploader("리포트 이미지를 업로드하세요.", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 리포트', use_column_width=True)
    
    if st.button("AI 분석 시작"):
        with st.spinner("분석 중입니다..."):
            try:
                prompt = "이 전력 리포트 이미지에서 피크 전력, 역률 저하 구간, 특이사항을 한국어로 분석해줘."
                # 분석 요청
                response = model.generate_content([prompt, image])
                
                st.success("분석 완료!")
                st.write(response.text)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
