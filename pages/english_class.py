import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.set_page_config(page_title="語言學院", page_icon="📖")
st.title("📖 語言學院")

# 核心邏輯：確保讀取的是跟它在同一目錄層級或根目錄的 csv
# 如果 words.csv 在根目錄，這樣寫是正確的
try:
    df = pd.read_csv("words.csv")
    st.dataframe(df, use_container_width=True)
    
    word_list = df['word'].tolist()
    selected_word = st.selectbox("請選擇一個單字：", word_list)
    
    if st.button("播放發音"):
        tts = gTTS(text=selected_word, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
except Exception as e:
    st.error("讀取單字資料時發生錯誤，請檢查 words.csv 是否存在。")
