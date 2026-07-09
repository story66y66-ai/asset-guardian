import streamlit as st
import english_class  # 這是直接把語言學院的程式「請」進來

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")
st.title("🎓 歡迎來到《澄玄大學》")

st.write("---")

# 直接把語言學院的內容顯示在首頁，這樣就不用切換頁面，就不會報錯了！
english_class.show_app()
