# 1. 導航選單設定
nav_options = {
    "訓練農場": "🏗️", "測驗中心": "🎮", "進化中心": "💡",
    "照顧服務": "🦺", "食品科技": "🧪", "創作農場": "🎨", "學習農場": "📚", "生活農場": "🏠"
}
selection = st.sidebar.radio("請選擇前往的區域：", list(nav_options.keys()), format_func=lambda x: f"{nav_options[x]} {x}")

# 2. 擴充單字庫 (這裡以後可以擴充到 100 個)
word_data = [
    
] word_data = [
    {"word": "Apple", "trans": "蘋果", "kk": "/ˈæp.əl/"}, {"word": "Banana", "trans": "香蕉", "kk": "/bəˈnæn.ə/"},
    {"word": "Cat", "trans": "貓", "kk": "/kæt/"}, {"word": "Dog", "trans": "狗", "kk": "/dɔːɡ/"},
    {"word": "Elephant", "trans": "大象", "kk": "/ˈel.ɪ.fənt/"}, {"word": "Fish", "trans": "魚", "kk": "/fɪʃ/"},
    {"word": "Girl", "trans": "女孩", "kk": "/ɡɜːrl/"}, {"word": "House", "trans": "房子", "kk": "/haʊs/"},
    {"word": "Ice", "trans": "冰", "kk": "/aɪs/"}, {"word": "Jump", "trans": "跳", "kk": "/dʒʌmp/"},
    {"word": "Key", "trans": "鑰匙", "kk": "/kiː/"}, {"word": "Lion", "trans": "獅子", "kk": "/ˈlaɪ.ən/"},
    {"word": "Moon", "trans": "月亮", "kk": "/muːn/"}, {"word": "Note", "trans": "筆記", "kk": "/noʊt/"},
    {"word": "Orange", "trans": "橘子", "kk": "/ˈɔːr.ɪndʒ/"}, {"word": "Pen", "trans": "筆", "kk": "/pen/"},
    {"word": "Queen", "trans": "皇后", "kk": "/kwiːn/"}, {"word": "Rain", "trans": "雨", "kk": "/reɪn/"},
    {"word": "Sun", "trans": "太陽", "kk": "/sʌn/"}, {"word": "Tree", "trans": "樹", "kk": "/triː/"},
    {"word": "Umbrella", "trans": "雨傘", "kk": "/ʌmˈbrel.ə/"}, {"word": "Van", "trans": "貨車", "kk": "/væn/"},
    {"word": "Water", "trans": "水", "kk": "/ˈwɔː.tər/"}, {"word": "Box", "trans": "盒子", "kk": "/bɑːks/"},
    {"word": "Yellow", "trans": "黃色", "kk": "/ˈjel.oʊ/"}, {"word": "Zoo", "trans": "動物園", "kk": "/zuː/"},
    {"word": "Bird", "trans": "鳥", "kk": "/bɜːrd/"}, {"word": "Cake", "trans": "蛋糕", "kk": "/keɪk/"},
    {"word": "Duck", "trans": "鴨子", "kk": "/dʌk/"}, {"word": "Egg", "trans": "蛋", "kk": "/eɡ/"},
    {"word": "Frog", "trans": "青蛙", "kk": "/frɑːɡ/"}, {"word": "Goat", "trans": "山羊", "kk": "/ɡoʊt/"},
    {"word": "Hat", "trans": "帽子", "kk": "/hæt/"}, {"word": "Ink", "trans": "墨水", "kk": "/ɪŋk/"},
    {"word": "Jet", "trans": "噴射機", "kk": "/dʒet/"}, {"word": "Kite", "trans": "風箏", "kk": "/kaɪt/"},
    {"word": "Lamp", "trans": "燈", "kk": "/læmp/"}, {"word": "Milk", "trans": "牛奶", "kk": "/mɪlk/"},
    {"word": "Net", "trans": "網", "kk": "/net/"}, {"word": "Owl", "trans": "貓頭鷹", "kk": "/aʊl/"},
    {"word": "Pig", "trans": "豬", "kk": "/pɪɡ/"}, {"word": "Quilt", "trans": "被子", "kk": "/kwɪlt/"},
    {"word": "Rat", "trans": "老鼠", "kk": "/ræt/"}, {"word": "Ship", "trans": "船", "kk": "/ʃɪp/"},
    {"word": "Toy", "trans": "玩具", "kk": "/tɔɪ/"}, {"word": "Up", "trans": "向上", "kk": "/ʌp/"},
    {"word": "Vest", "trans": "背心", "kk": "/vest/"}, {"word": "Wolf", "trans": "狼", "kk": "/wʊlf/"},
    {"word": "Yard", "trans": "庭院", "kk": "/jɑːrd/"}, {"word": "Zip", "trans": "拉鍊",

# 3. 各區邏輯
if selection == "訓練農場":
    st.header("🏗️ 訓練農場 (學習區)")
    if 'train_word' not in st.session_state: st.session_state.train_word = random.choice(word_data)
    word = st.session_state.train_word
    st.write(f"### 英文：{word['word']} | 中文：{word['trans']} | KK：{word['kk']}")
    if st.button("🔊 聽發音"):
        tts = gTTS(text=word['word'], lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    if st.button("換一個單字"): del st.session_state.train_word; st.rerun()

elif selection == "測驗中心":
    st.header("🎮 測驗中心")
    mode = st.radio("模式：", ["中文輸入挑戰", "拼字挑戰"], horizontal=True)
    if 'quiz_word' not in st.session_state: st.session_state.quiz_word = random.choice(word_data)
    word = st.session_state.quiz_word
    
    if mode == "中文輸入挑戰":
        st.write(f"請輸入 **{word['word']}** 的中文：")
        user_in = st.text_input("輸入：")
        if st.button("確認") and user_in == word['trans']:
            st.success("✅ 答對！"); del st.session_state.quiz_word; st.rerun()
    else:
        st.write(f"請拼出 **{word['trans']}** 的英文：")
        user_in = st.text_input("輸入：")
        if st.button("確認") and user_in.lower() == word['word'].lower():
            st.success("✅ 答對！"); del st.session_state.quiz_word; st.rerun()

elif selection == "進化中心":
    st.header("💡 進化中心")
    with open("streamlit_app.py", "r", encoding="utf-8") as f: st.code(f.read())

else:
    st.write(f"歡迎來到 {selection}，這裡正在建設中。")
