elif selection == "訓練農場":
    st.header("🏗️ 訓練農場")
    tab1, tab2, tab3 = st.tabs(["測試數據", "草稿區", "實驗紀錄"])
    
    with tab1:
        st.subheader("🍎 英文單字王")
        
        # 1. 資料庫初始化 (放在訓練農場分頁內)
        if 'word_list' not in st.session_state:
            st.session_state.word_list = [
                {"word": "Apple", "trans": "蘋果", "pron": "欸-波"},
                {"word": "Book", "trans": "書", "pron": "布-克"}
            ]
            st.session_state.index = 0
            st.session_state.show_trans = False

        # 2. 顯示單字
        current_data = st.session_state.word_list[st.session_state.index]
        st.markdown(f"<h1 style='text-align: center;'>{current_data['word']}</h1>", unsafe_allow_html=True)

        # 3. 按鈕邏輯
        col1, col2 = st.columns(2)
        with col1:
            if st.button("翻開卡片"):
                st.session_state.show_trans = True
        with col2:
            if st.button("下一個"):
                st.session_state.index = (st.session_state.index + 1) % len(st.session_state.word_list)
                st.session_state.show_trans = False
                st.rerun()

        # 4. 顯示答案
        if st.session_state.show_trans:
            st.success(f"中文翻譯：{current_data['trans']}")
            st.info(f"直觀拼音：{current_data['pron']}")

    with tab2:
        st.write("這裡是草稿區")
    with tab3:
        st.write("### 實驗紀錄")
        st.write("這裡是實驗紀錄區")
