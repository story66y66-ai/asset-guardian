import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import io
import urllib.parse
import csv
import streamlit.components.v1 as components

# 設定頁面為寬螢幕模式
st.set_page_config(layout="wide")

# CSS 樣式設定
st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    .stTextInput input, .stTextArea textarea { font-size: 20px !important; font-weight: bold !important; }
    .stButton > button { font-size: 18px !important; font-weight: bold !important; }
    .sentence-display { font-size: 22px !important; font-weight: bold !important; color: #ffffff; line-height: 1.6; }
    .yt-button { display: inline-flex; align-items: center; justify-content: center; background-color: #28a745; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; width: 100%; }
    .notebook-button { display: inline-flex; align-items: center; justify-content: center; background-color: #4285F4; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥋 澄玄大學 - 太極學院（全覆蓋穩定版）")

# 資料庫檔案名稱
TAIJI_CSV_FILE = "taiji_recipes_太極學院.csv"

# 初始化 Session State
if "taiji_playlist_names" not in st.session_state:
    st.session_state.taiji_playlist_names = {idx: f"套路 {idx}" for idx in range(1, 51)}

# 儲存與讀取邏輯 (全面採用 QUOTE_ALL 確保多行文字正確)
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
    # 使用 QUOTE_ALL 強制對所有欄位加雙引號，解決換行儲存問題
    csv_string = df_export.to_csv(index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
    with open(TAIJI_CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        f.write(csv_string)

def load_taiji_data():
    if os.path.exists(TAIJI_CSV_FILE):
        try:
            # 讀取時對應 QUOTE_ALL
            saved_df = pd.read_csv(TAIJI_CSV_FILE, quoting=csv.QUOTE_ALL, encoding="utf-8-sig")
            for _, row in saved_df.iterrows():
                idx = int(row['id'])
                st.session_state[f"taiji_yt_input_url_{idx}"] = str(row.get('url', ''))
                st.session_state.taiji_playlist_names[idx] = str(row.get('title', f"套路 {idx}"))
                st.session_state[f"taiji_my_text_input_{idx}"] = str(row.get('lyrics', ''))
        except:
            pass

# 初始化讀取
if "data_loaded" not in st.session_state:
    load_taiji_data()
    st.session_state.data_loaded = True

# 介面顯示
for idx in range(1, 51):
    if f"taiji_yt_input_url_{idx}" not in st.session_state:
        st.session_state[f"taiji_yt_input_url_{idx}"] = ""
    if f"taiji_my_text_input_{idx}" not in st.session_state:
        st.session_state[f"taiji_my_text_input_{idx}"] = ""

# 頁面內容 (這裡為簡潔展示邏輯，完整版可視需求展開)
tab_titles = [st.session_state.taiji_playlist_names[i] for i in range(1, 11)] # 展示前10
tabs = st.tabs(tab_titles)

for i, tab in enumerate(tabs):
    idx = i + 1
    with tab:
        url = st.text_input("網址", key=f"url_{idx}", value=st.session_state[f"taiji_yt_input_url_{idx}"])
        text = st.text_area("招式", key=f"text_{idx}", value=st.session_state[f"taiji_my_text_input_{idx}"])
        
        if st.button("💾 儲存此單元", key=f"save_{idx}"):
            st.session_state[f"taiji_yt_input_url_{idx}"] = url
            st.session_state[f"taiji_my_text_input_{idx}"] = text
            save_taiji_data_to_csv()
            st.success("已儲存！")
