import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("📖 澄玄大學 - 語言學院")

# 1. 讀取資料
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 2. 選擇等級
selected_level = st.selectbox("請選擇學習等級：", sorted(df['level'].unique()))

# 3. 篩選與隨機排序
filtered_df = df[df['level'] == selected_level].copy()
filtered_df = filtered_df.sample(frac=1, random_state=42).reset_index(drop=True)

# 4. 顯示表格 (使用較簡潔的寫法)
st.subheader(f"Level {selected_level} 學習清單")
st.dataframe(filtered_df[['word', 'trans', 'kk']], use_container_width=True, hide_index=True)

# 5. 互動式播放功能
st.divider()
st.subheader("🔊 單字聽力練習")

# 建立兩欄：左邊選單，右邊播放按鈕
col1, col2 = st.columns([3, 1])
with col1:
    selected_word = st.selectbox("請從下方選單選擇一個單字進行播放：", filtered_df['word'].tolist())
with col2:
    st.write("###") # 調整對齊
    if st.button("播放發音"):
        tts = gTTS(text=selected_word, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)

st.write("---")
st.info("校長，現在單字與發音已經重新整合，您可以隨時切換單字並點擊播放。")
