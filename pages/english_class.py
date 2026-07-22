import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import re
import random

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    .stTextArea textarea { font-size: 28px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院 & 單字本機智慧造句工坊")

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
        key="vocab_click_table_v15"
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
        if st.button("➕ 把此字加入清單", key="add_to_list_v15"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以點擊右側清除重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的清單", key="clear_list_v15"):
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("local_gen_v15_")]
            for k in keys_to_delete:
                del st.session_state[k]
            st.session_state.selected_vocab_list = []
            st.success("已清除清單與本機快取！")

    st.markdown(f"**📌 目前已選擇的單字（{len(st.session_state.selected_vocab_list)}/3）：**")
    if st.session_state.selected_vocab_list:
        st.write("、".join([f"**{w}**" for w in st.session_state.selected_vocab_list]))
    else:
        st.info("目前還沒有加入單字，請從上方點選喜歡的字後加入。")

    if st.session_state.selected_vocab_list:
        st.divider()
        st.subheader("✍️ 獨立單字多變造句工坊（從 Level 資料庫提取單字本地動態組合）")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            target_row = df[df['word'] == w]
            trans_w = target_row['trans'].values[0] if not target_row.empty else ""
            w_level = int(target_row['level'].values[0]) if (not target_row.empty and 'level' in target_row.columns and pd.notna(target_row['level'].values[0])) else 1
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w} | 難度Level {w_level}）")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    level_choice = st.selectbox("📚 程度：", ["初階", "中階", "高階"], key=f"lvl_v15_{idx}_{w}")
                with c2:
                    type_choice = st.selectbox("🔄 句型：", ["肯定句", "否定句", "疑問句"], key=f"typ_v15_{idx}_{w}")
                with c3:
                    scene_choice = st.selectbox("🌐 場合：", ["日常生活", "職場商務", "旅遊社交"], key=f"scn_v15_{idx}_{w}")
                
                state_key = f"local_gen_v15_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
                if state_key not in st.session_state:
                    # 從資料庫撈其他單字來豐富句子結構
                    other_words = df[df['word'] != w]['word'].tolist()
                    support_word1 = random.choice(other_words) if other_words else "time"
                    support_word2 = random.choice(other_words) if other_words else "place"
                    
                    # 根據場合與程度，利用資料庫單字在本地端拼湊出豐富句型
                    if scene_choice == "旅遊社交":
                        if level_choice == "初階":
                            if type_choice == "肯定句":
                                e_text = f"We can easily visit {w} near {support_word1}."
                                c_text = f"我們可以在 {support_word1} 附近輕鬆參觀 {w}。"
                            elif type_choice == "否定句":
                                e_text = f"We cannot visit {w} without {support_word1}."
                                c_text = f"沒有 {support_word1}，我們無法參觀 {w}。"
                            else:
                                e_text = f"Can we visit {w} near {support_word1}?"
                                c_text = f"我們可以在 {support_word1} 附近參觀 {w} 嗎？"
                        elif level_choice == "中階":
                            if type_choice == "肯定句":
                                e_text = f"Many travelers discovered {w} while exploring {support_word1}."
                                c_text = f"許多旅客在探索 {support_word1} 時發現了 {w}。"
                            elif type_choice == "否定句":
                                e_text = f"Tourists did not expect to find {w} around {support_word1}."
                                c_text = f"遊客沒想到會在 {support_word1} 周圍找到 {w}。"
                            else:
                                e_text = f"Did tourists find {w} while exploring {support_word1}?"
                                c_text = f"遊客在探索 {support_word1} 時有找到 {w} 嗎？"
                        else:
                            if type_choice == "肯定句":
                                e_text = f"An unexpected journey to {support_word1} revealed the true essence of {w}."
                                c_text = f"一趟前往 {support_word1} 的意外旅程揭示了 {w} 的真正本質。"
                            elif type_choice == "否定句":
                                e_text = f"No prior arrangement could prepare visitors for {w} at {support_word1}."
                                c_text = f"沒有任何事前安排能讓訪客對 {support_word1} 的 {w} 有所準備。"
                            else:
                                e_text = f"Could such a journey reveal {w} at {support_word1}?"
                                c_text = f"這樣的旅程能在 {support_word1} 揭示 {w} 嗎？"
                                
                    elif scene_choice == "職場商務":
                        if level_choice == "初階":
                            if type_choice == "肯定句":
                                e_text = f"Please check {w} before {support_word1}."
                                c_text = f"請在 {support_word1} 之前檢查 {w}。"
                            elif type_choice == "否定句":
                                e_text = f"Please do not change {w} during {support_word1}."
                                c_text = f"請不要在 {support_word1} 期間更改 {w}。"
                            else:
                                e_text = f"Should we check {w} before {support_word1}?"
                                c_text = f"我們應該在 {support_word1} 之前檢查 {w} 嗎？"
                        elif level_choice == "中階":
                            if type_choice == "肯定句":
                                e_text = f"The manager evaluated {w} during the {support_word1} meeting."
                                c_text = f"經理在 {support_word1} 會議期間評估了 {w}。"
                            elif type_choice == "否定句":
                                e_text = f"The team did not approve {w} for the {support_word1} project."
                                c_text = f"團隊未批准將 {w} 用於 {support_word1} 專案。"
                            else:
                                e_text = f"Did the team evaluate {w} during the {support_word1} meeting?"
                                c_text = f"團隊有在 {support_word1} 會議中評估 {w} 嗎？"
                        else:
                            if type_choice == "肯定句":
                                e_text = f"Comprehensive analysis regarding {w} was presented by {support_word1}."
                                c_text = f"關於 {w} 的全面分析由 {support_word1} 進行了報告。"
                            elif type_choice == "否定句":
                                e_text = f"No definitive conclusions regarding {w} were reached at {support_word1}."
                                c_text = f"在 {support_word1} 上沒有得出關於 {w} 的最終結論。"
                            else:
                                e_text = f"Was comprehensive analysis regarding {w} presented at {support_word1}?"
                                c_text = f"有關 {w} 的全面分析是在 {support_word1} 上提出的嗎？"
                                
                    else:  # 日常生活
                        if level_choice == "初階":
                            if type_choice == "肯定句":
                                e_text = f"I use {w} every {support_word1}."
                                c_text = f"我每個 {support_word1} 都會使用 {w}。"
                            elif type_choice == "否定句":
                                e_text = f"I do not need {w} for {support_word1}."
                                c_text = f"我不需要 {w} 來做 {support_word1}。"
                            else:
                                e_text = f"Do you use {w} every {support_word1}?"
                                c_text = f"你每個 {support_word1} 都會使用 {w} 嗎？"
                        elif level_choice == "中階":
                            if type_choice == "肯定句":
                                e_text = f"People often talk about {w} when they meet {support_word1}."
                                c_text = f"人們在遇到 {support_word1} 時經常談論 {w}。"
                            elif type_choice == "否定句":
                                e_text = f"She usually does not think about {w} during {support_word1}."
                                c_text = f"她在 {support_word1} 期間通常不會想到 {w}。"
                            else:
                                e_text = f"Do people talk about {w} when they meet {support_word1}?"
                                c_text = f"人們在遇到 {support_word1} 時會談論 {w} 嗎？"
                        else:
                            if type_choice == "肯定句":
                                e_text = f"Subtle changes in {w} often reflect {support_word1}."
                                c_text = f"中 {w} 的微妙變化經常反映出 {support_word1}。"
                            elif type_choice == "否定句":
                                e_text = f"Few individuals can truly grasp {w} without {support_word1}."
                                c_text = f"沒有 {support_word1}，很少有人能真正理解 {w}。"
                            else:
                                e_text = f"Do subtle changes in {w} reflect {support_word1}?"
                                c_text = f"{w} 的微妙變化反映了 {support_word1} 嗎？"

                    st.session_state[state_key] = {"eng": e_text, "chi": c_text}

                current_data = st.session_state[state_key]
                demo_eng = current_data["eng"]
                demo_chi = current_data["chi"]
                
                highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                
                st.markdown(f"**💡 本地智慧動態示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 示範句英文發音", key=f"audio_v15_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_v15_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}", height=90)
                if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_v15_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    if w.lower() in user_practice.lower():
                        st.success(f"🎉 太棒了！[{w}] 使用正確！")
                    else:
                        st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次!")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
