import streamlit as st
import random
from gtts import gTTS
import io

st.set_page_config(page_title="澄玄的農場", layout="wide")
st.sidebar.title("🌱 澄玄的農場導航")

# 這裡擴充妳的 50 個單字書庫 (請持續補完)
word_data = [
    {"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"},
    {"word": "Banana", "trans": "香蕉", "kk": "/bəˈnæn.ə/"},
    {"word": "Cat", "trans": "貓", "kk": "/kæt/"},
    {"word": "Dog", "trans": "狗", "kk": "/dɔːɡ/"},
    {"word": "Elephant", "trans": "大象", "kk": "/ˈel.ɪ.fənt/"}
    # 妳可以在這裡繼續添加剩下的 45 個單字，格式保持一致即可
]

nav_options = {
    "訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡",
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", "學習農場": "📚", "生活農場": "🏠"
}

selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 區域邏輯
if selection == "訓練農場":
    st.header("🏗️ 訓練農場 (學習區)")
    if 'current_word' not in st.session_state: st.session_state.current_word = random.choice(word_data)
    st.markdown(f"### 英文：{st.session_state.current_word['word']}")
    st.write(f"**KK 音標：** {st.session_state.current_word['kk']} | **中文：** {st.session_state.current_word['trans']}")
    if st.button("🔊 聽發音"):
        tts = gTTS(text=st.session_state.current_word['word'], lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    if st.button("換一個單字學習"): st.session_state.current_word = random.choice(word_data); st.rerun()

elif selection == "測驗中心":
    st.header("🎮 測驗中心")
    sub_nav = st.radio("選擇測驗等級：", ["等級 1：中文輸入挑戰", "等級 2：拼字挑戰"], horizontal=True)
    
    if sub_nav == "等級 1：中文輸入挑戰":
        if 'q1' not in st.session_state: st.session_state.q1 = random.choice(word_data)
        st.write(f"請輸入 **{st.session_state.q1['word']}** 的中文：")
        user_input = st.text_input("輸入中文：", key="i1")
        if st.button("確認答案"):
            if user_input == st.session_state.q1['trans']:
                st.success("✅ 答對了！"); st.session_state.q1 = random.choice(word_data); st.rerun()
            else: st.error("❌ 答錯了，再試一次！")

    elif sub_nav == "等級 2：拼字挑戰":
        if 'q2' not in st.session_state: st.session_state.q2 = random.choice(word_data)
        st.write(f"題目：請拼出「{st.session_state.q2['trans']}」的英文單字")
        user_ans = st.text_input("輸入拼寫結果：", key="i2")
        if st.button("確認拼寫"):
            if user_ans.lower() == st.session_state.q2['word'].lower():
                st.success("✅ 拼寫正確！"); st.session_state.q2 = random.choice(word_data); st.rerun()
            else: st.error("❌ 錯了，再試一次！")

elif selection == "進化中心":
    st.header("🏗️ 農場進化紀錄中心")
    with st.expander("核心資源：查看完整程式碼"):
        with open("streamlit_app.py", "r", encoding="utf-8") as f: st.code(f.read(), language="python")

else: st.write(f"歡迎來到 {selection}，這裡正在建設中。")
