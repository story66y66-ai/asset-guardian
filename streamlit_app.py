import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")

st.title("🎓 歡迎來到《澄玄大學》")
st.write("---")

# 使用 columns 排版讓首頁更整齊
col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 語言學院")
    # 這裡的路徑是關鍵：因為檔案在 pages/english_class.py
    # switch_page 只需要寫 "pages/english_class.py"
    if st.button("進入語言學院"):
        st.switch_page("pages/english_class.py")
