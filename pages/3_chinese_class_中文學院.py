import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="電腦學院 - 澄玄大學", layout="wide", page_icon="💻")

st.title("💻 澄玄大學 - 電腦學院：疑難雜症與程式筆記")
st.write("---")

CSV_FILE = "computer_recipes.csv"

# 初始化 CSV 檔案
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["name", "ingredients", "steps", "notes", "improvement"])
    df_init.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# 讀取檔案函式
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

# 智慧排版：問題與現象
def smart_format_ingredients(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text).strip()
    t = t.replace("• ", "").replace("\n", " ").strip()
    
    keywords = [
        "問題現象", "錯誤訊息", "環境設定", "操作步驟",
        "Python", "Streamlit", "GitHub", "Windows", "VS Code"
    ]
    for kw in keywords:
        t = t.replace(kw, f"\n• {kw}")
        
    lines = [line.strip() for line in t.split("\n") if line.strip()]
    return "\n".join(lines)

# 智慧排版：解決方案步驟
def smart_format_steps(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text)
    while "🛠️ 解決步驟：" in t:
        t = t.replace("🛠️ 解決步驟：", "")
    while "🛠️" in t:
        t = t.replace("🛠️", "")
    t = t.replace("\n• ", "").replace("• ", "").strip()
    
    parts = t.split("。")
    formatted_parts = ["🛠️ 解決步驟："]
    for p in parts:
        cleaned = p.strip()
        if not cleaned:
            continue
        if cleaned in ["解決步驟", "操作流程"]:
            formatted_parts.append(f"📋 {cleaned}")
        else:
            formatted_parts.append(f"• {cleaned}。")
    return "\n".join(formatted_parts)

# 智慧排版：注意事項
def smart_format_notes(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text).replace("• ", "").replace("\n", "").strip()
    t = t.replace("。", "。\n• ")
    return "• " + t.strip()

