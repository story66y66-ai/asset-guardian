import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")

st.title("🎓 歡迎來到《澄玄大學》")
st.write("---")
st.subheader("📚 語言學院")

# 關鍵：將跳轉指令放在 button 被點擊的事件內，不要放在最外層
if st.button("進入語言學院"):
    st.switch_page("pages/english_class.py")
