import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="烘焙教室 - 澄玄大學", layout="wide", page_icon="🍞")

st.title("🍞 澄玄大學 - 食品學院：烘焙教室")
st.write("---")

CSV_FILE = "baking_recipes.csv"

if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["name", "ingredients", "steps", "notes", "improvement"])
    df_init.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

def load_recipes():
    try:
        df_loaded = pd.read_csv(CSV_FILE, encoding="utf-8-sig", on_bad_lines="skip")
        expected_cols = ["name", "ingredients", "steps", "notes", "improvement"]
        for col in expected_cols:
            if col not in df_loaded.columns:
                df_loaded[col] = ""
        return df_loaded[expected_cols]
    except Exception:
        return pd.DataFrame(columns=["name", "ingredients", "steps", "notes", "improvement"])

df = load_recipes()

# 1. 材料智慧排版
def smart_format_ingredients(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text)
    if "\n•" in t:
        return t
    keywords = [
        "材料準備", "中筋麵粉", "低筋麵粉", "高筋麵粉", "雞蛋", 
        "融化無鹽奶油", "無鹽奶油", "植物油", "砂糖", "鮮乳", "牛奶", 
        "香草精", "裝飾物", "海苔粉", "白芝麻", "配方一", "配方二"
    ]
    for kw in keywords:
        t = t.replace(f"{kw}：", f"\n• {kw}：")
        t = t.replace(f"{kw}:", f"\n• {kw}:")
    t = t.replace("材料準備", "\n📌 材料準備")
    return t.strip()

# 2. 製作步驟智慧排版
def smart_format_steps(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text)
    if "\n•" in t:
        return t
    action_keywords = [
        "打發", "加入", "篩入", "混合", "調整", "香草精", 
        "預熱", "鋪上", "用湯匙", "覆蓋", "壓成", "烘烤", 
        "取出", "再鋪", "完全冷卻", "出爐"
    ]
    t = t.replace("製作步驟：", "\n👨‍🍳 製作步驟：")
    for kw in action_keywords:
        t = t.replace(f"。{kw}", f"。\n• {kw}")
        t = t.replace(f"，{kw}", f"，\n• {kw}")
    return t.strip()

# 3. 注意事項智慧排版
def smart_format_notes(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text)
    if "\n•" in t:
        return t
    t = t.replace("。", "。\n• ")
    return "• " + t.strip()

# 4. 改良做法智慧排版
def smart_format_improvement(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text)
    if "\n•" in t:
        return t
    t = t.replace("。", "。\n• ")
    return "• " + t.strip()

# 初始化 Session State
if "input_name" not in st.session_state:
    st.session_state["input_name"] = ""
if "input_ingredients" not in st.session_state:
    st.session_state["input_ingredients"] = ""
if "input_steps" not in st.session_state:
    st.session_state["input_steps"] = ""
if "input_notes" not in st.session_state:
    st.session_state["input_notes"] = ""
if "input_improvement" not in st.session_state:
    st.session_state["input_improvement"] = ""
if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None

# 用來控制當前顯示哪個分頁 (0 = 新增/修改頁, 1 = 搜尋瀏覽頁)
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 0

# --- 分頁籤設計 ---
tab_selection = st.radio(
    "選擇功能", 
    ["✍️ 新增與修改配方", "🔍 搜尋與瀏覽配方"], 
    index=st.session_state["active_tab"], 
    horizontal=True, 
    label_visibility="collapsed"
)

# 同步 radio 與 session_state
if tab_selection == "✍️ 新增與修改配方":
    st.session_state["active_tab"] = 0
else:
    st.session_state["active_tab"] = 1

