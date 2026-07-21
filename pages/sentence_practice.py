import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import random
import base64

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
    
    /* 自訂超大、像真按鈕一樣的語音觸發器 */
    .sound-btn {
        background-color: #ff4b4b;
        color: white;
        padding: 10px 20px;
        font-size: 22px;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: 0.2s;
    }
    .sound-btn:hover {
        background-color: #ff2b2b;
        transform: scale(1.05);
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

if len(filtered_df) < 3:
    filtered_df = df

# 💡 口語化英文好句庫
CONV_SENTENCE_POOL = [
    (
        "Could you please help me check if this order is ready?",
        "可以請幫忙 (help) 我確認 (check) 一下這筆訂單 (order) 準備好了嗎？",
        ["order", "help", "check"]
    ),
    (
        "I really need to focus on my study plan for this semester.",
        "我真的需要專注於 (focus) 我這學期的讀書計畫 (plan) 與學習 (study) 上。",
        ["focus", "study", "plan"]
    ),
    (
        "Let us take a short break before we start the next task.",
        "我們在開始 (start) 下一個任務 (task) 之前，先休息 (break) 一下吧。",
        ["break", "start", "task"]
    ),
    (
        "She always brings a positive energy to everyone around her.",
        "她總是為身邊周圍 (around) 的每個人 (everyone) 帶來積極的正能量 (energy)。",
        ["energy", "everyone", "around"]
    ),
    (
        "Finding a good balance between work and life is truly important.",
        "在工作 (work) 和生活 (life) 之間找到良好的平衡 (balance) 真得很重要。",
        ["balance", "work", "life"]
    ),
    (
        "Do you remember where we parked our car this morning?",
        "妳記得 (remember) 我們今天早晨 (morning) 把車子 (car) 停在哪裡嗎？",
        ["remember", "car", "morning"]
    )
]

# 當切換等級、初次載入、或按重新抽籤時，隨機選一句口語好句
if ('chosen_conv_item' not in st.session_state 
    or st.session_state.get('need_refresh', False)):
    
    chosen_sentence, chosen_chinese, target_words = random.choice(CONV_SENTENCE_POOL)
    
    sub_df_list = []
    for tw in target_words:
        match_row = df[df['word'].str.lower() == tw.lower()]
        if not match_row.empty:
            sub_df_list.append(match_row.iloc[0])
        else:
            sub_df_list.append(df.sample(n=1).iloc[0])
            
    st.session_state.challenge = pd.DataFrame(sub_df_list)
    st.session_state.raw_eng_sentence = chosen_sentence
    st.session_state.raw_chi_sentence = chosen_chinese
    st.session_state.need_refresh = False

# 取得目前的目標單字清單
words = st.session_state.challenge['word'].tolist()
trans_list = st.session_state.challenge['trans'].tolist()

# 頂部區塊：目標單字與「換一題」按鈕並排
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.subheader("🎯 今日目標單字（來自實用口語句）：")
with col_top2:
    if st.button("🔄 換一題", key="top_refresh_btn"):
        st.session_state.need_refresh = True
        st.rerun()

for idx, row in st.session_state.challenge.iterrows():
    # 欄位分配：左邊放獨立發音按鈕，右邊放單字與中文
    col_audio, col_word = st.columns([1.5, 3.5])
    word_str = str(row['word'])
    
    # 製作語音的 Base64 編碼
    tts = gTTS(text=word_str, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_bytes = fp.getvalue()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    
    with col_audio:
        # 使用 HTML 語音物件，點擊按鈕直接呼叫 play()，絕對不重新整理、不換題目！
        audio_html = f"""
            <audio id="audio_{idx}" src="data:audio/mp3;base64,{audio_base64}"></audio>
            <button class="sound-btn" onclick="document.getElementById('audio_{idx}').play()">
                🔊 讀音
            </button>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        
    with col_word:
        st.markdown(f"### {word_str}  ({row['trans']}) <span style='font-size: 20px; color: #888888;'>(L{row['level']})</span>", unsafe_allow_html=True)

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
        st.session_state.need_refresh = True
        st.rerun()
