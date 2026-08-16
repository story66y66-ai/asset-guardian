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

    .stTextArea textarea {
        font-size: 22px !important;
        color: #ffffff !important;
        font-weight: bold !important;
        line-height: 1.5 !important;
    }

    div[data-baseweb="base-input"] textarea {
        font-size: 22px !important;
        color: #ffffff !important;
        font-weight: bold !important;
        line-height: 1.5 !important;
    }
    
    .sentence-display {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        line-height: 1.6 !important;
    }

    .chinese-hint {
        font-size: 20px !important;
        color: #a0a0a0 !important;
        font-style: italic !important;
        margin-bottom: 8px !important;
    }

    .yt-button {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #28a745; color: white !important; padding: 10px 20px;
        border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%;
    }
    .notebook-button {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #4285F4; color: white !important; padding: 10px 20px;
        border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; border: none; width: 100%;
    }
    .translate-button {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #1a73e8; color: white !important; padding: 6px 14px;
        border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 16px; border: none; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

# 最上方的兩個專屬按鈕
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    yt_url_top = "https://www.youtube.com/@%E8%8B%B1%E8%AA%9E%E5%A4%A9%E5%A4%A9%E5%AD%B8/shorts?view=0&sort=p&flow=grid"
    st.markdown(f'<a href="{yt_url_top}" target="_blank" class="yt-button">🔥 英語天天學熱門 Shorts 任意門</a>', unsafe_allow_html=True)
with col_btn2:
    notebook_url = "https://notebooklm.google.com/"
    st.markdown(f'<a href="{notebook_url}" target="_blank" class="notebook-button">✨ 澄玄的隨身英文秘書任意門</a>', unsafe_allow_html=True)

st.write("")

# === 全覆蓋讀取詞庫函式 ===
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
                if col not in df.columns:
                    df[col] = ""
            all_data.append(df[expected_cols])
        except Exception:
            continue
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df = final_df.dropna(subset=["word"])
        final_df = final_df.drop_duplicates(subset=["word"], keep='last')
        return final_df
    else:
        return pd.DataFrame(columns=expected_cols)

df = load_and_merge_data()

word_dict = {}
if not df.empty and "word" in df.columns:
    for _, row in df.iterrows():
        w_str = str(row['word']).strip().lower()
        trans_str = str(row['trans']) if pd.notna(row['trans']) else ""
        kk_str = str(row['kk']) if pd.notna(row['kk']) else ""
        word_dict[w_str] = {"trans": trans_str, "kk": kk_str}

# === 頁面與曲目狀態初始化 ===
if "page_names" not in st.session_state:
    st.session_state.page_names = {p: f"第 {p} 頁 (曲目 {(p-1)*10 + 1} ~ {p*10})" for p in range(1, 6)}

if "playlist_names" not in st.session_state:
    st.session_state.playlist_names = {idx: f"曲目 {idx}" for idx in range(1, 51)}

for idx in range(1, 51):
    if f"yt_input_url_{idx}" not in st.session_state:
        st.session_state[f"yt_input_url_{idx}"] = ""
    if f"my_text_input_{idx}" not in st.session_state:
        st.session_state[f"my_text_input_{idx}"] = ""

# 自動讀取已儲存的資料庫檔案
if os.path.exists("playlist_heart_歌曲結連庫.csv"):
    try:
        saved_df = pd.read_csv("playlist_heart_歌曲結連庫.csv", encoding='utf-8-sig')
        for _, row in saved_df.iterrows():
            idx_val = int(row['id'])
            if 1 <= idx_val <= 50:
                if pd.notna(row.get('url')):
                    st.session_state[f"yt_input_url_{idx_val}"] = str(row['url'])
                if pd.notna(row.get('title')):
                    st.session_state.playlist_names[idx_val] = str(row['title'])
                if pd.notna(row.get('lyrics')):
                    st.session_state[f"my_text_input_{idx_val}"] = str(row['lyrics'])
    except Exception:
        pass

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

st.write("")

# 建立匯出 DataFrame
csv_data_list = []
for idx in range(1, 51):
    csv_data_list.append({
        "id": idx,
        "url": st.session_state.get(f"yt_input_url_{idx}", "").strip(),
        "title": st.session_state.playlist_names.get(idx, f"曲目 {idx}"),
        "lyrics": st.session_state.get(f"my_text_input_{idx}", "")
    })

df_export = pd.DataFrame(csv_data_list)
csv_text_output = df_export.to_csv(index=False, encoding="utf-8-sig", quoting=1)

with st.expander("📥 產生並下載包含完整歌詞的 CSV 庫（支援 Excel 直接開啟與 GitHub）"):
    st.download_button(
        label="📥 點我直接下載 playlist_heart_歌曲結連庫.csv 檔案",
        data=csv_text_output,
        file_name="playlist_heart_歌曲結連庫.csv",
        mime="text/csv",
        use_container_width=True
    )

st.write("")
st.markdown("<h3 style='font-size: 26px; color: #ffffff;'>📚 選擇練習冊（翻書頁面）：</h3>", unsafe_allow_html=True)

page_cols = st.columns(5)
for p in range(1, 6):
    with page_cols[p-1]:
        btn_label = f"👉 【第 {p} 頁】" if st.session_state.current_page == p else f"第 {p} 頁"
        if st.button(btn_label, key=f"page_btn_{p}", use_container_width=True):
            st.session_state.current_page = p
            st.rerun()

current_page = st.session_state.current_page
st.write("")

start_idx = (current_page - 1) * 10 + 1
end_idx = current_page * 10

tab_titles = [f"第 {idx} 首\n{st.session_state.playlist_names[idx]}" for idx in range(start_idx, end_idx + 1)]
tabs = st.tabs(tab_titles)

for tab_idx, tab in enumerate(tabs):
    absolute_idx = start_idx + tab_idx
    
    with tab:
        url_key = f"yt_input_url_{absolute_idx}"
        text_key = f"my_text_input_{absolute_idx}"

        st.subheader(f"第 {absolute_idx} 首")
        with st.expander(f"✏️ 修改【曲目 {absolute_idx}】的歌名或用途"):
            curr_name = st.session_state.playlist_names[absolute_idx]
            new_track_name = st.text_input(f"曲目 {absolute_idx} 名稱：", value=curr_name, key=f"rename_track_{absolute_idx}")
            if new_track_name != curr_name:
                st.session_state.playlist_names[absolute_idx] = new_track_name
                df_export.to_csv("playlist_heart_歌曲結連庫.csv", index=False, encoding="utf-8-sig", quoting=1)
                st.rerun()

        left_col, right_col = st.columns([1, 1.2], vertical_alignment="top")

        # 左側：YouTube 影片與網址區
        with left_col:
            user_yt_link = st.text_input(
                f"請在此貼上 YouTube 或 Shorts 網址：",
                value=st.session_state[url_key],
                key=f"input_{url_key}"
            )
            st.session_state[url_key] = user_yt_link

            # 💾 儲存按鈕（明確加入點擊觸發與狀態儲存）
            if st.button(f"💾 儲存【曲目 {absolute_idx}】的資料", key=f"save_url_{absolute_idx}", use_container_width=True):
                update_list_all = []
                for idx_sub in range(1, 51):
                    update_list_all.append({
                        "id": idx_sub,
                        "url": st.session_state.get(f"yt_input_url_{idx_sub}", "").strip(),
                        "title": st.session_state.playlist_names.get(idx_sub, f"曲目 {idx_sub}"),
                        "lyrics": st.session_state.get(f"my_text_input_{idx_sub}", "")
                    })
                df_to_save = pd.DataFrame(update_list_all)
                df_to_save.to_csv("playlist_heart_歌曲結連庫.csv", index=False, encoding="utf-8-sig", quoting=1)
                st.success(f"🎉 【曲目 {absolute_idx}】的資料已成功儲存完成！")
                st.balloons()
                st.rerun()

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
                except Exception as e:
                    st.error(f"影片載入發生錯誤：{e}")

        # 右側：歌詞文字框與朗讀區
        with right_col:
            title_col, btn_col = st.columns([3, 1.4], vertical_alignment="center")
            with title_col:
                st.subheader("✍️ 歌詞文字框與朗讀練習：")
            with btn_col:
                encoded_text = urllib.parse.quote(st.session_state[text_key])
                translate_url = f"https://translate.google.com/?hl=zh-TW&sl=en&tl=zh-TW&text={encoded_text}&op=translate"
                st.markdown(f'<a href="{translate_url}" target="_blank" class="translate-button">🌐 Google 翻譯</a>', unsafe_allow_html=True)

            user_input_text = st.text_area(
                "輸入文字或歌詞：",
                value=st.session_state[text_key],
                key=f"textarea_{absolute_idx}",
                height=650
            )
            st.session_state[text_key] = user_input_text

            col1, col2, col3, col4 = st.columns([1.2, 1.2, 1, 1])
            with col1:
                play_btn = st.button(f"🔊 播放整段", key=f"play_{absolute_idx}")
            with col2:
                smart_split_btn = st.button(f"✨ 智慧分句排版", key=f"split_{absolute_idx}")
            with col3:
                update_trans_btn = st.button(f"🔄 更新翻譯", key=f"update_t_{absolute_idx}")
            with col4:
                clear_btn = st.button(f"🗑️ 清空", key=f"clear_{absolute_idx}")

            if clear_btn:
                st.session_state[text_key] = ""
                st.rerun()

            if smart_split_btn and user_input_text.strip():
                raw_text = user_input_text.replace("\n", " ")
                words_list = raw_text.split()
                new_lines = []
                current_line = []
                for w in words_list:
                    if w.lower() in ["that", "i", "you", "and", "where", "when"] and len(current_line) >= 4:
                        new_lines.append(" ".join(current_line))
                        current_line = [w]
                    else:
                        current_line.append(w)
                if current_line:
                    new_lines.append(" ".join(current_line))
                st.session_state[text_key] = "\n".join(new_lines)
                st.rerun()

            if play_btn and user_input_text.strip():
                try:
                    tts = gTTS(text=user_input_text, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True, loop=True)
                except Exception as e:
                    st.error(f"語音錯誤：{e}")

        st.divider()

        # === 逐句英文輸入測驗區（含中文自動提示與清除鍵） ===
        st.subheader("✍️ 逐句英文輸入測驗與朗讀練習：")
        
        lines = [line.strip() for line in user_input_text.split('\n') if line.strip()]
        
        pairs = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.search(r'[A-Za-z]', line):
                eng_line = line
                zh_hint = None
                if i + 1 < len(lines) and not re.search(r'[A-Za-z]', lines[i + 1]):
                    zh_hint = lines[i + 1]
                    i += 1
                pairs.append((eng_line, zh_hint))
            i += 1
        
        if pairs:
            for line_idx, (eng_sentence, zh_hint) in enumerate(pairs):
                st.markdown(f"---")
                st.markdown(f"<div class='sentence-display'>第 {line_idx + 1} 句原句：<br>✨ {eng_sentence}</div>", unsafe_allow_html=True)
                
                if zh_hint:
                    st.markdown(f"<div class='chinese-hint'>中文對應：{zh_hint}</div>", unsafe_allow_html=True)
                
                cols = st.columns([1.1, 1.4, 3.5, 1])
                with cols[0]:
                    if st.button(f"🔊 聽發音", key=f"line_audio_{absolute_idx}_{line_idx}"):
                        try:
                            s_tts = gTTS(text=eng_sentence, lang='en', slow=False)
                            s_fp = io.BytesIO()
                            s_tts.write_to_fp(s_fp)
                            st.audio(s_fp, autoplay=True)
                        except Exception as e:
                            st.error(f"語音錯誤：{e}")
                            
                with cols[1]:
                    clean_sentence = re.sub(r'[\(\„\“\“\”\‘\’\(\’].*?[\)\）\”\‘\’]', '', eng_sentence).strip()
                    safe_sentence_js = clean_sentence.replace("'", "\\'")
                    components.html(f"""
                        <button onclick="
                            const utterance = new SpeechSynthesisUtterance('{safe_sentence_js}');
                            utterance.lang = 'en-US';
                            utterance.rate = 0.4;
                            window.speechSynthesis.cancel();
                            window.speechSynthesis.speak(utterance);
                        " style="
                            background-color: #f0f2f6; color: #262730; border: 1px solid #d6d6d8;
                            padding: 8px 12px; border-radius: 4px; font-size: 16px; font-weight: bold;
                            cursor: pointer; width: 100%;
                        ">🐢 0.4倍超慢</button>
                    """, height=45)
                
                ans_key = f"ans_input_{absolute_idx}_{line_idx}"
                
                def make_clear_callback(k):
                    def clear_func():
                        st.session_state[k] = ""
                    return clear_func

                with cols[2]:
                    user_answer = st.text_input(
                        f"請輸入第 {line_idx + 1} 句英文：",
                        key=ans_key,
                        label_visibility="collapsed",
                        placeholder="請在此輸入對應的英文..."
                    )
                
                with cols[3]:
                    st.button(f"🗑️ 清除", key=f"clear_line_{absolute_idx}_{line_idx}", on_click=make_clear_callback(ans_key))
                
                if user_answer.strip():
                    clean_target = re.sub(r'[\(\（].*?[\)\）]', '', eng_sentence).strip()
                    target_letters = "".join(re.findall(r'[A-Za-z ]', clean_target)).lower()
                    user_letters = "".join(re.findall(r'[A-Za-z ]', user_answer)).lower()
                    
                    if user_letters and user_letters == target_letters:
                        st.markdown(f"<span style='font-size: 22px; color: #28a745; font-weight: bold;'>🎉 答對了！英文拼寫正確！</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-size: 22px; color: #ff4b4b; font-weight: bold;'>❌ 拼寫有誤，再試一次！💡 提示：{clean_target}</span>", unsafe_allow_html=True)
        else:
            st.info("💡 請在上方歌詞框輸入內容（英文與中文交替換行），下方就會自動產生對應的測驗與中文提示囉！")

        st.divider()

        # 單字解析區
        if user_input_text.strip():
            st.subheader("🔍 歌詞單字解析、KK音標與個別發音：")
            words_in_text = re.findall(r'\b[A-Za-z]+\b', user_input_text)
            unique_words = sorted(list(set(words_in_text)), key=lambda x: words_in_text.index(x))
            
            if unique_words:
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
