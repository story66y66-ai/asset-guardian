import streamlit as st
import random
from gtts import gTTS
import io

st.set_page_config(page_title="澄玄的農場", layout="wide")
st.sidebar.title("🌱 澄玄的農場導航")

# 1. 這是妳原本完整的農場導航區域
nav_options = {
    "訓練農場": "🏗️", "進化中心": "💡", "測驗中心": "🎮",
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", "學習農場": "📚", "生活農場": "🏠"
}

selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

word_data = [
    {"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"},
    {"word": "Banana", "trans": "香蕉", "kk": "/bəˈnæn.ə/"},
    {"word": "Cat", "trans": "貓", "kk": "/kæt/"},
    {"word": "Dog", "trans": "狗", "kk": "/dɔːɡ/"},
    {"word": "Elephant", "trans": "大象", "kk": "/ˈel.ɪ.fənt/"}
]

# 2. 這是各區域的邏輯
if selection == "測驗中心":
    st.header("🎮 測驗中心")
    sub_nav = st.radio("選擇測驗等級：", ["等級 1：中文輸入挑戰", "等級 2：單字排列挑戰"], horizontal=True)
    
    if sub_nav == "等級 1：中文輸入挑戰":
        if 'quiz_word' not in st.session_state:
            st.session_state.quiz_word = random.choice(word_data)
        st.write(f"請輸入英文單字 **{st.session_state.quiz_word['word']}** 的中文意思：")
        user_input = st.text_input("輸入中文：")
        if st.button("確認答案"):
            if user_input == st.session_state.quiz_word['trans']:
                st.success("✅ 答對了！")
                st.session_state.quiz_word = random.choice(word_data)
            else:
                st.error("❌ 答錯了，再試一次！")

elif selection == "訓練農場":
    st.header("🏗️ 訓練農場")
    st.write("這裡是原本的單字練習區。")

elif selection == "進化中心":
    st.header("🏗️ 農場進化紀錄中心")
    with st.expander("核心資源：完整程式碼"):
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            st.code(f.read(), language="python")

else:
    st.write(f"歡迎來到 {selection}，這裡正在建設中。")
