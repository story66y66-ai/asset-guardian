import streamlit as st
import random

# 設定頁面配置
st.set_page_config(page_title="澄玄的農場", layout="wide")

# 側邊欄導航系統
st.sidebar.title("🌱 澄玄的農場導航")

nav_options = {
    "照顧服務": "🦺",
    "食品科技": "🧪",
    "創作農場": "🎨",
    "學習農場": "📚",
    "生活農場": "🏠",
    "訓練農場": "🏗️"
}

selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 單字庫資料 (國小程度)
word_data = [
    {"word": "Apple", "trans": "蘋果"},
    {"word": "Banana", "trans": "香蕉"},
    {"word": "Cat", "trans": "貓"},
    {"word": "Dog", "trans": "狗"},
    {"word": "Elephant", "trans": "大象"},
    {"word": "Flower", "trans": "花"}
]

# 頁面主體
st.title(f"歡迎來到：{selection}")

if selection == "訓練農場":
    st.header("🏗️ 訓練農場")
    tab1, tab2, tab3 = st.tabs(["測試數據 (單字挑戰)", "草稿區", "實驗紀錄"])
    
    with tab1:
        st.subheader("🔤 英文單字練習")
        
        # 使用 session_state 來記住當前的單字，這樣按按鈕時才不會消失
        if 'current_word' not in st.session_state:
            st.session_state.current_word = random.choice(word_data)
        
        # 顯示單字
        st.markdown(f"### 英文：{st.session_state.current_word['word']}")
        
        # 點擊顯示中文按鈕
        if st.button("顯示中文"):
            st.success(f"中文意思：{st.session_state.current_word['trans']}")
            
        # 下一個單字按鈕
        if st.button("換一個單字"):
            st.session_state.current_word = random.choice(word_data)
            st.rerun() # 重新載入畫面
            
    with tab2:
        st.write("這裡是草稿區。")
    with tab3:
        st.write("這裡是實驗紀錄區。")
else:
    st.write(f"歡迎來到 {selection}，這裡正在建設中。")
