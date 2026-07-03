import streamlit as st

# 設定頁面配置
st.set_page_config(page_title="澄玄的農場", layout="wide")

# 側邊欄導航系統
st.sidebar.title("🌱 澄玄的農場導航")

# 定義導航選項
nav_options = {
    "照顧服務": "🩺",
    "食品科技": "🧪",
    "創作農場": "✍️",
    "學習農場": "📚",
    "生活農場": "🏠"
}

# 建立選擇器
selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 頁面主體渲染邏輯
st.title(f"歡迎來到：{selection}")
st.markdown("---")

# 這裡為後續擴充預留邏輯空間
if selection == "照顧服務":
    st.write("這裡是您的照服專業知識庫。")
    # 未來可在此連結至資料庫或 Notion API
elif selection == "食品科技":
    st.write("這裡是您的食品科技學科筆記。")
elif selection == "創作農場":
    st.write("記錄您的創作靈感與心情點滴。")
elif selection == "學習農場":
    st.write("記錄各學科的學習路徑。")
elif selection == "生活農場":
    st.write("管理您的生活瑣事。")

# 頁腳，維持農場簡潔感
st.sidebar.markdown("---")
st.sidebar.info("開發模式：活躍中")
