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
        key="vocab_click_table_v16"
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
        if st.button("➕ 把此字加入清單", key="add_to_list_v16"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以點擊右側清除重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的清單", key="clear_list_v16"):
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("local_gen_v16_")]
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
        st.subheader("✍️ 獨立單字多變造句工坊（本機文法智慧生成）")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            target_row = df[df['word'] == w]
            trans_w = target_row['trans'].values[0] if not target_row.empty else ""
            w_level = int(target_row['level'].values[0]) if (not target_row.empty and 'level' in target_row.columns and pd.notna(target_row['level'].values[0])) else 1
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w} | 難度Level {w_level}）")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    level_choice = st.selectbox("📚 程度：", ["初階", "中階", "高階"], key=f"lvl_v16_{idx}_{w}")
                with c2:
                    type_choice = st.selectbox("🔄 句型：", ["肯定句", "否定句", "疑問句"], key=f"typ_v16_{idx}_{w}")
                with c3:
                    scene_choice = st.selectbox("🌐 場合：", ["日常生活", "職場商務", "旅遊社交"], key=f"scn_v16_{idx}_{w}")
                
                state_key = f"local_gen_v16_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
                if state_key not in st.session_state:
                    # 針對特殊單字或一般單字建立極具文法邏輯的句型庫
                    w_lower = w.lower()
                    
                    if w_lower in ["a", "an", "the"]:
                        if type_choice == "否定句":
                            e_text = f"This is not just {w} ordinary situation."
                            c_text = f"這不只是個普通的狀況。"
                        elif type_choice == "疑問句":
                            e_text = f"Is this {w} good choice for us?"
                            c_text = f"這對我們來說是個好選擇嗎？"
                        else:
                            e_text = f"We need to find {w} better solution."
                            c_text = f"我們需要找到一個更好的解決辦法。"
                    else:
                        # 根據場合與程度套用高品質自然句型
                        if scene_choice == "旅遊社交":
                            if level_choice == "初階":
                                if type_choice == "否定句":
                                    e_text = f"We did not see {w} during the trip."
                                    c_text = f"我們在旅途中沒有看到 {w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Did you find {w} in this city?"
                                    c_text = f"你在這座城市找到 {w} 了嗎？"
                                else:
                                    e_text = f"We can enjoy {w} together in the city."
                                    c_text = f"我們可以在城市裡一起享受 {w}。"
                            elif level_choice == "中階":
                                if type_choice == "否定句":
                                    e_text = f"Travelers rarely expect to experience {w} so soon."
                                    c_text = f"旅客很少預料到這麼快就會體驗到 {w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Have you ever experienced {w} while traveling abroad?"
                                    c_text = f"你出國旅遊時曾體驗過 {w} 嗎？"
                                else:
                                    e_text = f"Tourists often look forward to discovering {w} abroad."
                                    c_text = f"遊客經常期待在國外發現 {w}。"
                            else:
                                if type_choice == "否定句":
                                    e_text = f"No itinerary could fully capture the profound charm of {w}."
                                    c_text = f"沒有任何行程能完全捕捉到 {w} 的深奧魅力。"
                                elif type_choice == "疑問句":
                                    e_text = f"Could any traveler truly appreciate {w} without guidance?"
                                    c_text = f"沒有導覽，任何旅客真的能欣賞 {w} 嗎？"
                                else:
                                    e_text = f"Exploring distant destinations often unveils the true essence of {w}."
                                    c_text = f"探索遠方目的地往往能揭示 {w} 的真實本質。"
                        elif scene_choice == "職場商務":
                            if level_choice == "初階":
                                if type_choice == "否定句":
                                    e_text = f"Please do not ignore {w} in your report."
                                    c_text = f"請不要在報告中忽略 {w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Did you check {w} before the meeting?"
                                    c_text = f"你在會議前有檢查 {w} 嗎？"
                                else:
                                    e_text = f"We must prepare {w} for the office project."
                                    c_text = f"我們必須為辦公室專案準備 {w}。"
                            elif level_choice == "中階":
                                if type_choice == "否定句":
                                    e_text = f"The management team did not approve {w} this week."
                                    c_text = f"管理團隊這週未批准 {w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Will the committee discuss {w} in the next meeting?"
                                    c_text = f"委員會會在下次會議中討論 {w} 嗎？"
                                else:
                                    e_text = f"The director carefully evaluated {w} during the review."
                                    c_text = f"主管在審查期間仔細評估了 {w}。"
                            else:
                                if type_choice == "否定句":
                                    e_text = f"No strategic decisions regarding {w} were finalized yesterday."
                                    c_text = f"昨天沒有敲定任何關於 {w} 的策略決策。"
                                elif type_choice == "疑問句":
                                    e_text = f"Were all compliance requirements regarding {w} fully satisfied?"
                                    c_text = f"所有關於 {w} 的合規要求都完全滿足了嗎？"
                                else:
                                    e_text = f"Comprehensive analysis concerning {w} was submitted to executives."
                                    c_text = f"關於 {w} 的全面分析已提交給高階主管。"
                        else:  # 日常生活
                            if level_choice == "初階":
                                if type_choice == "否定句":
                                    e_text = f"I do not need {w} right now."
                                    c_text = f"我現在不需要 {w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Do you like {w} for dinner?"
                                    c_text = f"你晚餐喜歡 {w} 嗎？"
                                else:
                                    e_text = f"I use {w} every single day."
                                    c_text = f"我每天都會使用 {w}。"
                            elif level_choice == "中階":
                                if type_choice == "否定句":
                                    e_text = f"She usually does not think about {w} in the morning."
                                    c_text = f"她通常在早上不會想到 {w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Do you often talk about {w} with your friends?"
                                    c_text = f"你經常和朋友談論 {w} 嗎？"
                                else:
                                    e_text = f"People often appreciate {w} during quiet moments."
                                    c_text = f"人們經常在安靜的時刻欣賞 {w}。"
                            else:
                                if type_choice == "否定句":
                                    e_text = f"Few individuals can truly master {w} without constant practice."
                                    c_text = f"沒有持續的練習，很少有人能真正掌握 {w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Do subtle changes in daily habits reflect {w}?"
                                    c_text = f"日常習慣的微妙變化反映了 {w} 嗎？"
                                else:
                                    e_text = f"Profound understanding of {w} brings inner peace."
                                    c_text = f"對 {w} 的深刻理解會帶來內心的平靜。"

                    st.session_state[state_key] = {"eng": e_text, "chi": c_text}

                current_data = st.session_state[state_key]
                demo_eng = current_data["eng"]
                demo_chi = current_data["chi"]
                
                highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                
                st.markdown(f"**💡 本地智慧動態示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 示範句英文發音", key=f"audio_v16_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_v16_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}", height=90)
                if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_v16_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    if w.lower() in user_practice.lower():
                        st.success(f"🎉 太棒了！[{w}] 使用正確！")
                    else:
                        st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次!")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
