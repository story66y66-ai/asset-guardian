import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("🎲 隨機挑戰 - 語言學院")

# 讀取資料
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 核心差異：在此處進行隨機化處理，不影響原本的檔案
# 使用 random_state 固定隨機結果，這樣每次重整不會跳掉
random_df = df.sample(frac=1, random_state=42).reset_index(drop=True)

st.subheader("隨機單字清單 (非字母順序)")
event = st.dataframe(
    random_df[['word', 'trans', 'kk', 'level']], 
    use_container_width=True, 
    hide_index=True, 
    on_select="rerun",
    selection_mode="single-row"
)

# 互動邏輯同上
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    st.session_state.random_selected = random_df.iloc[selected_index]['word']

if 'random_selected' not in st.session_state:
    st.session_state.random_selected = random_df['word'].iloc[0]

selected_word = st.selectbox(
    "目前選取的隨機單字：", 
    random_df['word'].tolist(), 
    index=random_df['word'].tolist().index(st.session_state.random_selected)
)

st.session_state.random_selected = selected_word

if selected_word:
    tts = gTTS(text=selected_word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3', autoplay=True)
