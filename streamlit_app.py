import streamlit as st
import random
from gtts import gTTS
import io

# 設定頁面配置
st.set_page_config(page_title="澄玄的農場", layout="wide")
st.sidebar.title("🌱 澄玄的農場導航")

nav_options = {
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", 
    "學習農場": "📚", "生活農場": "🏠", "訓練農場": "🏗️", "進化中心": "💡"
}

selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 單字庫
# 這是妳的「擴充書庫」，以後想加什麼字都在這裡加
word_data = [
    {"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"},
    {"word": "Banana", "trans": "香蕉", "kk": "/bəˈnæn.ə/"},
    {"word": "Cat", "trans": "貓", "kk": "/kæt/"},
    {"word": "Dog", "trans": "狗", "kk": "/dɔːɡ/"},
    {"word": "Elephant", "trans": "大象", "kk": "/ˈel.ɪ.fənt/"}
    {"word": "Elephant", "trans": "大象", "kk": "/ˈel.ɪ.fənt/"},
    {"word": "Fish", "trans": "魚", "kk": "/fɪʃ/"},
    {"word": "Girl", "trans": "女孩", "kk": "/ɡɜːrl/"},
    {"word": "House", "trans": "房子", "kk": "/haʊs/"},
    {"word": "Ice", "trans": "冰", "kk": "/aɪs/"},
    {"word": "Jump", "trans": "跳", "kk": "/dʒʌmp/"}
]

st.title(f"歡迎來到：{selection}")
@@ -31,7 +36,7 @@
    tab1, tab2, tab3 = st.tabs(["測試數據 (單字挑戰)", "草稿區", "實驗紀錄"])

    with tab1:
        st.subheader("🔤 英文單字挑戰")
        st.subheader(f"🔤 英文單字挑戰 (目前庫存: {len(word_data)} 個單字)")
        if 'current_word' not in st.session_state:
            st.session_state.current_word = random.choice(word_data)
