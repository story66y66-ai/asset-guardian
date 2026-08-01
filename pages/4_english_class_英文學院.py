import streamlit as st
import pandas as pd
import glob
import os
from gTTS import gTTS
import io
import re
import base64
import urllib.parse

st.markdown("""
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    .red-word { color: #ff2b2b !important; font-weight: bold !important; }
    .stTextInput input { font-size: 28px !important; color: #000000 !important; font-weight: bold !important; }
    div.stButton > button { font-size: 22px !important; padding: 10px 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院 & 中英任意門造句工坊")

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

st.subheader(f"📋 單字總表（校長大人專屬單字庫：目前共計 {len(df)} 筆）")
st.write("---")

if not df.empty:
    # 仿造中文學院的分頁機制與循環朗讀控制台
    page_size = 20
    total_pages = (len(df) + page_size - 1) // page_size
    if total_pages < 1:
        total_pages = 1
    
    if "eng_current_page" not in st.session_state:
        st.session_state.eng_current_page = 1

    col_p1, col_p2 = st.columns([2, 3])
    with col_p1:
        new_page = st.number_input(f"跳至頁數 (共 {total_pages} 頁)：", min_value=1, max_value=total_pages, value=st.session_state.eng_current_page, step=1, key="eng_page_input")
        if new_page != st.session_state.eng_current_page:
            st.session_state.eng_current_page = new_page
            st.rerun()
    
    with col_p2:
        st.write("")
        sub1, sub2 = st.columns(2)
        with sub1:
            if st.button("⬅️ 上一頁", key="eng_prev_page") and st.session_state.eng_current_page > 1:
                st.session_state.eng_current_page -= 1
                st.rerun()
        with sub2:
            if st.button("下一頁 ➡️", key="eng_next_page") and st.session_state.eng_current_page < total_pages:
                st.session_state.eng_current_page += 1
                st.rerun()

    current_page = st.session_state.eng_current_page
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    
    st.write(f"目前顯示第 **{current_page}** 頁（第 {start_idx + 1} ~ {end_idx} 筆）：")
    st.write("---")
    
    page_data = df.iloc[start_idx:end_idx]
    
    js_idioms_array = ""
    for idx, row in page_data.iterrows():
        word = row["word"]
        trans = row["trans"] if pd.notna(row["trans"]) else ""
        kk = row["kk"] if pd.notna(row["kk"]) else ""
        level = row["level"] if pd.notna(row["level"]) else 1
        full_text = f"{word}，{trans}"
        js_idioms_array += f"{{ index: {idx}, word: '{word}', text: '{full_text}' }},\n"

    rows_html = ""
    for idx, row in page_data.iterrows():
        word = row["word"]
        trans = row["trans"] if pd.notna(row["trans"]) else ""
        kk = row["kk"] if pd.notna(row["kk"]) else ""
        level = row["level"] if pd.notna(row["level"]) else 1
        display_num = idx + 1
        text_to_speak = f"{word}。"
        
        rows_html += f"""
        <tr style="border-bottom: 1px solid #ddd; height: 50px;" id="eng_row_item_{idx}">
            <td style="width: 10%; font-weight: bold;">#{display_num}</td>
            <td style="width: 25%; font-weight: bold;" id="eng_word_cell_{idx}">
                <a href="#" onclick="selectAndPlayWord('{word}', {idx}); return false;" style="text-decoration: none; color: #ff4b4b;">{word}</a>
            </td>
            <td style="width: 25%;">{trans}</td>
            <td style="width: 20%;">{kk}</td>
            <td style="width: 20%;">
                <button onclick="engPlaySingle({idx}, '{word}', '{text_to_speak}')" 
                        id="eng_btn_{idx}" 
                        style="background-color: #f0f2f6; border: 1px solid #d6d6d6; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-weight: bold;">
                    🔊 朗讀
                </button>
            </td>
        </tr>
        """

    audio_control_html = f"""
    <div style="margin-bottom: 15px; background-color: #f9f9f9; padding: 12px; border-radius: 6px; border: 1px solid #e0e0e0;">
        <div style="font-weight: bold; margin-bottom: 8px;">🎧 英文語音朗讀控制台：</div>
        <button onclick="engStartLoopPlay()" id="eng_loop_btn" style="background-color: #17a2b8; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 8px;">
            🔁 本頁循環朗讀
        </button>
        <button onclick="engStopAutoPlay()" style="background-color: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold;">
            ⏹ 停止朗讀
        </button>
        <span id="eng_auto_status" style="margin-left: 15px; color: #555; font-size: 14px; font-weight: bold;">狀態：待命中</span>
    </div>

    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="border-bottom: 2px solid #ccc; text-align: left;">
                <th style="padding-bottom: 8px;">序號</th>
                <th style="padding-bottom: 8px;">單字 (可點擊)</th>
                <th style="padding-bottom: 8px;">中文翻譯</th>
                <th style="padding-bottom: 8px;">KK音標</th>
                <th style="padding-bottom: 8px;">語音操作</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <script>
    const engPageIdiomsData = [
    {js_idioms_array}
    ];

    let engAutoPlaying = false;
    let engCurrentAutoIdx = 0;

    function engClearAllHighlights() {{
        for (let i = 0; i < engPageIdiomsData.length; i++) {{
            let item = engPageIdiomsData[i];
            let btn = document.getElementById('eng_btn_' + item.index);
            if (btn) {{
                btn.innerText = '🔊 朗讀';
                btn.style.backgroundColor = '#f0f2f6';
                btn.style.color = 'black';
            }}
        }}
    }}

    function engPlaySingle(idx, word, textToSpeak) {{
        engStopAutoPlay();
        engClearAllHighlights();
        
        let targetBtn = document.getElementById('eng_btn_' + idx);
        let targetRow = document.getElementById('eng_row_item_' + idx);
        
        if (targetBtn) {{
            targetBtn.innerText = '🔊 朗讀中...';
            targetBtn.style.backgroundColor = '#ff4b4b';
            targetBtn.style.color = 'white';
        }}
        if (targetRow) {{
            targetRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
        
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        
        utterance.onend = function() {{
            if (targetBtn) {{
                targetBtn.innerText = '🔊 朗讀';
                targetBtn.style.backgroundColor = '#f0f2f6';
                targetBtn.style.color = 'black';
            }}
        }};
        
        window.speechSynthesis.speak(utterance);
    }}

    function engStartLoopPlay() {{
        if (engPageIdiomsData.length === 0) return;
        engAutoPlaying = true;
        engCurrentAutoIdx = 0;
        document.getElementById('eng_auto_status').innerText = '狀態：[本頁循環] 播放中...';
        let btn = document.getElementById('eng_loop_btn');
        if(btn) btn.style.backgroundColor = '#6c757d';
        engPlayNextInQueue();
    }}

    function engPlayNextInQueue() {{
        if (!engAutoPlaying) return;

        if (engCurrentAutoIdx >= engPageIdiomsData.length) {{
            engCurrentAutoIdx = 0;
        }}

        let item = engPageIdiomsData[engCurrentAutoIdx];
        let idx = item.index;
        let word = item.word;
        let textToSpeak = item.text;

        engClearAllHighlights();

        let targetBtn = document.getElementById('eng_btn_' + idx);
        let targetRow = document.getElementById('eng_row_item_' + idx);

        if (targetBtn) {{
            targetBtn.innerText = '🎵 朗讀中...';
            targetBtn.style.backgroundColor = '#ff4b4b';
            targetBtn.style.color = 'white';
        }}
        if (targetRow) {{
            targetRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}

        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;

        utterance.onend = function() {{
            if (targetBtn) {{
                targetBtn.innerText = '🔊 朗讀';
                targetBtn.style.backgroundColor = '#f0f2f6';
                targetBtn.style.color = 'black';
            }}
            if (engAutoPlaying) {{
                engCurrentAutoIdx++;
                setTimeout(engPlayNextInQueue, 800);
            }}
        }};

        window.speechSynthesis.speak(utterance);
    }}

    function engStopAutoPlay() {{
        engAutoPlaying = false;
        window.speechSynthesis.cancel();
        engClearAllHighlights();
        let statusEl = document.getElementById('eng_auto_status');
        if(statusEl) statusEl.innerText = '狀態：已停止';
        let btn = document.getElementById('eng_loop_btn');
        if(btn) btn.style.backgroundColor = '#17a2b8';
    }}

    function selectAndPlayWord(word, idx) {{
        // 透過隱藏表單或觸發 Streamlit 狀態來更新選取單字（此處保留原本點擊總表的相容性）
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    }}
    </script>
    """

    st.components.v1.html(audio_control_html, height=450, scrolling=True)

    st.divider()

    # 完整保留您原本愛的單字選取、造句清單與中英任意門造句工坊
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
        if st.button("➕ 把此字加入清單", key="add_to_list_v38"):
            if selected_word not in st.session_state.selected_vocab_list:
                if len(st.session_state.selected_vocab_list) < 3:
                    st.session_state.selected_vocab_list.append(selected_word)
                else:
                    st.warning("最多只能選 3 個單字喔！您可以點擊右側清除重新選擇。")
    with col2:
        if st.button("🗑️ 清除目前的清單", key="clear_list_v38"):
            st.session_state.selected_vocab_list = []
            st.success("已清除目前選擇的單字清單！")

    st.markdown(f"**📌 目前已選擇的單字（{len(st.session_state.selected_vocab_list)}/3）：**")
    if st.session_state.selected_vocab_list:
        st.write("、".join([f"**{w}**" for w in st.session_state.selected_vocab_list]))
    else:
        st.info("目前還沒有加入單字，請從上方點選喜歡的字後加入。")

    if st.session_state.selected_vocab_list:
        st.divider()
        st.subheader("✍️ 中英任意門造句工坊（自行輸入中文 ➔ 輕鬆翻譯）")

        for idx, w in enumerate(st.session_state.selected_vocab_list):
            target_row = df[df['word'] == w]
            trans_w = target_row['trans'].values[0] if not target_row.empty else ""
            w_level = int(target_row['level'].values[0]) if (not target_row.empty and 'level' in target_row.columns and pd.notna(target_row['level'].values[0])) else 1
            
            with st.container(border=True):
                st.markdown(f"### 🔹 單字 {idx+1}：`{w}` （{trans_w} | 難度Level {w_level}）")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    level_choice = st.selectbox("📚 程度：", ["初階", "中階", "高階"], key=f"lvl_v38_{idx}_{w}")
                with c2:
                    type_choice = st.selectbox("🔄 句型：", ["肯定句", "否定句", "疑問句"], key=f"typ_v38_{idx}_{w}")
                with c3:
                    scene_choice = st.selectbox("🌐 場合：", ["日常生活", "職場商務", "旅遊社交"], key=f"scn_v38_{idx}_{w}")
                
                state_key = f"grammar_v38_{w}_{level_choice}_{type_choice}_{scene_choice}"
                
                if state_key not in st.session_state:
                    w_lower = w.lower()
                    
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
                
                st.markdown(f"**💡 內建文法示範：** {highlighted_demo}", unsafe_allow_html=True)
                st.markdown(f"*(中文：{demo_chi})*", unsafe_allow_html=True)
                
                if st.button(f"🔊 聽 [{w}] 內建示範句發音", key=f"audio_v38_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"):
                    tts = gTTS(text=demo_eng, lang='en')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, autoplay=True)

                st.divider()
                st.markdown(f"**🌐 Google 翻譯任意門（輸入中文 ➔ 取得英文口語例句）**")
                
                user_chinese_key = f"isolated_zh_input_{idx}_{w}"
                clear_flag_key = f"isolated_zh_flag_{idx}_{w}"

                if clear_flag_key not in st.session_state:
                    st.session_state[clear_flag_key] = False

                if st.session_state[clear_flag_key]:
                    st.session_state[user_chinese_key] = ""
                    st.session_state[clear_flag_key] = False

                if user_chinese_key not in st.session_state:
                    st.session_state[user_chinese_key] = ""

                col_in, col_cl = st.columns([4, 1])
                with col_in:
                    user_chinese_input = st.text_input(
                        f"請輸入您想表達的中文（記得包含單字 [{w}] 喔）：",
                        key=user_chinese_key,
                        placeholder="請在此輸入中文句子..."
                    )
                with col_cl:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🧹 清除", key=f"btn_clean_zh_isolated_{idx}_{w}"):
                        st.session_state[clear_flag_key] = True
                        st.rerun()

                current_text = st.session_state.get(user_chinese_key, "").strip()
                if current_text:
                    encoded_text = urllib.parse.quote(current_text)
                    target_url = f"https://translate.google.com/?sl=zh-TW&tl=en&text={encoded_text}&op=translate"
                    st.markdown(
                        f'<a href="{target_url}" target="_blank" style="text-decoration: none;">'
                        f'<div style="background-color: #2b6cb0; color: white; padding: 10px 20px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 18px;">'
                        f'🚀 點擊直接開啟 Google 翻譯任意門</div></a>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="background-color: #555555; color: #cccccc; padding: 10px 20px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 18px; cursor: not-allowed;">'
                        f'🚀 請先在上方輸入中文，即可開啟任意門</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("---")
                st.markdown(f"**🌟 Google 道地文法示範（與您的單字連動）**")
                
                memine_input_key = f"isolated_memine_eng_{idx}_{w}"
                trans_input_key = f"isolated_memine_chi_{idx}_{w}"

                if memine_input_key not in st.session_state:
                    st.session_state[memine_input_key] = ""
                if trans_input_key not in st.session_state:
                    st.session_state[trans_input_key] = ""

                def process_pasted_sentence():
                    raw_val = st.session_state.get(memine_input_key, "")
                    match_paren = re.search(r'^(.*?)\s*[\(\（](.*?)[\)\）]\s*$', raw_val)
                    if match_paren:
                        st.session_state[memine_input_key] = match_paren.group(1).strip()
                        st.session_state[trans_input_key] = match_paren.group(2).strip()
                        return
                    match_dot = re.search(r'^([A-Za-z0-9\s,\.\?!\'\"-]+[.?!])\s+([\u4e00-\u9fa5].*)$', raw_val)
                    if match_dot:
                        st.session_state[memine_input_key] = match_dot.group(1).strip()
                        st.session_state[trans_input_key] = match_dot.group(2).strip()

                memine_sentence = st.text_input(
                    f"請貼上經由任意門翻譯或 Google 幫您用 [{w}] 造的英文句子：",
                    key=memine_input_key,
                    on_change=process_pasted_sentence,
                    placeholder="在此貼上英文句子..."
                )
                
                if memine_sentence:
                    highlighted_memine = re.sub(r'\b' + re.escape(str(w)) + r'\b', f"<span class='red-word'>{w}</span>", memine_sentence, flags=re.IGNORECASE)
                    st.markdown(f"**💡 自訂/任意門示範句：** {highlighted_memine}", unsafe_allow_html=True)
                    
                    st.markdown("🐢 **選擇句子發音速度：**")
                    b_col1, b_col2, b_col3 = st.columns(3)
                    
                    tts_m = gTTS(text=memine_sentence, lang='en')
                    fp_m = io.BytesIO()
                    tts_m.write_to_fp(fp_m)
                    audio_bytes = fp_m.getvalue()
                    b64_audio = base64.b64encode(audio_bytes).decode()
                    
                    with b_col1:
                        if st.button("🔊 正常 (1.0x)", key=f"spd_1_{idx}_{w}"):
                            audio_html = f"""
                                <audio id="player_{idx}_{w}" controls autoplay>
                                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                                </audio>
                                <script>
                                    var audioEl = document.getElementById("player_{idx}_{w}");
                                    audioEl.playbackRate = 1.0;
                                </script>
                            """
                            st.components.v1.html(audio_html, height=60)
                    with b_col2:
                        if st.button("🐢 0.5倍速", key=f"spd_05_{idx}_{w}"):
                            audio_html = f"""
                                <audio id="player_{idx}_{w}" controls autoplay>
                                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                                </audio>
                                <script>
                                    var audioEl = document.getElementById("player_{idx}_{w}");
                                    audioEl.playbackRate = 0.5;
                                </script>
                            """
                            st.components.v1.html(audio_html, height=60)
                    with b_col3:
                        if st.button("🐌 0.2倍速", key=f"spd_02_{idx}_{w}"):
                            audio_html = f"""
                                <audio id="player_{idx}_{w}" controls autoplay>
                                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                                </audio>
                                <script>
                                    var audioEl = document.getElementById("player_{idx}_{w}");
                                    audioEl.playbackRate = 0.2;
                                </script>
                            """
                            st.components.v1.html(audio_html, height=60)

                    memine_translation = st.text_input(
                        f"📝 中文翻譯：",
                        key=trans_input_key,
                        placeholder="在此輸入或對照中文翻譯..."
                    )
                    
                    if memine_translation:
                        st.markdown(f"*(中文翻譯：{memine_translation})*", unsafe_allow_html=True)
                        if st.button(f"🔊 聽中文翻譯語音", key=f"audio_memine_trans_{idx}_{w}"):
                            tts_t = gTTS(text=memine_translation, lang='zh-tw')
                            fp_t = io.BytesIO()
                            tts_t.write_to_fp(fp_t)
                            st.audio(fp_t, autoplay=True)

                st.markdown("<br>", unsafe_allow_html=True)
                
                prac_key = f"isolated_prac_input_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"
                status_key = f"isolated_prac_status_{idx}_{w}_{level_choice}_{type_choice}_{scene_choice}"
                prac_clear_flag = f"isolated_prac_flag_{idx}_{w}"

                if prac_clear_flag not in st.session_state:
                    st.session_state[prac_clear_flag] = False

                if st.session_state[prac_clear_flag]:
                    st.session_state[prac_key] = ""
                    st.session_state[status_key] = None
                    st.session_state[prac_clear_flag] = False
                
                if prac_key not in st.session_state:
                    st.session_state[prac_key] = ""

                def check_user_practice():
                    user_val = st.session_state.get(prac_key, "").strip()
                    target_sentence = st.session_state.get(memine_input_key, "").strip()
                    if not target_sentence:
                        target_sentence = demo_eng.strip()
                    
                    if user_val:
                        if user_val == target_sentence:
                            st.session_state[status_key] = ("success", f"🎉 太棒了！句子完全正確！大小寫規範完美掌握！")
                        else:
                            st.session_state[status_key] = ("error", f"❌ 檢查結果：句子中有拼字錯誤或大小寫與示範句不符喔！(正確示範: {target_sentence})")
                    else:
                        st.session_state[status_key] = None

                user_practice = st.text_input(
                    f"📝 請輸入您用 [{w}] 練習造的句子（嚴格檢查大小寫，輸入完按 Enter）：",
                    key=prac_key,
                    on_change=check_user_practice,
                    placeholder="在此輸入句子後按 Enter..."
                )
                
                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if st.button("🔄 清空重練", key=f"btn_clear_prac_{idx}_{w}"):
                        st.session_state[prac_clear_flag] = True
                        st.rerun()

                if status_key in st.session_state and st.session_state[status_key]:
                    st_type, st_msg = st.session_state[status_key]
                    if st_type == "success":
                        st.success(st_msg)
                    elif st_type == "error":
                        st.error(st_msg)
else:
    st.warning("目前沒有找到任何單字資料，請確認是否有上傳 level 檔案！")
