import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .stTextArea textarea { font-size: 28px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院 & YouTube 影音學習工坊")

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
    
    if "level" in combined_df.columns:
        combined_df["level"] = pd.to_numeric(combined_df["level"], errors="coerce")
        combined_df = combined_df.sort_values(by="level", ascending=True)
        
    combined_df = combined_df.reset_index(drop=True)
    return combined_df

df = load_and_merge_data()

if 'selected_word' not in st.session_state:
    st.session_state.selected_word = df['word'].iloc[0] if not df.empty else ""

# 建立兩個分頁：一個是原本乾淨的單字查詢與發音，一個是 YouTube 影音學習
tab1, tab2 = st.tabs(["📚 單字總表與查字發音", "🎬 YouTube 影音隨看隨學"])

with tab1:
    st.subheader("📋 單字總表（點擊表格列即可聽發音）：")

    if not df.empty:
        display_df = df[['word', 'trans', 'kk', 'level']]
        
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="vocab_click_table_clean"
        )

        if len(event.selection.rows) > 0:
            selected_index = event.selection.rows[0]
            clicked_word = df.iloc[selected_index]['word']
            if st.session_state.selected_word != clicked_word:
                st.session_state.selected_word = clicked_word
                
                tts = gTTS(text=str(clicked_word), lang='en')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp, autoplay=True)

        st.divider()

        word_list = df['word'].tolist()
        if st.session_state.selected_word not in word_list:
            st.session_state.selected_word = word_list[0]

        st.subheader("🎯 單字快速搜尋與聆聽：")
        selected_word = st.selectbox(
            "目前選取的單字：",
            word_list,
            index=word_list.index(st.session_state.selected_word),
            key="selected_word_clean"
        )

        target_row = df[df['word'] == selected_word]
        if not target_row.empty:
            trans_w = target_row['trans'].values[0]
            kk_w = target_row['kk'].values[0] if 'kk' in target_row.columns else ""
            w_level = target_row['level'].values[0] if 'level' in target_row.columns else ""
            
            with st.container(border=True):
                st.markdown(f"### 🔍 單字詳情：`{selected_word}`")
                st.markdown(f"**中文翻譯：** {trans_w}")
                st.markdown(f"**KK 音標：** {kk_w} | **難度級別：** Level {w_level}")
                
                if st.button(f"🔊 播放 [{selected_word}] 標準發音", key="play_selected_word_btn"):
                    tts = gTTS(text=str(selected_word), lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)
    else:
        st.warning("目前沒有找到任何單字資料！")

with tab2:
    st.subheader("🌐 YouTube 影片隨看隨學與多段速練功坊")
    yt_url = st.text_input("請在此貼上 YouTube 影片或 Shorts 網址：", placeholder="https://www.youtube.com/watch?v=...", key="yt_url_input_clean")

    if yt_url:
        st.success("✅ 成功載入影片！請一邊觀看影片，一邊利用下方多段速按鈕進行聽力特訓：")
        st.video(yt_url)
        
        st.divider()
        st.subheader("📚 影音精選實用短句與多段速發音控制")
        
        sample_yt_sentences = [
            {"word": "effort", "trans": "努力", "sentence": "Persistent effort is the key to mastering any language."},
            {"word": "splendor", "trans": "壯麗", "sentence": "No travel guide could fully describe the true splendor of this place."},
            {"word": "routine", "trans": "日常", "sentence": "I try to learn something new in my daily routine."}
        ]
        
        for idx, item in enumerate(sample_yt_sentences):
            w = item["word"]
            trans = item["trans"]
            sentence = item["sentence"]
            
            with st.container(border=True):
                st.markdown(f"### 🔹 精選單字：`{w}` （{trans}）")
                st.markdown(f"**💡 例句：** {sentence}")
                
                st.markdown("🔊 **多段速發音練習：**")
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    if st.button(f"正常速度 🔊", key=f"norm_clean_{idx}_{w}"):
                        tts = gTTS(text=sentence, lang='en', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        st.audio(fp, autoplay=True)
                with col_s2:
                    if st.button(f"慢速練習 🐢", key=f"slow_clean_{idx}_{w}"):
                        tts = gTTS(text=sentence, lang='en', slow=True)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        st.audio(fp, autoplay=True)
                with col_s3:
                    if st.button(f"極慢拆解 🐌", key=f"x_slow_clean_{idx}_{w}"):
                        tts = gTTS(text=f"{w}... {w}... {sentence}", lang='en', slow=True)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        st.audio(fp, autoplay=True)
    else:
        st.info("💡 請在上方輸入框貼上想要學習的 YouTube 網址，即可在分頁中展開專屬影音學習！")
