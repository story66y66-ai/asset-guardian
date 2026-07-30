import streamlit as st

st.set_page_config(page_title="中文學院 - 澄玄大學", layout="wide", page_icon="📖")

st.title("📖 中文學院（成語學習專區）")
st.write("---")

st.subheader("💡 今日精選成語")
st.info("這裡即將展開我們的成語學習之旅！校長大人準備好要輸入第一筆成語資料了嗎？")

# 返回首頁按鈕
if st.button("⬅️ 返回澄玄大學首頁"):
    st.switch_page("streamlit_app.py")
