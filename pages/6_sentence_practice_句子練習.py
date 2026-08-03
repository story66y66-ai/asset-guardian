import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import urllib.parse

# 設定頁面為寬螢幕模式
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    
    /* 放大 YouTube 網址輸入框的文字與高度 */
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

# 建立 10 個分頁籤
tab_titles = [f"🎵 曲目 {i}" for i in range(1, 11)]
tabs = st.tabs(tab_titles)

# 迴圈建立 10 個分頁的獨立內容
for i, tab in enumerate(tabs):
    with tab:
        url_key = f"yt_input_url_{i}"
        text_key = f"my_text_input_{i}"
        
        if url_key not in st.session_state:
            st.session_state[url_key] = ""
            
        if text_key not in st.session_state:
            if i == 0:
                st.session_state[text_key] = "My Heart Will Go On 我心永恆\nEvery night in my dreams I see you, I feel you\n每個深夜在我的夢中，我見到你，感受到你"
            else:
                st.session_state[text_key] = ""

        # 左右雙欄排版：左側放影片，右側放歌詞文字框
        left_col, right_col = st.columns([1, 1.2], vertical_alignment="top")

        with left_col:
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
                        <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                            <iframe width="350" height="580" src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"影片載入發生錯誤：{e}")
            else:
                st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: center; height: 580px; border: 2px dashed #444; border-radius: 10px; color: #888; font-size: 20px; margin-bottom: 15px;">
                        📺 請在下方輸入網址以顯示影片
                    </div>
                """, unsafe_allow_html=True)

            new_yt_link = st.text_input(f"請在此貼上 YouTube 或 Shorts 網址：", value=st.session_state[url_key], key=f"input_{url_key}")
            if new_yt_link != st.session_state[url_key]:
                st.session_state[url_key] = new_yt_link
                st.rerun()

            col_copy1, col_copy2 = st.columns([1, 3])
            with col_copy1:
                copy_btn = st.button(f"📋 複製網址", key=f"copy_{i}")
            with col_copy2:
                if copy_btn:
                    if user_yt_link.strip():
                        st.code(user_yt_link, language="text")
                    else:
                        st.warning("目前網址框是空的！")

        with right_col:
            encoded_text = urllib.parse.quote(st.session_state[text_key])
            translate_url = f"https://translate.google.com/?hl=zh-TW&sl=en&tl=zh-TW&text={encoded_text}&op=translate"

            title_col, btn_col = st.columns([3, 1.4], vertical_alignment="center")
            with title_col:
                st.subheader("✍️ 歌詞文字框與朗讀練習：")
            with btn_col:
                st.markdown(f'<a href="{translate_url}" target="_blank" class="translate-button">🌐 Google 翻譯</a>', unsafe_allow_html=True)

            user_input_text = st.text_area(
                "輸入文字或歌詞：",
                value=st.session_state[text_key],
                key=f"textarea_{i}"
            )

            st.session_state[text_key] = user_input_text

            col1, col2 = st.columns([1, 1])
            with col1:
                play_btn = st.button(f"🔊 播放整段發音 (循環)", key=f"play_{i}")
            with col2:
                clear_btn = st.button(f"🗑️ 清空文字框", key=f"clear_{i}")

            if clear_btn:
                st.session_state[text_key] = ""
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
        # 逐句互動輸入測驗區（輸入完按 Enter 即自動比對）
        # ----------------------------------------------------
        st.subheader("✍️ 逐句英文輸入測驗與朗讀練習：")
        
        all_lines = user_input_text.split('\n')
        english_lines = [line.strip() for line in all_lines if line.strip() and re.search(r'[A-Za-z]', line)]
        
        if english_lines:
            st.markdown(f"<span style='font-size: 20px;'>**已自動抓取 {len(english_lines)} 個英文句子進行逐句練習（輸入完直接按 Enter 檢查）：**</span>", unsafe_allow_html=True)
            
            for line_idx, eng_sentence in enumerate(english_lines):
                st.markdown(f"---")
                st.markdown(f"<div class='sentence-display'>第 {line_idx + 1} 句原句：<br>✨ {eng_sentence}</div>", unsafe_allow_html=True)
                
                cols = st.columns([1.2, 5])
                with cols[0]:
                    if st.button(f"🔊 聽發音", key=f"line_audio_{i}_{line_idx}"):
                        try:
                            s_tts = gTTS(text=eng_sentence, lang='en')
                            s_fp = io.BytesIO()
                            s_tts.write_to_fp(s_fp)
                            st.audio(s_fp, autoplay=True)
                        except Exception as e:
                            st.error(f"語音錯誤：{e}")
                
                ans_key = f"ans_input_{i}_{line_idx}"
                
                with cols[1]:
                    user_answer = st.text_input(
                        f"請輸入第 {line_idx + 1} 句英文：",
                        key=ans_key,
                        label_visibility="collapsed",
                        placeholder="請在此輸入英文，輸入完請直接按 Enter..."
                    )
                
                # 只要輸入框有內容，按下 Enter (畫面重新整理) 後就會自動檢查答案
                if user_answer.strip():
                    clean_target = re.sub(r'\s+', ' ', eng_sentence).strip()
                    clean_user = re.sub(r'\s+', ' ', user_answer).strip()
                    
                    if clean_user.lower() == clean_target.lower():
                        st.markdown(f"<span style='font-size: 22px; color: #28a745; font-weight: bold;'>🎉 答對了！太棒囉！</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-size: 22px; color: #ff4b4b; font-weight: bold;'>❌ 再試一次看看喔！<br>💡 正確解答提示：{eng_sentence}</span>", unsafe_allow_html=True)
        else:
            st.info("💡 請在上方右側的「歌詞文字框」輸入包含英文的句子，下方就會自動產生對應的逐句練習題囉！")

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
                        if st.button(f"🔊 聽發音", key=f"word_audio_{i}_{w_idx}_{w}"):
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
