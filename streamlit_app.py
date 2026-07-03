import streamlit as st

# 設定頁面配置
st.set_page_config(page_title="澄玄的農場", layout="wide")

# 側邊欄導航系統
st.sidebar.title("🌱 澄玄的農場導航")

# 定義導航選項
nav_options = {
    "照顧服務": "🦺",
    "食品科技": "🧪",
    "創作農場": "🎨",
    "學習農場": "📚",
    "生活農場": "🏠",
    "訓練農場": "🏗️"
}

# 建立選擇器
selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 頁面主體渲染邏輯
st.title(f"歡迎來到：{selection}")

if selection == "照顧服務":
    st.write("這裡是您的照服專業知識庫。")
elif selection == "食品科技":
    st.write("這裡是您的食品科技筆記。")
elif selection == "訓練農場":
    st.header("🏗️ 訓練農場")
    tab1, tab2, tab3 = st.tabs(["英文單字王", "草稿區", "實驗紀錄"])
    with tab1:
        st.write("這裡是測試數據區")
    with tab2:
        st.write("這裡是草稿區")
    with tab3:
        st.write("這裡是實驗紀錄區")
else:
    st.write(f"歡迎來到 {selection}，這裡目前正在施工中。")
