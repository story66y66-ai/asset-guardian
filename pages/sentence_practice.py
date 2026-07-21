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

# 隨機挑選 3 個單字（如果按重新整理或按鈕可以換一批）
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

# 設定 Gemini API Key (可以直接把你的金鑰字串填在下面雙引號中，或者放空使用備用句型)
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

def generate_dynamic_sentence(w1, w2, w3):
    if not api_key:
        # 如果沒有設定 API Key 的防呆句型
        return (
            f"We tried to check {w1[0]}, handle {w2[0]}, and focus on {w3[0]} today.",
            f"我們今天試著檢查 {w1[0]} ({w1[1]})、處理 {w2[0]} ({w2[1]})，並且專注於 {w3[0]} ({w3[1]})。"
        )
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an English teacher. Please write ONE natural, creative, and coherent English sentence that incorporates these three English words: "{w1[0]}", "{w2[0]}", and "{w3[0]}".
        Do not use a generic template. Make it sound like a real, context-rich scenario.
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
        return (
            f"Faced with {w1[0]}, we must carefully manage {w2[0]} and understand {w3[0]}.",
            f"面對 {w1[0]} ({w1[1]})，我們必須小心處理 {w2[0]} ({w2[1]}) 並理解 {w3[0]} ({w3[1]})。"
        )

# 取得動態例句
w_eng, w_chi = generate_dynamic_sentence(target_words[0], target_words[1], target_words[2])

# 將目標單字上色突顯
display_eng = w_eng
for w, _, _ in target_words:
    display_eng = display_eng.replace(w, f"<span style='color:red; font-weight:bold;'>{w}</span>")

st.markdown("### 💡 助教示範句：")
if st.button("🔊 播放示範句"):
    tts_text = w_eng
    tts = gTTS(text=tts_text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format='audio/mp3')

st.markdown(f"> **{display_eng}**")
st.markdown(f"> *(中文：{w_chi})*")

st.markdown("---")

# 恢復底下你原本的學生造句輸入區與互動區
st.markdown("### ✍️ 請輸入您的句子：")
user_sentence = st.text_input("在這裡輸入包含目標單字的英文句子：", key="user_input")

if st.button("送出批改 / 檢查"):
    if user_sentence:
        st.success("句子已收到！做得很好，請繼續保持練習！")
    else:
        st.warning("請先輸入您的英文句子再送出喔！")

if st.button("🔄 換一組新單字"):
    if "selected_words" in st.session_state:
        del st.session_state.selected_words
    st.rerun()
