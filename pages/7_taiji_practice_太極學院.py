import os
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="太極學院", page_icon="🥋", layout="wide")

st.title("🥋 太極學院 - 招式與句子練習")


# 1. 讀取 CSV 資料函數
@st.cache_data
def load_data():
    csv_paths = ["taiji_recipes_太極學院.csv", "pages/taiji_recipes_太極學院.csv"]
    df = None
    for path in csv_paths:
        if os.path.exists(path):
            df = pd.read_csv(path, encoding="utf-8-sig")
            break
    if df is None:
        df = pd.DataFrame(
            {
                "id": [1],
                "url": [
                    "https://youtu.be/FFAnPE9dvSo?si=1UVou4UawOr0TCfo"
                ],
                "title": ["1.起勢"],
            }
        )
    return df


df = load_data()

# 初始化 Session State
if "selected_index" not in st.session_state:
    st.session_state.selected_index = 0

total_items = len(df)
if st.session_state.selected_index >= total_items:
    st.session_state.selected_index = 0

current_row = df.iloc[st.session_state.selected_index]
current_title_raw = str(current_row["title"])

# 自動將標題前面的數字和點濾掉，留下純招式名稱給句子測驗用
clean_move_name = re.sub(r"^\d+\.", "", current_title_raw).strip()

# 2. 上方按鈕列：點擊切換招式
st.markdown("### 📌 選擇招式")
cols_per_row = 8
for i in range(0, total_items, cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        idx = i + j
        if idx < total_items:
            row_item = df.iloc[idx]
            btn_label = str(row_item["title"])
            with cols[j]:
                if st.button(btn_label, key=f"btn_{idx}", use_container_width=True):
                    st.session_state.selected_index = idx
                    st.rerun()

st.markdown("---")

# 3. 左右分欄介面
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader(f"📺 影片教學：{current_title_raw}")
    current_url = (
        str(current_row["url"])
        if pd.notna(current_row["url"])
        else ""
    )

    user_url = st.text_input(
        "輸入或修改 YouTube 網址：",
        value=current_url,
        key=f"url_input_{st.session_state.selected_index}",
    )

    if user_url and "youtu" in user_url:
        try:
            embed_url = user_url
            if "watch?v=" in user_url:
                embed_url = user_url.replace("watch?v=", "embed/")
            elif "youtu.be/" in user_url:
                parts = user_url.split("youtu.be/")
                if len(parts) > 1:
                    video_id = parts[1].split("?")[0]
                    embed_url = f"https://www.youtube.com/embed/{video_id}"

            st.components.v1.iframe(embed_url, height=315)
        except Exception:
            st.warning("無法載入影片預覽，請確認網址格式是否正確。")
    else:
        st.info("目前尚無此招式的 YouTube 網址，請在上方輸入框貼上。")

with col_right:
    st.subheader("📝 太極招式文字與句子測驗")

    st.markdown(
        f"""
    <div style="padding: 15px; border-radius: 8px; background-color: #262730; color: white; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 20px;">
        當前練習招式：{clean_move_name}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ✍️ 句子測驗練習")
    st.text(f"請依據上方招式進行輸入練習：")

    user_input = st.text_input(
        "請在此輸入招式名稱：", key=f"quiz_input_{st.session_state.selected_index}"
    )

    if st.button("檢查答案"):
        if not user_input.strip():
            st.warning("請先輸入文字再檢查喔！")
        elif user_input.strip() == clean_move_name:
            st.success(f"🎉 太棒了！答對了！正確答案就是【{clean_move_name}】")
        else:
            st.error(f"❌ 哎呀，再試一次看看！您輸入的是：{user_input}")

    with st.expander("📂 檢視全部 24 式清單"):
        for idx, row in df.iterrows():
            prefix = "👉 " if idx == st.session_state.selected_index else "  "
            st.text(f"{prefix} {row['title']}")
