
import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")
st.title("🎓 歡迎來到《澄玄大學》")

st.write("---")
if st.button("🏫 進入 語言學院 (點擊進入單字農場)", use_container_width=True):
    st.switch_page("english_class.py")
