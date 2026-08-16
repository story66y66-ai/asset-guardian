import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import urllib.parse
import streamlit.components.v1 as components

# 設定頁面為寬螢幕模式
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    .stTextInput input { font-size: 22px !important; color: #000000 !important; font-weight: bold !important; height: 50px !important; }
    .stTextArea textarea { font-size: 22px !important; color: #ffffff !important; font-weight: bold !important; line-height: 1.5 !important; }
    .sentence-display { font-size: 24px !important; font-weight: bold !important; color: #ffffff !important; line-height: 1.6 !important; }
    .chinese-hint { font-size: 20px !important; color: #a0a0a0 !important; font-style: italic !important; margin-bottom: 8px !important; }
    .yt-button { display: inline-flex; align-items: center; justify-content: center; background-color: #28a745; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%; }
    .notebook-button { display: inline-flex; align-items: center; justify-content: center; background-color: #4285F4; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%; }
    .translate-button { display: inline-flex; align-items: center; justify-content: center; background-color: #1a73e8; color: white !important; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 16px; border: none; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

# 初始化狀態
if "playlist_names" not in st.session_state:
    st.session_state.playlist_names = {idx: f"曲目 {idx}" for idx in range(1, 51)}

# --- 核心邏輯：顯示曲目與歌詞 ---
# 假設您是在「第 1 頁」開始
current_page = 1
start_idx = (current_page - 1) * 10 + 1
end_idx = current_page * 10

# 建立分頁
tab_titles = [f"{idx}\n{st.session_state.playlist_names[idx]}" for idx in range(start_idx, end_idx + 1)]
tabs = st.tabs(tab_titles)

for tab_idx, tab in enumerate(tabs):
    absolute_idx = start_idx + tab_idx
    with tab:
        st.subheader(f"第 {absolute_idx} 首")
        st.markdown(f"### {st.session_state.playlist_names[absolute_idx]}")
        
        # 歌詞輸入區
        text_key = f"my_text_input_{absolute_idx}"
        if text_key not in st.session_state: st.session_state[text_key] = ""
        
        user_input_text = st.text_area("輸入歌詞（英文/中文需單行對應）：", value=st.session_state[text_key], key=f"area_{absolute_idx}")
        st.session_state[text_key] = user_input_text

        # 逐句分析與測驗
        st.subheader("✍️ 逐句練習：")
        lines = [line.strip() for line in user_input_text.split('\n') if line.strip()]
        
        # 配對邏輯：奇數行英文，偶數行中文
        for i in range(0, len(lines), 2):
            eng = lines[i]
            zh = lines[i+1] if i+1 < len(lines) else ""
            
            st.markdown(f"---")
            st.markdown(f"<div class='sentence-display'>✨ {eng}</div>", unsafe_allow_html=True)
            if zh: st.markdown(f"<div class='chinese-hint'>中文：{zh}</div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns([1, 4])
            with col_a:
                if st.button("🔊 播放", key=f"btn_{absolute_idx}_{i}"):
                    tts = gTTS(text=eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)
            with col_b:
                st.text_input(f"輸入第 {i//2 + 1} 句英文：", key=f"inp_{absolute_idx}_{i}")
