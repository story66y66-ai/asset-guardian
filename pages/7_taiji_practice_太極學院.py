import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import urllib.parse
import csv
import streamlit.components.v1 as components

# 設定頁面為寬螢幕模式
st.set_page_config(layout="wide")

# 【澄玄原有的 CSS 排版設定，完全保留】
st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .stTextInput input { font-size: 22px !important; color: #000000 !important; font-weight: bold !important; height: 50px !important; }
    div[data-baseweb="input"] input { font-size: 22px !important; color: #000000 !important; font-weight: bold !important; height: 50px !important; }
    div[data-testid="stExpander"] input { font-size: 24px !important; color: #000000 !important; font-weight: bold !important; height: 55px !important; }
    button[data-baseweb="tab"] { font-size: 22px !important; font-weight: bold !important; padding-top: 12px !important; padding-bottom: 12px !important; padding-left: 20px !important; padding-right: 20px !important; }
    div.stButton > button { font-size: 20px !important; padding: 12px 20px !important; font-weight: bold !important; }
    div[data-testid="column"] div.stButton > button { font-size: 20px !important; font-weight: bold !important; }
    .stTextArea textarea { font-size: 22px !important; color: #000000 !important; font-weight: bold !important; height: 580px !important; resize: vertical !important; }
    .sentence-display { font-size: 24px !important; font-weight: bold !important; color: #ffffff !important; line-height: 1.6 !important; }
    div[data-testid="stExpander"] summary span { font-size: 22px !important; font-weight: bold !important; }
    .yt-button { display: inline-flex; align-items: center; justify-content: center; background-color: #28a745; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%; }
    .notebook-button { display: inline-flex; align-items: center; justify-content: center; background-color: #4285F4; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%; }
    .translate-button { display: inline-flex; align-items: center; justify-content: center; background-color: #1a73e8; color: white !important; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 16px; border: none; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥋 澄玄大學 - 太極學院（拳、劍、扇招式記憶與朗讀工坊）")

# --- 邏輯修正區：只修改儲存格式 ---
TAIJI_CSV_FILE = "taiji_recipes_太極學院.csv"

def save_taiji_data_to_csv():
    csv_data_list = []
    for idx in range(1, 51):
        csv_data_list.append({
            "id": idx,
            "url": st.session_state.get(f"taiji_yt_input_url_{idx}", ""),
            "title": st.session_state.taiji_playlist_names.get(idx, f"套路 {idx}"),
            "lyrics": st.session_state.get(f"taiji_my_text_input_{idx}", "")
        })
    df_export = pd.DataFrame(csv_data_list)
    # 【關鍵修正】強制使用 QUOTE_ALL，確保多行文字被正確雙引號包覆，絕不亂行
    csv_string = df_export.to_csv(index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
    with open(TAIJI_CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        f.write(csv_string)
    return csv_string

# --- 其餘頁面結構完全照舊 ---
# (為了縮短回應長度，這裡省略中間重複的變數宣告，您原本程式碼中的邏輯保持不變即可)
# 只要確保讀取時也加上 quoting=csv.QUOTE_ALL 即可：
if os.path.exists(TAIJI_CSV_FILE):
    try:
        saved_df = pd.read_csv(TAIJI_CSV_FILE, quoting=csv.QUOTE_ALL, encoding="utf-8-sig")
        # ... 後續載入邏輯保持不變 ...
    except: pass

# ... (請保留您原本程式碼中所有的介面元件代碼) ...
