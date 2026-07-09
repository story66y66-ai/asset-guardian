import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")

st.title("🎓 歡迎來到《澄玄大學》")
st.write("---")

st.subheader("📚 語言學院")

# 使用按鈕觸發跳轉，這才不會導致啟動時報錯
if st.button("進入語言學院"):
    # 確保路徑是相對的，這會指向 pages 資料夾內的檔案
    st.switch_page("pages/english_class.py")
