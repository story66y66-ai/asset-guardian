import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="烘焙教室 - 澄玄大學", layout="wide", page_icon="🍞")

# 初始化 session_state
if "input_name" not in st.session_state:
    st.session_state.update({
        "input_name": "", "input_ingredients": "", "input_steps": "", 
        "input_notes": "", "input_improvement": "", "input_videos": [""]*5, 
        "edit_index": None, "active_tab": 0
    })

st.title("🍞 澄玄大學 - 食品學院：烘焙教室")
st.write("---")

CSV_FILE = "baking_recipes_烘焙學院.csv"

# 初始化 CSV
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["name", "ingredients", "steps", "notes", "improvement", "video_urls"])
    df_init.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

def load_recipes():
    try:
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig", on_bad_lines="skip")
        expected_cols = ["name", "ingredients", "steps", "notes", "improvement", "video_urls"]
        for col in expected_cols:
            if col not in df.columns: df[col] = ""
        return df[expected_cols]
    except:
        return pd.DataFrame(columns=["name", "ingredients", "steps", "notes", "improvement", "video_urls"])

# 清理 YouTube 網址的小工具
def clean_youtube_url(url):
    if not pd.notna(url) or not str(url).strip(): return ""
    u = str(url).strip()
    if "?" in u:
        u = u.split("?")[0]
    return u

# 智慧排版函數
def smart_format_ingredients(text):
    if not pd.notna(text) or not str(text).strip(): return ""
    t = str(text).replace("• ", "").replace("\n", " ").strip()
    keywords = [
        "配方一", "配方二", "材料準備", "中筋麵粉", "高筋麵粉", "低筋麵粉", 
        "清水", "全脂鮮乳", "雞蛋", "速發酵母", "砂糖", "植物油", "無鹽奶油",
        "鹽", "微溫水", "拉麵劑", "蓬灰", "全蛋液", "冰水", "蜂蜜", "脫脂奶粉", "鮮酵母", "蛋黃", "黃油"
    ]
    for kw in keywords: 
        t = t.replace(kw, f"\n• {kw}")
    return "\n".join([line.strip() for line in t.split("\n") if line.strip()])

def smart_format_steps(text):
    if not pd.notna(text) or not str(text).strip(): return ""
    t = str(text).replace("👨‍🍳 製作步驟：", "").replace("👨‍🍳", "").replace("\n• ", "").replace("• ", "").strip()
    parts = t.split("。")
    res = ["👨‍🍳 製作步驟："]
    for p in parts:
        c = p.strip()
        if c: res.append(f"• {c}。" if "📋" not in c else f"📋 {c}")
    return "\n".join(res)

def smart_format_notes(text):
    if not pd.notna(text) or not str(text).strip(): return ""
    return "• " + str(text).replace("• ", "").replace("\n", "").replace("。", "。\n• ").strip()

# 頁面顯示
tab_options = ["✍️ 新增與修改配方", "🔍 搜尋與瀏覽配方"]
tab_selection = st.radio("功能", tab_options, index=st.session_state["active_tab"], horizontal=True, label_visibility="collapsed")
st.session_state["active_tab"] = tab_options.index(tab_selection)

if st.session_state["active_tab"] == 0:
    st.subheader("✏️ 新增/修改烘焙配方")

    # 🎥 參考影片（移到表單外面，這樣打字時就能即時連動與預覽）
    st.markdown("🎥 參考影片（最多 5 部）")
    cols_vid = st.columns(5)
    for i in range(5):
        with cols_vid[i]:
            st.session_state["input_videos"][i] = st.text_input(
                f"影片 {i+1}", 
                value=st.session_state["input_videos"][i], 
                key=f"vid_{i}"
            )
    
    # 即時顯示影片預覽
    valid_preview_vids = [clean_youtube_url(v) for v in st.session_state["input_videos"] if v.strip()]
    if valid_preview_vids:
        st.markdown("📺 **影片預覽：**")
        prev_cols = st.columns(min(len(valid_preview_vids), 5) or 1)
        for i, v in enumerate(valid_preview_vids):
            if v: prev_cols[i%len(prev_cols)].video(v)

    st.write("---")

    with st.form("recipe_form"):
        recipe_name = st.text_input("📝 烘焙名稱", value=st.session_state["input_name"])
        
        st.session_state["input_ingredients"] = st.text_area("⚖️ 材料", value=st.session_state["input_ingredients"], height=400)
        st.session_state["input_steps"] = st.text_area("👩‍🍳 步驟", value=st.session_state["input_steps"], height=600)
        st.session_state["input_notes"] = st.text_area("📌 注意事項", value=st.session_state["input_notes"], height=400)
        st.session_state["input_improvement"] = st.text_area("💡 改良做法", value=st.session_state["input_improvement"], height=400)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit_format = st.form_submit_button("✨ 一鍵自動排版")
        with col_btn2:
            submit_save = st.form_submit_button("💾 儲存配方")

        if submit_format:
            st.session_state.update({
                "input_name": recipe_name, 
                "input_ingredients": smart_format_ingredients(st.session_state["input_ingredients"]),
                "input_steps": smart_format_steps(st.session_state["input_steps"]),
                "input_notes": smart_format_notes(st.session_state["input_notes"])
            })
            st.rerun()

        if submit_save:
            df = load_recipes()
            if st.session_state["edit_index"] is not None:
                df = df.drop(st.session_state["edit_index"]).reset_index(drop=True)
            
            cleaned_vids = [clean_youtube_url(v) for v in st.session_state["input_videos"]]
            
            new_row = pd.DataFrame([{
                "name": recipe_name, 
                "ingredients": st.session_state["input_ingredients"], 
                "steps": st.session_state["input_steps"], 
                "notes": st.session_state["input_notes"], 
                "improvement": st.session_state["input_improvement"], 
                "video_urls": ",".join(cleaned_vids)
            }])
            pd.concat([df, new_row], ignore_index=True).to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
            st.success("儲存成功！")
            st.rerun()

else:
    df = load_recipes()
    for index, row in df.iterrows():
        with st.expander(f"🍞 {row['name']}"):
            vids = str(row['video_urls']).split(',') if pd.notna(row['video_urls']) else []
            valid_vids = [clean_youtube_url(v) for v in vids if v.strip()]
            
            cols = st.columns(min(len(valid_vids), 5) or 1)
            for i, v in enumerate(valid_vids):
                if v: cols[i%len(cols)].video(v)
            
            st.text(row['ingredients'])
            st.text(row['steps'])
            if st.button("✏️ 帶入編輯", key=f"edit_{index}"):
                st.session_state.update({
                    "input_name": row['name'], "input_ingredients": row['ingredients'], 
                    "input_steps": row['steps'], "input_notes": row['notes'], 
                    "input_videos": (vids + [""]*5)[:5], "edit_index": index, "active_tab": 0
                })
                st.rerun()
