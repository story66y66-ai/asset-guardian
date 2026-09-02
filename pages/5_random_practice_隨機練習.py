import streamlit as st
import pandas as pd
import glob
import os
from gtts import gTTS
import io

st.set_page_config(layout="wide")

st.title("🎲 隨機挑戰 - 語言學院")

# 1. 使用與句子練習相同的「全覆蓋讀取詞庫函式」，完美解決找不到 words.csv 的問題
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

# 檢查資料庫是否為空
if df.empty:
    st.error("⚠️ 找不到任何 words_*.csv 單字庫檔案，請確認 GitHub 倉庫中是否有上傳這些檔案！")
    st.stop()

# 2. 初始化隨機題庫與索引
if 'shuffled_df' not in st.session_state:
    st.session_state.shuffled_df = df.sample(frac=1).reset_index(drop=True)
    st.session_state.target_index = 0

# 換一題按鈕
if st.button("🔄 重新隨機抽一題"):
    st.session_state.shuffled_df = df.sample(frac=1).reset_index(drop=True)
    st.session_state.target_index = 0
    st.rerun()

# 確保索引不超過範圍
if st.session_state.target_index >= len(st.session_state.shuffled_df):
    st.session_state.target_index = 0

current_row = st.session_state.shuffled_df.iloc[st.session_state.target_index]
target_word = str(current_row['word']).strip()
target_trans = str(current_row['trans']).strip()
target_kk = str(current_row['kk']).strip()

# 3. 畫面顯示區
st.subheader("請根據中文意思，在下方輸入框拼寫出對應的英文單字：")
st.info(f"**📝 中文意思：** {target_trans}")

# 使用者輸入框
user_input = st.text_input("請輸入英文單字：", key="user_answer_input")

# 4. 判斷對錯與互動邏輯
if user_input:
    if user_input.strip().lower() == target_word.lower():
        st.success(f"🎉 答對了！太棒了！")
        st.markdown(f"**正確單字：** `{target_word}`")
        st.markdown(f"**KK 音標：** `/{target_kk}/`" if target_kk else "**KK 音標：** (暫無)")
        
        # 發音按鈕區 (正常速度與慢速)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🔊 **正常速度發音**")
            try:
                tts_normal = gTTS(text=target_word, lang='en', slow=False)
                fp_normal = io.BytesIO()
                tts_normal.write_to_fp(fp_normal)
                st.audio(fp_normal, format='audio/mp3')
            except Exception as e:
                st.error(f"語音錯誤：{e}")
            
        with col2:
            st.write("🐢 **慢速發音**")
            try:
                tts_slow = gTTS(text=target_word, lang='en', slow=True)
                fp_slow = io.BytesIO()
                tts_slow.write_to_fp(fp_slow)
                st.audio(fp_slow, format='audio/mp3')
            except Exception as e:
                st.error(f"語音錯誤：{e}")
            
        # 下一題按鈕
        if st.button("下一題 ➡️"):
            st.session_state.target_index = (st.session_state.target_index + 1) % len(st.session_state.shuffled_df)
            # 清空輸入框狀態或重新整理
            st.rerun()
            
    else:
        st.error("❌ 拼寫錯誤，再試一次看看！")
        # 提供貼心小提示
        if st.checkbox("💡 需要 KK 音標提示嗎？"):
            st.info(f"提示 - KK 音標：/{target_kk}/" if target_kk else "提示：此單字暫無 KK 音標")

# 備用：檢視目前的隨機清單總覽
with st.expander("查看目前的隨機單字清單總覽"):
    st.dataframe(
        st.session_state.shuffled_df[['word', 'trans', 'kk', 'level']], 
        use_container_width=True, 
        hide_index=True
    )
