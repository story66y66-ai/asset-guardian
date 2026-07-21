import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import os
import google.generativeai as genai

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
    # 取得選定的數字等級 (例如 "Level 1" 轉成數字 1)
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

# 設定 Gemini API Key
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

@st.cache_data(show_spinner=False)
def get_ai_sentence(w0, w1, w2):
    if not api_key:
        return f"We need to consider {w0}, handle {w1}, and focus on {w2}."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an English teacher. Write ONE natural, coherent English sentence that naturally incorporates these three words: "{w0}", "{w1}", and "{w2}".
        Do not use rigid formulas. Make it sound like a real, context-rich scenario.
        Output ONLY the English sentence. No extra text or labels.
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        if not text:
            raise Exception("empty")
        return text
    except Exception:
        return f"We need to consider {w0}, handle {w1}, and focus on {w2}."

# 取得動態產生的英文示範句
raw_sentence = get_ai_sentence(words[0], words[1], words[2])

# 🎯 英文示範句：目標單字帶紅色
red_word_0 = f"<span class='red-word'>{words[0]}</span>"
red_word_1 = f"<span class='red-word'>{words[1]}</span>"
red_word_2 = f"<span class='red-word'>{words[2]}</span>"

colored_sentence = raw_sentence
colored_sentence = colored_sentence.replace(words[0], red_word_0)
colored_sentence = colored_sentence.replace(words[1], red_word_1)
colored_sentence = colored_sentence.replace(words[2], red_word_2)

st.subheader("💡 助教示範句：")
if st.button("🔊 播放示範句"):
    tts = gTTS(text=raw_sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)

# 顯示紅字英文句
st.markdown(f"### {colored_sentence}", unsafe_allow_html=True)

# 🎯 中文示範句：採用固定優雅句型，確保中英文單字完美對應與加粗
zh_word_0 = f"<b>{words[0]}</b> ({trans_list[0]})"
zh_word_1 = f"<b>{words[1]}</b> ({trans_list[1]})"
zh_word_2 = f"<b>{words[2]}</b> ({trans_list[2]})"

st.markdown(f"*(中文：我們今天需要特別注意 {zh_word_0}，妥善處理 {zh_word_1}，並深入理解 {zh_word_2}。)*", unsafe_allow_html=True)

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