# 智慧排版：心得與優化
def smart_format_improvement(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    t = str(text).replace("• ", "").replace("\n", "").strip()
    t = t.replace("。", "。\n• ")
    return "• " + t.strip()

# 初始化 Session State
if "c_input_name" not in st.session_state:
    st.session_state["c_input_name"] = ""
if "c_input_ingredients" not in st.session_state:
    st.session_state["c_input_ingredients"] = ""
if "c_input_steps" not in st.session_state:
    st.session_state["c_input_steps"] = ""
if "c_input_notes" not in st.session_state:
    st.session_state["c_input_notes"] = ""
if "c_input_improvement" not in st.session_state:
    st.session_state["c_input_improvement"] = ""
if "c_edit_index" not in st.session_state:
    st.session_state["c_edit_index"] = None
if "c_active_tab" not in st.session_state:
    st.session_state["c_active_tab"] = 0

# 分頁籤
tab_options = ["✍️ 新增與修改電腦問題", "🔍 搜尋與瀏覽筆記"]
tab_selection = st.radio(
    "選擇功能", 
    tab_options, 
    index=st.session_state["c_active_tab"], 
    horizontal=True, 
    label_visibility="collapsed"
)

st.session_state["c_active_tab"] = tab_options.index(tab_selection)

if st.session_state["c_active_tab"] == 0:
    if st.session_state["c_edit_index"] is not None:
        st.subheader(f"✏️ 正在修改電腦問題（第 {st.session_state['c_edit_index'] + 1} 筆）")
        save_btn_text = "💾 儲存修改內容（更新資料）"
    else:
        st.subheader("💻 新增一筆電腦問題與解決方案")
        save_btn_text = "💾 儲存並寫入資料庫"

    with st.form("computer_form"):
        recipe_name = st.text_input("📝 問題標題（例如：Streamlit 側邊欄排序、GitHub 權限錯誤）", value=st.session_state["c_input_name"])
        submitted_format = st.form_submit_button("✨ 點我一鍵自動整理排版")
        
        st.markdown("⚖️ 問題現象與關鍵字")
        st.session_state["c_input_ingredients"] = st.text_area("問題現象內容", value=st.session_state["c_input_ingredients"], height=200, label_visibility="collapsed")

        st.markdown("🛠️ 解決步驟")
        st.session_state["c_input_steps"] = st.text_area("解決步驟內容", value=st.session_state["c_input_steps"], height=250, label_visibility="collapsed")
        
        st.markdown("📌 注意事項")
        st.session_state["c_input_notes"] = st.text_area("注意事項內容", value=st.session_state["c_input_notes"], height=120, label_visibility="collapsed")
        
        st.markdown("💡 心得與優化")
        st.session_state["c_input_improvement"] = st.text_area("心得內容", value=st.session_state["c_input_improvement"], height=120, label_visibility="collapsed")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            submitted_save = st.form_submit_button(save_btn_text)
        with col_f2:
            submitted_cancel = st.form_submit_button("❌ 放棄修改 / 清空重來")
        
        if submitted_format:
            st.session_state["c_input_name"] = recipe_name
            st.session_state["c_input_ingredients"] = smart_format_ingredients(st.session_state["c_input_ingredients"])
            st.session_state["c_input_steps"] = smart_format_steps(st.session_state["c_input_steps"])
            st.session_state["c_input_notes"] = smart_format_notes(st.session_state["c_input_notes"])
            st.session_state["c_input_improvement"] = smart_format_improvement(st.session_state["c_input_improvement"])
            st.rerun()
            
        if submitted_cancel:
            st.session_state["c_input_name"] = ""
            st.session_state["c_input_ingredients"] = ""
            st.session_state["c_input_steps"] = ""
            st.session_state["c_input_notes"] = ""
            st.session_state["c_input_improvement"] = ""
            st.session_state["c_edit_index"] = None
            st.success("已清除或取消編輯！")
            st.rerun()

        if submitted_save:
            if recipe_name.strip():
                current_df = load_recipes()
                
                final_ingredients = smart_format_ingredients(st.session_state["c_input_ingredients"])
                final_steps = smart_format_steps(st.session_state["c_input_steps"])
                final_notes = smart_format_notes(st.session_state["c_input_notes"])
                final_improvement = smart_format_improvement(st.session_state["c_input_improvement"])
                
                if st.session_state["c_edit_index"] is not None:
                    idx = st.session_state["c_edit_index"]
                    if idx < len(current_df):
                        current_df = current_df.drop(idx).reset_index(drop=True)
                    st.session_state["c_edit_index"] = None
                    success_msg = f"成功更新電腦問題：【{recipe_name}】！"
                else:
                    success_msg = f"成功新增電腦問題：【{recipe_name}】！"
                
                new_data = pd.DataFrame([{
                    "name": recipe_name,
                    "ingredients": final_ingredients,
                    "steps": final_steps,
                    "notes": final_notes,
                    "improvement": final_improvement
                }])
                current_df = pd.concat([current_df, new_data], ignore_index=True)
                current_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                
                st.session_state["c_input_name"] = ""
                st.session_state["c_input_ingredients"] = ""
                st.session_state["c_input_steps"] = ""
                st.session_state["c_input_notes"] = ""
                st.session_state["c_input_improvement"] = ""
                
                st.success(success_msg)
                st.rerun()
            else:
                st.error("請至少填寫「問題標題」才能儲存唷！")

else:
    st.subheader("📚 電腦筆記清單與搜尋")
    df = load_recipes()
    
    if df.empty:
        st.info("目前還沒有任何電腦筆記，快去新增第一筆問題紀錄吧！")
    else:
        search_query = st.text_input("🔍 輸入關鍵字搜尋標題或現象：", "").strip().lower()
        
        if search_query:
            filtered_df = df[
                df["name"].astype(str).str.lower().str.contains(search_query) | 
                df["ingredients"].astype(str).str.lower().str.contains(search_query)
            ]
        else:
            filtered_df = df
            
        st.write(f"共找到 **{len(filtered_df)}** 筆電腦筆記：")
        st.write("---")
        
        for index, row in filtered_df.iterrows():
            with st.expander(f"💻 {row['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("##### ⚖️ 問題現象與關鍵字：")
                    st.text(smart_format_ingredients(row["ingredients"]))
                    st.markdown("##### 📌 注意事項：")
                    st.text(smart_format_notes(row["notes"]))
                with col2:
                    st.markdown("##### 🛠️ 解決步驟：")
                    st.text(smart_format_steps(row["steps"]))
                    st.markdown("##### 💡 心得與優化：")
                    st.text(smart_format_improvement(row["improvement"]))
                
                st.write("---")
                col_b1, col_b2, _ = st.columns([1, 1, 4])
                with col_b1:
                    if st.button("✏️ 帶入至新增頁面修改", key=f"c_edit_{index}"):
                        st.session_state["c_input_name"] = row["name"]
                        st.session_state["c_input_ingredients"] = smart_format_ingredients(row["ingredients"])
                        st.session_state["c_input_steps"] = smart_format_steps(row["steps"])
                        st.session_state["c_input_notes"] = smart_format_notes(row["notes"])
                        st.session_state["c_input_improvement"] = smart_format_improvement(row["improvement"])
                        st.session_state["c_edit_index"] = index
                        st.session_state["c_active_tab"] = 0
                        st.rerun()
                with col_b2:
                    if st.button("🗑️ 刪除", key=f"c_del_{index}"):
                        df = df.drop(index).reset_index(drop=True)
                        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                        st.success(f"已刪除【{row['name']}】")
                        st.rerun()
