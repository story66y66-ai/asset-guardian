import streamlit as st

# 1. 澄玄的單字資料庫 (可隨時擴充)
if 'word_list' not in st.session_state:
    st.session_state.word_list = [
        {"word": "Apple", "trans": "蘋果", "pron": "欸-波"},
        {"word": "Book", "trans": "書", "pron": "布-克"},
        {"word": "Cat", "trans": "貓", "pron": "凱-特"}
    ]
    st.session_state.index = 0

# 2. 核心翻牌邏輯
def next_word():
    st.session_state.index = (st.session_state.index + 1) % len(st.session_state.word_list)
    st.session_state.show_trans = False

# 初始化顯示狀態
if 'show_trans' not in st.session_state:
    st.session_state.show_trans = False

# 3. 視覺化介面呈現
st.title("🍎 澄玄的單字訓練農場")

current_data = st.session_state.word_list[st.session_state.index]

# 單字卡顯示區
st.markdown(f"""
    <div style="padding: 20px; border: 2px solid #27ae60; border-radius: 15px; text-align: center;">
        <h1 style="font-size: 50px;">{current_data['word']}</h1>
    </div>
""", unsafe_allow_html=True)

# 點擊翻開按鈕
if st.button("翻開卡片 / 下一個"):
    if not st.session_state.show_trans:
        st.session_state.show_trans = True
    else:
        next_word()
        st.rerun()

# 翻開後的資訊
if st.session_state.show_trans:
    st.success(f"中文翻譯：{current_data['trans']}")
    st.info(f"直觀拼音：{current_data['pron']}")
        st.write("### 實驗紀錄")
        st.success("目前無異常紀錄。")

# 頁腳
st.sidebar.markdown("---")
st.sidebar.info("開發模式：活躍中")
