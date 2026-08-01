import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")

st.title("🎓 歡迎來到《澄玄大學》")
st.write("---")

# 電腦學院（排在第一位）
st.subheader("💻 電腦學院")

if st.button("進入電腦學院"):
    st.switch_page("pages/1_computer_class.py")

st.write("---")
st.subheader("📚 語言學院")

if st.button("進入英文學院"):
    st.switch_page("pages/english_class.py")

if st.button("進入中文學院"):
    st.switch_page("pages/chinese_class.py")

st.write("---")
st.subheader("🍲 食品學院")

if st.button("進入烘焙教室"):
    st.switch_page("pages/baking_class.py")
