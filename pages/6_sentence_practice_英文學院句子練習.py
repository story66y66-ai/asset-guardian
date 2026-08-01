import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    .stTextArea textarea { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 300px !important;
        resize: vertical !important; 
    }
    div.stButton > button { font-size: 20px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

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

st.subheader("✍️ 請在下方文字框輸入或貼上整首歌詞（可自由拉曳放大）：")

if "my_text_input" not in st.session_state:
    st.session_state.my_text_input = "I can do all things through Christ who strengthens me."

user_input_text = st.text_area(
    "輸入文字或歌詞：",
    value=st.session_state.my_text_input
)

st.session_state.my_text_input = user_input_text

col1, col2 = st.columns([1, 4])
with col1:
    play_btn = st.button("🔊 播放整段發音")
with col2:
    clear_btn = st.button("🗑️ 清空文字框")

if clear_btn:
    st.session_state.my_text_input = ""
    st.rerun()

if play_btn and user_input_text.strip():
    try:
        tts = gTTS(text=user_input_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, autoplay=True)
    except Exception as e:
        st.error(f"語音生成發生錯誤：{e}")

st.divider()

if user_input_text.strip():
    st.subheader("🔍 歌詞單字解析、KK音標與個別發音：")
    
    # 抓出不重複的單字（保留原本順序）
    words_in_text = re.findall(r'\b[A-Za-z]+\b', user_input_text)
    unique_words = sorted(list(set(words_in_text)), key=lambda x: words_in_text.index(x))
    
    if unique_words:
        st.markdown(f"**偵測到以下英文單字（共 {len(unique_words)} 個）：**")
        
        for i, w in enumerate(unique_words):
            w_lower = w.lower()
            info = word_dict.get(w_lower, {"trans": "", "kk": ""})
            kk_display = f"/{info['kk']}/" if info['kk'] else "(暫無KK音標)"
            trans_display = f"【{info['trans']}】" if info['trans'] else ""
            
            cols = st.columns([3, 1, 2])
            with cols[0]:
                st.markdown(f"🔹 **{w}** &nbsp; ` {kk_display} ` &nbsp; <span style='color:gray;'>{trans_display}</span>", unsafe_allow_html=True)
            with cols[1]:
                if st.button(f"🔊 聽發音", key=f"word_audio_{i}_{w}"):
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
