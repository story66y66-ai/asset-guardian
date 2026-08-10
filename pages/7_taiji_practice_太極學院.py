import streamlit as st

st.title("🥋 太極學院 - 招式練習與測試")
st.write("---")

# 1. 太極招式資料庫（直接寫在程式碼裡，完全不需要 csv 檔！）
taiji_data = {
    "起式": {
        "description": "兩腳與肩同寬，身體放鬆，雙手緩緩抬起與肩平。",
        "tips": "呼吸要深長，意念放鬆，重心平穩。",
        "question": "請問在「起式」時，雙手要抬到什麼高度？",
        "options": ["頭頂", "與肩平", "腰部以下"],
        "answer": "與肩平"
    },
    "野馬分鬃": {
        "description": "轉腰分掌，左右交替如野馬鬃毛分開之意。",
        "tips": "上體保持中正，動作要圓轉連貫。",
        "question": "請問「野馬分鬃」的主要動作核心是什麼？",
        "options": ["轉腰分掌", "原地跳躍", "單腳站立"],
        "answer": "轉腰分掌"
    },
    "白鶴亮翅": {
        "description": "虛步挑掌，右手上提，左手向下按。",
        "tips": "虛實分明，眼神隨手勢望向前方。",
        "question": "請問「白鶴亮翅」的步型是什麼？",
        "options": ["弓步", "馬步", "虛步"],
        "answer": "虛步"
    }
}

# 2. 選擇模式：看說明 還是 做測試
mode = st.radio("請選擇學習模式：", ["📖 招式動作說明", "✍️ 太極隨堂小測驗"])

st.write("---")

if mode == "📖 招式動作說明":
    st.subheader("📍 招式動作導覽")
    selected_move = st.selectbox("選擇想要查看的招式：", list(taiji_data.keys()))
    
    st.info(f"**動作說明**：{taiji_data[selected_move]['description']}")
    st.success(f"**練習要領**：{taiji_data[selected_move]['tips']}")

else:
    st.subheader("✍️ 招式隨堂小測驗")
    quiz_move = st.selectbox("選擇要測試的招式題目：", list(taiji_data.keys()))
    
    q_info = taiji_data[quiz_move]
    st.write(f"**【題目】** {q_info['question']}")
    
    user_answer = st.radio("請選擇正確答案：", q_info['options'], key=quiz_move)
    
    if st.button("送出答案"):
        if user_answer == q_info['answer']:
            st.success("🎉 太棒了！回答正確，您的太極功力又更深厚了！")
        else:
            st.error("❌ 答錯囉！再回頭看一下動作說明複習一下吧！")
