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

st.title("📖 澄玄大學 - 語言學院 & 智慧動態造句工坊")

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
        key="vocab_click_table_v20"
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
        if st.button("➕ 把此字加入清單", key="add_to_list_v20"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以點擊右側清除重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的清單", key="clear_list_v20"):
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("grammar_v20_")]
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
        st.subheader("✍️ 智慧動態造句工坊（隨情境靈活演變）")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            target_row = df[df['word'] == w]
            trans_w = target_row['trans'].values[0] if not target_row.empty else ""
            w_level = int(target_row['level'].values[0]) if (not target_row.empty and 'level' in target_row.columns and pd.notna(target_row['level'].values[0])) else 1
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w} | 難度Level {w_level}）")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    level_choice = st.selectbox("📚 程度：", ["初階", "中階", "高階"], key=f"lvl_v20_{idx}_{w}")
                with c2:
                    type_choice = st.selectbox("🔄 句型：", ["肯定句", "否定句", "疑問句"], key=f"typ_v20_{idx}_{w}")
                with c3:
                    scene_choice = st.selectbox("🌐 場合：", ["日常生活", "職場商務", "旅遊社交"], key=f"scn_v20_{idx}_{w}")
                
                state_key = f"grammar_v20_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
                # 這裡使用動態演算法來合成符合該單字中文含意的自然句子
                if state_key not in st.session_state:
                    w_lower = w.lower()
                    
                    # 智慧動態模板合成器：根據詞義彈性生成
                    if type_choice == "否定句":
                        if scene_choice == "職場商務":
                            e_text = f"We should not overlook {w_lower} during our quarterly review."
                            c_text = f"在季度檢討期間，我們不應忽視「{trans_w}」。"
                        elif scene_choice == "旅遊社交":
                            e_text = f"Visitors typically do not expect to encounter {w_lower} so unexpectedly."
                            c_text = f"遊客通常沒預料到會如此意外地遇到「{trans_w}」。"
                        else:
                            e_text = f"I really do not want to compromise on {w_lower} today."
                            c_text = f"我今天真的不想在「{trans_w}」這件事上妥協。"
                    elif type_choice == "疑問句":
                        if scene_choice == "職場商務":
                            e_text = f"How can we effectively manage {w_lower} in the new project?"
                            c_text = f"我們該如何在新的專案中有效處理「{trans_w}」？"
                        elif scene_choice == "旅遊社交":
                            e_text = f"Would you mind telling me more about {w_lower} around here?"
                            c_text = f"你介意跟我多聊聊這裡關於「{trans_w}」的事嗎？"
                        else:
                            e_text = f"Why do people always care so much about {w_lower}?"
                            c_text = f"為什麼人們總是這麼在意「{trans_w}」？"
                    else: # 肯定句
                        if level_choice == "高階":
                            e_text = f"A profound understanding of {w_lower} significantly shapes our perspective."
                            c_text = f"對「{trans_w}」的深刻理解顯著形塑了我們的觀點。"
                        elif level_choice == "中階":
                            e_text = f"We should carefully evaluate the role of {w_lower} in this context."
                            c_text = f"我們應該在此情境中仔細評估「{trans_w}」的作用。"
                        else:
                            e_text = f"I try to learn more about {w_lower} in my daily routine."
                            c_text = f"我試著在日常生活中多了解「{trans_w}」。"

                    st.session_state[state_key] = {"eng": e_text, "chi": c_text}

                current_data = st.session_state[state_key]
                demo_eng = current_data["eng"]
                demo_chi = current_data["chi"]
                
                highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                
                st.markdown(f"**💡 智慧動態示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 示範句英文發音", key=f"audio_v20_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_v20_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}", height=90)
                if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_v20_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    if w.lower() in user_practice.lower():
                        st.success(f"🎉 太棒了！您成功在句子中運用了 [{w}]！繼續保持這個靈活的造句靈感！")
                    else:
                        st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次看看！")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
