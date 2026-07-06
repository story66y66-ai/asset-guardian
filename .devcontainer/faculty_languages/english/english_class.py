import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.title("📚 英文學院 - 單字農場")

# 1. 讀取單字庫 (請注意路徑一定要這樣寫)
@st.cache_data
def load_data():
    # 因為檔案在 .devcontainer 裡面，所以路徑要這樣寫
    df = pd.read_csv(".devcontainer/faculty_languages/english/words.csv")
    return df.to_dict('records')

word_data = load_data()

# 2. 顯示單字訓練邏輯
if 'train_word' not in st.session_state:
    st.session_state.train_word = random.choice(word_data)

word = st.session_state.train_word
st.write(f"### 英文：{word['word']} | 中文：{word['trans']} | KK：{word['kk']}")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔊 聽發音"):
        tts = gTTS(text=word['word'], lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
with col2:
    if st.button("➡️ 下一張"):
        st.session_state.train_word = random.choice(word_data)
        st.rerun()
