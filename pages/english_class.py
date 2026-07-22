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
                
                # 【關鍵修復】state_key 完整納入 level, type, scene，確保場合與句型能完美獨立切換！
                state_key = f"ai_data_v10_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
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
                    
                    # 智慧動態備用機制（完美對應各場合與句型，不再讓怪異字串亂跑）
                    if not e_text or not c_text:
                        if scene_choice == "旅遊社交":
                            if level_choice == "初階":
                                if type_choice == "肯定句":
                                    e_text, c_text = f"We can meet {w} the hotel lobby.", f"我們可以在飯店大廳見面。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"We cannot meet {w} the hotel lobby.", f"我們無法在飯店大廳見面。"
                                else:
                                    e_text, c_text = f"Can we meet {w} the hotel lobby?", f"我們可以在飯店大廳見面嗎？"
                            elif level_choice == "中階":
                                if type_choice == "肯定句":
                                    e_text, c_text = f"Tourists usually gather {w} this famous square.", f"遊客通常會聚集在這個著名的廣場。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"Tourists do not usually gather {w} this famous square.", f"遊客通常不會聚集在這個著名的廣場。"
                                else:
                                    e_text, c_text = f"Do tourists usually gather {w} this famous square?", f"遊客通常會聚集在這個著名的廣場嗎？"
                            else:
                                if type_choice == "肯定句":
                                    e_text, c_text = f"An unforgettable experience awaits guests {w} the resort.", f"難忘的體驗在度假村等待著賓客。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"No unforgettable experience awaits guests {w} the resort.", f"度假村沒有為賓客提供難忘的體驗。"
                                else:
                                    e_text, c_text = f"Does any unforgettable experience await guests {w} the resort?", f"度假村是否有提供賓客難忘的體驗呢？"
                        elif scene_choice == "職場商務":
                            if level_choice == "初階":
                                if type_choice == "肯定句":
                                    e_text, c_text = f"The meeting starts {w} nine o'clock.", f"會議在九點開始。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"The meeting does not start {w} nine o'clock.", f"會議不是在九點開始。"
                                else:
                                    e_text, c_text = f"Does the meeting start {w} nine o'clock?", f"會議是在九點開始嗎？"
                            elif level_choice == "中階":
                                if type_choice == "肯定句":
                                    e_text, c_text = f"We need to finish the project {w} this stage.", f"我們需要在這個階段完成專案。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"We do not need to finish the project {w} this stage.", f"我們不需要在這個階段完成專案。"
                                else:
                                    e_text, c_text = f"Do we need to finish the project {w} this stage?", f"我們需要在這個階段完成專案嗎？"
                            else:
                                if type_choice == "肯定句":
                                    e_text, c_text = f"Key performance metrics were evaluated {w} the quarterly review.", f"在季度評估中評估了關鍵績效指標。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"No key performance metrics were evaluated {w} the quarterly review.", f"在季度評估中未評估關鍵績效指標。"
                                else:
                                    e_text, c_text = f"Were key performance metrics evaluated {w} the quarterly review?", f"在季度評估中是否評估了關鍵績效指標？"
                        else:  # 日常生活
                            if level_choice == "初階":
                                if type_choice == "肯定句":
                                    e_text, c_text = f"I am resting {w} home today.", f"我今天在家休息。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"I am not resting {w} home today.", f"我今天沒有在家休息。"
                                else:
                                    e_text, c_text = f"Are you resting {w} home today?", f"你今天在家休息嗎？"
                            elif level_choice == "中階":
                                if type_choice == "肯定句":
                                    e_text, c_text = f"She likes to read books {w} night.", f"她喜歡在晚上看書。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"She does not like to read books {w} night.", f"她不喜歡在晚上看書。"
                                else:
                                    e_text, c_text = f"Does she like to read books {w} night?", f"她喜歡在晚上看書嗎？"
                            else:
                                if type_choice == "肯定句":
                                    e_text, c_text = f"Peaceful moments can be truly appreciated {w} dawn.", f"在黎明時分可以真正體會到平靜的時刻。"
                                elif type_choice == "否定句":
                                    e_text, c_text = f"Peaceful moments cannot be truly appreciated {w} dawn.", f"在黎明時分無法真正體會到平靜的時刻。"
                                else:
                                    e_text, c_text = f"Can peaceful moments be truly appreciated {w} dawn?", f"在黎明時分真的能體會到平靜的時刻嗎？"
                            
                    st.session_state[state_key] = {"eng": e_text, "chi": c_text}

                current_data = st.session_state[state_key]
                demo_eng = current_data["eng"]
                demo_chi = current_data["chi"]
                
                highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                
                st.markdown(f"**💡 助教示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 示範句英文發音", key=f"audio_v10_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_v10_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}", height=90)
                if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_v10_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    if w.lower() in user_practice.lower():
                        st.success(f"🎉 太棒了！[{w}] 使用正確！")
                    else:
                        st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次!")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
