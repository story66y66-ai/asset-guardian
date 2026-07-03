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
selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 2. 自動讀取 CSV
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("words.csv")
        return df.to_dict('records')
    except:
        return [{"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"}]

word_data = load_data()

# 3. 完整導航邏輯
if selection == "訓練農場":
    st.header("🏗️ 訓練農場 (學習區)")
    if 'current_word' not in st.session_state:
        st.session_state.current_word = random.choice(word_data)
    word = st.session_state.current_word
    st.write(f"### 英文：{word['word']} | 中文：{word['trans']} | KK：{word['kk']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 聽發音"):
            tts = gTTS(text=word['word'], lang='en')
            fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    with col2:
        if st.button("➡️ 下一張"):
            st.session_state.current_word = random.choice(word_data)
            st.rerun()

elif selection == "測驗中心":
    st.header("🎮 測驗中心")
    mode = st.radio("測驗模式：", ["中文輸入挑戰", "單字排列挑戰"], horizontal=True)
    word = random.choice(word_data)
    
    if mode == "中文輸入挑戰":
        st.write(f"請輸入 **{word['word']}** 的中文意思：")
        user_in = st.text_input("輸入中文：")
        if st.button("確認答案") and user_in == word['trans']: st.success("✅ 答對了！")
    else:
        st.write(f"### 提示中文：{word['trans']}")
        st.write(f"請拼出：{''.join(random.sample(word['word'].upper(), len(word['word'])))}")
        ans = st.text_input("輸入拼寫：")
        if st.button("確認"):
            if ans.upper() == word['word'].upper(): st.success("✅ 答對！")
            else: st.error(f"❌ 錯了，正確是 {word['word']}")

elif selection == "進化中心":
    st.header("💡 進化中心")
    st.write(f"農場書庫已連結，目前載入了 {len(word_data)} 個單字。")
    st.write("---")
    st.subheader("📝 當前運作程式碼 (streamlit_app.py)")
    with open("streamlit_app.py", "r", encoding="utf-8") as f:
        st.code(f.read(), language="python")

else:
    st.header(f"{selection}")
    st.write("這片區域正在耕耘中，敬請期待！")
