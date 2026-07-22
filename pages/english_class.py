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

st.title("📖 澄玄大學 - 語言學院 & 智慧詞性對應造句工坊")

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
        key="vocab_click_table_v21"
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
        if st.button("➕ 把此字加入清單", key="add_to_list_v21"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以點擊右側清除重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的清單", key="clear_list_v21"):
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("grammar_v21_")]
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
        st.subheader("✍️ 智慧詞性對應造句工坊（精準匹配動詞、名詞、形容詞）")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            target_row = df[df['word'] == w]
            trans_w = target_row['trans'].values[0] if not target_row.empty else ""
            w_level = int(target_row['level'].values[0]) if (not target_row.empty and 'level' in target_row.columns and pd.notna(target_row['level'].values[0])) else 1
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w} | 難度Level {w_level}）")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    level_choice = st.selectbox("📚 程度：", ["初階", "中階", "高階"], key=f"lvl_v21_{idx}_{w}")
                with c2:
                    type_choice = st.selectbox("🔄 句型：", ["肯定句", "否定句", "疑問句"], key=f"typ_v21_{idx}_{w}")
                with c3:
                    scene_choice = st.selectbox("🌐 場合：", ["日常生活", "職場商務", "旅遊社交"], key=f"scn_v21_{idx}_{w}")
                
                state_key = f"grammar_v21_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
                if state_key not in st.session_state:
                    w_lower = w.lower()
                    
                    # 智慧詞性判定邏輯：依據字尾或字義特性自動分類為「動作動詞」、「實體/抽象名詞」或「副詞」
                    is_likely_verb = any(w_lower.endswith(suffix) for suffix in ['ate', 'ize', 'fy', 'en', 'ish']) or w_lower in ['act', 'sell', 'make', 'take', 'get', 'run', 'give', 'look']
                    is_likely_adverb = w_lower in ['always', 'never', 'often', 'sometimes', 'usually', 'really', 'very']
                    
                    if is_likely_adverb:
                        if type_choice == "否定句":
                            e_text = f"I {w_lower} forget to check my messages."
                            c_text = f"我{trans_w}不會忘記查看訊息。"
                        elif type_choice == "疑問句":
                            e_text = f"Do you {w_lower} arrive early at work?"
                            c_text = f"你上班{trans_w}會提早到嗎？"
                        else:
                            e_text = f"We {w_lower} strive for the best results."
                            c_text = f"我們{trans_w}力求最好的成果。"
                            
                    elif is_likely_verb:
                        if type_choice == "否定句":
                            e_text = f"We decided not to {w_lower} right now."
                            c_text = f"我們決定現在不要{trans_w}。"
                        elif type_choice == "疑問句":
                            e_text = f"When will you {w_lower} this document?"
                            c_text = f"你什麼時候要{trans_w}這份文件？"
                        else:
                            if scene_choice == "職場商務":
                                e_text = f"The team needs to {w_lower} the project efficiently."
                                c_text = f"團隊需要有效率地{trans_w}這個專案。"
                            elif scene_choice == "旅遊社交":
                                e_text = f"Visitors can {w_lower} freely in this cultural zone."
                                c_text = f"訪客可以在這個文化區自由地{trans_w}。"
                            else:
                                e_text = f"I usually {w_lower} during my free time."
                                c_text = f"我通常會在空閒時間{trans_w}。"
                                
                    else: # 預設當作名詞處理
                        if type_choice == "否定句":
                            e_text = f"We did not notice any {w_lower} in the report."
                            c_text = f"我們在報告中沒有注意到任何「{trans_w}」。"
                        elif type_choice == "疑問句":
                            e_text = f"Have you considered the impact of {w_lower}?"
                            c_text = f"你有考慮過「{trans_w}」的影響嗎？"
                        else:
                            if scene_choice == "職場商務":
                                e_text = f"Effective management of {w_lower} is crucial for the company."
                                c_text = f"對「{trans_w}」的有效管理對公司至關重要。"
                            elif scene_choice == "旅遊社交":
                                e_text = f"Every traveler looks forward to experiencing {w_lower}."
                                c_text = f"每個旅客都很期待體驗「{trans_w}」。"
                            else:
                                e_text = f"Paying attention to {w_lower} makes life much easier."
                                c_text = f"多注意「{trans_w}」會讓生活輕鬆許多。"

                    st.session_state[state_key] = {"eng": e_text, "chi": c_text}

                current_data = st.session_state[state_key]
                demo_eng = current_data["eng"]
                demo_chi = current_data["chi"]
                
                highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                
                st.markdown(f"**💡 智慧詞性示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 示範句英文發音", key=f"audio_v21_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_v21_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}", height=90)
                if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_v21_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    if w.lower() in user_practice.lower():
                        st.success(f"🎉 太棒了！您成功在句子中運用了 [{w}]！")
                    else:
                        st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次看看！")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
