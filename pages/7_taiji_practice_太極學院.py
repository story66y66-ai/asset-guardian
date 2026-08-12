import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import io

st.set_page_config(layout="wide")

# CSS 樣式設定
st.markdown("""
    <style>
    /* 1. 放大上方 10 個切換按鈕的文字 */
    .stButton button {
        height: 90px !important;
        border-radius: 12px !important;
        width: 100% !important;
    }
    .stButton button p {
        font-size: 36px !important;
        font-weight: bold !important;
    }
    
    /* 2. 左側文字輸入框字體放大到 40px */
    .stTextArea textarea { font-size: 40px !important; height: 450px !important; }
    
    /* 3. 徹底放大右側單行輸入框的外框高度與內部字體 */
    .stTextInput input {
        font-size: 55px !important;
        height: 80px !important;
        padding: 10px !important;
    }
    
    .stTextInput > div > div {
        min-height: 90px !important;
        align-items: center !important;
    }
    
    /* 4. 頁面標題放大到 70px */
    h1 { font-size: 70px !important; }
    
    /* 5. 欄位標題放大到 40px */
    h2, h3 { 
        font-size: 40px !important; 
        font-weight: bold !important; 
        margin-bottom: 15px !important;
    }
    
    /* 6. 右側逐招練習區的招式標題字體放大到 80px */
    .sentence-display { 
        font-size: 80px !important; 
        font-weight: bold !important; 
        color: #ffffff !important; 
        padding: 20px 0 !important;
        line-height: 1.4 !important;
    }
    
    /* 7. 自定義超大提示文字樣式 */
    .custom-input-label {
        font-size: 60px !important;
        font-weight: bold !important;
        color: #ffcc00 !important;
        margin-top: 20px !important;
        margin-bottom: 10px !important;
        line-height: 1.2 !important;
    }
    
    /* 8. 自定義超大對與錯結果顯示區 */
    .result-success {
        font-size: 50px !important;
        font-weight: bold !important;
        color: #00ff66 !important;
        background-color: rgba(0, 255, 102, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
    }
    .result-error {
        font-size: 45px !important;
        font-weight: bold !important;
        color: #ff3333 !important;
        background-color: rgba(255, 51, 51, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        line-height: 1.3;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥋 澄玄大學 - 太極學院")

# 初始化狀態
if "taiji_data" not in st.session_state:
    st.session_state.taiji_data = {i: {"title": f"套路 {i}", "lyrics": "", "video_url": ""} for i in range(1, 11)}

if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 1

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

# 上方 10 個大按鈕切換區
st.markdown("### 🔍 請點選要練習的套路：")
row1 = st.columns(5)
row2 = st.columns(5)
all_cols = row1 + row2

for i in range(1, 11):
    with all_cols[i-1]:
        btn_label = f"{i}. {st.session_state.taiji_data[i]['title']}"
        if st.button(btn_label, key=f"nav_btn_{i}"):
            st.session_state.selected_idx = i

idx = st.session_state.selected_idx
st.markdown("---")

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
        st.subheader("✍️ 逐招練習與輸入測試區：")
        lines = [l.strip() for l in new_lyrics.split('\n') if l.strip()]

        for line_idx, line in enumerate(lines):
            st.markdown(f"---")
            st.markdown(f"<div class='sentence-display'>第 {line_idx+1} 招：{line}</div>", unsafe_allow_html=True)
            
            if st.button(f"🔊 聽第 {line_idx+1} 招發音", key=f"play_{idx}_{line_idx}"):
                tts = gTTS(text=line, lang='zh-TW')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp, autoplay=True)
            
            st.markdown(f"<div class='custom-input-label'>請輸入第 {line_idx+1} 招名稱進行測試：</div>", unsafe_allow_html=True)
            
            input_col, clear_col = st.columns([4, 1])
            input_key = f"input_{idx}_{line_idx}"
            version_key = f"version_{idx}_{line_idx}"
            
            if version_key not in st.session_state:
                st.session_state[version_key] = 0
            
            actual_input_key = f"{input_key}_v{st.session_state[version_key]}"
            
            with input_col:
                user_input = st.text_input(actual_input_key, label_visibility="collapsed")
            
            with clear_col:
                if st.button("🗑️ 清除", key=f"clear_{idx}_{line_idx}"):
                    st.session_state[version_key] += 1
                    st.rerun()
            
            if user_input:
                clean_input = user_input.strip()
                if clean_input == line:
                    st.markdown(f"<div class='result-success'>🎉 太棒了！完全正確！</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='result-error'>❌ 答錯囉！您輸入的是「{clean_input}」，正確答案是「{line}」</div>", unsafe_allow_html=True)
