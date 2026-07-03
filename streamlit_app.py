import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 頁面基本設定
st.set_page_config(page_title="澄玄的農場", layout="wide")

# 1. 導航選單設定
st.sidebar.title("🌱 澄玄的農場導航")
nav_options = {
    "訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡",
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", "學習農場": "📚", "生活農場": "🏠"
}
selection = st.sidebar.radio("請選擇區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 2. 自動讀取 CSV
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("words.csv")
        return df.to_dict('records')
    except:
        return [{"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"}]

word_data = load_data()

# 3. 各區域邏輯
if selection == "訓練農場":
    st.header("🏗️ 訓練農場 (學習區)")
    # 使用 session_state 來確保題目穩定
    if 'train_word' not in st.session_state: st.session_state.train_word = random.choice(word_data)
    word = st.session_state.train_word
    st.write(f"### 英文：{word['word']} | 中文：{word['trans']} | KK：{word['kk']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 聽發音"):
            tts = gTTS(text=word['word'], lang='en')
            fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    with col2:
        if st.button("➡️ 下一張"):
            st.session_state.train_word = random.choice(word_data); st.rerun()

elif selection == "測驗中心":
    st.header("🎮 測驗中心")
    mode = st.radio("測驗模式：", ["中文輸入挑戰", "單字排列挑戰"], horizontal=True)
    
    # 建立一個唯一的識別碼，每次換題都改變它，強制輸入框重置
    if 'quiz_key' not in st.session_state: st.session_state.quiz_key = random.random()
    if 'quiz_word' not in st.session_state: st.session_state.quiz_word = random.choice(word_data)
    
    word = st.session_state.quiz_word
    
    # 測驗區域邏輯
    if mode == "中文輸入挑戰":
        st.write(f"請輸入 **{word['word']}** 的中文意思：")
        user_in = st.text_input("輸入中文：", key=f"c_{st.session_state.quiz_key}")
        if st.button("確認"):
            if user_in == word['trans']:
                st.success("✅ 答對了！恭喜！"); st.balloons()
            else: st.error("❌ 錯了，再試試看！")
    
    else:
        st.write(f"### 提示中文：{word['trans']}")
        letters = list(word['word'].upper())
        random.shuffle(letters)
        st.write(f"請拼出：{''.join(letters)}")
        ans = st.text_input("輸入拼寫：", key=f"e_{st.session_state.quiz_key}")
        
        if st.button("確認"):
            if ans.upper() == word['word'].upper():
                st.success("✅ 答對！太棒了！"); st.balloons()
            else: st.error(f"❌ 錯了，正確是 {word['word']}")
    
    # 強制重置按鈕
    if st.button("🔄 跳過/換一題"):
        st.session_state.quiz_key = random.random() # 改變 key，強制輸入框清空
        st.session_state.quiz_word = random.choice(word_data)
        st.rerun()

elif selection == "進化中心":
    st.header("💡 進化中心")
    st.write(f"農場書庫已連結，共有 {len(word_data)} 個單字。")
    st.subheader("📝 當前運作程式碼 (streamlit_app.py)")
    with open("streamlit_app.py", "r", encoding="utf-8") as f: st.code(f.read(), language="python")

else:
    st.header(f"{selection}"); st.write("這片區域正在耕耘中，敬請期待！")
