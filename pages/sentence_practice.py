import streamlit as st
import random
import os
import google.generativeai as genai
from gtts import gTTS
import io

# 頁面標題
st.title("澄玄大學 - 造句實戰室")

# 模擬單字資料庫
VOCAB_LIST = [
    ("adventure", "冒險", "L3"), ("scratch", "抓", "L2"), ("demolish", "拆除", "L2"),
    ("husband", "丈夫", "L1"), ("deport", "驅逐", "L2"), ("deliberation", "深思熟慮", "L2"),
    ("insolent", "傲慢的", "L2"), ("deep", "深的", "L1"), ("indian", "印第安人", "L2"),
    ("perceptual", "知覺的", "L2"), ("product", "產品", "L3"), ("disappointment", "失望", "L3"),
    ("parch", "烤乾", "L2"), ("beach", "海灘", "L2"), ("city", "城市", "L2"),
    ("iodine", "碘", "L2"), ("gig", "輕便馬車", "L2"), ("angle", "角/角度", "L3"),
    ("fearless", "大膽的", "L2"), ("craven", "懦弱的", "L2"), ("interpretation", "解釋", "L2")
]

# 選擇難度
level_filter = st.selectbox("請選擇單字等級 (Level) :", ["全部等級 (隨機)"])

# 隨機挑選 3 個單字
if "selected_words" not in st.session_state:
    st.session_state.selected_words = random.sample(VOCAB_LIST, 3)

target_words = st.session_state.selected_words

st.markdown("### 🎯 今日目標單字：")
cols = st.columns(3)
for i, (word, meaning, lvl) in enumerate(target_words):
    with cols[i]:
        st.button(f"🔊 {word}", key=f"btn_{word}")
        st.markdown(f"**{word} ({meaning})** `({lvl})`")

st.markdown("---")

# 設定 Gemini API Key (請確保你有設定對應的 Secret 或環境變數)
# 這裡會嘗試讀取 Streamlit secrets，若無則看環境變數
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

def generate_dynamic_sentence(w1, w2, w3):
    if not api_key:
        # 如果沒有 API Key 的備用防呆句型
        return (
            f"We tried to check {w1[0]}, handle {w2[0]}, and focus on {w3[0]} today.",
            f"我們今天試著檢查 {w1[0]} ({w1[1]})、處理 {w2[0]} ({w2[1]})，並且專注於 {w3[0]} ({w3[1]})。"
        )
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an English teacher. Please write ONE natural, creative, and coherent English sentence that incorporates these three English words: "{w1[0]}", "{w2[0]}", and "{w3[0]}".
        Do not use a generic template like "We tried to check X, handle Y, and focus on Z". Make it sound like a real, context-rich scenario.
        Also provide a Traditional Chinese (繁體中文) translation for the sentence.
        
        Output format strictly as:
        ENGLISH: [Your sentence here]
        CHINESE: [Your translation here]
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        eng_line = ""
        chi_line = ""
        for line in text.split('\n'):
            if line.startswith("ENGLISH:"):
                eng_line = line.replace("ENGLISH:", "").strip()
            elif line.startswith("CHINESE:"):
                chi_line = line.replace("CHINESE:", "").strip()
                
        if not eng_line or not chi_line:
            raise Exception("Parsing failed")
            
        return eng_line, chi_line
    except Exception as e:
        # 發生錯誤時的備用方案
        return (
            f"Faced with {w1[0]}, we must carefully manage {w2[0]} and understand {w3[0]}.",
            f"面對 {w1[0]} ({w1[1]})，我們必須小心處理 {w2[0]} ({w2[1]}) 並理解 {w3[0]} ({w3[1]})。"
        )

# 取得動態例句
w_eng, w_chi = generate_dynamic_sentence(target_words[0], target_words[1], target_words[2])

# 將目標單字上色突顯
for w, _, _ in target_words:
    w_eng = w_eng.replace(w, f"<span style='color:red; font-weight:bold;'>{w}</span>")

st.markdown("### 💡 助教示範句：")
if st.button("🔊 播放示範句"):
    tts_text = w_eng.replace("<span>", "").replace("</span>", "").replace("style='color:red; font-weight:bold;'", "")
    tts = gTTS(text=tts_text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format='audio/mp3')

st.markdown(f"> **{w_eng}**")
st.markdown(f"> *(中文：{w_chi})*")
