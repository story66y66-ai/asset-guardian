import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# 強制調整整體字體大小的 CSS
st.markdown("""
    <style>
    div[data-baseweb="textarea"] textarea { font-size: 24px !important; }
    .stButton>button { font-size: 20px !important; height: 3em !important; }
    h1, h2, h3, h4 { font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("✍️ 澄玄大學 - 造句實戰室")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

if 'challenge' not in st.session_state:
    st.session_state.challenge = df.sample(n=3)

# 1. 目標單字區 (使用更大的顯示方式)
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
        st.markdown(f"## {row['word']}  ({row['trans']})")

# 2. 助教示範區 (放大字體)
st.divider()
words = st.session_state.challenge['word'].tolist()
example_sentence = f"I have to take {words[0]}, put on my {words[1]}, and travel {words[2]} away."

st.subheader("💡 助教示範句：")
if st.button("🔊 播放示範句 (點我)"):
    tts = gTTS(text=example_sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)
st.markdown(f"### {example_sentence}")
st.write(f"*(中文：我必須注意{words[0]}，穿上{words[1]}，並到{words[2]}的地方去。)*")

# 3. 輸入區 (使用 CSS 強制放大)
st.divider()
st.subheader("📝 請輸入您的句子：")
user_input = st.text_area("請在此輸入句子，字體已放大...", height=200)

# 4. 檢查區 (按鈕已透過 CSS 放大)
col_a, col_b = st.columns(2)
with col_a:
    if st.button("✅ 檢查句子"):
        is_correct = all(w.lower() in user_input.lower() for w in words)
        if is_correct:
            st.success("## 太棒了！完全正確！")
            st.balloons()
        else:
            st.error("## ❌ 缺少關鍵字，請再試試！")
with col_b:
    if st.button("🔄 重新抽籤"):
        st.session_state.challenge = df.sample(n=3)
        st.rerun()
