import streamlit as st
import pandas as pd
import glob
import os
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

# 背景自動合併與讀取資料函式
@st.cache_data
def load_and_merge_data():
    # 1. 自動搜尋所有 level 檔案
    all_files = glob.glob("words_level*.csv")
    
    df_list = []
    if all_files:
        for filename in sorted(all_files):
            try:
                temp_df = pd.read_csv(filename)
                df_list.append(temp_df)
            except Exception:
                pass
                
    if df_list:
        # 合併所有 level 檔案
        combined_df = pd.concat(df_list, ignore_index=True)
    else:
        # 如果找不到 level 檔案，就退回直接讀取 words.csv
        try:
            combined_df = pd.read_csv("words.csv")
        except Exception:
            combined_df = pd.DataFrame(columns=["word", "trans", "kk", "level"])

    # 2. 自動過濾重複的單字
    if "word" in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=["word"])
    
    # 3. 將 level 轉換為數字並由小到大排序
    if "level" in combined_df.columns:
        combined_df["level"] = pd.to_numeric(combined_df["level"], errors="coerce")
        combined_df = combined_df.sort_values(by="level", ascending=True)
        
    combined_df = combined_df.reset_index(drop=True)
    return combined_df

df = load_and_merge_data()

# 初始化 Session State，用來同步單字
if 'selected_word' not in st.session_state:
    st.session_state.selected_word = df['word'].iloc[0] if not df.empty else ""

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
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
