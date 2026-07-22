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
if 'challenge_sentence' not in st.session_state:
    st.session_state.challenge_sentence = {"eng": "", "chi": "", "words": []}

st.subheader("📋 單字總表（點擊表格中的單字列即可聽發音，並可勾選 3 個單字進行造句）：")

if not df.empty:
    display_df = df[['word', 'trans', 'kk', 'level']].copy()
    
    checked_words = st.session_state.get('checked_words_set', set())
    display_df.insert(0, '選擇', display_df['word'].isin(checked_words))

    # 使用 dataframe 結合 on_select 來達成點擊直接發音
    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="vocab_table"
    )

    # 如果點擊了某一行，直接取得該單字並自動發音
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        clicked_word = df.iloc[selected_index]['word']
        
        # 執行語音播放
        tts = gTTS(text=str(clicked_word), lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, autoplay=True)

    st.markdown("---")
    st.subheader("✨ 勾選造句區")
    st.write("請在上方表格左側的方框中**勾選剛好 3 個單字**，即可解鎖 AI 示範句：")

    # 為了讓使用者能夠勾選並即時反應，提供一個簡便的勾選管理介面或透過 data_editor 調整
    edited_df = st.data_editor(
        display_df,
        use_container_width=True,
        hide_index=True,
        disabled=['word', 'trans', 'kk', 'level'],
        key="vocab_editor_checkbox"
    )

    selected_rows = edited_df[edited_df['選擇'] == True]
    current_checked_words = selected_rows['word'].tolist()
    st.session_state['checked_words_set'] = set(current_checked_words)

    st.markdown(f"**📌 目前已勾選 {len(current_checked_words)} 個單字**：")
    if current_checked_words:
        st.write("、".join([f"**{w}**" for w in current_checked_words]))

    if len(current_checked_words) == 3:
        if st.button("🚀 根據這 3 個單字生成 AI 示範句", key="generate_btn"):
            w1, w2, w3 = current_checked_words[0], current_checked_words[1], current_checked_words[2]
            
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
                "words": current_checked_words,
                "trans": [t1, t2, t3]
            }

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
        
        if st.button("🔊 播放示範句語音", key="play_demo"):
            tts = gTTS(text=c_eng, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, autoplay=True)

        st.subheader("📝 請輸入您的造句練習：")
        user_input = st.text_area("在這裡輸入...", height=130, key="user_sentence_input")

        if st.button("✅ 檢查我的句子", key="check_sentence"):
            is_correct = all(str(w).lower() in user_input.lower() for w in c_words)
            if is_correct:
                st.success("## 太棒了！完全正確！包含了所有勾選的單字！")
                st.balloons()
            else:
                st.error("## ❌ 缺少部分勾選的關鍵字，請再檢查看看喔！")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
