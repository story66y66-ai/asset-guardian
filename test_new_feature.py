import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 頁面基本設定
st.set_page_config(page_title="澄玄的農場", layout="wide")

# 1. 導航選單設定
st.sidebar.title("🌱 澄玄的農場導航")
# 在選項最上方加入一個 "首頁"
nav_options = {
    "農場首頁": "🏠", "訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡",
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", "學習農場": "📚"
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

# 3. 完整導航邏輯
if selection == "農場首頁":
    st.header("🌟 歡迎回到澄玄的智慧農場")
    st.write("---")
    st.subheader("農場狀態：")
    st.write(f"✅ 資料庫已同步：目前共培育了 {len(word_data)} 個單字。")
    st.write("✅ 系統已進化：單字庫與程式碼分離，運作穩定。")
    st.write("---")
    st.write("請從左側導航選單，選擇妳想前往的區域開始今天的耕耘！")
    st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfacb?q=80&w=1000&auto=format&fit=crop") # 這是示意圖

elif selection == "訓練農場":
    # (維持原本的訓練邏輯)
    st.header("🏗️ 訓練農場")
    if 'train_word' not in st.session_state: st.session_state.train_word = random.choice(word_data)
    word = st.session_state.train_word
    st.write(f"### 英文：{word['word']} | 中文：{word['trans']} | KK：{word['kk']}")
    if st.button("🔊 聽發音"):
        tts = gTTS(text=word['word'], lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    if st.button("➡️ 下一張"):
        st.session_state.train_word = random.choice(word_data); st.rerun()

# ... (其餘測驗中心、進化中心邏輯維持不變)
