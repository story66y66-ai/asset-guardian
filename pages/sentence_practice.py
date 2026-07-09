import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("✍️ 澄玄大學 - 造句實戰室")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

if 'challenge' not in st.session_state:
    st.session_state.challenge = df.sample(n=3)

# 1. 大字體顯示目標單字並加入發音
st.subheader("🎯 今日目標單字：")
for _, row in st.session_state.challenge.iterrows():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(f"🔊 {row['word']}", key=f"btn_{row['word']}"):
            tts = gTTS(text=row['word'], lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, autoplay=True)
    with col2:
        st.markdown(f"### {row['word']}  ({row['trans']})")

# 2. 助教示範區 (放大字體與發音)
st.divider()
words = st.session_state.challenge['word'].tolist()
example_sentence = f"I have to take {words[0]}, put on my {words[1]}, and travel {words[2]} away."

st.subheader("💡 助教示範句：")
col_ex1, col_ex2 = st.columns([1, 6])
with col_ex1:
    if st.button("🔊 播放全句", key="btn_full"):
        tts = gTTS(text=example_sentence, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, autoplay=True)
with col_ex2:
    st.markdown(f"#### {example_sentence}")
    st.write(f"*(中文：我必須注意{words[0]}，穿上{words[1]}，並到{words[2]}的地方去。)*")

# 3. 大字體輸入區
st.divider()
st.subheader("📝 請輸入您的句子：")
user_input = st.text_area("在這裡輸入...", height=150) # 增加高度

if st.button("檢查句子"):
    is_correct = all(w.lower() in user_input.lower() for w in words)
    if is_correct:
        st.success("✅ 太棒了！")
        st.balloons()
    else:
        st.error("❌ 句子缺少關鍵單字，再試一次！")

if st.button("重新抽籤"):
    st.session_state.challenge = df.sample(n=3)
    st.rerun()
