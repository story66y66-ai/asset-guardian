import streamlit as st
import pandas as pd

st.title("✍️ 澄玄大學 - 造句實戰室")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 1. 抽詞區
if 'challenge' not in st.session_state:
    st.session_state.challenge = df.sample(n=3)

st.subheader("今日目標單字：")
st.table(st.session_state.challenge[['word', 'trans']])

if st.button("重新抽籤"):
    st.session_state.challenge = df.sample(n=3)
    st.rerun()

# 2. 造句區
st.divider()
st.subheader("請輸入包含上述單字的句子：")
user_sentence = st.text_area("在這裡輸入您的句子：")

if st.button("檢查句子"):
    if not user_sentence:
        st.warning("校長，請先輸入句子喔！")
    else:
        st.subheader("📝 助教分析：")
        
        # 簡易邏輯檢核：檢查是否包含目標單字
        found_words = [word for word in st.session_state.challenge['word'] if word.lower() in user_sentence.lower()]
        
        if len(found_words) == len(st.session_state.challenge):
            st.success("太棒了！您成功用上了所有目標單字。")
            st.write("解析：您的句子架構清晰，建議可以多練習使用更專業的連接詞。")
        elif len(found_words) > 0:
            st.info(f"不錯喔！您用到了這些字：{', '.join(found_words)}")
            missing = set(st.session_state.challenge['word']) - set(found_words)
            st.warning(f"還差這些字沒用到喔：{', '.join(missing)}")
        else:
            st.error("校長，目標單字好像還沒出現，再試一次吧！")

        # 基礎文法解說提示
        st.markdown("""
        ### 💡 文法重點建議：
        - 檢查主詞與動詞是否一致 (Subject-Verb Agreement)。
        - 確認時態 (Tense) 是否統一。
        - 專業語境建議：若是在食品科技領域，建議多使用主動語態描述實驗過程。
        """)
