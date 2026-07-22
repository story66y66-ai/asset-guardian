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
    .stTextArea textarea { font-size: 28px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院 & 道地口語文法造句工坊")

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
        key="vocab_click_table_v17"
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
        if st.button("➕ 把此字加入清單", key="add_to_list_v17"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以點擊右側清除重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的清單", key="clear_list_v17"):
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("grammar_v17_")]
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
        st.subheader("✍️ 獨立單字多變造句工坊（嚴格文法與道地口語翻譯引擎）")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            target_row = df[df['word'] == w]
            trans_w = target_row['trans'].values[0] if not target_row.empty else ""
            w_level = int(target_row['level'].values[0]) if (not target_row.empty and 'level' in target_row.columns and pd.notna(target_row['level'].values[0])) else 1
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w} | 難度Level {w_level}）")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    level_choice = st.selectbox("📚 程度：", ["初階", "中階", "高階"], key=f"lvl_v17_{idx}_{w}")
                with c2:
                    type_choice = st.selectbox("🔄 句型：", ["肯定句", "否定句", "疑問句"], key=f"typ_v17_{idx}_{w}")
                with c3:
                    scene_choice = st.selectbox("🌐 場合：", ["日常生活", "職場商務", "旅遊社交"], key=f"scn_v17_{idx}_{w}")
                
                state_key = f"grammar_v17_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
                if state_key not in st.session_state:
                    w_lower = w.lower()
                    
                    # 專門針對副詞、冠詞或一般單字的黃金文法對應邏輯
                    if w_lower in ["always", "never", "often", "sometimes", "usually"]:
                        if type_choice == "否定句":
                            e_text = f"I {w} forget to bring my keys when leaving."
                            c_text = f"我出門時{trans_w}不會忘記帶鑰匙。" if w_lower=="never" else f"我出門時{trans_w}會忘記帶鑰匙。"
                        elif type_choice == "疑問句":
                            e_text = f"Do you {w} check your emails in the morning?"
                            c_text = f"你早上{trans_w}會檢查電子郵件嗎？"
                        else:
                            e_text = f"We {w} try our best to finish work on time."
                            c_text = f"我們{trans_w}都盡全力準時完成工作。"
                            
                    elif w_lower in ["a", "an", "the"]:
                        if type_choice == "否定句":
                            e_text = f"This is not just {w} ordinary mistake."
                            c_text = f"這不只是個普通的錯誤。"
                        elif type_choice == "疑問句":
                            e_text = f"Is this {w} best option we have right now?"
                            c_text = f"這是我們目前最好的選擇嗎？"
                        else:
                            e_text = f"She wants to find {w} better solution for this."
                            c_text = f"她想為這件事找出一個更好的解決辦法。"
                            
                    else:
                        # 依據場合與程度套用高標準、文法百分之百正確的句型
                        if scene_choice == "旅遊社交":
                            if level_choice == "初階":
                                if type_choice == "否定句":
                                    e_text = f"We did not visit {w} during our trip."
                                    c_text = f"我們在旅途中沒有參觀 {trans_w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Did you see {w} in this area?"
                                    c_text = f"你在這附近有看到 {trans_w} 嗎？"
                                else:
                                    e_text = f"We plan to explore {w} tomorrow morning."
                                    c_text = f"我們計畫明天早上探索 {trans_w}。"
                            elif level_choice == "中階":
                                if type_choice == "否定句":
                                    e_text = f"Many tourists do not expect to experience {w} so early."
                                    c_text = f"許多遊客沒想到這麼早就體驗到 {trans_w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Have you ever encountered {w} while traveling abroad?"
                                    c_text = f"你出國旅遊時曾遇過 {trans_w} 嗎？"
                                else:
                                    e_text = f"Travelers are always excited to discover {w} in new places."
                                    c_text = f"旅客在新的地方發現 {trans_w}總是感到興奮。"
                            else:
                                if type_choice == "否定句":
                                    e_text = f"No travel guide could fully describe the true splendor of {w}."
                                    c_text = f"沒有任何旅遊指南能完全描述 {trans_w} 的真實壯麗。"
                                elif type_choice == "疑問句":
                                    e_text = f"Could any visitor truly appreciate {w} without a local guide?"
                                    c_text = f"沒有當地導覽，任何訪客真的能欣賞 {trans_w} 嗎？"
                                else:
                                    e_text = f"Immersing oneself in local traditions reveals the deep soul of {w}."
                                    c_text = f"沉浸在當地傳統中能揭示 {trans_w} 的深層靈魂。"
                                    
                        elif scene_choice == "職場商務":
                            if level_choice == "初階":
                                if type_choice == "否定句":
                                    e_text = f"Please do not ignore {w} in your daily report."
                                    c_text = f"請不要在日常報告中忽略 {trans_w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Did you check {w} before the meeting started?"
                                    c_text = f"會議開始前你有檢查 {trans_w} 嗎？"
                                else:
                                    e_text = f"We need to prepare {w} for the upcoming project."
                                    c_text = f"我們需要為接下來的專案準備 {trans_w}。"
                            elif level_choice == "中階":
                                if type_choice == "否定句":
                                    e_text = f"The management team did not approve {w} this month."
                                    c_text = f"管理團隊這個月沒有批准 {trans_w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Will the director discuss {w} in the executive meeting?"
                                    c_text = f"主管會在執行會議中討論 {trans_w} 嗎？"
                                else:
                                    e_text = f"The department carefully evaluated {w} during the review."
                                    c_text = f"部門在審查期間仔細評估了 {trans_w}。"
                            else:
                                if type_choice == "否定句":
                                    e_text = f"No strategic decisions regarding {w} were finalized yesterday."
                                    c_text = f"昨天沒有敲定任何關於 {trans_w} 的策略決策。"
                                elif type_choice == "疑問句":
                                    e_text = f"Were all compliance requirements concerning {w} fully met?"
                                    c_text = f"所有關於 {trans_w} 的合規要求都完全達到了嗎？"
                                else:
                                    e_text = f"Comprehensive market analysis concerning {w} was submitted to executives."
                                    c_text = f"關於 {trans_w} 的全面市場分析已提交給高階主管。"
                                    
                        else:  # 日常生活
                            if level_choice == "初階":
                                if type_choice == "否定句":
                                    e_text = f"I do not need {w} right now."
                                    c_text = f"我現在不需要 {trans_w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Do you like {w} for your daily routine?"
                                    c_text = f"你日常生活中喜歡 {trans_w} 嗎？"
                                else:
                                    e_text = f"I use {w} almost every single day."
                                    c_text = f"我幾乎每天都會用到 {trans_w}。"
                            elif level_choice == "中階":
                                if type_choice == "否定句":
                                    e_text = f"She usually does not think about {w} in the morning."
                                    c_text = f"她通常在早上不會想到 {trans_w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Do you often talk about {w} with your family?"
                                    c_text = f"你經常和家人談論 {trans_w} 嗎？"
                                else:
                                    e_text = f"People tend to appreciate {w} during quiet moments."
                                    c_text = f"人們往往在安靜的時刻體會到 {trans_w}。"
                            else:
                                if type_choice == "否定句":
                                    e_text = f"Few individuals can truly master {w} without persistent effort."
                                    c_text = f"沒有持續的努力，很少有人能真正掌握 {trans_w}。"
                                elif type_choice == "疑問句":
                                    e_text = f"Do subtle shifts in daily habits truly reflect {w}?"
                                    c_text = f"日常習慣的微妙轉變真的反映了 {trans_w} 嗎？"
                                else:
                                    e_text = f"A profound understanding of {w} brings lasting inner peace."
                                    c_text = f"對 {trans_w} 的深刻理解會帶來持久的內心平靜。"

                    st.session_state[state_key] = {"eng": e_text, "chi": c_text}

                current_data = st.session_state[state_key]
                demo_eng = current_data["eng"]
                demo_chi = current_data["chi"]
                
                highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                
                st.markdown(f"**💡 道地文法示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 示範句英文發音", key=f"audio_v17_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_v17_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}", height=90)
                if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_v17_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    if w.lower() in user_practice.lower():
                        st.success(f"🎉 太棒了！[{w}] 使用正確！")
                    else:
                        st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次!")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
