import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="英文學院", page_icon="📚")
st.title("📚 英文學院 - 單字農場")

@st.cache_data
def load_data():
    # sep=None 讓系統自動偵測空白、Tab 或逗號分隔，避免格式報錯
    df = pd.read_csv("words.csv", sep=None, engine='python')
    return df.to_dict('records')

try:
    word_data = load_data()
    
    if 'train_word' not in st.session_state:
        st.session_state.train_word = random.choice(word_data)

    word = st.session_state.train_word
    
    st.success("💡 **今日單字卡**")
    st.markdown(f"## 🔠 英文： **{word['word']}**")
    st.markdown(f"## 🇹🇼 中文： **{word['trans']}**")
    st.markdown(f"## 🗣️ 音標： **{word['kk']}**")
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 聽聽發音", use_container_width=True):
            tts = gTTS(text=str(word['word']), lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3')
            
    with col2:
        if st.button("➡️ 換下一個", use_container_width=True):
            st.session_state.train_word = random.choice(word_data)
            st.rerun()

except Exception as e:
    st.error("讀取單字本時發生錯誤，請確認 words.csv 是否為空白。")
