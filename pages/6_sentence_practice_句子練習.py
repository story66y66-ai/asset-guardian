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
    }
    .yt-button:hover {
        background-color: #218838;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自訂文字與歌詞語音朗讀工坊")

# 1. 最上方的綠色任意門按鈕
yt_url = "https://www.youtube.com/@%E8%8B%B1%E8%AA%9E%E5%A4%A9%E5%A4%A9%E5%AD%B8/shorts?view=0&sort=p&flow=grid"
st.markdown(f'<a href="{yt_url}" target="_blank" class="yt-button">🔥 英語天天學熱門 Shorts 任意門</a>', unsafe_allow_html=True)

st.write("")

# 2. 新增：讓澄玄貼入 YouTube 網址的專屬輸入框與影片嵌入區
st.subheader("📺 YouTube 影片/Shorts 網址貼入與嵌入區：")
if "yt_input_url" not in st.session_state:
    st.session_state.yt_input_url = ""

user_yt_link = st.text_input("請在此貼上您喜歡的 YouTube 或 Shorts 網址：", value=st.session_state.yt_input_url)
st.session_state.yt_input_url = user_yt_link

if user_yt_link.strip():
    try:
        # 處理一般 YouTube 網址與 Shorts 網址轉換成嵌入格式 (embed)
        embed_url = user_yt_link.strip()
        if "shorts/" in embed_url:
            video_id = embed_url.split("shorts/")[-1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        elif "watch?v=" in embed_url:
            video_id = embed_url.split("watch?v=")[-1].split("&")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in embed_url:
            video_id = embed_url.split("youtu.be/")[-1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <iframe width="350" height="600" src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"影片載入發生錯誤，請確認網址是否正確：{e}")

st.divider()

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
