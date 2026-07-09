import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("📖 澄玄大學 - 語言學院")

# 讀取資料
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 顯示表格 (直接顯示，不使用 level 篩選，避免錯誤)
st.dataframe(df, use_container_width=True, hide_index=True)

# 選擇單字
selected_word = st.selectbox("請點選或輸入想聽的單字：", df['word'].tolist())

# 自動播放邏輯
if selected_word:
    tts = gTTS(text=selected_word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3', autoplay=True)
