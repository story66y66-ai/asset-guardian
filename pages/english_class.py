
import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("📚 語言學院")

# 讀取根目錄下的 words.csv
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

try:
    df = load_data()
    st.dataframe(df, use_container_width=True)

    # 選擇單字發音
    word_list = df['word'].tolist()
    selected_word = st.selectbox("請選擇一個單字：", word_list)
    
    if st.button("播放發音"):
        tts = gTTS(text=selected_word, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
        
except Exception as e:
    st.warning("請確認根目錄下是否有 words.csv 檔案，且格式正確。")