if st.session_state["active_tab"] == 0:
    # --- 頁面一：新增與修改配方 ---
    if st.session_state["edit_index"] is not None:
        st.subheader(f"✏️ 正在修改配方（第 {st.session_state['edit_index'] + 1} 筆）")
        save_btn_text = "💾 儲存修改內容（更新資料）"
    else:
        st.subheader("🥐 新增一筆烘焙紀錄與配方")
        save_btn_text = "💾 儲存並寫入資料庫"

    with st.form("recipe_form"):
        recipe_name = st.text_input("📝 烘焙名稱（例如：鮮奶吐司、手作貝果）", value=st.session_state["input_name"])
        
        submitted_format = st.form_submit_button("✨ 點我一鍵自動整理「全部四個欄位」排版")
        
        st.markdown("⚖️ 材料與比例")
        st.session_state["input_ingredients"] = st.text_area(
            "材料內容", 
            value=st.session_state["input_ingredients"], 
            height=200, 
            placeholder="直接整段貼上...", 
            label_visibility="collapsed"
        )

        st.markdown("👩‍🍳 製作步驟")
        st.session_state["input_steps"] = st.text_area(
            "步驟內容", 
            value=st.session_state["input_steps"], 
            height=200, 
            placeholder="直接貼上製作步驟...", 
            label_visibility="collapsed"
        )
        
        st.markdown("📌 注意事項")
        st.session_state["input_notes"] = st.text_area(
            "注意事項內容", 
            value=st.session_state["input_notes"], 
            height=120, 
            placeholder="注意事項...", 
            label_visibility="collapsed"
        )
        
        st.markdown("💡 改良做法")
        st.session_state["input_improvement"] = st.text_area(
            "改良內容", 
            value=st.session_state["input_improvement"], 
            height=120, 
            placeholder="心得與調整記錄...", 
            label_visibility="collapsed"
        )
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            submitted_save = st.form_submit_button(save_btn_text)
        with col_f2:
            submitted_cancel = st.form_submit_button("❌ 放棄修改 / 清空重來")
        
        if submitted_format:
            st.session_state["input_name"] = recipe_name
            st.session_state["input_ingredients"] = smart_format_ingredients(st.session_state["input_ingredients"])
            st.session_state["input_steps"] = smart_format_steps(st.session_state["input_steps"])
            st.session_state["input_notes"] = smart_format_notes(st.session_state["input_notes"])
            st.session_state["input_improvement"] = smart_format_improvement(st.session_state["input_improvement"])
            st.rerun()
            
        if submitted_cancel:
            st.session_state["input_name"] = ""
            st.session_state["input_ingredients"] = ""
            st.session_state["input_steps"] = ""
            st.session_state["input_notes"] = ""
            st.session_state["input_improvement"] = ""
            st.session_state["edit_index"] = None
            st.success("已清除或取消編輯！")
            st.rerun()

        if submitted_save:
            if recipe_name.strip():
                final_ingredients = smart_format_ingredients(st.session_state["input_ingredients"])
                final_steps = smart_format_steps(st.session_state["input_steps"])
                final_notes = smart_format_notes(st.session_state["input_notes"])
                final_improvement = smart_format_improvement(st.session_state["input_improvement"])
                
                if st.session_state["edit_index"] is not None:
                    # 更新指定的舊資料
                    idx = st.session_state["edit_index"]
                    df.at[idx, "name"] = recipe_name
                    df.at[idx, "ingredients"] = final_ingredients
                    df.at[idx, "steps"] = final_steps
                    df.at[idx, "notes"] = final_notes
                    df.at[idx, "improvement"] = final_improvement
                    st.session_state["edit_index"] = None
                    success_msg = f"成功更新烘焙品項：【{recipe_name}】！"
                else:
                    # 新增新資料
                    new_data = pd.DataFrame([{
                        "name": recipe_name,
                        "ingredients": final_ingredients,
                        "steps": final_steps,
                        "notes": final_notes,
                        "improvement": final_improvement
                    }])
                    df = pd.concat([df, new_data], ignore_index=True)
                    success_msg = f"成功新增烘焙品項：【{recipe_name}】！"
                
                df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                
                st.session_state["input_name"] = ""
                st.session_state["input_ingredients"] = ""
                st.session_state["input_steps"] = ""
                st.session_state["input_notes"] = ""
                st.session_state["input_improvement"] = ""
                
                st.success(success_msg)
                st.rerun()
            else:
                st.error("請至少填寫「烘焙名稱」才能儲存唷！")

else:
    # --- 頁面二：搜尋與瀏覽配方 ---
    st.subheader("📚 烘焙配方清單與搜尋")
    
    if df.empty:
        st.info("目前還沒有任何烘焙配方，快去新增第一道美味點心吧！")
    else:
        search_query = st.text_input("🔍 輸入關鍵字搜尋烘焙名稱或材料：", "").strip().lower()
        
        if search_query:
            filtered_df = df[
                df["name"].astype(str).str.lower().str.contains(search_query) | 
                df["ingredients"].astype(str).str.lower().str.contains(search_query)
            ]
        else:
            filtered_df = df
            
        st.write(f"共找到 **{len(filtered_df)}** 筆烘焙紀錄：")
        st.write("---")
        
        for index, row in filtered_df.iterrows():
            with st.expander(f"🍞 {row['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("##### ⚖️ 材料與比例：")
                    st.text(smart_format_ingredients(row["ingredients"]))
                    
                    st.markdown("##### 📌 注意事項：")
                    st.text(smart_format_notes(row["notes"]))
                    
                with col2:
                    st.markdown("##### 👩‍🍳 製作步驟：")
                    st.text(smart_format_steps(row["steps"]))
                    
                    st.markdown("##### 💡 改良做法：")
                    st.text(smart_format_improvement(row["improvement"]))
                
                st.write("---")
                col_b1, col_b2, _ = st.columns([1, 1, 4])
                with col_b1:
                    # 點擊後，自動把資料帶入「新增頁面」的大格子裡，並切過去讓澄玄修改！
                    if st.button("✏️ 帶入至新增頁面修改", key=f"edit_to_tab1_{index}"):
                        st.session_state["input_name"] = row["name"]
                        st.session_state["input_ingredients"] = row["ingredients"]
                        st.session_state["input_steps"] = row["steps"]
                        st.session_state["input_notes"] = row["notes"]
                        st.session_state["input_improvement"] = row["improvement"]
                        st.session_state["edit_index"] = index
                        st.session_state["active_tab"] = 0
                        st.rerun()
                with col_b2:
                    if st.button("🗑️ 刪除", key=f"del_{index}"):
                        df = df.drop(index).reset_index(drop=True)
                        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                        st.success(f"已刪除【{row['name']}】")
                        st.rerun()
