import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import google.generativeai as genai

# 強制調整整體字體與側邊欄位字體
st.markdown("""
    <style>
    /* 放大左側選單欄位的字體 */
    [data-testid="stSidebar"] {
        font-size: 28px !important;
    }
    /* 放大選單內部的選項文字 */
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a {
        font-size: 28px !important;
    }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    .stTextArea textarea { font-size: 32px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院 & 造句實戰室")

# 背景自動合併與讀取資料函式
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

# 初始化 Session State
if 'selected_word' not in st.session_state:
    st.session_state.selected_word = df['word'].iloc[0] if not df.empty else ""

if 'selected_vocab_list' not in st.session_state:
    st.session_state.selected_vocab_list = []

if 'challenge_sentence' not in st.session_state:
    st.session_state.challenge_sentence = {"eng": "", "chi": "", "words": []}

st.subheader("📋 單字總表（點擊表格中的單字列即可直接聽發音）：")

if not df.empty:
    display_df = df[['word', 'trans', 'kk', 'level']]
    
    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="vocab_click_table"
    )

    # 如果點擊了表格中的某一行，更新 session_state 裡的選取單字並發音
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        clicked_word = df.iloc[selected_index]['word']
        if st.session_state.selected_word != clicked_word:
            st.session_state.selected_word = clicked_word
            
            # 播放發音
            tts = gTTS(text=str(clicked_word), lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, autoplay=True)

    st.divider()

    word_list = df['word'].tolist()
    if st.session_state.selected_word not in word_list:
        st.session_state.selected_word = word_list[0]

    st.subheader("🎯 造句實戰選字區（會與上方點擊同步）：")
    
    # 這裡直接用 selectbox，讓它完美對應 session_state.selected_word
    selected_word = st.selectbox(
        "目前選取的單字：",
        word_list,
        index=word_list.index(st.session_state.selected_word),
        key="selected_word"
    )

    # 加入到造句清單的按鈕
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➕ 把此字加入造句清單", key="add_to_list"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以先點擊「清除清單」重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的造句清單", key="clear_list"):
            st.session_state.selected_vocab_list = []
            st.success("已清除清單！")

    # 顯示目前已加入的單字清單（目標 3 個）
    st.markdown(f"**📌 目前已選擇的造句單字（{len(st.session_state.selected_vocab_list)}/3）：**")
    if st.session_state.selected_vocab_list:
        st.write("、".join([f"**{w}**" for w in st.session_state.selected_vocab_list]))
    else:
        st.info("目前還沒有加入單字，請從上方點選喜歡的字後，點擊「把此字加入造句清單」。")

    # 當剛好收集到 3 個單字時，顯示 AI 生成按鈕
    if len(st.session_state.selected_vocab_list) == 3:
        if st.button("✨ 根據這 3 個單字生成 AI 示範句", key="generate_ai_btn"):
            w1, w2, w3 = st.session_state.selected_vocab_list[0], st.session_state.selected_vocab_list[1], st.session_state.selected_vocab_list[2]
            
            t1 = df[df['word'] == w1]['trans'].values[0] if not df[df['word'] == w1].empty else ""
            t2 = df[df['word'] == w2]['trans'].values[0] if not df[df['word'] == w2].empty else ""
            t3 = df[df['word'] == w3]['trans'].values[0] if not df[df['word'] == w3].empty else ""

            eng_sent, chi_sent = "", ""
            try:
                if "general" in st.secrets and "GOOGLE_API_KEY" in st.secrets["general"]:
                    api_key = st.secrets["general"]["GOOGLE_API_KEY"]
                elif "GOOGLE_API_KEY" in st.secrets:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                else:
                    api_key = ""
                    
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                You are an expert English teacher. 
                I have 3 English words with their Chinese translations:
                1. {w1} ({t1})
                2. {w2} ({t2})
                3. {w3} ({t3})
                
                Please write ONE natural, logical, and grammatically correct English sentence that incorporates all 3 words together in a meaningful context.
                Then, provide its natural Traditional Chinese translation. 
                In the Chinese translation, format each target word strictly as: 中文翻譯(English_word).
                
                Return ONLY valid text in this exact format, with no extra markdown or conversational filler:
                ENGLISH: [Your English sentence here]
                CHINESE: [Your Chinese translation here]
                """
                response = model.generate_content(prompt)
                text = response.text.strip()
                
                for line in text.split('\n'):
                    if line.startswith("ENGLISH:"):
                        eng_sent = line.replace("ENGLISH:", "").strip()
                    elif line.startswith("CHINESE:"):
                        chi_sent = line.replace("CHINESE:", "").strip()
                
                if not eng_sent or not chi_sent:
                    raise Exception("Invalid AI format")
            except Exception as e:
                eng_sent = f"Please configure GOOGLE_API_KEY in Streamlit Secrets to let AI generate sentences for: {w1}, {w2}, {w3}."
                chi_sent = f"請在 Streamlit Secrets 設定 GOOGLE_API_KEY：{t1}({w1})、{t2}({w2})、{t3}({w3})。"

            st.session_state.challenge_sentence = {
                "eng": eng_sent,
                "chi": chi_sent,
                "words": st.session_state.selected_vocab_list.copy(),
                "trans": [t1, t2, t3]
            }

    # 如果已經生成句子，顯示在下方供造句練習
    if st.session_state.challenge_sentence["eng"]:
        st.divider()
        st.subheader("💡 助教示範句：")
        
        c_words = st.session_state.challenge_sentence["words"]
        c_eng = st.session_state.challenge_sentence["eng"]
        c_chi = st.session_state.challenge_sentence["chi"]
        
        colored_sent = c_eng
        for w in c_words:
            pattern = re.compile(r'\b' + re.escape(str(w)) + r'\b', re.IGNORECASE)
            colored_sent = pattern.sub(f"<span class='red-word'>{w}</span>", colored_sent)
            
        st.markdown(f"### {colored_sent}", unsafe_allow_html=True)
        st.markdown(f"*(中文：{c_chi})*", unsafe_allow_html=True)
        
        if st.button("🔊 播放示範句語音", key="play_demo_audio"):
            tts = gTTS(text=c_eng, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, autoplay=True)

        st.subheader("📝 請輸入您的造句練習：")
        user_input = st.text_area("在這裡輸入...", height=130, key="user_sentence_input_box")

        if st.button("✅ 檢查我的句子", key="check_user_sentence"):
            is_correct = all(str(w).lower() in user_input.lower() for w in c_words)
            if is_correct:
                st.success("## 太棒了！完全正確！包含了所有選取的單字！")
                st.balloons()
            else:
                st.error("## ❌ 缺少部分選取的關鍵字，請再檢查看看喔！")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
