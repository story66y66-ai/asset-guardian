import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.title("📖 互動語言學院")

# 讀取資料
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

df = load_data()

# 使用 data_editor，讓表格變成可互動的介面
st.write("請點選表格中的任一單字行：")
edited_df = st.data_editor(
    df, 
    use_container_width=True, 
    hide_index=True,
    disabled=df.columns # 設為 disable 讓使用者不能修改資料，只能點選
)

# 偵測是否有被選取的列
# 當使用者點選表格中的某一行時，我們可以抓取該行內容
# 注意：data_editor 本身在點選時會更新狀態
# 這裡我們簡化處理，讓使用者點選後按確認發音，或是透過選擇器
selected_word = st.selectbox("確認選擇的單字：", df['word'].tolist())

if st.button("點擊發音"):
    tts = gTTS(text=selected_word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3')
