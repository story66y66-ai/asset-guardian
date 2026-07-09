import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("📖 澄玄大學 - 語言學院")

# 讀取資料
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 選擇等級（保持分級功能）
levels = sorted(df['level'].unique())
selected_level = st.selectbox("請選擇學習等級：", levels)

# 篩選資料
filtered_df = df[df['level'] == selected_level].copy()
# 為了避免 A-Z 排序，這裡不執行 sort_values，保持原始 CSV 順序

# 顯示表格
st.dataframe(filtered_df[['word', 'trans', 'kk']], use_container_width=True, hide_index=True)

# 優化互動：將選單作為核心輸入，一旦選單變更，音訊會自動更新
selected_word = st.selectbox("請點選或輸入想聽的單字：", filtered_df['word'].tolist())

# 核心改善：將自動播放邏輯封裝，不再需要「發音按鈕」
if selected_word:
    tts = gTTS(text=selected_word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    # 將 autoplay 設為 True，讓它自動開始播放
    st.audio(fp, format='audio/mp3', autoplay=True)
