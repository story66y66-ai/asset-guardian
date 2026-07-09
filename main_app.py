import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")
st.title("🎓 歡迎來到《澄玄大學》")

st.write("---")

# 這裡我們改用最基礎的連結方式，確保絕對能運作
if st.button("進入語言學院"):
    st.write("請直接從左側選單點擊 english_class.py 進入")
