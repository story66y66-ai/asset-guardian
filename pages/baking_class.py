import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="烘焙教室 - 澄玄大學", layout="wide", page_icon="🍞")

st.title("🍞 澄玄大學 - 食品學院：烘焙教室")
st.write("---")

CSV_FILE = "baking_recipes.csv"

# 初始化 CSV 檔案（如果不存在的話自動建立）
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["name", "ingredients", "steps", "improvement", "notes"])
    df_init.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# 讀取現有資料
@st.cache_data
def load_recipes():
    try:
        return pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame(columns=["name", "ingredients", "steps", "improvement", "notes"])

df = load_recipes()

# --- 分頁籤設計：新增配方 / 搜尋與瀏覽 ---
tab1, tab2 = st.tabs(["✍️ 新增烘焙配方", "🔍 搜尋與瀏覽配方"])

with tab1:
    st.subheader("🥐 新增一筆烘焙紀錄與配方")
    
    with st.form("recipe_form", clear_on_submit=True):
        recipe_name = st.text_input("📝 烘焙名稱（例如：鮮奶吐司、手作貝果）")
        recipe_ingredients = st.text_area("⚖️ 材料與比例", height=120, placeholder="例如：中筋麵粉 500克、鮮奶 290克...")
        recipe_steps = st.text_area("👩‍🍳 製作步驟", height=150, placeholder="1. 揉麵團...\n2. 基礎發酵...")
        recipe_improvement = st.text_area("💡 改良做法（心得、失敗檢討或調整記錄）", height=100, placeholder="例如：下次水可以少減 10克，發酵時間拉長...")
        recipe_notes = st.text_area("📌 備註", height=80, placeholder="例如：口感Q軟，家人很喜歡...")
        
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
                
                # 將新資料附加到舊資料後方並寫入 CSV
                updated_df = pd.concat([df, new_data], ignore_index=True)
                updated_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                st.cache_data.clear() # 清除快取以便立即讀取新資料
                st.success(f"成功新增烘焙品項：【{recipe_name}】！資料已自動存入資料庫。")
                st.rerun()
            else:
                st.error("請至少填寫「烘焙名稱」才能儲存唷！")

with tab2:
    st.subheader("📚 烘焙配方清單與搜尋")
    
    if df.empty:
        st.info("目前還沒有任何烘焙配方，快去「新增烘焙配方」頁籤新增第一道美味點心吧！")
    else:
        # 搜尋功能
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
        
        # 逐筆呈現卡片或展開清單
        for index, row in filtered_df.iterrows():
            with st.expander(f"🍞 {row['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("##### ⚖️ 材料與比例：")
                    st.text(row["ingredients"] if pd.notna(row["ingredients"]) else "無")
                    
                    st.markdown("##### 📌 備註：")
                    st.text(row["notes"] if pd.notna(row["notes"]) else "無")
                    
                with col2:
                    st.markdown("##### 👩‍🍳 製作步驟：")
                    st.text(row["steps"] if pd.notna(row["steps"]) else "無")
                    
                    st.markdown("##### 💡 改良做法：")
                    st.text(row["improvement"] if pd.notna(row["improvement"]) else "無")
