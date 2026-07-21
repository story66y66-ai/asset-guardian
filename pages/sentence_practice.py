import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import random

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
        if st.button(f"🔊 {row['word']}", key=f"btn_{row['word']}_{random.randint(1,1000)}"):
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

# 💡 智慧句型庫：準備多種不同情境的英文與中文句型模板
PATTERN_POOL = [
    (
        "When we look at {w0}, we can easily connect it with {w1} through {w2}.",
        "當我們看到 {w0} 時，可以透過 {w2} 輕鬆把它和 {w1} 連結起來。"
    ),
    (
        "People often find that {w0} plays a key role when dealing with {w1} and {w2}.",
        "人們常發現，在處理 {w1} 與 {w2} 時，{w0} 扮演著關鍵的角色。"
    ),
    (
        "If you are interested in {w0}, you should also pay attention to {w1} and {w2}.",
        "如果你對 {w0} 感興趣，你也應該同時關注 {w1} 和 {w2}。"
    ),
    (
        "Instead of ignoring {w0}, we started to explore {w1} alongside {w2}.",
        "我們沒有忽視 {w0}，而是開始同時探索 {w1} 以及 {w2}。"
    ),
    (
        "The expert explained how {w0} affects both {w1} and {w2} in daily life.",
        "專家解釋了 {w0} 如何在日常生活中影響 {w1} 與 {w2}。"
    )
]

# 隨機挑選其中一套句型
if 'chosen_pattern_idx' not in st.session_state or st.session_state.get('need_refresh', False):
    st.session_state.chosen_pattern_idx = random.randint(0, len(PATTERN_POOL) - 1)

eng_template, chi_template = PATTERN_POOL[st.session_state.chosen_pattern_idx]

# 將抽到的單字塞進範本中
raw_sentence = eng_template.format(w0=words[0], w1=words[1], w2=words[2])
chi_sentence = chi_template.format(
    w0=f"<b>{words[0]}</b> ({trans_list[0]})",
    w1=f"<b>{words[1]}</b> ({trans_list[1]})",
    w2=f"<b>{words[2]}</b> ({trans_list[2]})"
)

# 🎯 英文示範句：目標單字帶紅色
red_word_0 = f"<span class='red-word'>{words[0]}</span>"
red_word_1 = f"<span class='red-word'>{words[1]}</span>"
red_word_2 = f"<span class='red-word'>{words[2]}</span>"

colored_sentence = raw_sentence
colored_sentence = colored_sentence.replace(words[0], red_word_0)
colored_sentence = colored_sentence.replace(words[1], red_word_1)
colored_sentence = colored_sentence.replace(words[2], red_word_2)

st.subheader("💡 助教示範句：")
if st.button("🔊 播放示範句", key="play_demo_sentence"):
    tts = gTTS(text=raw_sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)

# 顯示紅字英文句
st.markdown(f"### {colored_sentence}", unsafe_allow_html=True)
# 顯示中文對應句
st.markdown(f"*(中文：{chi_sentence})*", unsafe_allow_html=True)

st.divider()
st.subheader("📝 請輸入您的句子：")
user_input = st.text_area("在這裡輸入...", height=150)

col_a, col_b = st.columns(2)
with col_a:
    if st.button("✅ 檢查句子", key="check_user_sentence"):
        is_correct = all(str(w).lower() in user_input.lower() for w in words)
        if is_correct:
            st.success("## 太棒了！完全正確！")
            st.balloons()
        else:
            st.error("## ❌ 缺少關鍵字，請再試試！")

with col_b:
    if st.button("🔄 重新抽籤", key="refresh_challenge"):
        st.session_state.need_refresh = True
        st.rerun()
