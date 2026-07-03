# 這是澄玄農場目前的最終版本，請複製並存在妳電腦的記事本裡作為永久備份
import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="澄玄的農場", layout="wide")

# 導航
st.sidebar.title("🌱 澄玄的農場導航")
nav_options = {"訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡"}
selection = st.sidebar.radio("請選擇區域：", list(nav_options.keys()))

@st.cache_data
def load_data():
    try: return pd.read_csv("words.csv").to_dict('records')
    except: return [{"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"}]

word_data = load_data()

if selection == "訓練農場":
    if 'train_word' not in st.session_state: st.session_state.train_word = random.choice(word_data)
    word = st.session_state.train_word
    st.write(f"### {word['word']} ({word['trans']})")
    if st.button("➡️ 下一張"): st.session_state.train_word = random.choice(word_data); st.rerun()

elif selection == "測驗中心":
    if 'quiz_key' not in st.session_state: st.session_state.quiz_key = random.random()
    if 'quiz_word' not in st.session_state: st.session_state.quiz_word = random.choice(word_data)
    word = st.session_state.quiz_word
    st.write(f"### 提示：{word['trans']}")
    letters = list(word['word'].upper()); random.shuffle(letters)
    st.write(f"請拼出：{''.join(letters)}")
    ans = st.text_input("輸入拼寫：", key=f"e_{st.session_state.quiz_key}")
    if st.button("確認"):
        if ans.upper() == word['word'].upper(): st.success("✅ 答對！"); st.balloons()
        else: st.error("❌ 錯了")
    if st.button("🔄 換一題"): st.session_state.quiz_key = random.random(); st.session_state.quiz_word = random.choice(word_data); st.rerun()

elif selection == "進化中心":
    with open("streamlit_app.py", "r", encoding="utf-8") as f: st.code(f.read())
