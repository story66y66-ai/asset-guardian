import streamlit as st
from gtts import gTTS
import io
import re

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    .stTextArea textarea { font-size: 24px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 20px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

st.subheader("✍️ 請在下方文字框輸入或貼上你想練習的文字／句子：")

# 初始化 session_state
if "my_text_input" not in st.session_state:
    st.session_state.my_text_input = "I can do all things through Christ who strengthens me."

# 使用者自訂文字輸入框（不直接用 key 綁定衝突的狀態）
user_input_text = st.text_area(
    "輸入文字或歌詞：",
    value=st.session_state.my_text_input,
    height=120
)

# 同步更新變數
st.session_state.my_text_input = user_input_text

col1, col2 = st.columns([1, 4])
with col1:
    play_btn = st.button("🔊 播放整段發音")
with col2:
    clear_btn = st.button("🗑️ 清空文字框")

if clear_btn:
    st.session_state.my_text_input = ""
    st.rerun()

if play_btn and user_input_text.strip():
    try:
        tts = gTTS(text=user_input_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, autoplay=True)
    except Exception as e:
        st.error(f"語音生成發生錯誤：{e}")

st.divider()

# 拆解單字與互動區塊
if user_input_text.strip():
    st.subheader("🔍 句子單字解析與個別發音：")
    
    words_in_text = re.findall(r'\b[A-Za-z]+\b', user_input_text)
    unique_words = sorted(list(set(words_in_text)), key=lambda x: words_in_text.index(x))
    
    if unique_words:
        st.markdown(f"**偵測到以下英文單字（共 {len(unique_words)} 個）：**")
        
        for i, w in enumerate(unique_words):
            cols = st.columns([2, 1, 3])
            with cols[0]:
                st.markdown(f"🔹 **{w}**")
            with cols[1]:
                if st.button(f"🔊 聽發音", key=f"word_audio_{i}_{w}"):
                    w_tts = gTTS(text=w, lang='en')
                    w_fp = io.BytesIO()
                    w_tts.write_to_fp(w_fp)
                    st.audio(w_fp, autoplay=True)
            with cols[2]:
                st.write("")
    else:
        st.info("請輸入包含英文的句子以便拆解單字。")
else:
    st.warning("目前文字框是空的，請輸入想練習的英文句子！")
