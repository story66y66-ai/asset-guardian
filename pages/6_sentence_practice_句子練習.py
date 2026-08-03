import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import urllib.parse
import json

# 設定頁面為寬螢幕模式
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    
    /* 放大一般 YouTube 網址與輸入框的文字與高度 */
    .stTextInput input { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 50px !important;
    }
    
    /* 放大逐句練習輸入框的文字與高度 */
    div[data-baseweb="input"] input {
        font-size: 22px !important;
        color: #000000 !important;
        font-weight: bold !important;
        height: 50px !important;
    }
    
    /* 專門放大第一到第五冊/頁名稱修改的輸入框文字與高度 */
    div[data-testid="stExpander"] input {
        font-size: 24px !important;
        color: #000000 !important;
        font-weight: bold !important;
        height: 55px !important;
    }

    /* 放大上方分頁籤 (Tabs) 的文字大小 */
    button[data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: bold !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    
    .stTextArea textarea { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 580px !important;
        resize: vertical !important; 
    }
    div.stButton > button { font-size: 20px !important; padding: 10px 20px !important; }
    
    /* 放大逐句練習區的原句文字大小（英文與中文） */
    .sentence-display {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        line-height: 1.6 !important;
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
    }
    .translate-button:hover {
        background-color: #1557b0;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

# 最上方的兩個專屬任意門按鈕
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    yt_url = "https://www.youtube.com/@%E8%8B%B1%E8%AA%9E%E5%A4%A9%E5%A4%A9%E5%AD%B8/shorts?view=0&sort=p&flow=grid"
    st.markdown(f'<a href="{yt_url}" target="_blank" class="yt-button">🔥 英語天天學熱門 Shorts 任意門</a>', unsafe_allow_html=True)
with col_btn2:
    notebook_url = "https://notebooklm.google.com/"
    st.markdown(f'<a href="{notebook_url}" target="_blank" class="notebook-button">✨ 澄玄的隨身英文秘書任意門</a>', unsafe_allow_html=True)

st.write("")

# 讀取單字資料庫以對應 KK 音標與翻譯
@st.cache_data
def load_and_merge_data():
    all_files = glob.glob("words_level*.csv")
    df_list = []
    if all_files:
        for filename in sorted(all_files):
            try:
                temp_df = pd.read_csv(filename)
                df_list.append(temp_df)
            except Exception:
                pass
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
    else:
        try:
            combined_df = pd.read_csv("words.csv")
        except Exception:
            combined_df = pd.DataFrame(columns=["word", "trans", "kk", "level"])
    if "word" in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=["word"])
    return combined_df

df = load_and_merge_data()

# 建立字典加速查詢 (word -> {trans, kk})
word_dict = {}
if not df.empty and "word" in df.columns:
    for _, row in df.iterrows():
        w_str = str(row['word']).strip().lower()
        trans_str = str(row['trans']) if 'trans' in df.columns and pd.notna(row['trans']) else ""
        kk_str = str(row['kk']) if 'kk' in df.columns and pd.notna(row['kk']) else ""
        word_dict[w_str] = {"trans": trans_str, "kk": kk_str}

# 初始化 5 頁的翻頁與曲目名稱記錄 (共 50 首)
if "page_names" not in st.session_state:
    st.session_state.page_names = {
        p: f"第 {p} 冊 (曲目 {(p-1)*10 + 1} ~ {p*10})" for p in range(1, 6)
    }

if "playlist_names" not in st.session_state:
    st.session_state.playlist_names = {
        idx: f"曲目 {idx}" for idx in range(1, 51)
    }
    st.session_state["my_text_input_1"] = "My Heart Will Go On 我心永恆\nEvery night in my dreams I see you, I feel you\n每個深夜在我的夢中，我見到你，感受到你"
    st.session_state.playlist_names[1] = "My Heart Will Go On"

# 確保所有 50 首的網址與文字都有在 session_state 內初始化
for idx in range(1, 51):
    url_key = f"yt_input_url_{idx}"
    text_key = f"my_text_input_{idx}"
    if url_key not in st.session_state:
        st.session_state[url_key] = ""
    if text_key not in st.session_state:
        st.session_state[text_key] = ""

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# ----------------------------------------------------
# 💾 存檔與讀檔專屬控制面板（側邊欄或上方區塊）
# ----------------------------------------------------
with st.expander("💾 澄玄的專屬備份與還原中心（下載/上傳存檔）"):
    col_save1, col_save2 = st.columns(2)
    with col_save1:
        st.markdown("**1. 備份下載目前的全部網址與歌詞：**")
        backup_data = {
            "page_names": st.session_state.page_names,
            "playlist_names": st.session_state.playlist_names,
        }
        for idx in range(1, 51):
            backup_data[f"yt_input_url_{idx}"] = st.session_state.get(f"yt_input_url_{idx}", "")
            backup_data[f"my_text_input_{idx}"] = st.session_state.get(f"my_text_input_{idx}", "")
        
        json_str = json.dumps(backup_data, ensure_ascii=False, indent=4)
        st.download_button(
            label="📥 下載備份存檔 (.json)",
            data=json_str,
            file_name="chengyuan_backup.json",
            mime="application/json"
        )
    
    with col_save2:
        st.markdown("**2. 還原上傳先前的備份存檔：**")
        uploaded_file = st.file_uploader("選擇備份的 json 檔案", type=["json"])
        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)
                if "page_names" in loaded_data:
                    st.session_state.page_names = loaded_data["page_names"]
                if "playlist_names" in loaded_data:
                    st.session_state.playlist_names = loaded_data["playlist_names"]
                for idx in range(1, 51):
                    if f"yt_input_url_{idx}" in loaded_data:
                        st.session_state[f"yt_input_url_{idx}"] = loaded_data[f"yt_input_url_{idx}"]
                    if f"my_text_input_{idx}" in loaded_data:
                        st.session_state[f"my_text_input_{idx}"] = loaded_data[f"my_text_input_{idx}"]
                st.success("🎉 成功還原備份檔案！")
                st.rerun()
            except Exception as e:
                st.error(f"檔案讀取失敗：{e}")

