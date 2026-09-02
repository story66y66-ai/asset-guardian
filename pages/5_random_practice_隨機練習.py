import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("🎲 隨機挑戰 - 語言學院")

# 1. 讀取資料（加入防錯處理）
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"讀取 CSV 檔案失敗，請確認檔案是否存在。錯誤訊息：{e}")
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

# 取得目前題目
current_row = st.session_state.shuffled_df.iloc[st.session_state.target_index]
target_word = current_row['word']
target_trans = current_row['trans']
target_kk = current_row['kk']

# 3. 畫面顯示區
st.subheader("請根據中文意思，在下方輸入框拼寫出對應的英文單字：")
st.info(f"**📝 中文意思：** {target_trans}")

# 使用者輸入框
user_input = st.text_input("請輸入英文單字：", key="user_answer_input")

# 4. 判斷對錯與互動邏輯
if user_input:
    # 轉成小寫比對，避免大小寫差異造成誤判
    if user_input.strip().lower() == str(target_word).lower():
        st.success(f"🎉 答對了！太棒了！")
        st.markdown(f"**正確單字：** `{target_word}`")
        st.markdown(f"**KK 音標：** `{target_kk}`")
        
        # 發音按鈕區 (正常速度與慢速)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🔊 **正常速度發音**")
            tts_normal = gTTS(text=str(target_word), lang='en', slow=False)
            fp_normal = io.BytesIO()
            tts_normal.write_to_fp(fp_normal)
            st.audio(fp_normal, format='audio/mp3')
            
        with col2:
            st.write("🐢 **慢速發音**")
            tts_slow = gTTS(text=str(target_word), lang='en', slow=True)
            fp_slow = io.BytesIO()
            tts_slow.write_to_fp(fp_slow)
            st.audio(fp_slow, format='audio/mp3')
            
        # 下一題按鈕
        if st.button("下一題 ➡️"):
            st.session_state.target_index = (st.session_state.target_index + 1) % len(st.session_state.shuffled_df)
            st.rerun()
            
    else:
        st.error("❌ 拼寫錯誤，再試一次看看！")
        # 提供貼心小提示
        if st.checkbox("💡 需要 KK 音標提示嗎？"):
            st.info(f"提示 - KK 音標：{target_kk}")

# 備用：若想隨時查看目前的完整隨機清單核對
with st.expander("查看目前的隨機單字清單總覽"):
    st.dataframe(
        st.session_state.shuffled_df[['word', 'trans', 'kk', 'level']], 
        use_container_width=True, 
        hide_index=True
    )
