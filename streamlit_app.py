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
    "生活農場": "🏠",
    "訓練農場": "🛠️"
}

# 建立選擇器
selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 頁面主體渲染邏輯
st.title(f"歡迎來到：{selection}")
st.markdown("---")

# 各區塊邏輯
if selection == "照顧服務":
    st.write("這裡是您的照服專業知識庫。")
elif selection == "食品科技":
    st.write("這裡是您的食品科技學科筆記。")
elif selection == "創作農場":
    st.write("記錄您的創作靈感與心情點滴。")
elif selection == "學習農場":
    st.記錄各學科的學習路徑。
elif selection == "生活農場":
    st.write("管理您的生活瑣事。")
elif selection == "訓練農場":
    st.subheader("🛠 訓練農場")
    
    # 子分類標籤頁
    tab1, tab2, tab3 = st.tabs(["📊 英文單字王", "📝 草稿區", "🧪 實驗紀錄"])
    
    with tab1:
        st.write("### 英文單字王")
        st.write("您已安裝此 App，點擊下方按鈕即可快速開啟練習：")
        
        # 使用意圖連結 (intent link) 嘗試直接呼叫 App
        # 格式為 market://details?id=com.chaos.lwk，在手機瀏覽器上會優先嘗試呼叫已安裝的 App
        st.link_button("🎮 開始練習：小小單字王", "intent://details?id=com.chaos.lwk#Intent;scheme=market;package=com.google.android.gms;end")
        
        st.caption("備註：若手機無法自動開啟，請直接從桌面點擊圖示進入。")
        
    with tab2:
        st.write("### 草稿區")
        st.text_area("在這裡輸入您的草稿內容：", height=150)
        
    with tab3:
        st.write("### 實驗紀錄")
        st.success("目前無異常紀錄。")

# 頁腳
st.sidebar.markdown("---")
st.sidebar.info("開發模式：活躍中")
