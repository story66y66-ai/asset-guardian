import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# 強制調整整體字體與側邊欄位字體
st.markdown("""
    <style>
    /* 放大左側選單欄位的字體 */
    [data-testid="stSidebar"] {
        font-size: 28px !important;
    }
    /* 放大選單內部的選項文字 */
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a {
        font-size: 28px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院")

# 讀取資料並自動過濾重複單字
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")
    if "word" in df.columns:
        df = df.drop_duplicates(subset=["word"]).reset_index(drop=True)
    return df

df = load_data()

# 初始化 Session State，用來同步單字
if 'selected_word' not in st.session_state:
    st.session_state.selected_word = df['word'].iloc[0]

# 1. 顯示表格
st.subheader("點選表格中的單字：")
event = st.dataframe(
    df[['word', 'trans', 'kk', 'level']],
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# 如果使用者點了表格，自動同步更新選單變數
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    st.session_state.selected_word = df.iloc[selected_index]['word']

# 2. 同步的選單
word_list = df['word'].tolist()
# 確保選取的單字在列表中，避免索引超出範圍
if st.session_state.selected_word not in word_list:
    st.session_state.selected_word = word_list[0]

selected_word = st.selectbox(
    "目前選取的單字：",
    word_list,
    index=word_list.index(st.session_state.selected_word)
)

# 更新 Session State
st.session_state.selected_word = selected_word

# 3. 自動發音
if selected_word:
    tts = gTTS(text=selected_word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)
