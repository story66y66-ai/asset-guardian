elif selection == "訓練農場":
    st.header("🏗️ 訓練農場")
    tab1, tab2, tab3 = st.tabs(["測試數據", "草稿區", "實驗紀錄"])
    with tab1:
        st.write("這裡是測試數據區")
    with tab2:
        st.write("這裡是草稿區")
    with tab3:
        st.write("這裡是實驗紀錄區")
