import glob
import io
import os
import re
import urllib.parse
import gTTS
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 設定頁面為寬螢幕模式
st.set_page_config(layout="wide", page_title="澄玄太極學院", page_icon="☯️")

# 樣式設定
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { font-size: 28px !important; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] a { font-size: 28px !important; }
    
    .stTextInput input { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 50px !important;
    }
    
    div[data-baseweb="input"] input {
        font-size: 22px !important;
        color: #000000 !important;
        font-weight: bold !important;
        height: 50px !important;
    }

    button[data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: bold !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
    
    div.stButton > button { 
        font-size: 20px !important; 
        padding: 12px 20px !important; 
        font-weight: bold !important;
    }

    .stTextArea textarea { 
        font-size: 22px !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        height: 580px !important;
        resize: vertical !important; 
    }
    
    .sentence-display {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        line-height: 1.6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("☯️ 澄玄太極學院 - 太極拳/劍套路與招式筆記")

# 鎖定正確的 CSV 檔名
TAICHI_CSV_FILE = "taiji_recipes_太極學院.csv"

# 預設 key 與 State 初始化 (支援 50 個招式/章節欄位)
for idx in range(1, 51):
  if f"yt_input_url_{idx}" not in st.session_state:
    st.session_state[f"yt_input_url_{idx}"] = ""
  if f"taichi_text_input_{idx}" not in st.session_state:
    st.session_state[f"taichi_text_input_{idx}"] = ""

if "playlist_names" not in st.session_state:
  st.session_state.playlist_names = {
      idx: f"招式/段落 {idx}" for idx in range(1, 51)
  }

# 讀取太極學院專屬 CSV 資料
if os.path.exists(TAICHI_CSV_FILE):
  try:
    saved_df = pd.read_csv(TAICHI_CSV_FILE)
    for _, row in saved_df.iterrows():
      idx_val = int(row["id"])
      if 1 <= idx_val <= 50:
        if pd.notna(row.get("url")):
          st.session_state[f"yt_input_url_{idx_val}"] = str(row["url"])
        if pd.notna(row.get("title")):
          st.session_state.playlist_names[idx_val] = str(row["title"])

        # 自動相容各種可能紀錄招式文字的欄位名稱 (text, lyrics, content)
        text_val = ""
        if "text" in saved_df.columns and pd.notna(row.get("text")):
          text_val = str(row["text"])
        elif "lyrics" in saved_df.columns and pd.notna(row.get("lyrics")):
          text_val = str(row["lyrics"])
        elif "content" in saved_df.columns and pd.notna(row.get("content")):
          text_val = str(row["content"])

        if text_val:
          st.session_state[f"taichi_text_input_{idx_val}"] = text_val
  except Exception:
    pass

if "current_page" not in st.session_state:
  st.session_state.current_page = 1

st.write("")

# 匯出與儲存功能（檔案名稱精準鎖定 taiji_recipes_太極學院.csv）
csv_data_list = []
for idx in range(1, 51):
  csv_data_list.append({
      "id": idx,
      "url": st.session_state.get(f"yt_input_url_{idx}", "").strip(),
      "title": st.session_state.playlist_names.get(idx, f"招式 {idx}"),
      "text": st.session_state.get(f"taichi_text_input_{idx}", ""),
  })

df_export = pd.DataFrame(csv_data_list)
csv_text_output = df_export.to_csv(index=False, encoding="utf-8-sig", quoting=1)

with st.expander(f"📥 匯出與下載太極招式庫（{TAICHI_CSV_FILE}）"):
  st.download_button(
      label=f"📥 點我直接下載 {TAICHI_CSV_FILE} 檔案",
      data=csv_text_output,
      file_name=TAICHI_CSV_FILE,
      mime="text/csv",
      use_container_width=True,
  )
  st.text_area(
      "完整資料預覽：",
      value=csv_text_output,
      height=120,
      label_visibility="collapsed",
  )

st.write("")

# 頁碼切換 (1~5頁，每頁10個招式)
if "page_names" not in st.session_state:
  st.session_state.page_names = {
      p: f"第 {p} 區段 (招式 {(p-1)*10 + 1} ~ {p*10})" for p in range(1, 6)
  }

page_cols = st.columns(5)
for p in range(1, 6):
  with page_cols[p - 1]:
    btn_label = (
        f"👉 【第 {p} 頁】\n{st.session_state.page_names[p]}"
        if st.session_state.current_page == p
        else f"第 {p} 頁\n{st.session_state.page_names[p]}"
    )
    if st.button(btn_label, key=f"page_btn_{p}", use_container_width=True):
      st.session_state.current_page = p
      st.rerun()

current_page = st.session_state.current_page
start_idx = (current_page - 1) * 10 + 1
end_idx = current_page * 10

tab_titles = [
    f"🥋 {st.session_state.playlist_names[idx]}"
    for idx in range(start_idx, end_idx + 1)
]
tabs = st.tabs(tab_titles)

for tab_idx, tab in enumerate(tabs):
  absolute_idx = start_idx + tab_idx

  with tab:
    url_key = f"yt_input_url_{absolute_idx}"
    text_key = f"taichi_text_input_{absolute_idx}"

    with st.expander(f"✏️ 修改【招式/段落 {absolute_idx}】名稱"):
      curr_name = st.session_state.playlist_names[absolute_idx]
      new_track_name = st.text_input(
          f"招式 {absolute_idx} 名稱：",
          value=curr_name,
          key=f"rename_track_{absolute_idx}",
      )
      if new_track_name != curr_name:
        st.session_state.playlist_names[absolute_idx] = new_track_name
        st.rerun()

    left_col, right_col = st.columns([1, 1.2], vertical_alignment="top")

    with left_col:
      # 直接綁定 key，確保 YouTube 網址順利帶入框中
      user_yt_link = st.text_input(
          "請在此貼上太極教學影片網址：", key=url_key
      )

      if st.button(
          f"💾 儲存【招式 {absolute_idx}】資料",
          key=f"save_url_{absolute_idx}",
          use_container_width=True,
      ):
        st.success(f"🎉 招式 {absolute_idx} 資料已成功儲存！")
        st.rerun()

      if user_yt_link.strip():
        try:
          raw_url = user_yt_link.strip()
          video_id = ""
          if "shorts/" in raw_url:
            video_id = (
                raw_url.split("shorts/")[-1].split("?")[0].split("/")[0]
            )
          elif "watch?v=" in raw_url:
            video_id = raw_url.split("watch?v=")[-1].split("&")[0]
          elif "youtu.be/" in raw_url:
            video_id = (
                raw_url.split("youtu.be/")[-1].split("?")[0].split("/")[0]
            )

          if video_id:
            embed_url = f"https://www.youtube.com/embed/{video_id}?loop=1&playlist={video_id}"
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; margin-top: 15px;">
                    <iframe width="100%" height="450" src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
                """,
                unsafe_allow_html=True,
            )
          else:
            st.warning("無法辨識影片網址，請確認連結。")
        except Exception as e:
          st.error(f"影片載入失敗：{e}")
      else:
        st.info("📺 請在上方輸入網址以顯示太極教學影片。")

    with right_col:
      st.subheader("✍️ 太極招式說明、口訣與筆記：")

      # 直接綁定 key=text_key，徹底解決 CSV 太極招式文字帶不進輸入框的問題
      user_input_text = st.text_area(
          "輸入招式口訣或動作細節：", key=text_key, height=480
      )

      col1, col2 = st.columns([1, 1])
      with col1:
        if st.button(f"🔊 朗讀招式口訣", key=f"play_{absolute_idx}"):
          if user_input_text.strip():
            try:
              tts = gTTS(text=user_input_text, lang="zh-TW")
              fp = io.BytesIO()
              tts.write_to_fp(fp)
              st.audio(fp, autoplay=True)
            except Exception as e:
              st.error(f"語音生成發生錯誤：{e}")
          else:
            st.warning("請先輸入口訣文字！")
      with col2:
        if st.button(f"🗑️ 清空筆記", key=f"clear_{absolute_idx}"):
          st.session_state[text_key] = ""
          st.rerun()

    st.divider()

    # 太極分句/分式口訣展示區
    st.subheader("📋 招式分解動作清單：")
    lines = [
        line.strip()
        for line in user_input_text.split("\n")
        if line.strip()
    ]

    if lines:
      for l_idx, line in enumerate(lines):
        st.markdown(
            f"<div class='sentence-display'>動作 {l_idx + 1}： {line}</div>",
            unsafe_allow_html=True,
        )
    else:
      st.info("💡 在上方輸入招式說明或口訣後，這裡會自動呈現分段列表。")
