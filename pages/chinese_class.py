import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="中文學院 - 澄玄大學", layout="wide", page_icon="📖")

st.title("📖 中文學院（成語學習專區）")
st.write("---")

# 設定成語資料儲存的 CSV 檔案名稱
DATA_FILE = "chinese_idioms.csv"

# 初始化資料檔案
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["成語", "解釋"])
    df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# 讀取現有資料
df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")

# 區塊一：新增成語輸入介面
st.subheader("✍️ 新增一筆成語")
with st.form("idiom_form"):
    new_idiom = st.text_input("請輸入成語（例如：一心一意）：")
    new_meaning = st.text_input("請輸入成語解釋或典故：")
    submit_button = st.form_submit_button("儲存成語")

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

# 區塊二：顯示成語清單
st.subheader("📚 成語學習清單")
if len(df) > 0:
    st.dataframe(df, use_container_width=True)
else:
    st.info("目前還沒有成語資料，快在上方新增第一筆吧！")

st.write("---")

# 返回首頁按鈕
if st.button("⬅️ 返回澄玄大學首頁"):
    st.switch_page("streamlit_app.py")
