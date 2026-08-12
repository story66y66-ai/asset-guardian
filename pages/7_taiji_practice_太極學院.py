import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import io

st.set_page_config(layout="wide")

# CSS 樣式設定：針對選單框強制放大
st.markdown("""
    <style>
    /* 1. 這是最關鍵的一步：強制放大選單框內的顯示文字 */
    div[data-baseweb="select"] {
        font-size: 50px !important;
    }
    
    /* 強制放大下拉選單裡的文字 */
    div[role="listbox"] {
        font-size: 45px !important;
    }

    /* 2. 放大選單上方的標題文字 */
    .stMarkdown h3 { 
        font-size: 45px !important; 
        font-weight: bold !important; 
    }
    
    /* 3. 左側文字輸入框字體放大到 40px */
    .stTextArea textarea { font-size: 40px !important; height: 450px !important; }
    
    /* 4. 網址輸入框字體放大到 40px */
    .stTextInput input { font-size: 40px !important; height: 60px !important; }
    
    /* 5. 頁面標題放大到 70px */
    h1 { font-size: 70px !important; }
    
    /* 6. 右側逐招練習區的招式字體放大到 80px */
    .sentence-display { 
        font-size: 80px !important; 
        font-weight: bold !important; 
        color: #ffffff !important; 
        padding: 40px 0 !important;
        line-height: 1.4 !important;
    }
    
    /* 7. 按鈕字體放大到 35px */
    .stButton button {
        font-size: 35px !important;
        padding: 15px 30px !important;
    }
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

# 建立大字體下拉選單
st.markdown("### 🔍 請選擇要練習的套路：")
options = [f"{i}. {st.session_state.taiji_data[i]['title']}" for i in range(1, 11)]
selected_option = st.selectbox("選擇套路", options, label_visibility="collapsed")
idx = int(selected_option.split(".")[0])

# 顯示當前選中的套路編輯與練習區
with st.container():
    st.subheader(f"✏️ 編輯 {st.session_state.taiji_data[idx]['title']} 的內容")
    
    new_title = st.text_input("設定套路名稱：", value=st.session_state.taiji_data[idx]["title"], key=f"title_{idx}")
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
