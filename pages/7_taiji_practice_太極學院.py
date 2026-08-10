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
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    
    .stTextInput input { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 50px !important;
    }
    
    div[data-baseweb="input"] input {
        font-size: 22px !important;
        color: #000000 !important;
        font-weight: bold !important;
        height: 50px !important;
    }
    
    div[data-testid="stExpander"] input {
        font-size: 24px !important;
        color: #000000 !important;
        font-weight: bold !important;
        height: 55px !important;
    }

    button[data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: bold !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
    
    div.stButton > button { 
        font-size: 20px !important; 
        padding: 12px 20px !important; 
        font-weight: bold !important;
    }

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
    
    .sentence-display {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        line-height: 1.6 !important;
    }

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

st.title("🥋 澄玄大學 - 太極學院（拳、劍、扇招式記憶與朗讀工坊）")

# 最上方的兩個專屬按鈕
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    yt_url_top = "https://www.youtube.com/"
    st.markdown(f'<a href="{yt_url_top}" target="_blank" class="yt-button">🔥 太極教學熱門影片任意門</a>', unsafe_allow_html=True)
with col_btn2:
    notebook_url = "https://notebooklm.google.com/"
    st.markdown(f'<a href="{notebook_url}" target="_blank" class="notebook-button">✨ 澄玄的隨身太極筆記任意門</a>', unsafe_allow_html=True)

st.write("")

if "taiji_page_names" not in st.session_state:
    st.session_state.taiji_page_names = {
        p: f"第 {p} 冊 (套路 {(p-1)*10 + 1} ~ {p*10})" for p in range(1, 6)
    }

if "taiji_playlist_names" not in st.session_state:
    st.session_state.taiji_playlist_names = {idx: f"套路 {idx}" for idx in range(1, 51)}

for idx in range(1, 51):
    if f"taiji_yt_input_url_{idx}" not in st.session_state:
        st.session_state[f"taiji_yt_input_url_{idx}"] = ""
    if f"taiji_my_text_input_{idx}" not in st.session_state:
        st.session_state[f"taiji_my_text_input_{idx}"] = ""

# 從太極專屬 CSV 讀取並強制載入到 session_state 中
TAIJI_CSV_FILE = "taiji_playlist_heart_太極結連庫.csv"
if os.path.exists(TAIJI_CSV_FILE):
    try:
        saved_df = pd.read_csv(TAIJI_CSV_FILE)
        for _, row in saved_df.iterrows():
            idx_val = int(row['id'])
            if 1 <= idx_val <= 50:
                if pd.notna(row.get('url')):
                    st.session_state[f"taiji_yt_input_url_{idx_val}"] = str(row['url'])
                if pd.notna(row.get('title')):
                    st.session_state.taiji_playlist_names[idx_val] = str(row['title'])
                if 'lyrics' in saved_df.columns and pd.notna(row.get('lyrics')):
                    # 確保正確寫入 session_state
                    st.session_state[f"taiji_my_text_input_{idx_val}"] = str(row['lyrics'])
    except Exception as e:
        print(f"CSV 讀取錯誤: {e}")

if "taiji_current_page" not in st.session_state:
    st.session_state.taiji_current_page = 1

st.write("")

def save_taiji_data_to_csv():
    csv_data_list = []
    for idx in range(1, 51):
        csv_data_list.append({
            "id": idx,
            "url": st.session_state.get(f"taiji_yt_input_url_{idx}", "").strip(),
            "title": st.session_state.taiji_playlist_names.get(idx, f"套路 {idx}"),
            "lyrics": st.session_state.get(f"taiji_my_text_input_{idx}", "")
        })
    df_export = pd.DataFrame(csv_data_list)
    df_export.to_csv(TAIJI_CSV_FILE, index=False, encoding="utf-8-sig", quoting=1)
    return df_export.to_csv(index=False, encoding="utf-8-sig", quoting=1)

def auto_save_taiji():
    save_taiji_data_to_csv()

csv_text_output = save_taiji_data_to_csv()

with st.expander("📥 產生並下載包含完整太極招式的 CSV 庫（支援 Excel 直接開啟與 GitHub）"):
    st.markdown("<span style='font-size: 20px; font-weight: bold;'>系統已啟用自動儲存與聯動帶入，點擊選項即可無縫切換！</span>", unsafe_allow_html=True)
    
    st.download_button(
        label="📥 點我直接下載 taiji_playlist_heart_太極結連庫.csv 檔案",
        data=csv_text_output,
        file_name=TAIJI_CSV_FILE,
        mime="text/csv",
        use_container_width=True
    )

st.write("")

st.markdown("<h3 style='font-size: 26px; color: #ffffff;'>📚 選擇太極練習冊（翻書頁面）：</h3>", unsafe_allow_html=True)

page_cols = st.columns(5)
for p in range(1, 6):
    with page_cols[p-1]:
        btn_label = f"👉 【第 {p} 頁】\n{st.session_state.taiji_page_names[p]}" if st.session_state.taiji_current_page == p else f"第 {p} 頁\n{st.session_state.taiji_page_names[p]}"
        if st.button(btn_label, key=f"taiji_page_btn_{p}", use_container_width=True):
            st.session_state.taiji_current_page = p
            st.rerun()

current_page = st.session_state.taiji_current_page
st.write("")

with st.expander(f"✏️ 自訂【第 {current_page} 頁】的用途與名稱設定"):
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        new_page_name = st.text_input(f"第 {current_page} 頁總用途名稱：", value=st.session_state.taiji_page_names[current_page], key=f"input_taiji_page_name_{current_page}")
        if new_page_name != st.session_state.taiji_page_names[current_page]:
            st.session_state.taiji_page_names[current_page] = new_page_name
            st.rerun()

st.write("")

start_idx = (current_page - 1) * 10 + 1
end_idx = current_page * 10

tab_titles = [f"🥋 {st.session_state.taiji_playlist_names[idx]}" for idx in range(start_idx, end_idx + 1)]
tabs = st.tabs(tab_titles)

for tab_idx, tab in enumerate(tabs):
    absolute_idx = start_idx + tab_idx
    
    with tab:
        url_key = f"taiji_yt_input_url_{absolute_idx}"
        text_key = f"taiji_my_text_input_{absolute_idx}"

        with st.expander(f"✏️ 修改【單元 {absolute_idx}】的套路名稱"):
            curr_name = st.session_state.taiji_playlist_names[absolute_idx]
            new_track_name = st.text_input(f"單元 {absolute_idx} 名稱：", value=curr_name, key=f"rename_taiji_track_{absolute_idx}")
            if new_track_name != curr_name:
                st.session_state.taiji_playlist_names[absolute_idx] = new_track_name
                save_taiji_data_to_csv()
                st.rerun()

        left_col, right_col = st.columns([1, 1.2], vertical_alignment="top")

        with left_col:
            user_yt_link = st.text_input(
                f"請在此貼上 YouTube 或 Shorts 網址：",
                value=st.session_state.get(url_key, ""),
                key=f"input_{url_key}",
                on_change=auto_save_taiji
            )
            st.session_state[url_key] = user_yt_link

            if user_yt_link.strip():
                try:
                    raw_url = user_yt_link.strip()
                    video_id = ""
                    
                    if "shorts/" in raw_url:
                        video_id = raw_url.split("shorts/")[-1].split("?")[0].split("/")[0]
                    elif "watch?v=" in raw_url:
                        video_id = raw_url.split("watch?v=")[-1].split("&")[0]
                    elif "youtu.be/" in raw_url:
                        video_id = raw_url.split("youtu.be/")[-1].split("?")[0].split("/")[0]
                        
                    if video_id:
                        embed_url = f"https://www.youtube.com/embed/{video_id}?loop=1&playlist={video_id}"
                        st.markdown(f"""
                            <div style="display: flex; justify-content: center; margin-bottom: 15px; margin-top: 15px;">
                                <iframe width="350" height="580" src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("無法辨識此網址格式，請確認是否為正確的 YouTube 網址。")
                except Exception as e:
                    st.error(f"影片載入發生錯誤：{e}")
            else:
                st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: center; height: 350px; border: 2px dashed #444; border-radius: 10px; color: #888; font-size: 20px; margin-top: 15px; margin-bottom: 15px;">
                        📺 請在上方輸入網址以顯示影片
                    </div>
                """, unsafe_allow_html=True)

            col_copy1, col_copy2 = st.columns([1, 3])
            with col_copy1:
                copy_btn = st.button(f"📋 複製網址", key=f"copy_taiji_{absolute_idx}")
            with col_copy2:
                if copy_btn:
                    if user_yt_link.strip():
                        st.code(user_yt_link, language="text")
                    else:
                        st.warning("目前網址框是空的！")

        with right_col:
            # 確保文字框每次切換都能抓到 session_state 裡從 CSV 讀進來的值
            current_lyrics_value = st.session_state.get(text_key, "")
            
            title_col, btn_col = st.columns([3, 1.4], vertical_alignment="center")
            with title_col:
                st.subheader("✍️ 太極招式文字框與朗讀練習：")
            with btn_col:
                encoded_text = urllib.parse.quote(current_lyrics_value)
                translate_url = f"https://translate.google.com/?hl=zh-TW&sl=zh-TW&tl=zh-TW&text={encoded_text}&op=translate"
                st.markdown(f'<a href="{translate_url}" target="_blank" class="translate-button">🌐 Google 搜尋</a>', unsafe_allow_html=True)

            # 移除 value 參數，直接讓 text_area 與 session_state 綁定，避免狀態衝突
            user_input_text = st.text_area(
                "輸入太極招式：",
                value=current_lyrics_value,
                key=f"textarea_taiji_{absolute_idx}",
                on_change=auto_save_taiji
            )
            
            # 即時同步更新 session_state
            if user_input_text != current_lyrics_value:
                st.session_state[text_key] = user_input_text

            col1, col2, col3 = st.columns([1.2, 1.2, 1])
            with col1:
                play_btn = st.button(f"🔊 播放整段", key=f"play_taiji_{absolute_idx}")
            with col2:
                smart_split_btn = st.button(f"✨ 自動換行排版", key=f"split_taiji_{absolute_idx}")
            with col3:
                clear_btn = st.button(f"🗑️ 清空", key=f"clear_taiji_{absolute_idx}")

            if clear_btn:
                st.session_state[text_key] = ""
                save_taiji_data_to_csv()
                st.rerun()

            if smart_split_btn and user_input_text.strip():
                lines = [l.strip() for l in user_input_text.split('\n') if l.strip()]
                formatted_result = "\n".join(lines)
                st.session_state[text_key] = formatted_result
                save_taiji_data_to_csv()
                st.success("✨ 已成功完成排版整理並自動儲存！")
                st.rerun()

            if play_btn and user_input_text.strip():
                try:
                    tts = gTTS(text=user_input_text, lang='zh-TW')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True, loop=True)
                except Exception as e:
                    st.error(f"語音生成發生錯誤：{e}")

        st.divider()

        # 逐句互動輸入測驗區
        st.subheader("✍️ 逐招太極輸入測驗與朗讀練習：")
        
        all_lines = user_input_text.split('\n')
        taiji_lines = [line.strip() for line in all_lines if line.strip()]
        
        if taiji_lines:
            st.markdown(f"<span style='font-size: 20px;'>**已自動抓取 {len(taiji_lines)} 個招式進行逐句練習：**</span>", unsafe_allow_html=True)
            
            for line_idx, taiji_sentence in enumerate(taiji_lines):
                st.markdown(f"---")
                st.markdown(f"<div class='sentence-display'>第 {line_idx + 1} 招原招式：<br>🥋 {taiji_sentence}</div>", unsafe_allow_html=True)
                
                cols = st.columns([1.1, 1.4, 3.5, 1])
                with cols[0]:
                    if st.button(f"🔊 聽發音", key=f"taiji_line_audio_{absolute_idx}_{line_idx}"):
                        try:
                            s_tts = gTTS(text=taiji_sentence, lang='zh-TW', slow=False)
                            s_fp = io.BytesIO()
                            s_tts.write_to_fp(s_fp)
                            st.audio(s_fp, autoplay=True)
                        except Exception as e:
                            st.error(f"語音錯誤：{e}")
                            
                with cols[1]:
                    safe_sentence_js = taiji_sentence.replace("'", "\\'")
                    components.html(f"""
                        <button onclick="
                            const utterance = new SpeechSynthesisUtterance('{safe_sentence_js}');
                            utterance.lang = 'zh-TW';
                            utterance.rate = 0.5;
                            window.speechSynthesis.cancel();
                            window.speechSynthesis.speak(utterance);
                        " style="
                            background-color: #f0f2f6;
                            color: #262730;
                            border: 1px solid #d6d6d8;
                            padding: 8px 12px;
                            border-radius: 4px;
                            font-size: 16px;
                            font-weight: bold;
                            cursor: pointer;
                            width: 100%;
                        ">🐢 0.5倍慢速</button>
                    """, height=45)
                
                ans_key = f"taiji_ans_input_{absolute_idx}_{line_idx}"
                
                def make_clear_callback(k):
                    def clear_func():
                        st.session_state[k] = ""
                    return clear_func

                with cols[2]:
                    user_answer = st.text_input(
                        f"請輸入第 {line_idx + 1} 招：",
                        key=ans_key,
                        label_visibility="collapsed",
                        placeholder="請在此輸入對應的招式名稱..."
                    )
                
                with cols[3]:
                    st.button(f"🗑️ 清除", key=f"clear_taiji_line_{absolute_idx}_{line_idx}", on_click=make_clear_callback(ans_key))
                
                if user_answer.strip():
                    if user_answer.strip() == taiji_sentence:
                        st.markdown(f"<span style='font-size: 22px; color: #28a745; font-weight: bold;'>🎉 答對了！招式名稱正確，太棒囉！</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-size: 22px; color: #ff4b4b; font-weight: bold;'>❌ 名稱有出入，再試一次看看喔！<br>💡 正確解答提示：{taiji_sentence}</span>", unsafe_allow_html=True)
        else:
            st.info("💡 請在上方右側的文字框輸入太極招式（一行一招），下方就會自動產生對應的逐招練習題囉！")
