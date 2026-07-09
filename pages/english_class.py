import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("📖 澄玄大學 - 語言學院")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()
selected_level = st.selectbox("請選擇學習等級：", sorted(df['level'].unique()))

# 篩選並固定隨機排序
filtered_df = df[df['level'] == selected_level].copy()
filtered_df = filtered_df.sample(frac=1, random_state=42).reset_index(drop=True)

# 顯示帶有選擇框的編輯器
st.subheader(f"Level {selected_level} 學習清單")
# 建立一個包含選取欄位的 DataFrame
df_to_show = filtered_df[['word', 'trans', 'kk']].copy()
# 使用 data_editor 來產生左邊的勾選框
edited_df = st.data_editor(
    df_to_show, 
    column_config={"_index": None}, 
    disabled=["word", "trans", "kk"], 
    use_container_width=True
)

# 偵測是否有勾選，並提取選取的單字
# 這裡我們模擬之前您習慣的操作方式
st.subheader("🔊 單字聽力練習")
selected_word = st.selectbox("請確認您想播放的單字：", filtered_df['word'].tolist())

if st.button("播放發音"):
    tts = gTTS(text=selected_word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp)
