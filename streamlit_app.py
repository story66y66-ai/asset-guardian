import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 設定頁面佈局
st.set_page_config(page_title="澄玄的農場", layout="wide")

# 1. 導航選單設定
st.sidebar.title("🌱 澄玄的農場導航")
nav_options = {
    "訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡",
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", "學習農場": "📚", "生活農場": "🏠"
}
selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 2. 自動讀取 CSV 的單字庫 (請確保 GitHub 根目錄有 words.csv)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("words.csv")
        return df.to_dict('records')
    except:
        return [{"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"}] # 備用資料

word_data = load_data()

# 3. 各區域功能邏輯
if selection == "訓練農場":
    st.header("🏗️ 訓練農場 (學習區)")
    word = random.choice(word_data)
    st.write(f"### 英文：{word['word']} | 中文：{word['trans']} | KK：{word['kk']}")
    if st.button("🔊 聽發音"):
        tts = gTTS(text=word['word'], lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')

elif selection == "測驗中心":
    st.header("🎮 測驗中心")
    mode = st.radio("選擇測驗等級：", ["中文輸入挑戰", "單字排列挑戰"], horizontal=True)
    word = random.choice(word_data)
    
    if mode == "中文輸入挑戰":
        st.write(f"請輸入 **{word['word']}** 的中文意思：")
        user_in = st.text_input("輸入中文：")
        if st.button("確認答案") and user_in == word['trans']:
            st.success("✅ 答對了！")
    else:
        st.write(f"請拼出：{''.join(random.sample(word['word'].upper(), len(word['word'])))}")
        st.write(f"正確答案應該是：{word['word'].upper()}")

elif selection == "進化中心":
    st.header("💡 進化中心")
    st.write(f"目前農場單字庫中共有 {len(word_data)} 個單字。")
    st.code("只需編輯 words.csv 即可無限擴充，無須修改程式碼。")

else:
    st.header(f"{selection}")
    st.write("此區域正在建設中...")
