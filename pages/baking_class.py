import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="烘焙教室 - 澄玄大學", layout="wide", page_icon="🍞")

st.title("🍞 澄玄大學 - 食品學院：烘焙教室")
st.write("---")

CSV_FILE = "baking_recipes.csv"

# 初始化 CSV 檔案
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["name", "ingredients", "steps", "notes", "improvement"])
    df_init.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# 讀取檔案函式：每次都直接從真正的檔案讀
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

# 智慧排版函式
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

def smart_format_steps(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text)
    
    # 確保開頭有標題
    if "製作步驟" not in t:
        t = "👨‍🍳 製作步驟：\n" + t
    else:
        t = t.replace("製作步驟：", "👨‍🍳 製作步驟：\n").replace("製作步驟", "👨‍🍳 製作步驟：\n")

    # 移除多餘的項目符號避免重複疊加
    t = t.replace("\n• ", "").replace("• ", "")

    # 核心新規則：看到句號就自動換行並加上項目符號
    parts = t.split("。")
    formatted_parts = []
    for i, p in enumerate(parts):
        cleaned = p.strip()
        if not cleaned:
            continue
        # 如果是第一部分（標題），不要加項目符號
        if "👨‍🍳 製作步驟：" in cleaned and i == 0:
            formatted_parts.append(cleaned)
        else:
            formatted_parts.append(f"• {cleaned}。")
            
    return "\n".join(formatted_parts)

def smart_format_notes(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text)
    if "\n•" in t:
        return t
    t = t.replace("。", "。\n• ")
    return "• " + t.strip()

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
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 0

# 分頁籤：透過 index 綁定 st.session_state["active_tab"]
tab_options = ["✍️ 新增與修改配方", "🔍 搜尋與瀏覽配方"]
tab_selection = st.radio(
    "選擇功能", 
    tab_options, 
    index=st.session_state["active_tab"], 
    horizontal=True, 
    label_visibility="collapsed"
)

# 同步更新當前頁籤狀態
st.session_state["active_tab"] = tab_options.index(tab_selection)

if st.session_state["active_tab"] == 0:
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
        st.session_state["input_ingredients"] = st.text_area("材料內容", value=st.session_state["input_ingredients"], height=200, label_visibility="collapsed")

        st.markdown("👩‍🍳 製作步驟")
        st.session_state["input_steps"] = st.text_area("步驟內容", value=st.session_state["input_steps"], height=200, label_visibility="collapsed")
        
        st.markdown("📌 注意事項")
        st.session_state["input_notes"] = st.text_area("注意事項內容", value=st.session_state["input_notes"], height=120, label_visibility="collapsed")
        
        st.markdown("💡 改良做法")
        st.session_state["input_improvement"] = st.text_area("改良內容", value=st.session_state["input_improvement"], height=120, label_visibility="collapsed")
        
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
                current_df = load_recipes()
                
                final_ingredients = smart_format_ingredients(st.session_state["input_ingredients"])
                final_steps = smart_format_steps(st.session_state["input_steps"])
                final_notes = smart_format_notes(st.session_state["input_notes"])
                final_improvement = smart_format_improvement(st.session_state["input_improvement"])
                
                if st.session_state["edit_index"] is not None:
                    idx = st.session_state["edit_index"]
                    if idx < len(current_df):
                        current_df.at[idx, "name"] = recipe_name
                        current_df.at[idx, "ingredients"] = final_ingredients
                        current_df.at[idx, "steps"] = final_steps
                        current_df.at[idx, "notes"] = final_notes
                        current_df.at[idx, "improvement"] = final_improvement
                    st.session_state["edit_index"] = None
                    success_msg = f"成功更新烘焙品項：【{recipe_name}】！"
                else:
                    new_data = pd.DataFrame([{
                        "name": recipe_name,
                        "ingredients": final_ingredients,
                        "steps": final_steps,
                        "notes": final_notes,
                        "improvement": final_improvement
                    }])
                    current_df = pd.concat([current_df, new_data], ignore_index=True)
                    success_msg = f"成功新增烘焙品項：【{recipe_name}】！"
                
                current_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                
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
    st.subheader("📚 烘焙配方清單與搜尋")
    df = load_recipes()
    
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
                    if st.button("✏️ 帶入至新增頁面修改", key=f"edit_to_tab1_{index}"):
                        st.session_state["input_name"] = row["name"]
                        st.session_state["input_ingredients"] = row["ingredients"]
                        st.session_state["input_steps"] = row["steps"]
                        st.session_state["input_notes"] = row["notes"]
                        st.session_state["input_improvement"] = row["improvement"]
                        st.session_state["edit_index"] = index
                        st.session_state["active_tab"] = 0  # 設定跳回第一頁
                        st.rerun()
                with col_b2:
                    if st.button("🗑️ 刪除", key=f"del_{index}"):
                        df = df.drop(index).reset_index(drop=True)
                        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                        st.success(f"已刪除【{row['name']}】")
                        st.rerun()
