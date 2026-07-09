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

# 2. 助教示範區（新增：自動產出範例句）
words = st.session_state.challenge['word'].tolist()
example_sentence = f"I have to take **{words[0]}**, put on my **{words[1]}**, and travel **{words[2]}** away."
st.info(f"💡 助教示範句：\n{example_sentence}\n\n(中文：我必須注意{words[0]}，穿上{words[1]}，並到{words[2]}的地方去。)")

# 3. 練習與檢查區
st.divider()
st.subheader("請照著範例（或自創）輸入句子：")
user_input = st.text_area("請在此輸入您的句子：")

if st.button("檢查句子"):
    # 邏輯檢查：是否包含目標單字
    is_correct = all(w.lower() in user_input.lower() for w in words)
    
    if is_correct:
        st.success("✅ 太棒了！您成功運用了所有目標單字！")
        st.balloons() # 給校長一點鼓勵！
    else:
        # 錯誤顯示：顯示叉叉標示
        st.error("❌ 喔喔！句子裡好像缺少了某些關鍵單字，請檢查一下喔！")
        st.write("提示：請確保您的句子包含了上述三個目標單字。")

if st.button("重新抽籤"):
    st.session_state.challenge = df.sample(n=3)
    st.rerun()
