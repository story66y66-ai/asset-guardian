import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# 全域注入 CSS：大幅放大所有文字、輸入框、表格內的字體大小與行高
st.markdown("""
    <style>
    /* 放大所有一般文字與標題 */
    html, body, [class*="css"] {
        font-size: 20px !important;
    }
    /* 放大輸入框的標題文字 */
    .stTextInput label {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
    /* 放大輸入框裡面打出來的字與高度 */
    .stTextInput input {
        font-size: 24px !important;
        height: 55px !important;
    }
    /* 放大表格內的所有文字、標題與行高 */
    dataframe, [data-testid="stDataFrame"] {
        font-size: 22px !important;
    }
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span, [data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td {
        font-size: 22px !important;
    }
    /* 調整表格儲存格的上下空間，讓大字體看起來更舒適 */
    [data-testid="stDataFrame"] td {
        padding-top: 15px !important;
        padding-bottom: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📖 澄玄大學 - 自主單字與句子查詢背誦學院")

# 1. 讀取並合併所有 words_*.csv 檔案
@st.cache_data
def load_and_merge_data():
    expected_cols = ["word", "trans", "kk", "level"]
    all_data = []
    all_files = glob.glob("words_*.csv")
    
    for f in all_files:
        try:
            df = pd.read_csv(f, encoding='utf-8-sig', on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = ""
            all_data.append(df[expected_cols])
        except Exception:
            continue
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df = final_df.dropna(subset=["word"])
        final_df = final_df.drop_duplicates(subset=["word"], keep='last')
        return final_df
    else:
        return pd.DataFrame(columns=expected_cols)

df = load_and_merge_data()

if df.empty:
    st.error("⚠️ 找不到任何 words_*.csv 單字庫檔案，請確認 GitHub 倉庫中是否有上傳這些檔案！")
    st.stop()

# 建立一個方便查詢的字典
word_dict = {}
for _, row in df.iterrows():
    w_str = str(row['word']).strip().lower()
    trans_str = str(row['trans']) if pd.notna(row['trans']) else ""
    kk_str = str(row['kk']) if pd.notna(row['kk']) else ""
    level_str = str(row['level']) if pd.notna(row['level']) else ""
    word_dict[w_str] = {"original_word": str(row['word']).strip(), "trans": trans_str, "kk": kk_str, "level": level_str}

st.divider()

# ==================== 第一階段：澄玄自己輸入單字來查詢、看 KK、聽發音 ====================
st.markdown("### 🔍 第一階段：自主輸入單字查詢與發音練習")
search_input = st.text_input("請在此輸入您想查詢或學習的英文單字：", key="search_word_input")

matched_level = ""
real_word = ""

if search_input.strip():
    search_key = search_input.strip().lower()
    
    if search_key in word_dict:
        target_info = word_dict[search_key]
        real_word = target_info["original_word"]
        word_trans = target_info["trans"]
        word_kk = target_info["kk"]
        matched_level = target_info["level"]
        
        st.success(f"🎉 成功從資料庫找到單字！")
        
        # 放大顯示查詢結果（含 Level 等級顯示）
        st.markdown(f"### ✨ 查詢結果：")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 8px solid #4CAF50; color: #000000;">
            <p style="font-size: 26px; margin: 12px 0;"><b>英文單字：</b> <span style="color: #1f77b4; font-size: 32px;"><b>{real_word}</b></span></p>
            <p style="font-size: 26px; margin: 12px 0;"><b>中文翻譯：</b> <span style="font-size: 28px;"><b>{word_trans if word_trans else '(暫無翻譯)'}</b></span></p>
            <p style="font-size: 26px; margin: 12px 0;"><b>KK 音標：</b> <span style="font-size: 28px;"><b>/{word_kk}/</b></span></p>
            <p style="font-size: 26px; margin: 12px 0;"><b>所屬級別：</b> <span style="color: #d9534f; font-size: 30px;"><b>Level {matched_level}</b></span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("#### 🔊 請選擇發音速度來熟悉它：")
        
        col_audio1, col_audio2 = st.columns(2)
        
        # 正常速度 (gTTS)
        with col_audio1:
            if st.button("🔊 正常速度發音", key="play_normal_btn"):
                try:
                    tts = gTTS(text=real_word, lang='en', slow=False)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp, format='audio/mp3', autoplay=True)
                except Exception as e:
                    st.error(f"發音錯誤：{e}")
                    
        # 0.4倍慢速 (JavaScript SpeechSynthesis)
        with col_audio2:
            safe_word_js = real_word.replace("'", "\\'")
            components.html(f"""
                <button onclick="
                    const utterance = new SpeechSynthesisUtterance('{safe_word_js}');
                    utterance.lang = 'en-US';
                    utterance.rate = 0.4;
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                " style="
                    background-color: #f0f2f6; color: #262730; border: 1px solid #d6d6d8;
                    padding: 14px 18px; border-radius: 8px; font-size: 20px; font-weight: bold;
                    cursor: pointer; width: 100%;
                ">🐢 0.4倍超慢速發音</button>
            """, height=70)
            
        st.divider()
        
        # ==================== 背誦測驗輸入框 ====================
        st.markdown("### ✍️ 單字記憶自我挑戰")
        st.markdown(f"💡 *剛剛已經看過與聽過這個單字了，請在下方輸入框閉眼或憑記憶拼寫一次看看，測試自己背起來了沒！*")
        
        quiz_input = st.text_input(f"請重新輸入剛剛查詢的英文單字（{word_trans}）：", key=f"quiz_input_{real_word}")
        
        if quiz_input.strip():
            if quiz_input.strip().lower() == real_word.lower():
                st.markdown(f"<span style='font-size: 24px; color: #28a745; font-weight: bold;'>🎉 太厲害了！完全拼寫正確，您已經記住這個單字了！它位於 Level {matched_level} 喔！</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='font-size: 24px; color: #ff4b4b; font-weight: bold;'>❌ 拼寫有誤唷！正確答案是：`{real_word}`（屬於 Level {matched_level}），再加油練習一次！</span>", unsafe_allow_html=True)
                
    else:
        st.warning(f"⚠️ 在資料庫中找不到「{search_input}」這個單字，請確認拼字或檢查 `words_*.csv` 庫中是否有收錄喔！")

else:
    st.info("💡 請在上方輸入框中打入您想練習的英文單字（例如：apple, book 等），程式就會自動幫您調出超大字體的中文、KK音標、Level 級別與雙速發音按鈕囉！")

st.divider()

# ==================== 智慧總覽與自動連動定位區 ====================
st.markdown("### 📚 完整單字庫總覽（與上方查詢自動連動）")

target_filter = search_input.strip()

if target_filter:
    filtered_df = df[df['word'].str.contains(target_filter, case=False, na=False)]
    if not filtered_df.empty:
        st.markdown(f"""
        <div style="background-color: #262730; padding: 15px; border-radius: 8px; border-left: 6px solid #ff4b4b; margin-bottom: 10px;">
            <p style="font-size: 24px; color: #ffffff; margin: 0;">🎯 <b>已自動為您定位並找出包含「<span style="color: #4CAF50;">{target_filter}</span>」的單字與對應 Level：</b></p>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(filtered_df[['word', 'trans', 'kk', 'level']], use_container_width=True, hide_index=True)
    else:
        st.markdown("<p style='font-size: 22px; color: #ffa500;'>💡 目前上方查詢的單字在總覽中找不到對應項目，以下顯示完整清單：</p>", unsafe_allow_html=True)
        st.dataframe(df[['word', 'trans', 'kk', 'level']], use_container_width=True, hide_index=True)
else:
    st.markdown("<p style='font-size: 22px;'>📌 <b>目前顯示完整單字庫清單（只要在上方輸入單字，這裡就會自動幫您過濾出來喔！）：</b></p>", unsafe_allow_html=True)
    st.dataframe(df[['word', 'trans', 'kk', 'level']], use_container_width=True, hide_index=True)

st.divider()

# ==================== 第二階段：整句 / 片語自主輸入與朗讀挑戰區 ====================
st.markdown("### 💬 第二階段：整句 / 片語自主輸入與雙速朗讀挑戰")
st.markdown("💡 *在這裡您可以輸入一整句英文句子或常用片語，進行整句朗讀與複誦練習！*")

sentence_input = st.text_input("請在此輸入您想練習的英文句子或片語：", key="sentence_input_field")

if sentence_input.strip():
    target_sentence = sentence_input.strip()
    
    st.success("🎉 句子已成功載入！")
    
    # 顯示句子結果區塊
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 8px solid #ff9800; color: #000000;">
        <p style="font-size: 26px; margin: 12px 0;"><b>輸入的句子：</b> <span style="color: #d9534f; font-size: 30px;"><b>{target_sentence}</b></span></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.markdown("#### 🔊 請選擇整句朗讀速度：")
    
    col_sent1, col_sent2 = st.columns(2)
    
    # 正常速度整句發音 (gTTS)
    with col_sent1:
        if st.button("🔊 正常速度整句朗讀", key="play_sent_normal"):
            try:
                tts = gTTS(text=target_sentence, lang='en', slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp, format='audio/mp3', autoplay=True)
            except Exception as e:
                st.error(f"發音錯誤：{e}")
                
    # 0.4倍慢速整句發音 (JavaScript SpeechSynthesis)
    with col_sent2:
        safe_sent_js = target_sentence.replace("'", "\\'")
        components.html(f"""
            <button onclick="
                const utterance = new SpeechSynthesisUtterance('{safe_sent_js}');
                utterance.lang = 'en-US';
                utterance.rate = 0.4;
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            " style="
                background-color: #f0f2f6; color: #262730; border: 1px solid #d6d6d8;
                padding: 14px 18px; border-radius: 8px; font-size: 20px; font-weight: bold;
                cursor: pointer; width: 100%;
            ">🐢 0.4倍超慢速整句朗讀</button>
        """, height=70)
        
    st.divider()
    
    # 整句自我默寫與拼寫挑戰
    st.markdown("### ✍️ 整句默寫記憶自我挑戰")
    sent_quiz = st.text_input("請在下方重新輸入剛才練習的完整句子，測試自己有沒有完全記住：", key="sent_quiz_input")
    
    if sent_quiz.strip():
        # 這裡用標準化去頭尾與忽略大小寫來比對
        if sent_quiz.strip().lower() == target_sentence.lower():
            st.markdown("<span style='font-size: 24px; color: #28a745; font-weight: bold;'>🎉 太強了！整句完全拼寫正確，您的記憶力太棒了！</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='font-size: 24px; color: #ff4b4b; font-weight: bold;'>❌ 有點小誤差喔！正確的句子是：`{target_sentence}`，再對照一下練幾次吧！</span>", unsafe_allow_html=True)

else:
    st.info("💡 請在上方句子輸入框打入任何想練習的英文對話、諺語或片語（例如：Practice makes perfect.），即可享受專屬的整句雙速朗讀與默寫挑戰！")
