import streamlit as st
import random
from gtts import gTTS
import io

st.set_page_config(page_title="澄玄的農場", layout="wide")
st.sidebar.title("🌱 澄玄的農場導航")

nav_options = {
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", 
    "學習農場": "📚", "生活農場": "🏠", "訓練農場": "🏗️", "進化中心": "💡"
}

selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

if selection == "訓練農場":
    st.header("🏗️ 訓練農場")
    # ... (原本訓練農場的邏輯) ...
    
elif selection == "進化中心":
    st.header("🏗️ 農場進化紀錄中心")
    with st.expander("核心資源：完整程式碼 (streamlit_app.py)"):
        # 這是最聰明的做法，直接讀取自己這個檔案的內容！
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            code_content = f.read()
        st.code(code_content, language="python")

else:
    st.write(f"歡迎來到 {selection}，這裡正在建設中。")
