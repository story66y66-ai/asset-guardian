import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# 強制調整整體字體與側邊欄位字體
st.markdown("""
    <style>
    /* 放大左側選單欄位的字體 */
    [data-testid="stSidebar"] {
        font-size: 28px !important;
    }
    /* 放大選單內部的選項文字 */
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a {
        font-size: 28px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 澄玄大學 - 語言學院")

# 真正的完整大合體：同時讀取 words.csv 與 Level 1 ~ 6，自動合併、過濾重複、排序
@st.cache_data
def load_data():
    all_dfs = []
    
    # 1. 先把 words.csv 納入清單（如果存在的話）
    try:
        df_words = pd.read_csv("words.csv")
        all_dfs.append(df_words)
    except Exception:
        pass

    # 2. 依序把 words_level1.csv 到 words_level6.csv 全部納入清單
    for i in range(1, 7):
        file_name = f"words_level{i}.csv"
        try:
            df_temp = pd.read_csv(file_name)
            all_dfs.append(df_temp)
        except Exception:
            pass  # 如果某個檔案暫時不存在就跳過
            
    # 3. 如果有讀到任何資料，把它們全部上下合併在一起
    if all_dfs:
        df = pd.concat(all_dfs, ignore_index=True)
    else:
        # 萬一都讀不到，給個空的防呆
        df = pd.DataFrame(columns=['word', 'trans', 'kk', 'level'])
        
    # 4. 自動過濾重複的單字（保留第一次出現的）
    if "word" in df.columns:
        df = df.drop_duplicates(subset=["word"])
        
    # 5. 按照 level 排序（由小到大）
    if "level" in df.columns:
        df = df.sort_values(by="level", ascending=True)
        
    df = df.reset_index(drop=True)
    return df

df = load_data()

# 初始化 Session State，用來同步單字
if 'selected_word' not in st.session_state:
    if not df.empty:
        st.session_state.selected_word = df['word'].iloc[0]
    else:
        st.session_state.selected_word = ""

# 1. 顯示表格
st.subheader("點選表格中的單字：")
if not df.empty:
    event = st.dataframe(
        df[['word', 'trans', 'kk', 'level']],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # 如果使用者點了表格，自動同步更新選單變數
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        st.session_state.selected_word = df.iloc[selected_index]['word']

    # 2. 同步的選單
    word_list = df['word'].tolist()
    if st.session_state.selected_word not in word_list:
        st.session_state.selected_word = word_list[0]

    selected_word = st.selectbox(
        "目前選取的單字：",
        word_list,
        index=word_list.index(st.session_state.selected_word)
    )

    # 更新 Session State
    st.session_state.selected_word = selected_word

    # 3. 自動發音
    if selected_word:
        tts = gTTS(text=selected_word, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, autoplay=True)
else:
    st.warning("目前找不到任何單字資料，請確認檔案是否有正確上傳！")
