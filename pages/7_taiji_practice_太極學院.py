import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import io

st.set_page_config(layout="wide")

# CSS 樣式設定
st.markdown("""
    <style>
    .stButton button { 
        height: 70px !important; 
        border-radius: 12px !important; 
        width: 100% !important; 
    }
    .stButton button p { 
        font-size: 24px !important; 
        font-weight: bold !important; 
    }

    /* 專屬儲存按鈕：螢光綠文字與發光邊框 */
    div.save-btn-wrapper button {
        border: 4px solid #00ff66 !important;
        background-color: rgba(0, 255, 102, 0.05) !important;
        height: 90px !important;
        box-shadow: 0px 0px 15px rgba(0, 255, 102, 0.3) !important;
    }
    div.save-btn-wrapper button p {
        font-size: 32px !important;
        font-weight: 900 !important;
        color: #00ff66 !important;
        text-shadow: 0px 0px 10px rgba(0, 255, 102, 0.5) !important;
    }
    div.save-btn-wrapper button:hover {
        background-color: rgba(0, 255, 102, 0.15) !important;
    }

    .stTextArea textarea { font-size: 24px !important; height: 400px !important; }
    .stTextInput input { font-size: 28px !important; height: 60px !important; padding: 10px !important; color: #ffffff !important; font-weight: bold !important; }
    .stTextInput > div > div { min-height: 65px !important; align-items: center !important; }
    h1 { font-size: 50px !important; }
    h2, h3 { font-size: 30px !important; font-weight: bold !important; margin-bottom: 15px !important; }
    
    /* 縮小招式間距與對應文字 */
    .sentence-display { font-size: 27px !important; font-weight: bold !important; color: #ffffff !important; padding: 4px 0 !important; line-height: 1.3 !important; }
    .custom-input-label { font-size: 20px !important; font-weight: bold !important; color: #ffcc00 !important; margin-top: 4px !important; margin-bottom: 2px !important; line-height: 1.2 !important; }
    
    .result-success { font-size: 20px !important; font-weight: bold !important; color: #00ff66 !important; background-color: rgba(0, 255, 102, 0.1); padding: 6px; border-radius: 6px; margin-top: 4px; }
    .result-error { font-size: 20px !important; font-weight: bold !important; color: #ff3333 !important; background-color: rgba(255, 51, 51, 0.1); padding: 6px; border-radius: 6px; margin-top: 4px; line-height: 1.3; }
    
    /* 縮小分隔線上下留白 */
    hr {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥋 澄玄大學 - 太極學院")

# 初始化狀態
if "taiji_data" not in st.session_state:
    st.session_state.taiji_data = {i: {"title": f"套路 {i}", "lyrics": "", "video_urls": ["", "", "", "", ""]} for i in range(1, 11)}

if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 1

TAIJI_CSV_FILE = "taiji_recipes_太極學院.csv"

# 讀取 CSV
if os.path.exists(TAIJI_CSV_FILE):
    try:
        df = pd.read_csv(TAIJI_CSV_FILE, encoding="utf-8-sig")
        for _, row in df.iterrows():
            idx_val = int(row['id'])
            if 1 <= idx_val <= 10:
                raw_urls = str(row['video_url']).split(',') if pd.notna(row['video_url']) else []
                urls = []
                for i in range(5):
                    if i < len(raw_urls):
                        urls.append(raw_urls[i].strip())
                    else:
                        urls.append("")
                
                st.session_state.taiji_data[idx_val] = {
                    "title": row['title'], 
                    "lyrics": str(row['lyrics']) if pd.notna(row['lyrics']) else "",
                    "video_urls": urls
                }
    except Exception as e:
        st.error(f"讀取存檔時發生錯誤: {e}")

def save_to_csv():
    df_new = pd.DataFrame([{
        "id": i, 
        "title": st.session_state.taiji_data[i]['title'], 
        "lyrics": st.session_state.taiji_data[i]['lyrics'], 
        "video_url": ",".join([url.strip() for url in st.session_state.taiji_data[i]['video_urls']])
    } for i in range(1, 11)])
    df_new.to_csv(TAIJI_CSV_FILE, index=False, encoding="utf-8-sig")

# 介面渲染：選擇套路
st.markdown("### 🔍 請點選要練習的套路：")
row1, row2 = st.columns(5), st.columns(5)
for i in range(1, 11):
    with (row1 + row2)[i-1]:
        if st.button(f"{i}. {st.session_state.taiji_data[i]['title']}", key=f"nav_btn_{i} wanita"):
            st.session_state.selected_idx = i

idx = st.session_state.selected_idx
st.markdown("---")

with st.container():
    st.subheader(f"✏️ 編輯 {st.session_state.taiji_data[idx]['title']} 的內容")
    
    new_title = st.text_input("設定套路名稱：", value=st.session_state.taiji_data[idx]["title"], key=f"input_title_{idx}")
    
    st.markdown("🎥 參考影片（最多 5 部，請直接貼上網址）：")
    new_urls = []
    for i in range(5):
        current_val = st.session_state.taiji_data[idx]["video_urls"][i] if i < len(st.session_state.taiji_data[idx]["video_urls"]) else ""
        url_input = st.text_input(f"影片網址 {i+1}", value=current_val, key=f"ind_url_{idx}_{i}")
        new_urls.append(url_input)
    
    new_lyrics = st.text_area("輸入完整套路內容（一行一招）：", value=st.session_state.taiji_data[idx]["lyrics"], height=300, key=f"input_lyrics_{idx}")
    
    # 儲存按鈕
    st.markdown('<div class="save-btn-wrapper">', unsafe_allow_html=True)
    if st.button("💾 【 點我立刻儲存太極套路 】", key=f"save_btn_{idx}"):
        st.session_state.taiji_data[idx]["title"] = new_title
        st.session_state.taiji_data[idx]["video_urls"] = new_urls
        st.session_state.taiji_data[idx]["lyrics"] = new_lyrics
        save_to_csv()
        st.success("儲存成功！")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📺 影片預覽區")
        for url in st.session_state.taiji_data[idx]["video_urls"]:
            if url.strip():
                st.video(url.strip())
    
    with col2:
        st.subheader("✍️ 逐招練習與輸入測試區：")
        current_lyrics = st.session_state.taiji_data[idx]["lyrics"]
        lines = [l.strip() for l in current_lyrics.split('\n') if l.strip()]
        for line_idx, line in enumerate(lines):
            st.markdown("---")
            st.markdown(f"<div class='sentence-display'>第 {line_idx+1} 招：{line}</div>", unsafe_allow_html=True)
            if st.button(f"🔊 聽發音", key=f"play_{idx}_{line_idx}"):
                fp = io.BytesIO()
                gTTS(text=line, lang='zh-TW').write_to_fp(fp)
                st.audio(fp, autoplay=True)
            st.markdown(f"<div class='custom-input-label'>請輸入第 {line_idx+1} 招名稱：</div>", unsafe_allow_html=True)
            
            input_col, clear_col = st.columns([4, 1])
            v_key = f"version_{idx}_{line_idx}"
            if v_key not in st.session_state: st.session_state[v_key] = 0
            
            with input_col:
                user_input = st.text_input(f"in_{idx}_{line_idx}_{st.session_state[v_key]}", label_visibility="collapsed")
            with clear_col:
                if st.button("🗑️", key=f"clear_{idx}_{line_idx}"):
                    st.session_state[v_key] += 1
                    st.rerun()
            
            if user_input:
                def norm(t): return t.strip().replace(" ", "").replace(" ", "").replace("．", ".").replace("，", ",")
                if norm(user_input) == norm(line):
                    st.markdown(f"<div class='result-success'>🎉 正確！</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='result-error'>❌ 答錯了！答案是「{line}」</div>", unsafe_allow_html=True)
