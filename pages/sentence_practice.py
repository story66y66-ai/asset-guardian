import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import os
import google.generativeai as genai

# 設定 Gemini API (自動抓取 Streamlit 的 Secrets 或環境變數)
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    elif "GOOGLE_API_KEY" in os.environ:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except Exception:
    pass

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

    # 🎯 呼叫 AI 針對這三個新單字量身打造最道地的造句
    words_list = st.session_state.challenge['word'].tolist()
    
    prompt = f"""
    You are an English teaching assistant. I have three English words: {words_list[0]}, {words_list[1]}, {words_list[2]}.
    Please create ONE natural, conversational English sentence that includes all three words.
    Also provide a natural, colloquial Traditional Chinese (繁體中文) translation of this sentence.
    
    Return the result strictly in this format without extra markdown code blocks:
    ENGLISH: [The English sentence]
    CHINESE: [The Traditional Chinese translation]
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n')
        eng_line = ""
        chi_line = ""
        for line in lines:
            if line.startswith("ENGLISH:"):
                eng_line = line.replace("ENGLISH:", "").strip()
            elif line.startswith("CHINESE:"):
                chi_line = line.replace("CHINESE:", "").strip()
        
        if not eng_line or not chi_line:
            raise Exception("Format error")
            
        st.session_state.ai_eng = eng_line
        st.session_state.ai_chi = chi_line
    except Exception:
        # 萬一 API 沒設定或連線失敗的備用方案
        st.session_state.ai_eng = f"Please use {words_list[0]}, {words_list[1]}, and {words_list[2]} correctly in context."
        st.session_state.ai_chi = f"請在語境中正確使用 {words_list[0]}、{words_list[1]} 和 {words_list[2]}。"

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

words = st.session_state.challenge['word'].tolist()
trans_list = st.session_state.challenge['trans'].tolist()

# 取得 AI 生成的句子
raw_sentence = st.session_state.get('ai_eng', f"Practice with {words[0]}, {words[1]}, and {words[2]}.")
ai_chinese = st.session_state.get('ai_chi', "請練習造句。")

# 將英文句子中的目標單字加上紅字高亮
colored_sentence = raw_sentence
for w in words:
    colored_sentence = colored_sentence.replace(w, f"<span class='red-word'>{w}</span>")

st.subheader("💡 助教示範句：")
if st.button("🔊 播放示範句"):
    tts = gTTS(text=raw_sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)

# 顯示紅字英文句
st.markdown(f"### {colored_sentence}", unsafe_allow_html=True)

# 將中文句子中的目標單字加上粗體與原中文翻譯對照
formatted_chinese = ai_chinese
for i, w in enumerate(words):
    target_str = f"{w}"
    replacement = f"<b>{w}</b> ({trans_list[i]})"
    formatted_chinese = formatted_chinese.replace(target_str, replacement)

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
