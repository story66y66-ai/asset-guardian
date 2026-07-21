import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 強制調整整體字體大小
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 32px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 24px !important; padding: 15px 30px !important; }
    h1, h2, h3, h4 { font-weight: bold !important; }
    p { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("✍️ 澄玄大學 - 造句實戰室")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 🎯 選擇單字等級 (Level)
selected_level = st.selectbox(
    "📊 請選擇單字等級 (Level)：",
    ["全部等級 (隨機)", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6"]
)

# 依選擇過濾資料庫
if selected_level == "全部等級 (隨機)":
    filtered_df = df
else:
    target_lvl = int(selected_level.split(" ")[1])
    filtered_df = df[df['level'] == target_lvl]

# 防呆機制：若選取的等級裡面單字不足 3 個，就降級以防報錯
if len(filtered_df) < 3:
    st.warning(f"⚠️ {selected_level} 目前資料庫裡的單字少於 3 個，已自動開啟全庫抽籤喔！")
    filtered_df = df

# 關鍵邏輯：切換等級、第一次載入、或按下重新抽籤時重新選取
if ('challenge' not in st.session_state 
    or st.session_state.get('need_refresh', False)
    or st.session_state.get('current_level') != selected_level):
    
    st.session_state.challenge = filtered_df.sample(n=3)
    st.session_state.current_level = selected_level
    st.session_state.need_refresh = False # 重置刷新狀態

st.subheader("🎯 今日目標單字：")
for _, row in st.session_state.challenge.iterrows():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(f"🔊 {row['word']}", key=f"btn_{row['word']}"):
            tts = gTTS(text=str(row['word']), lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, autoplay=True)
    with col2:
        st.markdown(f"### {row['word']}  ({row['trans']}) <span style='font-size: 20px; color: #888888;'>(L{row['level']})</span>", unsafe_allow_html=True)

st.divider()

# 取得單字與中文翻譯清單
words = st.session_state.challenge['word'].tolist()
trans_list = st.session_state.challenge['trans'].tolist()

# 🎯 多元情境智慧輪替句型（不論抽到什麼單字，自動切換最順暢的日常對話結構）
templates = [
    (
        f"Whenever I look at {words[0]}, I always think about how to use {words[1]} and deal with {words[2]}.",
        f"每當我看到 {words[0]} 時，我總是在想該如何使用 {words[1]} 並處理好 {words[2]}。"
    ),
    (
        f"It is important to understand {words[0]}, prepare for {words[1]}, and remember {words[2]}.",
        f"理解 {words[0]}、為 {words[1]} 做準備，並且記住 {words[2]}，這非常重要。"
    ),
    (
        f"We tried to check {words[0]}, handle {words[1]}, and focus on {words[2]} today.",
        f"我們今天試著檢查 {words[0]}、處理 {words[1]}，並且專注於 {words[2]}。"
    )
]

# 根據當次抽到的單字組合隨機挑選一句最合適的萬用情境
chosen_template = random.choice(templates)
raw_sentence = chosen_template[0]
chinese_translation = chosen_template[1]

red_word_0 = f"<span class='red-word'>{words[0]}</span>"
red_word_1 = f"<span class='red-word'>{words[1]}</span>"
red_word_2 = f"<span class='red-word'>{words[2]}</span>"

colored_sentence = raw_sentence.replace(words[0], red_word_0).replace(words[1], red_word_1).replace(words[2], red_word_2)

st.subheader("💡 助教示範句：")
if st.button("🔊 播放示範句"):
    tts = gTTS(text=raw_sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)

# 顯示紅字英文句
st.markdown(f"### {colored_sentence}", unsafe_allow_html=True)

# 🎯 中文動態對應單字與翻譯
zh_word_0 = f"<b>{words[0]}</b> ({trans_list[0]})"
zh_word_1 = f"<b>{words[1]}</b> ({trans_list[1]})"
zh_word_2 = f"<b>{words[2]}</b> ({trans_list[2]})"

formatted_chinese = chinese_translation.replace(words[0], zh_word_0).replace(words[1], zh_word_1).replace(words[2], zh_word_2)

st.markdown(f"*(中文：{formatted_chinese})*", unsafe_allow_html=True)

st.divider()
st.subheader("📝 請輸入您的句子：")
user_input = st.text_area("在這裡輸入...", height=150)

col_a, col_b = st.columns(2)
with col_a:
    if st.button("✅ 檢查句子"):
        is_correct = all(str(w).lower() in user_input.lower() for w in words)
        if is_correct:
            st.success("## 太棒了！完全正確！")
            st.balloons()
        else:
            st.error("## ❌ 缺少關鍵字，請再試試！")

with col_b:
    if st.button("🔄 重新抽籤"):
        st.session_state.need_refresh = True
        st.rerun()
