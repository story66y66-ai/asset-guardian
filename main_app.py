import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide")

st.title("🎓 歡迎來到《澄玄大學》")
st.subheader("每一門專業，都是你未來的一塊拼圖")

# 學院卡片設計
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📚 語言學院")
    st.write("單字記憶與拼字訓練")
    # 這裡我們直接幫妳連結到該學院的程式碼路徑
    if st.button("進入 語言學院"):
        st.switch_page("./faculty_languages/english/english_class.py")

with col2:
    st.markdown("### ❤️ 照服學院")
    st.write("敬請期待...")

with col3:
    st.markdown("### 🍎 食科學院")
    st.write("敬請期待...")
