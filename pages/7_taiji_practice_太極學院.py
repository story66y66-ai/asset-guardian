import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import io
import urllib.parse
import csv
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# 樣式設定
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 20px !important; height: 500px !important; }
    .sentence-display { font-size: 22px !important; font-weight: bold !important; color: #ffffff !important; }
    .translate-button { background-color: #1a73e8; color: white !important; padding: 10px; border-radius: 6px; text-align: center; display: block; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥋 澄玄大學 - 太極學院")

# 初始化狀態
if "taiji_data" not in st.session_state:
    st.session_state.taiji_data = {i: {"title": f"套路 {i}", "lyrics": ""} for i in range(1, 11)}

# 讀取 CSV
TAIJI_CSV_FILE = "taiji_recipes_太極學院.csv"
if os.path.exists(TAIJI_CSV_FILE):
    try:
        df = pd.read_csv(TAIJI_CSV_FILE, encoding="utf-8-sig")
        for _, row in df.iterrows():
            idx = int(row['id'])
            if 1 <= idx <= 10:
                st.session_state.taiji_data[idx] = {"title": row['title'], "lyrics": str(row['lyrics']) if pd.notna(row['lyrics']) else ""}
    except: pass

def save_to_csv():
    df_new = pd.DataFrame([{"id": i, "title": st.session_state.taiji_data[i]["title"], "lyrics": st.session_state.taiji_data[i]["lyrics"]} for i in range(1, 11)])
    df_new.to_csv(TAIJI_CSV_FILE, index=False, encoding="utf-8-sig")

# 頁面架構
tabs = st.tabs([f"曲目 {i}" for i in range(1, 11)])

for i, tab in enumerate(tabs):
    idx = i + 1
    with tab:
        st.subheader(f"✏️ 編輯 {st.session_state.taiji_data[idx]['title']} 的內容")
        
        # 修改標題
        new_title = st.text_input(f"設定曲目 {idx} 名稱：", value=st.session_state.taiji_data[idx]["title"], key=f"title_{idx}")
        if new_title != st.session_state.taiji_data[idx]["title"]:
            st.session_state.taiji_data[idx]["title"] = new_title
            save_to_csv()
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            # 歌詞編輯框
            new_lyrics = st.text_area("輸入完整套路內容（一行一招）：", value=st.session_state.taiji_data[idx]["lyrics"], key=f"lyrics_{idx}")
            if new_lyrics != st.session_state.taiji_data[idx]["lyrics"]:
                st.session_state.taiji_data[idx]["lyrics"] = new_lyrics
                save_to_csv()
        
        with col2:
            st.subheader("✍️ 逐招練習區：")
            lines = [l.strip() for l in new_lyrics.split('\n') if l.strip()]
            for line_idx, line in enumerate(lines):
                st.markdown(f"---")
                st.markdown(f"<div class='sentence-display'>第 {line_idx+1} 招：{line}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 聽 {line_idx+1}", key=f"play_{idx}_{line_idx}"):
                    tts = gTTS(text=line, lang='zh-TW')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)
