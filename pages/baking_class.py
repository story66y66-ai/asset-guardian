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

# 完整關鍵字清單自動排版函數（聽澄玄的話，把想得到的材料全包了！）
def comprehensive_format(text):
    if not pd.notna(text) or not str(text).strip():
        return "無"
    
    t = str(text)
    
    # 涵蓋麵包、餅乾、蛋糕所有常見材料與配方標頭
    ingredients_keywords = [
        "配方一", "配方二", "配方三",
        "中筋麵粉", "高筋麵粉", "低筋麵粉", "全麥麵粉", "黑麥粉", "粘米粉", "糯米粉", "太白粉", "玉米澱粉", "地瓜粉",
        "清水", "冰水", "溫水", "全脂鮮乳", "低脂鮮乳", "奶粉", "動物性鮮奶油", "植物性鮮奶油", "優格", "優酪乳", "煉乳",
        "雞蛋", "蛋白", "蛋黃",
        "速發酵母", "新鮮酵母", "老麵", "泡打粉", "小蘇打粉", "塔塔粉",
        "細砂糖", "黃砂糖", "紅糖", "黑糖", "糖粉", "海藻糖", "麥芽糖", "蜂蜜", "楓糖漿",
        "無鹽奶油", "有鹽奶油", "酥油", "豬油", "植物油", "沙拉油", "橄欖油", "玉米油", "椰子油",
        "鹽", "細鹽", "玫瑰鹽",
        "可可粉", "巧克力", "抹茶粉", "香草精", "肉桂粉", "咖啡粉", "檸檬汁", "檸檬皮屑",
        "葡萄乾", "蔓越莓乾", "核桃", "杏仁片", "腰果", "芝麻", "乳酪", "起司片", "卡士達醬"
    ]
    
    # 強制在每個關鍵字前面加上換行與項目符號
    for kw in ingredients_keywords:
        t = t.replace(kw, f"\n• {kw}")
        
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
                    # 使用完整關鍵字排版
                    st.markdown(comprehensive_format(row["ingredients"]))
                    
                    st.markdown("##### 📌 備註：")
                    st.markdown(comprehensive_format(row["notes"]))
                    
                with col2:
                    st.markdown("##### 👩‍🍳 製作步驟：")
                    st.markdown(comprehensive_format(row["steps"]))
                    
                    st.markdown("##### 💡 改良做法：")
                    st.markdown(comprehensive_format(row["improvement"]))
