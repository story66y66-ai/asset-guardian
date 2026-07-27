import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="烘焙教室 - 澄玄大學", layout="wide", page_icon="🍞")

st.title("🍞 澄玄大學 - 食品學院：烘焙教室")
st.write("---")

CSV_FILE = "baking_recipes.csv"

# 初始化 CSV 檔案
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["name", "ingredients", "steps", "improvement", "notes"])
    df_init.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

@st.cache_data
def load_recipes():
    try:
        return pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame(columns=["name", "ingredients", "steps", "improvement", "notes"])

df = load_recipes()

# 強效排版清理函數：把黏在一起的材料用「克」或「配方」自動切開換行
def clean_and_format(text):
    if not pd.notna(text) or not str(text).strip():
        return "無"
    
    t = str(text)
    
    # 如果裡面含有「克」，我們在「克」的後面強制加一個換行，讓每個材料獨立一行
    # 同時把「配方一」、「配方二」前面也換行
    t = t.replace("克", "克\n• ")
    t = t.replace("配方", "\n\n配方")
    
    # 確保不會有多餘的重複符號
    return t.strip()

# --- 分頁籤設計 ---
tab1, tab2 = st.tabs(["✍️ 新增烘焙配方", "🔍 搜尋與瀏覽配方"])

with tab1:
    st.subheader("🥐 新增一筆烘焙紀錄與配方")
    
    with st.form("recipe_form", clear_on_submit=True):
        recipe_name = st.text_input("📝 烘焙名稱（例如：鮮奶吐司、手作貝果）")
        recipe_ingredients = st.text_area("⚖️ 材料與比例", height=120, placeholder="直接貼上即可...")
        recipe_steps = st.text_area("👩‍🍳 製作步驟", height=150, placeholder="直接貼上即可...")
        recipe_improvement = st.text_area("💡 改良做法", height=100, placeholder="心得與調整記錄...")
        recipe_notes = st.text_area("📌 備註", height=80, placeholder="備註事項...")
        
        submitted = st.form_submit_button("💾 儲存並寫入資料庫")
        
        if submitted:
            if recipe_name.strip():
                new_data = pd.DataFrame([{
                    "name": recipe_name,
                    "ingredients": recipe_ingredients,
                    "steps": recipe_steps,
                    "improvement": recipe_improvement,
                    "notes": recipe_notes
                }])
                
                updated_df = pd.concat([df, new_data], ignore_index=True)
                updated_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                st.cache_data.clear()
                st.success(f"成功新增烘焙品項：【{recipe_name}】！")
                st.rerun()
            else:
                st.error("請至少填寫「烘焙名稱」才能儲存唷！")

with tab2:
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
                    # 透過強效排版函數處理顯示
                    st.text(clean_and_format(row["ingredients"]))
                    
                    st.markdown("##### 📌 備註：")
                    st.text(clean_and_format(row["notes"]))
                    
                with col2:
                    st.markdown("##### 👩‍🍳 製作步驟：")
                    st.text(clean_and_format(row["steps"]))
                    
                    st.markdown("##### 💡 改良做法：")
                    st.text(clean_and_format(row["improvement"]))
