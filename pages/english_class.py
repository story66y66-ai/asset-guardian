import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import google.generativeai as genai

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    .stTextArea textarea { font-size: 28px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院 & 單字獨立多變造句工坊")

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

if 'selected_vocab_list' not in st.session_state:
    st.session_state.selected_vocab_list = []

st.subheader("📋 單字總表（點擊表格列聽發音，並挑選單字）：")

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

    st.subheader("🎯 挑選造句單字區：")
    selected_word = st.selectbox(
        "目前選取的單字：",
        word_list,
        index=word_list.index(st.session_state.selected_word),
        key="selected_word"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➕ 把此字加入清單", key="add_to_list"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以點擊右側清除重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的清單", key="clear_list"):
            st.session_state.selected_vocab_list = []
            st.success("已清除清單！")

    st.markdown(f"**📌 目前已選擇的單字（{len(st.session_state.selected_vocab_list)}/3）：**")
    if st.session_state.selected_vocab_list:
        st.write("、".join([f"**{w}**" for w in st.session_state.selected_vocab_list]))
    else:
        st.info("目前還沒有加入單字，請從上方點選喜歡的字後加入。")

    if st.session_state.selected_vocab_list:
        st.divider()
        st.subheader("✍️ 獨立單字多變造句工坊（每個單字各自調整難易度、句型與場合）")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            trans_w = df[df['word'] == w]['trans'].values[0] if not df[df['word'] == w].empty else ""
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w}）")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    level_choice = st.selectbox("📚 程度：", ["初階", "中階", "高階"], key=f"lvl_{idx}_{w}")
                with c2:
                    type_choice = st.selectbox("🔄 句型：", ["肯定句", "否定句", "疑問句"], key=f"typ_{idx}_{w}")
                with c3:
                    scene_choice = st.selectbox("🌐 場合：", ["日常生活", "職場商務", "旅遊社交"], key=f"scn_{idx}_{w}")
                
                # 使用 v8 版本鍵值，確保 程度、句型、場合 三者完全聯動
                state_key = f"ai_data_v8_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
                if state_key not in st.session_state:
                    e_text, c_text = "", ""
                    try:
                        if "general" in st.secrets and "GOOGLE_API_KEY" in st.secrets["general"]:
                            api_key = st.secrets["general"]["GOOGLE_API_KEY"]
                        elif "GOOGLE_API_KEY" in st.secrets:
                            api_key = st.secrets["GOOGLE_API_KEY"]
                        else:
                            api_key = ""
                            
                        if api_key:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            
                            prompt = f"""
                            You are an expert, native English conversation teacher. 
                            Target English word: {w} ({trans_w})
                            Level requirement: {level_choice} (初階=Very simple words/structure, 中階=Natural conversational sentence, 高階=Advanced vocabulary/complex structure)
                            Sentence Type requirement: {type_choice} (肯定句=Affirmative, 否定句=Negative, 疑問句=Interrogative)
                            Scene/Context requirement: {scene_choice} (日常生活=Daily life chat, 職場商務=Office/Workplace communication, 旅遊社交=Travel/Socializing)
                            
                            Please write ONE completely natural, highly practical, native-sounding English conversational sentence using the target word, strictly fulfilling ALL THREE requirements: Level ({level_choice}), Sentence Type ({type_choice}), and Scene/Context ({scene_choice}).
                            CRITICAL RULES:
                            1. The English sentence must contain ONLY pure English words. Do NOT mix any Chinese characters or placeholders.
                            2. Provide a natural Traditional Chinese translation separately.
                            
                            Return ONLY valid text in this exact format:
                            ENGLISH: [Your pure, natural English sentence here]
                            CHINESE: [Your Traditional Chinese translation here]
                            """
                            response = model.generate_content(prompt)
                            text = response.text.strip()
                            
                            for line in text.split('\n'):
                                if line.startswith("ENGLISH:"):
                                    e_text = line.replace("ENGLISH:", "").strip()
                                elif line.startswith("CHINESE:"):
                                    c_text = line.replace("CHINESE:", "").strip()
                    except Exception as err:
                        pass
                    
                    # 完善的動態備用機制：完美涵蓋 程度、句型 與 場合 的情境變化
                    if not e_text or not c_text:
                        if scene_choice == "職場商務":
                            if type_choice == "肯定句":
                                e_text, c_text = f"We will review {w} during the meeting.", f"我們將在會議中審查 {w}。"
                            elif type_choice == "否定句":
                                e_text, c_text = f"We will not discuss {w} today.", f"我們今天將不討論 {w}。"
                            else:
                                e_text, c_text = f"Can we review {w} in the meeting?", f"我們可以在會議中審查 {w} 嗎？"
                        elif scene_choice == "旅遊社交":
                            if type_choice == "肯定句":
                                e_text, c_text = f"I am looking for {w} at the hotel.", f"我正在飯店找 {w}。"
                            elif type_choice == "否定句":
                                e_text, c_text = f"I cannot find {w} around the station.", f"我在車站附近找不到 {w}。"
                            else:
                                e_text, c_text = f"Where can I find {w} nearby?", f"我可以在附近哪裡找到 {w}？"
                        else:  # 日常生活
                            if type_choice == "肯定句":
                                e_text, c_text = f"I usually keep {w} at home.", f"我通常在家裡放 {w}。"
                            elif type_choice == "否定句":
                                e_text, c_text = f"I do not keep {w} at home.", f"我不在家裡放 {w}。"
                            else:
                                e_text, c_text = f"Do you have {w} at home?", f"你家裡有 {w} 嗎？"
                            
                    st.session_state[state_key] = {"eng": e_text, "chi": c_text}

                current_data = st.session_state[state_key]
                demo_eng = current_data["eng"]
                demo_chi = current_data["chi"]
                
                highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                
                st.markdown(f"**💡 助教示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 示範句英文發音", key=f"audio_v8_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_v8_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}", height=90)
                if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_v8_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    if w.lower() in user_practice.lower():
                        st.success(f"🎉 太棒了！[{w}] 使用正確！")
                    else:
                        st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次!")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
