import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page settings
st.set_page_config(page_title="Power Report Analyzer (Free)", layout="wide")
st.title("⚡ Power Report AI Analyzer (Gemini)")

# 2. Gemini API key settings (using Streamlit Secrets)
# Save the key issued from Google AI Studio as GOOGLE_API_KEY in Secrets.
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("GOOGLE_API_KEY is not set in Secrets.")

# 3. Model settings (gemini-1.5-flash capable of image analysis)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# 4. Upload image
uploaded_file = st.file_uploader("Upload a power report image.", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded report', use_column_width=True)
    
    if st.button("Analyze with free AI"):
        with st.spinner("Gemini AI is analyzing..."):
            # Prompt configuration
            prompt = """
            You are an energy management expert. Analyze the following in Korean based on this power report image:
            1. Peak power generation time and characteristics on the graph
            2. Points where the power factor drops and warnings
            3. Operational anomalies such as 'manually excluded' meters in the table below
            4. Three specific action items for cost reduction
            """
            
            # Gemini analysis request
            response = model.generate_content([prompt, image])
            
            st.success("✅ Analysis complete!")
            st.markdown("---")
            st.subheader("💡 AI Analysis Insights")
            st.write(response.text)
