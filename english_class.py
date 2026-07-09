import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("📚 語言學院 - 單字總覽")

# 讀取單字表
@st.cache_data
def load_data():
    # 讀取 words.csv，自動適應格式
    df = pd.read_csv("words.csv", sep=None, engine='python')
    return df

try:
    df = load_data()
    
    # 顯示表格讓妳一目了然
    st.write("這是目前儲存庫裡的單字清單：")
    st.dataframe(df, use_container_width=True)
    
    st.write("---")
    st.subheader("🔊 聽聽看單字發音")
    
    # 讓妳選一個單字來發音
    selected_word = st.selectbox("請選擇一個單字：", df['word'].tolist())
    
    if st.button("播放發音"):
        tts = gTTS(text=selected_word, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')

except Exception as e:
    st.error(f"讀取單字表時發生小狀況：{e}")
