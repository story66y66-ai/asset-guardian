import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import urllib.parse

# 設定頁面為寬螢幕模式
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    
    /* 放大一般 YouTube 網址與輸入框的文字與高度 */
    .stTextInput input { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 50px !important;
    }
    
    /* 放大逐句練習輸入框的文字與高度 */
    div[data-baseweb="input"] input {
        font-size: 22px !important;
        color: #000000 !important;
        font-weight: bold !important;
        height: 50px !important;
    }
    
    /* 專門放大第一到第五冊/頁名稱修改的輸入框文字與高度 */
    div[data-testid="stExpander"] input {
        font-size: 24px !important;
        color: #000000 !important;
        font-weight: bold !important;
        height: 55px !important;
    }

    /* 放大上方分頁籤 (Tabs) 的文字大小與寬度 */
    button[data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: bold !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
    
    /* 專門強力放大藍色框框內的翻書頁面按鈕與曲目按鈕字體 */
    div.stButton > button { 
        font-size: 20px !important; 
        padding: 12px 20px !important; 
        font-weight: bold !important;
    }

    /* 針對翻書頁面按鈕（多行按鈕）特別加大行距與字體 */
    div[data-testid="column"] div.stButton > button {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
    .stTextArea textarea { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 580px !important;
        resize: vertical !important; 
    }
    
    /* 放大逐句練習區的原句文字大小（英文與中文） */
    .sentence-display {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        line-height: 1.6 !important;
    }

    /* 放大 Expander 標題與內部文字（針對 CSV 下載區塊） */
    div[data-testid="stExpander"] summary span {
        font-size: 22px !important;
        font-weight: bold !important;
    }

    .yt-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #28a745;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 20px;
        border: none;
        width: 100%;
    }
    .yt-button:hover {
        background-color: #218838;
        color: white !important;
    }
    .notebook-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #4285F4;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 20px;
        border: none;
        width: 100%;
    }
    .notebook-button:hover {
        background-color: #3367D6;
        color: white !important;
    }
    .translate-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #1a73e8;
        color: white !important;
        padding: 6px 14px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
        border: none;
        width: 100%;
    }
    .translate-button:hover {
        background-color: #1557b0;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

# 最上方的兩個專屬按鈕
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    yt_url_top = "https://www.youtube.com/@%E8%8B%B1%E8%AA%9E%E5%A4%A9%E5%A4%A9%E5%AD%B8/shorts?view=0&sort=p&flow=grid"
    st.markdown(f'<a href="{yt_url_top}" target="_blank" class="yt-button">🔥 英語天天學熱門 Shorts 任意門</a>', unsafe_allow_html=True)
with col_btn2:
    notebook_url = "https://notebooklm.google.com/"
    st.markdown(f'<a href="{notebook_url}" target="_blank" class="notebook-button">✨ 澄玄的隨身英文秘書任意門</a>', unsafe_allow_html=True)

st.write("")

# 讀取單字資料庫（包含 level 與通用庫）
@st.cache_data
def load_and_merge_data():
    # 讀取所有 level 檔案
    all_files = glob.glob("words_level*.csv")
    df_list = []
    
    # 加入通用庫
    universal_file = "words_universal_通用庫.csv"
    if os.path.exists(universal_file):
        all_files.append(universal_file)
        
    if all_files:
        for filename in sorted(list(set(all_files))): # set 去重
            try:
                temp_df = pd.read_csv(filename)
                df_list.append(temp_df)
            except Exception:
                pass
    
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
    else:
        try:
            combined_df = pd.read_csv("words.csv")
        except Exception:
            combined_df = pd.DataFrame(columns=["word", "trans", "kk", "level"])
            
    if "word" in combined_df.columns:
        # 當單字重複時，保留最後出現的（這樣如果 level 檔有定義，會覆蓋通用庫）
        combined_df = combined_df.drop_duplicates(subset=["word"], keep='last')
    return combined_df

df = load_and_merge_data()

word_dict = {}
if not df.empty and "word" in df.columns:
    for _, row in df.iterrows():
        w_str = str(row['word']).strip().lower()
        trans_str = str(row['trans']) if 'trans' in df.columns and pd.notna(row['trans']) else ""
        kk_str = str(row['kk']) if 'kk' in df.columns and pd.notna(row['kk']) else ""
        word_dict[w_str] = {"trans": trans_str, "kk": kk_str}

# (其餘程式碼保持不變，略...)
# [因為長度限制，這裡省略中間重複的顯示邏輯與 UI 設定，請保留您原本程式中後續的部分]
