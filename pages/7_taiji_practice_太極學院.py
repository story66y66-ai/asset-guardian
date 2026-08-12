import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import io

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .stTextArea textarea { font-size: 20px !important; height: 300px !important; }
    .sentence-display { font-size: 22px !important; font-weight: bold !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥋 澄玄大學 - 太極學院")

# 初始化狀態
if "taiji_data" not in st.session_state:
    st.session_state.taiji_data = {i: {"title": f"套路 {i}", "lyrics": "", "video_url": ""} for i in range(1, 11)}

TAIJI_CSV_FILE = "taiji_recipes_太極學院.csv"

# 讀取 CSV
if os.path.exists(TAIJI_CSV_FILE):
    try:
        df = pd.read_csv(TAIJI_CSV_FILE, encoding="utf-8-sig")
        for _, row in df.iterrows():
            idx = int(row['id'])
            if 1 <= idx <= 10:
                st.session_state.taiji_data[idx] = {
                    "title": row['title'], 
                    "lyrics": str(row['lyrics']) if pd.notna(row['lyrics']) else "",
                    "video_url": str(row['video_url']) if pd.notna(row['video_url']) else ""
                }
    except: pass

def save_to_csv():
    df_new = pd.DataFrame([{"id": i, **st.session_state.taiji_data[i]} for i in range(1, 11)])
    df_new.to_csv(TAIJI_CSV_FILE, index=False, encoding="utf-8-sig")

tabs = st.tabs([f"曲目 {i}" for i in range(1, 11)])

for i, tab in enumerate(tabs):
    idx = i + 1
    with tab:
        st.subheader(f"✏️ 編輯 {st.session_state.taiji_data[idx]['title']} 的內容")
        new_title = st.text_input("設定曲目名稱：", value=st.session_state.taiji_data[idx]["title"], key=f"title_{idx}")
        new_url = st.text_input("請貼上 YouTube 或 Shorts 網址：", value=st.session_state.taiji_data[idx]["video_url"], key=f"url_{idx}")
        
        if new_title != st.session_state.taiji_data[idx]["title"] or new_url != st.session_state.taiji_data[idx]["video_url"]:
            st.session_state.taiji_data[idx]["title"] = new_title
            st.session_state.taiji_data[idx]["video_url"] = new_url
            save_to_csv()
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            new_lyrics = st.text_area("輸入完整套路內容（一行一招）：", value=st.session_state.taiji_data[idx]["lyrics"], key=f"lyrics_{idx}")
            if new_lyrics != st.session_state.taiji_data[idx]["lyrics"]:
                st.session_state.taiji_data[idx]["lyrics"] = new_lyrics
                save_to_csv()
            if new_url:
                st.video(new_url)
        
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
