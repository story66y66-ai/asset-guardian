
import streamlit as st
import pandas as pd
from gtts import gTTS
import io

def show_app():  # 新增這一行
    st.header("📚 語言學院")
    
    @st.cache_data
    def load_data():
        return pd.read_csv("words.csv")

    try:
        df = load_data()
        st.dataframe(df, use_container_width=True)
        
        selected_word = st.selectbox("請選擇一個單字：", df['word'].tolist())
        if st.button("播放發音"):
            tts = gTTS(text=selected_word, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3')
    except Exception as e:
        st.error(f"讀取資料庫時發生錯誤：{e}")
