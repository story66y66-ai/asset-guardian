import streamlit as st

st.set_page_config(page_title="澄玄大學", layout="wide", page_icon="🎓")

# 正式版首頁設計
st.title("🎓 歡迎來到《澄玄大學》")
st.subheader("在這裡，我們將知識轉化為力量。")

st.write("---")
st.write("### 學院導覽")

# 這裡我們用欄位設計，讓首頁看起來更專業
col1, col2 = st.columns(2)

with col1:
    if st.button("📚 進入語言學院"):
        st.switch_page("english_class.py")
    st.write("學習專業術語、生活對話與實用英文。")

with col2:
    st.info("更多學院（如：醫療照護、食科技術）即將建設中...")