st.write("")

# ----------------------------------------------------
# 上方「翻書式」頁面選擇器
# ----------------------------------------------------
st.markdown("<h3 style='font-size: 26px; color: #ffffff;'>📚 選擇練習冊（翻書頁面）：</h3>", unsafe_allow_html=True)

page_cols = st.columns(5)
for p in range(1, 6):
    with page_cols[p-1]:
        btn_label = f"👉 【第 {p} 頁】\n{st.session_state.page_names[p]}" if st.session_state.current_page == p else f"第 {p} 頁\n{st.session_state.page_names[p]}"
        if st.button(btn_label, key=f"page_btn_{p}", use_container_width=True):
            st.session_state.current_page = p
            st.rerun()

current_page = st.session_state.current_page
st.write("")

# 讓澄玄可以自訂當前這一頁（這一冊）的用途名稱
with st.expander(f"✏️ 自訂【第 {current_page} 頁】的用途與名稱設定"):
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        new_page_name = st.text_input(f"第 {current_page} 頁總用途名稱：", value=st.session_state.page_names[current_page], key=f"input_page_name_{current_page}")
        if new_page_name != st.session_state.page_names[current_page]:
            st.session_state.page_names[current_page] = new_page_name
            st.rerun()
    with col_p2:
        st.write("")
        st.markdown(f"<span style='font-size: 20px; color: #a0a0a0;'>💡 在此輸入這頁的專屬用途，方便辨識！</span>", unsafe_allow_html=True)

st.write("")

# 計算當前頁面涵蓋的 10 個曲目編號範圍
start_idx = (current_page - 1) * 10 + 1
end_idx = current_page * 10

# 建立該頁面專屬的 10 個分頁籤
tab_titles = [f"🎵 {st.session_state.playlist_names[idx]}" for idx in range(start_idx, end_idx + 1)]
tabs = st.tabs(tab_titles)

