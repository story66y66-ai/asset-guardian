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

if len(filtered_df) < 3:
    filtered_df = df

# 💡 核心創新：準備一套「口語化、生動實用」的現成英文好句庫
# 每個元素格式：(英文完整好句, 中文翻譯, [包含的三個單字英文原名])
# 系統會從我們的 words.csv 裡面去撈出對應的資料來顯示！
CONV_SENTENCE_POOL = [
    (
        "Could you please help me check if this order is ready?",
        "可以請幫我確認一下這筆訂單準備好了嗎？",
        ["order", "help", "check"]
    ),
    (
        "I really need to focus on my study plan for this semester.",
        "我真的需要專注在我這學期的讀書計畫上。",
        ["focus", "study", "plan"]
    ),
    (
        "Let us take a short break before we start the next task.",
        "我們在開始下一個任務之前，先休息一下吧。",
        ["break", "start", "task"]
    ),
    (
        "She always brings a positive energy to everyone around her.",
        "她總是為身邊的每個人帶來積極的正能量。",
        ["energy", "everyone", "around"]
    ),
    (
        "Finding a good balance between work and life is truly important.",
        "在工作和生活之間找到良好的平衡真的很重要。",
        ["balance", "work", "life"]
    ),
    (
        "Do you remember where we parked our car this morning?",
        "妳記得我們今天早上把車停在哪裡嗎？",
        ["remember", "car", "morning"]
    )
]

# 當切換等級、初次載入、或按重新抽籤時，隨機選一句口語好句
if ('chosen_conv_item' not in st.session_state 
    or st.session_state.get('need_refresh', False)):
    
    # 隨機挑選一句好句
    chosen_sentence, chosen_chinese, target_words = random.choice(CONV_SENTENCE_POOL)
    
    # 從 CSV 資料庫中把這三個單字的詳細資料（中文翻譯、等級）找出來
    sub_df_list = []
    for tw in target_words:
        match_row = df[df['word'].str.lower() == tw.lower()]
        if not match_row.empty:
            sub_df_list.append(match_row.iloc[0])
        else:
            # 萬一 CSV 找不到，就隨機從資料庫補一個
            sub_df_list.append(df.sample(n=1).iloc[0])
            
    st.session_state.challenge = pd.DataFrame(sub_df_list)
    st.session_state.raw_eng_sentence = chosen_sentence
    st.session_state.raw_chi_sentence = chosen_chinese
    st.session_state.need_refresh = False

# 取得目前的目標單字清單
words = st.session_state.challenge['word'].tolist()
trans_list = st.session_state.challenge['trans'].tolist()

st.subheader("🎯 今日目標單字（來自實用口語句）：")
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

# 處理助教示範句的紅字標註
eng_sentence = st.session_state.raw_eng_sentence
chi_sentence = st.session_state.raw_chi_sentence

colored_sentence = eng_sentence
for w in words:
    # 忽略大小寫替換成紅字
    import re
    pattern = re.compile(re.escape(w), re.IGNORECASE)
    colored_sentence = pattern.sub(f"<span class='red-word'>{w}</span>", colored_sentence)

st.subheader("💡 助教示範句：")
if st.button("🔊 播放示範句", key="play_demo_sentence"):
    tts = gTTS(text=eng_sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)

# 顯示紅字英文口語句
st.markdown(f"### {colored_sentence}", unsafe_allow_html=True)
# 顯示中文意思
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
