import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")
st.title("🎓 歡迎來到《澄玄大學》")

st.write("---")

# 這裡我們用一個簡單的文字按鈕，點擊後會引導系統去執行 english_class.py
if st.button("進入語言學院"):
    st.switch_page("english_class.py")
