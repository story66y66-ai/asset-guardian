import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="澄玄的農場", layout="wide")

# 讀取 CSV 檔案
@st.cache_data
def load_data():
    # 這會讀取妳剛剛建立的 words.csv
    df = pd.read_csv("words.csv")
    return df.to_dict('records')

word_data = load_data()

# 導航與邏輯
st.sidebar.title("🌱 澄玄的農場")
nav_options = {"訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡"}
selection = st.sidebar.radio("選擇區域：", list(nav_options.keys()))

if selection == "訓練農場":
    st.header("🏗️ 訓練農場")
    word = random.choice(word_data)
    st.write(f"### {word['word']} ({word['trans']})")
    if st.button("🔊 聽發音"):
        tts = gTTS(text=word['word'], lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')

elif selection == "測驗中心":
    st.header("🎮 測驗中心")
    word = random.choice(word_data)
    st.write(f"請拼出 **{word['trans']}** 的英文：")
    ans = st.text_input("輸入拼寫：")
    if st.button("確認"):
        if ans.lower() == word['word'].lower(): st.success("✅ 對了！")
        else: st.error(f"❌ 錯了，正確是 {word['word']}")

elif selection == "進化中心":
    st.write("單字庫已分離，現在可以輕鬆擴充至 50 個！")
