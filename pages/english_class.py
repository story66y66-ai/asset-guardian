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
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    .stTextArea textarea { font-size: 28px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院 & 單字多變造句工坊")

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

    # 當清單中有單字時，分別針對每一個單字獨立進行多變造句實戰
    if st.session_state.selected_vocab_list:
        st.divider()
        st.subheader("✍️ 獨立單字多變造句工坊")
        
        # 讓澄玄選擇程度與句型變化條件
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        with col_opt1:
            level_choice = st.selectbox("📚 選擇程度：", ["初階 (Beginner)", "中階 (Intermediate)", "高階 (Advanced)"], key="lvl_choice")
        with col_opt2:
            type_choice = st.selectbox("🔄 選擇句型形態：", ["肯定句 (Affirmative)", "否定句 (Negative)", "疑問句 (Interrogative)"], key="typ_choice")
        with col_opt3:
            scene_choice = st.selectbox("场景/場合：", ["日常生活 (Daily Life)", "職場商務 (Business)", "旅遊社交 (Travel & Social)"], key="scn_choice")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            trans_w = df[df['word'] == w]['trans'].values[0] if not df[df['word'] == w].empty else ""
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w}）")
                
                # 產生 AI 範例按鈕與邏輯
                gen_btn_key = f"gen_{idx}_{w}"
                ai_sent_key = f"ai_sent_{idx}_{w}"
                ai_chi_key = f"ai_chi_{idx}_{w}"
                
                if ai_sent_key not in st.session_state:
                    st.session_state[ai_sent_key] = ""
                    st.session_state[ai_chi_key] = ""

                if st.button(f"✨ 產出 [{w}] 的專屬示範句", key=gen_btn_key):
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
                        Target English word: {w} ({trans_w})
                        Level: {level_choice}
                        Sentence Type: {type_choice}
                        Scene/Context: {scene_choice}
                        
                        Please write ONE natural English sentence using the target word according to the specified level, sentence type, and scene.
                        Then provide its Traditional Chinese translation. In the Chinese translation, format the target word as: 中文翻譯({w}).
                        
                        Return ONLY valid text in this exact format:
                        ENGLISH: [Your English sentence]
                        CHINESE: [Your Chinese translation]
                        """
                        response = model.generate_content(prompt)
                        text = response.text.strip()
                        
                        e_text, c_text = "", ""
                        for line in text.split('\n'):
                            if line.startswith("ENGLISH:"):
                                e_text = line.replace("ENGLISH:", "").strip()
                            elif line.startswith("CHINESE:"):
                                c_text = line.replace("CHINESE:", "").strip()
                                
                        st.session_state[ai_sent_key] = e_text
                        st.session_state[ai_chi_key] = c_text
                    except Exception:
                        st.session_state[ai_sent_key] = f"This is an example sentence for {w}."
                        st.session_state[ai_chi_key] = f"這是 {w} ({trans_w}) 的範例句子。"

                # 顯示範例與練習區
                if st.session_state[ai_sent_key]:
                    demo_eng = st.session_state[ai_sent_key]
                    demo_chi = st.session_state[ai_chi_key]
                    
                    highlighted_demo = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", demo_eng, flags=re.IGNORECASE)
                    
                    st.markdown(f"**💡 助教示範：** {highlighted_demo}", unsafe_allow_html=True)
                    st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                    
                    if st.button(f"🔊 聽 [{w}] 示範句發音", key=f"audio_{idx}_{w}"):
                        tts = gTTS(text=demo_eng, lang='en')
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        st.audio(fp, autoplay=True)

                    user_practice = st.text_area(f"📝 請輸入您用 [{w}] 練習造的句子：", key=f"prac_{idx}_{w}", height=90)
                    if st.button(f"✅ 檢查 [{w}] 的造句", key=f"check_{idx}_{w}"):
                        if w.lower() in user_practice.lower():
                            st.success(f"🎉 太棒了！[{w}] 使用正確！")
                        else:
                            st.error(f"❌ 句子裡好像漏掉了單字 [{w}] 喔，再試一次!")
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
