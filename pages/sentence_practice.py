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

# 依選擇過濾資料庫
if selected_level == "全部等級 (隨機)":
    filtered_df = df
else:
    target_lvl = int(selected_level.split(" ")[1])
    filtered_df = df[df['level'] == target_lvl]

# 防呆：如果該等級選不到 3 個字，就退回使用全部資料庫
if len(filtered_df) < 3:
    filtered_df = df

# 動態產生題目函式：直接從當前過濾後的等級隨機抽 3 個字，並自動組成造句練習
def generate_new_challenge(pool_df):
    # 從當前等級隨機抽 3 個單字列
    sample_rows = pool_df.sample(n=min(3, len(pool_df)))
    words_list = sample_rows['word'].tolist()
    
    # 自動組合出一句練習句與中文提示
    chosen_sentence = f"Please use {' , '.join(words_list)} to make a meaningful sentence."
    chosen_chinese = f"請運用以下單字造句：{'、'.join(words_list)}"
    
    st.session_state.challenge = sample_rows
    st.session_state.raw_eng_sentence = chosen_sentence
    st.session_state.raw_chi_sentence = chosen_chinese

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

# 頂部區塊：目標單字與「換一題」按鈕並排
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.subheader(f"🎯 今日目標單字（來自 {selected_level}）：")
with col_top2:
    if st.button("🔄 換一題", key="top_refresh_btn"):
        generate_new_challenge(filtered_df)
        st.rerun()

for idx, row in st.session_state.challenge.iterrows():
    col_audio, col_word = st.columns([1.5, 3.5])
    word_str = str(row['word'])
    trans_str = str(row['trans'])
    
    # 取得 KK 音標
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
        st.markdown(f"### {word_str}{kk_str} ({trans_str}) <span style='font-size: 20px; color: #888888;'>(L{row['level']})</span>", unsafe_allow_html=True)

st.divider()

# 處理助教示範句的紅字標註
eng_sentence = st.session_state.raw_eng_sentence
chi_sentence = st.session_state.raw_chi_sentence

colored_sentence = eng_sentence
for w in words:
    import re
    pattern = re.compile(re.escape(w), re.IGNORECASE)
    colored_sentence = pattern.sub(f"<span class='red-word'>{w}</span>", colored_sentence)

# 中文翻譯帶括號與總結
vocab_notes = "、".join([f"{w} ({trans})" for w, trans in zip(words, trans_list)])
formatted_chi_sentence = f"{chi_sentence}  【本句核心單字：{vocab_notes}】"

st.subheader("💡 助教示範句：")

# 🎛️ 語速選擇選單
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

# 顯示紅字英文口語句
st.markdown(f"### {colored_sentence}", unsafe_allow_html=True)
# 顯示帶有括號與後方補充的中文意思
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
