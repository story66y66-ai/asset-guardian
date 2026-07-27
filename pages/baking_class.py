import streamlit as st

st.set_page_config(page_title="烘焙教室 - 澄玄大學", layout="wide", page_icon="🍞")

st.title("🍞 澄玄大學 - 食品學院：烘焙教室")
st.write("---")

st.subheader("🥐 歡迎來到烘焙天地！")
st.write("這裡將記錄烘焙科學、配方比例與製作筆記。")

# 這裡可以放妳之後想寫的烘焙筆記或小工具
user_note = st.text_area("📝 記錄你的烘焙心得或配方：", value="今天來學習基礎麵糰發酵比例...", height=150)

if st.button("💾 儲存筆記"):
    st.success("筆記記錄成功！")
