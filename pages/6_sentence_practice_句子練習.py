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
    .stTextInput input { font-size: 22px !important; font-weight: bold !important; height: 50px !important; }
    .sentence-display { font-size: 24px !important; font-weight: bold !important; color: #ffffff !important; line-height: 1.6 !important; }
    .chinese-hint { font-size: 20px !important; color: #a0a0a0 !important; font-style: italic !important; margin-bottom: 10px !important; }
    .yt-button { display: inline-flex; align-items: center; justify-content: center; background-color: #28a745; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%; }
    .notebook-button { display: inline-flex; align-items: center; justify-content: center; background-color: #4285F4; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%; }
    .translate-button { display: inline-flex; align-items: center; justify-content: center; background-color: #1a73e8; color: white !important; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 16px; border: none; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

# [載入資料函數]
@st.cache_data
def load_and_merge_data():
    expected_cols = ["word", "trans", "kk", "level"]
    all_data = []
    all_files = glob.glob("words_*.csv")
    for f in all_files:
        try:
            df = pd.read_csv(f, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            for col in expected_cols:
                if col not in df.columns: df[col] = ""
            all_data.append(df[expected_cols])
        except: continue
    return pd.concat(all_data, ignore_index=True).drop_duplicates(subset=["word"], keep='last') if all_data else pd.DataFrame(columns=expected_cols)

df = load_and_merge_data()
word_dict = {str(row['word']).strip().lower(): {"trans": str(row['trans']), "kk": str(row['kk'])} for _, row in df.iterrows() if pd.notna(row['word'])}

# [頁面變數初始化]
if "current_page" not in st.session_state: st.session_state.current_page = 1
if "playlist_names" not in st.session_state: st.session_state.playlist_names = {idx: f"曲目 {idx}" for idx in range(1, 51)}
if "page_names" not in st.session_state: st.session_state.page_names = {p: f"第 {p} 頁" for p in range(1, 6)}

# [主頁面邏輯]
start_idx = (st.session_state.current_page - 1) * 10 + 1
end_idx = st.session_state.current_page * 10
tabs = st.tabs([f"🎵 {st.session_state.playlist_names[i]}" for i in range(start_idx, end_idx + 1)])

for tab_idx, tab in enumerate(tabs):
    absolute_idx = start_idx + tab_idx
    with tab:
        text_key = f"my_text_input_{absolute_idx}"
        if text_key not in st.session_state: st.session_state[text_key] = ""
        
        user_input_text = st.text_area("輸入歌詞（英文句與中文句分行輸入）：", value=st.session_state[text_key], key=f"textarea_{absolute_idx}", height=400)
        st.session_state[text_key] = user_input_text

        st.divider()
        st.subheader("✍️ 逐句英文輸入測驗：")
        
        lines = [line.strip() for line in user_input_text.split('\n') if line.strip()]
        
        # [核心：自動配對英文與中文]
        pairs = []
        for i in range(len(lines)):
            if re.search(r'[A-Za-z]', lines[i]): # 判斷是英文句
                eng_line = lines[i]
                zh_hint = lines[i+1] if (i+1 < len(lines) and not re.search(r'[A-Za-z]', lines[i+1])) else None
                pairs.append((eng_line, zh_hint))
        
        if pairs:
            for idx, (eng, zh) in enumerate(pairs):
                st.markdown(f"---")
                st.markdown(f"<div class='sentence-display'>✨ {eng}</div>", unsafe_allow_html=True)
                if zh:
                    st.markdown(f"<div class='chinese-hint'>中文對應：{zh}</div>", unsafe_allow_html=True)
                
                # 測驗框
                ans_key = f"ans_{absolute_idx}_{idx}"
                user_ans = st.text_input(f"輸入第 {idx+1} 句英文", key=ans_key, label_visibility="collapsed", placeholder="輸入對應英文...")
                
                if user_ans.strip():
                    target = re.sub(r'[\(\（].*?[\)\）]', '', eng).strip()
                    if "".join(re.findall(r'[A-Za-z0-9]', user_ans)).lower() == "".join(re.findall(r'[A-Za-z0-9]', target)).lower():
                        st.success("🎉 正確！")
                    else:
                        st.error(f"❌ 錯誤，目標：{target}")
        else:
            st.info("💡 請在上方輸入內容（英中交錯），系統會自動配對顯示喔！")
