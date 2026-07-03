import streamlit as st
import random
from gtts import gTTS
import io

st.set_page_config(page_title="澄玄的農場", layout="wide")
st.sidebar.title("🌱 澄玄的農場測驗中心")

# 單字庫 (未來可擴充至 50 個)
word_data = [
    {"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"},
    {"word": "Banana", "trans": "香蕉", "kk": "/bəˈnæn.ə/"},
    {"word": "Cat", "trans": "貓", "kk": "/kæt/"},
    {"word": "Dog", "trans": "狗", "kk": "/dɔːɡ/"},
    {"word": "Elephant", "trans": "大象", "kk": "/ˈel.ɪ.fənt/"}
]

nav = st.sidebar.radio("選擇測驗等級：", ["等級 1：中文輸入挑戰", "等級 2：單字排列挑戰"])

st.title(f"🎮 {nav}")

# 等級 1 邏輯
if nav == "等級 1：中文輸入挑戰":
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

# 等級 2 邏輯 (簡化版：點選正確順序)
elif nav == "等級 2：單字排列挑戰":
    st.write("請依照正確順序點選以下字母組成單字：")
    target = st.session_state.get('target', random.choice(word_data)['word'].upper())
    st.session_state.target = target
    
    letters = list(target)
    random.shuffle(letters)
    
    if st.button(f"重置順序"): st.rerun()
    
    cols = st.columns(len(letters))
    for i, char in enumerate(letters):
        if cols[i].button(char, key=f"btn_{i}"):
            st.write(f"妳點了：{char}")
            # 這裡可以加入檢查邏輯

# 進化中心
with st.expander("核心資源：自動更新代碼"):
    with open("streamlit_app.py", "r", encoding="utf-8") as f:
        st.code(f.read(), language="python")
