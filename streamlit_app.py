import streamlit as st
import random
from gtts import gTTS
import io

st.set_page_config(page_title="澄玄的農場", layout="wide")
st.sidebar.title("🌱 澄玄的農場導航")

# 1. 導航選單設定
nav_options = {
    "訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡",
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", "學習農場": "📚", "生活農場": "🏠"
}
selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 2. 擴充單字庫 (這裡以後可以擴充到 50 個)
word_data = [
    {"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"},
    {"word": "Banana", "trans": "香蕉", "kk": "/bəˈnæn.ə/"},
    {"word": "Cat", "trans": "貓", "kk": "/kæt/"},
    {"word": "Dog", "trans": "狗", "kk": "/dɔːɡ/"},
    {"word": "Elephant", "trans": "大象", "kk": "/ˈel.ɪ.fənt/"}
]

# 3. 各區邏輯
if selection == "訓練農場":
    st.header("🏗️ 訓練農場 (學習區)")
    if 'train_word' not in st.session_state: st.session_state.train_word = random.choice(word_data)
    word = st.session_state.train_word
    st.write(f"### 英文：{word['word']} | 中文：{word['trans']} | KK：{word['kk']}")
    if st.button("🔊 聽發音"):
        tts = gTTS(text=word['word'], lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    if st.button("換一個單字"): del st.session_state.train_word; st.rerun()

elif selection == "測驗中心":
    st.header("🎮 測驗中心")
    mode = st.radio("模式：", ["中文輸入挑戰", "拼字挑戰"], horizontal=True)
    if 'quiz_word' not in st.session_state: st.session_state.quiz_word = random.choice(word_data)
    word = st.session_state.quiz_word
    
    if mode == "中文輸入挑戰":
        st.write(f"請輸入 **{word['word']}** 的中文：")
        user_in = st.text_input("輸入：")
        if st.button("確認") and user_in == word['trans']:
            st.success("✅ 答對！"); del st.session_state.quiz_word; st.rerun()
    else:
        st.write(f"請拼出 **{word['trans']}** 的英文：")
        user_in = st.text_input("輸入：")
        if st.button("確認") and user_in.lower() == word['word'].lower():
            st.success("✅ 答對！"); del st.session_state.quiz_word; st.rerun()

elif selection == "進化中心":
    st.header("💡 進化中心")
    with open("streamlit_app.py", "r", encoding="utf-8") as f: st.code(f.read())

else:
    st.write(f"歡迎來到 {selection}，這裡正在建設中。")
