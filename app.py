import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="전력 리포트 분석 AI", layout="wide")
st.title("⚡ 전력 리포트 인사이트 분석기")
st.info("리포트 이미지를 업로드하면 그래프와 데이터를 분석하여 특이사항을 도출합니다.")

# 2. OpenAI 클라이언트 설정 (Streamlit Secrets에서 키를 가져옴)
# 배포 전에는 로컬 환경 설정을 위해 직접 키를 넣을 수도 있지만, 보안상 Secrets 권장
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 3. 이미지 업로드 기능
uploaded_file = st.file_uploader("전력 리포트 이미지(PNG, JPG)를 선택하세요.", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # 화면에 업로드한 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 리포트 샘플', use_column_width=True)
    
    # 분석 버튼
    if st.button("돋보기로 분석하기"):
        with st.spinner("AI가 그래프의 추세와 데이터를 읽고 있습니다..."):
            
            # 이미지를 AI가 읽을 수 있는 base64 형식으로 변환
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # 4. AI에게 던지는 분석 요청 (프롬프트 핵심)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": (
                                    "너는 에너지 관리 전문가야. 이 전력 리포트 이미지를 보고 다음 내용을 분석해줘:\n"
                                    "1. 그래프 상의 피크 전력 발생 시간대와 특징\n"
                                    "2. 역률(Power Factor)이 낮아지는 지점 및 경고 사항\n"
                                    "3. 하단 표에서 '수동 제외'된 계측기 등 운영상의 특이사항\n"
                                    "4. 비용 절감을 위한 구체적인 액션 아이템 3가지"
                                )
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            }
                        ],
                    }
                ],
                max_tokens=1500,
            )
            
            # 5. 결과 출력
            st.success("✅ 분석이 완료되었습니다!")
            st.markdown("---")
            st.subheader("💡 AI 도출 인사이트")
            st.write(response.choices.message.content)
            
            # 다운로드 버튼 추가
            st.download_button("결과 보고서 저장", response.choices.message.content, file_name="insight_report.txt")