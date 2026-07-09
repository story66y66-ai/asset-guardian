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

# 2. 讓使用者選擇等級
selected_level = st.selectbox("請選擇學習等級：", sorted(df['level'].unique()))

# 3. 篩選該等級，並使用 'random_state' 固定排序
# 這樣做會打亂 A-Z，但每次重開頁面順序都會維持一樣，看起來像精心安排的順序
filtered_df = df[df['level'] == selected_level].copy()
filtered_df = filtered_df.sample(frac=1, random_state=42).reset_index(drop=True)

# 4. 顯示表格
st.subheader(f"Level {selected_level} 學習清單")
st.dataframe(filtered_df[['word', 'trans', 'kk']], use_container_width=True, hide_index=True)

# 5. 發音功能
word_list = filtered_df['word'].tolist()
selected_word = st.selectbox("請選擇一個單字：", word_list)

if st.button("播放發音"):
    tts = gTTS(text=selected_word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp)
