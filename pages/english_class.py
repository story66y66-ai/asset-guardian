import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import glob
import os

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

# 自動搜尋並合併所有 level 檔案的智慧讀取機制
@st.cache_data
def load_data():
    # 尋找所有符合 words_level*.csv 的檔案
    level_files = glob.glob("words_level*.csv")
    
    df_list = []
    for file in level_files:
        try:
            temp_df = pd.read_csv(file)
            if not temp_df.empty:
                df_list.append(temp_df)
        except Exception:
            pass
            
    if df_list:
        # 把所有 level 的檔案全部上下疊起來合併
        df = pd.concat(df_list, ignore_index=True)
    else:
        # 如果找不到任何 level 檔，才去讀 words.csv 備用
        try:
            df = pd.read_csv("words.csv")
        except Exception:
            df = pd.DataFrame(columns=["word", "trans", "kk", "level"])

    # 自動過濾重複的單字，並重新排序編號
    if "word" in df.columns:
        df = df.drop_duplicates(subset=["word"]).reset_index(drop=True)
        
    return df

df = load_data()

# 初始化 Session State，用來同步單字
if 'selected_word' not in st.session_state:
    if not df.empty:
        st.session_state.selected_word = df['word'].iloc[0]
    else:
        st.session_state.selected_word = ""

# 1. 顯示表格
st.subheader("點選表格中的單字：")
if not df.empty:
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
else:
    st.warning("目前找不到任何單字檔案，請確認 CSV 檔案是否已上傳。")
