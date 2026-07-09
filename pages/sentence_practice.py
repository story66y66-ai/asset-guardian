import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# 強制調整整體字體大小
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 32px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 24px !important; padding: 15px 30px !important; }
    h1, h2, h3, h4 { font-weight: bold !important; }
    p { font-size: 28px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("✍️ 澄玄大學 - 造句實戰室")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 關鍵邏輯：若沒挑戰單字，或使用者按了重新抽籤，就重新選取
if 'challenge' not in st.session_state or st.session_state.get('need_refresh', False):
    st.session_state.challenge = df.sample(n=3)
    st.session_state.need_refresh = False # 重置刷新狀態

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

st.divider()
words = st.session_state.challenge['word'].tolist()
example_sentence = f"I have to take {words[0]}, put on my {words[1]}, and travel {words[2]} away."

st.subheader("💡 助教示範句：")
if st.button("🔊 播放示範句"):
    tts = gTTS(text=example_sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)
st.markdown(f"### {example_sentence}")

# 加入粗體語法的翻譯
st.write(f"*(中文：我必須注意 **{words[0]}**，穿上 **{words[1]}**，並到 **{words[2]}** 的地方去。)*")

st.divider()
st.subheader("📝 請輸入您的句子：")
user_input = st.text_area("在這裡輸入...", height=150)

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
    # 點擊後設定 need_refresh 為 True，並強制重跑頁面
    if st.button("🔄 重新抽籤"):
        st.session_state.need_refresh = True
        st.rerun()