# 迴圈建立這 10 個分頁的獨立內容
for tab_idx, tab in enumerate(tabs):
    absolute_idx = start_idx + tab_idx  # 實際的全局曲目編號 (1~50)
    
    with tab:
        url_key = f"yt_input_url_{absolute_idx}"
        text_key = f"my_text_input_{absolute_idx}"

        with st.expander(f"✏️ 修改【曲目 {absolute_idx}】的歌名或用途"):
            curr_name = st.session_state.playlist_names[absolute_idx]
            new_track_name = st.text_input(f"曲目 {absolute_idx} 名稱：", value=curr_name, key=f"rename_track_{absolute_idx}")
            if new_track_name != curr_name:
                st.session_state.playlist_names[absolute_idx] = new_track_name
                st.rerun()

        left_col, right_col = st.columns([1, 1.2], vertical_alignment="top")

        with left_col:
            def update_yt_url(k):
                st.session_state[k] = st.session_state[f"input_{k}"]

            st.text_input(
                f"請在此貼上 YouTube 或 Shorts 網址：",
                value=st.session_state[url_key],
                key=f"input_{url_key}",
                on_change=update_yt_url,
                args=(url_key,)
            )
            
            user_yt_link = st.session_state[url_key]

            if user_yt_link.strip():
                try:
                    embed_url = user_yt_link.strip()
                    video_id = ""
                    if "shorts/" in embed_url:
                        video_id = embed_url.split("shorts/")[-1].split("?")[0]
                    elif "watch?v=" in embed_url:
                        video_id = embed_url.split("watch?v=")[-1].split("&")[0]
                    elif "youtu.be/" in embed_url:
                        video_id = embed_url.split("youtu.be/")[-1].split("?")[0]
                        
                    if video_id:
                        embed_url = f"https://www.youtube.com/embed/{video_id}?loop=1&playlist={video_id}"
                    else:
                        embed_url = user_yt_link.strip()
                        
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center; margin-bottom: 15px; margin-top: 15px;">
                            <iframe width="350" height="580" src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                        </div>
                    """, unsafe_allow_html=True)
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
                copy_btn = st.button(f"📋 複製網址", key=f"copy_{absolute_idx}")
            with col_copy2:
                if copy_btn:
                    if user_yt_link.strip():
                        st.code(user_yt_link, language="text")
                    else:
                        st.warning("目前網址框是空的！")

        with right_col:
            user_input_text = st.session_state[text_key]
            encoded_text = urllib.parse.quote(user_input_text)
            translate_url = f"https://translate.google.com/?hl=zh-TW&sl=en&tl=zh-TW&text={encoded_text}&op=translate"

            title_col, btn_col = st.columns([3, 1.4], vertical_alignment="center")
            with title_col:
                st.subheader("✍️ 歌詞文字框與朗讀練習：")
            with btn_col:
                st.markdown(f'<a href="{translate_url}" target="_blank" class="translate-button">🌐 Google 翻譯</a>', unsafe_allow_html=True)

            def update_text_area(k):
                st.session_state[k] = st.session_state[f"textarea_{k}"]

            st.text_area(
                "輸入文字或歌詞：",
                value=st.session_state[text_key],
                key=f"textarea_{absolute_idx}",
                on_change=update_text_area,
                args=(text_key,)
            )
            
            user_input_text = st.session_state[text_key]

            col1, col2 = st.columns([1, 1])
            with col1:
                play_btn = st.button(f"🔊 播放整段發音 (循環)", key=f"play_{absolute_idx}")
            with col2:
                clear_btn = st.button(f"🗑️ 清空文字框", key=f"clear_{absolute_idx}")

            if clear_btn:
                st.session_state[text_key] = ""
                st.session_state[f"textarea_{absolute_idx}"] = ""
                st.rerun()

            if play_btn and user_input_text.strip():
                try:
                    tts = gTTS(text=user_input_text, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True, loop=True)
                except Exception as e:
                    st.error(f"語音生成發生錯誤：{e}")

        st.divider()

        # ----------------------------------------------------
        # 逐句互動輸入測驗區
        # ----------------------------------------------------
        st.subheader("✍️ 逐句英文輸入測驗與朗讀練習：")
        
        all_lines = user_input_text.split('\n')
        english_lines = [line.strip() for line in all_lines if line.strip() and re.search(r'[A-Za-z]', line)]
        
        if english_lines:
            st.markdown(f"<span style='font-size: 20px;'>**已自動抓取 {len(english_lines)} 個句子進行逐句練習（若有括號請輸入括號內的英文，不分大小寫，按 Enter 檢查）：**</span>", unsafe_allow_html=True)
            
            for line_idx, eng_sentence in enumerate(english_lines):
                st.markdown(f"---")
                st.markdown(f"<div class='sentence-display'>第 {line_idx + 1} 句原句：<br>✨ {eng_sentence}</div>", unsafe_allow_html=True)
                
                cols = st.columns([1.2, 4.2, 1])
                with cols[0]:
                    if st.button(f"🔊 聽發音", key=f"line_audio_{absolute_idx}_{line_idx}"):
                        try:
                            s_tts = gTTS(text=eng_sentence, lang='en')
                            s_fp = io.BytesIO()
                            s_tts.write_to_fp(s_fp)
                            st.audio(s_fp, autoplay=True)
                        except Exception as e:
                            st.error(f"語音錯誤：{e}")
                
                ans_key = f"ans_input_{absolute_idx}_{line_idx}"
                
                def make_clear_callback(k):
                    def clear_func():
                        st.session_state[k] = ""
                    return clear_func

                with cols[1]:
                    user_answer = st.text_input(
                        f"請輸入第 {line_idx + 1} 句英文：",
                        key=ans_key,
                        label_visibility="collapsed",
                        placeholder="請在此輸入括號內的英文，輸入完請直接按 Enter..."
                    )
                
                with cols[2]:
                    st.button(f"🗑️ 清除", key=f"clear_line_{absolute_idx}_{line_idx}", on_click=make_clear_callback(ans_key))
                
                if user_answer.strip():
                    bracket_match = re.search(r'[\(\（](.*?)[\)\）]', eng_sentence)
                    if bracket_match:
                        compare_target = bracket_match.group(1)
                    else:
                        compare_target = eng_sentence
                    
                    target_letters = "".join(re.findall(r'[A-Za-z0-9]', compare_target)).lower()
                    user_letters = "".join(re.findall(r'[A-Za-z0-9]', user_answer)).lower()
                    
                    if user_letters and user_letters == target_letters:
                        st.markdown(f"<span style='font-size: 22px; color: #28a745; font-weight: bold;'>🎉 答對了！英文拼寫正確，太棒囉！</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-size: 22px; color: #ff4b4b; font-weight: bold;'>❌ 英文拼寫有誤，再試一次看看喔！<br>💡 正確解答提示：{compare_target}</span>", unsafe_allow_html=True)
        else:
            st.info("💡 請在上方右側的查詢框輸入包含英文的句子，下方就會自動產生對應的逐句練習題囉！")

        st.divider()

        # 下方的單字解析區
        if user_input_text.strip():
            st.subheader("🔍 歌詞單字解析、KK音標與個別發音：")
            
            words_in_text = re.findall(r'\b[A-Za-z]+\b', user_input_text)
            unique_words = sorted(list(set(words_in_text)), key=lambda x: words_in_text.index(x))
            
            if unique_words:
                st.markdown(f"<span style='font-size: 20px;'>**偵測到以下英文單字（共 {len(unique_words)} 個）：**</span>", unsafe_allow_html=True)
                
                for w_idx, w in enumerate(unique_words):
                    w_lower = w.lower()
                    info = word_dict.get(w_lower, {"trans": "", "kk": ""})
                    kk_display = f"/{info['kk']}/" if info['kk'] else "(暫無KK音標)"
                    trans_display = f"【{info['trans']}】" if info['trans'] else ""
                    
                    cols = st.columns([3, 1, 2])
                    with cols[0]:
                        st.markdown(f"<span style='font-size: 22px;'>🔹 **{w}** &nbsp; ` {kk_display} ` &nbsp; <span style='color:gray;'>{trans_display}</span></span>", unsafe_allow_html=True)
                    with cols[1]:
                        if st.button(f"🔊 聽發音", key=f"word_audio_{absolute_idx}_{w_idx}_{w}"):
                            w_tts = gTTS(text=w, lang='en')
                            w_fp = io.BytesIO()
                            w_tts.write_to_fp(w_fp)
                            st.audio(w_fp, autoplay=True)
                    with cols[2]:
                        st.write("")
            else:
                st.info("請輸入包含英文的歌詞以便拆解單字。")
        else:
            st.warning("目前文字框是空的，請輸入或貼上想練習的整首歌詞！")
