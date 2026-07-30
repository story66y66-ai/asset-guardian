import streamlit as st
import pandas as pd
import os
import random

st.set_page_config(page_title="中文學院 - 澄玄大學", layout="wide", page_icon="📖")

st.title("📖 中文學院（成語學習與挑戰專區）")
st.write("---")

# 設定成語資料儲存的 CSV 檔案名稱
DATA_FILE = "chinese_idioms.csv"

# 初始化資料檔案（預設帶入幾筆經典成語讓遊戲可以玩）
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame([
        {"成語": "一心一意", "解釋": "形容心思專一，毫無雜念。"},
        {"成語": "貌合神離", "解釋": "表面上關係親密，實際上心懷各異。"},
        {"成語": "水落石出", "解釋": "比喻事情真相大白。"},
        {"成語": "金玉良言", "解釋": "比喻寶貴的勸告或教益。"}
    ])
    df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# 讀取現有資料
df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")

# 使用標籤頁（Tabs）區隔「遊戲挑戰」與「私房成語管理」
tab1, tab2 = st.tabs(["🎮 成語填空挑戰賽", "✍️ 我的私房成語庫"])

with tab1:
    st.subheader("🎯 選擇挑戰難易度")
    difficulty = st.radio("請選擇您的挑戰等級：", ["🌱 初級（提示完整）", "⭐ 中級（標準挑戰）", "🔥 高級（大師闖關）"], horizontal=True)
    
    st.write("---")
    
    if len(df) > 0:
        # 隨機挑選一筆成語來出題
        if "current_idiom" not in st.session_state:
            st.session_state.current_idiom = df.sample(1).iloc[0].to_dict()
        
        target = st.session_state.current_idiom
        idiom_text = target["成語"]
        meaning_text = target["解釋"]
        
        st.markdown(f"**💡 本關提示（解釋）**：{meaning_text}")
        
        # 依據難易度決定挖空方式
        if "初級" in difficulty:
            st.info(f"【初級提示】這是一句 __ 字成語，開頭的第一個字是：【{idiom_text[0]}】")
        elif "中級" in difficulty:
            st.info(f"【中級提示】這是一句 __ 字成語，請根據上方提示填入完整成語！")
        else:
            st.info(f"【高級挑戰】完全盲猜！請憑實力輸入這句成語！")
            
        user_guess = st.text_input("請輸入您的答案：", key="game_input")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("送出答案"):
                if user_guess.strip() == idiom_text:
                    st.success(f"🎉 太棒了！答對啦！這就是【{idiom_text}】！")
                    st.balloons()
                else:
                    st.error("❌ 哎呀，答案不太對喔，再試試看！")
        with col_b:
            if st.button("換一題"):
                st.session_state.current_idiom = df.sample(1).iloc[0].to_dict()
                st.rerun()
    else:
        st.warning("目前資料庫沒有成語，請先到「我的私房成語庫」新增資料！")

with tab2:
    st.subheader("✍️ 新增自定義成語")
    with st.form("idiom_form"):
        new_idiom = st.text_input("請輸入成語（例如：一心一意）：")
        new_meaning = st.text_input("請輸入成語解釋或典故：")
        submit_button = st.form_submit_button("儲存至私房成語庫")

        if submit_button:
            if new_idiom and new_meaning:
                new_data = pd.DataFrame([{"成語": new_idiom, "解釋": new_meaning}])
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                st.success(f"成功新增成語：【{new_idiom}】！")
                st.rerun()
            else:
                st.warning("「成語」與「解釋」欄位都不能空白喔！")

    st.write("---")
    st.subheader("📚 現有成語清單")
    if len(df) > 0:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("目前還沒有成語資料！")

st.write("---")

# 返回首頁按鈕
if st.button("⬅️ 返回澄玄大學首頁"):
    st.switch_page("streamlit_app.py")
