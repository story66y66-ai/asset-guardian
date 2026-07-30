import streamlit as st
import pandas as pd

st.set_page_config(page_title="中文學院 - 澄玄400句成語旗艦挑戰賽", layout="wide", page_icon="📖")

@st.cache_data
def load_flagship_database():
    csv_url = "https://raw.githubusercontent.com/story66y66-ai/asset-guardian/main/idioms.csv"
    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        df = pd.read_csv("idioms.csv")
    
    if "idiom" in df.columns and "meaning" in df.columns:
        df = df.rename(columns={"idiom": "成語", "meaning": "解釋"})
    
    df = df.drop_duplicates(subset=["成語"]).reset_index(drop=True)
    return df

df = load_flagship_database()

st.title(f"📖 中文學院（校長大人專屬成語庫：目前共計 {len(df)} 筆全覆蓋真題）")
st.write("---")

st.success(f"🔥 系統已成功載入 **{len(df)} 筆** 完整不重複成語！")
st.write("---")

tab1, tab2 = st.tabs(["📚 完整題庫總覽", "🎮 成語填空挑戰賽"])

with tab1:
    st.subheader(f"📚 完整成語資料庫預覽（共計 {len(df)} 筆）")
    
    page_size = 20
    total_pages = (len(df) + page_size - 1) // page_size
    if total_pages < 1:
        total_pages = 1
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    col_p1, col_p2 = st.columns([2, 3])
    with col_p1:
        new_page = st.number_input("跳至頁數：", min_value=1, max_value=total_pages, value=st.session_state.current_page, step=1)
        if new_page != st.session_state.current_page:
            st.session_state.current_page = new_page
            st.rerun()
    
    with col_p2:
        st.write("")
        sub1, sub2 = st.columns(2)
        with sub1:
            if st.button("⬅️ 上一頁") and st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
        with sub2:
            if st.button("下一頁 ➡️") and st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()

    current_page = st.session_state.current_page
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    
    st.write(f"目前顯示第 **{current_page}** 頁（第 {start_idx + 1} ~ {end_idx} 筆）：")
    st.write("---")
    
    page_data = df.iloc[start_idx:end_idx]
    
    # 使用安全的原生 Streamlit 介面逐筆列出，完美支援語音朗讀與排版
    for idx, row in page_data.iterrows():
        idiom = row["成語"]
        meaning = row["解釋"]
        display_num = idx + 1
        
        c1, c2, c3 = st.columns([1, 4, 7])
        with c1:
            st.markdown(f"**#{display_num}**")
        with c2:
            st.markdown(f"**{idiom}**")
        with c3:
            st.write(meaning)
        st.divider()

with tab2:
    st.subheader("🎯 挑戰您的無敵成語腦力")
    difficulty = st.radio("請選擇難易度：", ["🌱 初級（提示首字）", "⭐ 中級（提示字數）", "🔥 高級（盲猜挑戰）"], horizontal=True)
    
    st.write("---")
    
    if "golden_target" not in st.session_state or st.button("🔄 點我隨機換一題"):
        st.session_state.golden_target = df.sample(1).iloc[0].to_dict()
        st.rerun()
        
    target = st.session_state.golden_target
    idiom_text = target["成語"]
    meaning_text = target["解釋"]
    
    st.markdown(f"**💡 成語解釋提示**：`{meaning_text}`")
    
    if "初級" in difficulty:
        st.info(f"【初級提示】第一個字是：【**{idiom_text[0]}**】")
    elif "中級" in difficulty:
        st.info(f"【中級提示】總字數為 {len(idiom_text)} 個字")
    else:
        st.info("【高級挑戰】完全盲猜！")
        
    user_guess = st.text_input("請輸入您的答案：", key="golden_guess_input")
    
    if st.button("送出答案"):
        if user_guess.strip() == idiom_text:
            st.success(f"👑 太神啦！校長大人完美答對！這就是【{idiom_text}】！")
            st.balloons()
        else:
            st.error("❌ 哎呀，答案不太對喔，再挑戰看看吧！")

st.write("---")

if st.button("⬅️ 返回澄玄大學首頁"):
    st.switch_page("streamlit_app.py")
