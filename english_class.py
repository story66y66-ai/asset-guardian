
import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.set_page_config(page_title="語言學院", page_icon="📚")
st.title("📚 語言學院")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# 讀取資料
try:
    df = load_data()
    st.dataframe(df, use_container_width=True)

    # 互動區
    selected_word = st.selectbox("請選擇一個單字：", df['word'].tolist())
    if st.button("播放發音"):
        tts = gTTS(text=selected_word, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
except Exception as e:
    st.error("目前無法讀取單字資料，請檢查 words.csv 是否存在。")
