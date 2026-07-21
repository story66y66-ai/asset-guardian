import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import random

# 強制調整整體字體大小與頁面寬度延展
st.markdown("""
    <style>
    .block-container { max-width: 95% !important; padding-top: 2rem !important; }
    .stTextArea textarea { font-size: 32px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    h1, h2, h3, h4 { font-weight: bold !important; }
    p { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    
    /* 放大紅框選單內的文字與下拉清單文字 */
    div[data-baseweb="select"] div, div[data-baseweb="select"] span {
        font-size: 28px !important;
        font-weight: bold !important;
    }
    div[role="listbox"] div {
        font-size: 26px !important;
        font-weight: bold !important;
    }
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

# 依選擇過濾資料庫（相容大小寫 level 欄位）
if selected_level == "全部等級 (隨機)":
    filtered_df = df
else:
    target_lvl = int(selected_level.split(" ")[1])
    level_col = 'level' if 'level' in df.columns else 'Level'
    filtered_df = df[df[level_col] == target_lvl]

# 防呆：如果該等級選不到 3 個字，就退回使用全部資料庫
if len(filtered_df) < 3:
    filtered_df = df

# 動態產生多變、生動且符合文法的句型
def generate_new_challenge(pool_df):
    sample_rows = pool_df.sample(n=min(3, len(pool_df)))
    words_list = sample_rows['word'].tolist()
    trans_list = sample_rows['trans'].tolist()
    
    w1, w2, w3 = words_list[0], words_list[1], words_list[2]
    t1, t2, t3 = trans_list[0], trans_list[1], trans_list[2]
    
    # 設計多種不同文法與情境的樣板，確保千變萬化
    templates = [
        (
            f"When you feel like {w1}, remember to look at {w2} and find a way to {w3}.",
            f"當你感覺到{t1}({w1})時，記得看看{t2}({w2})並找方法去{t3}({w3})。"
        ),
        (
            f"Why did he choose {w1} instead of {w2} when he tried to {w3}?",
            f"當他嘗試去{t3}({w3})時，為什麼他會選擇{t1}({w1})而不是{t2}({w2})？"
        ),
        (
            f"If we want to understand {w1}, we must first explore {w2} and learn how to {w3}.",
            f"如果我们想了解{t1}({w1})，我們必須先探索{t2}({w2})並學習如何{t3}({w3})。"
        ),
        (
            f"She used {w1} to describe {w2}, which helped everyone {w3}.",
            f"她用{t1}({w1})來描述{t2}({w2})，這幫助每個人都去{t3}({w3})。"
        ),
        (
            f"Never ignore {w1} or {w2} if you really want to {w3} successfully.",
            f"如果你真的想成功地{t3}({w3})，千萬不要忽視{t1}({w1})或{t2}({w2})。"
        ),
        (
            f"The teacher explained how {w1} connects with {w2} so that we could {w3}.",
            f"老師解釋了{t1}({w1})是如何與{t2}({w2})連結的，以便我們能夠{t3}({w3})。"
        )
    ]
    
    chosen_eng, chosen_chi = random.choice(templates)
    
    st.session_state.challenge = sample_rows
    st.session_state.raw_eng_sentence = chosen_eng
    st.session_state.raw_chi_sentence = chosen_chi

# 如果切換了等級，或者第一次進來，或手動按換一題，就重新出題
if ('current_selected_level' not in st.session_state 
    or st.session_state.current_selected_level != selected_level
    or 'challenge' not in st.session_state):
    st.session_state.current_selected_level = selected_level
    generate_new_challenge(filtered_df)

# 取得目前的目標單字清單與相關資訊
words = st.session_state.challenge['word'].tolist()
trans_list = st.session_state.challenge['trans'].tolist()

# 檢查 CSV 中是否有 kk 音標欄位
kk_col = None
for col in ['kk', 'phonetic', 'KK', '音標']:
    if col in st.session_state.challenge.columns:
        kk_col = col
        break

level_col = 'level' if 'level' in df.columns else 'Level'

# 頂部區塊：寬鬆的標題與「換一題」按鈕
col_top1, col_top2 = st.columns([5, 1])
with col_top1:
    st.subheader(f"🎯 今日目標單字（來自 {selected_level}）：")
with col_top2:
    if st.button("🔄 換一題", key="top_refresh_btn"):
        generate_new_challenge(filtered_df)
        st.rerun()

for idx, row in st.session_state.challenge.iterrows():
    col_audio, col_word = st.columns([2, 5])
    word_str = str(row['word'])
    trans_str = str(row['trans'])
    lvl_val = row[level_col]
    
    kk_str = ""
    if kk_col and pd.notna(row[kk_col]):
        kk_str = f" [{row[kk_col]}]"
    
    with col_audio:
        if st.button(f"🔊 讀音: {word_str}", key=f"word_btn_{idx}"):
            tts = gTTS(text=word_str, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, autoplay=True)
            
    with col_word:
        st.markdown(f"### {word_str}{kk_str} ({trans_str}) <span style='font-size: 20px; color: #888888;'>(L{lvl_val})</span>", unsafe_allow_html=True)

st.divider()

# 處理助教示範句的紅字標註
eng_sentence = st.session_state.raw_eng_sentence
chi_sentence = st.session_state.raw_chi_sentence

colored_sentence = eng_sentence
for w in words:
    import re
    pattern = re.compile(r'\b' + re.escape(str(w)) + r'\b', re.IGNORECASE)
    colored_sentence = pattern.sub(f"<span class='red-word'>{w}</span>", colored_sentence)

vocab_notes = "、".join([f"{trans} ({w})" for w, trans in zip(words, trans_list)])
formatted_chi_sentence = f"{chi_sentence}  【本句核心單字：{vocab_notes}】"

st.subheader("💡 助教示範句：")

speed_option = st.selectbox(
    "🐢 選擇語音播放速度（專為慢速跟讀設計）：",
    [
        "正常速", 
        "慢速 (gTTS 內建慢速)", 
        "超慢速 (重複單字拉長練習)", 
        "極慢速 (每個單字拆開慢慢念)"
    ],
    key="audio_speed_select"
)

if st.button("🔊 播放示範句", key="play_demo_sentence"):
    is_slow = False
    text_to_speak = eng_sentence
    
    if speed_option == "正常速":
        is_slow = False
    elif speed_option == "慢速 (gTTS 內建慢速)":
        is_slow = True
    elif speed_option == "超慢速 (重複單字拉長練習)":
        is_slow = True
        text_to_speak = f"{eng_sentence} ...... {eng_sentence}"
    elif speed_option == "極慢速 (每個單字拆開慢慢念)":
        is_slow = True
        words_spaced = " ... ".join(words)
        text_to_speak = f"Key words: {words_spaced} ...... Sentence: {eng_sentence}"

    tts = gTTS(text=text_to_speak, lang='en', slow=is_slow)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)

st.markdown(f"### {colored_sentence}", unsafe_allow_html=True)
st.markdown(f"*(中文：{formatted_chi_sentence})*", unsafe_allow_html=True)

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
    if st.button("🔄 換一題", key="refresh_challenge_bottom"):
        generate_new_challenge(filtered_df)
        st.rerun()
