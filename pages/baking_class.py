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

# 移除快取，確保每次重新整理網頁時，都會直接從 GitHub 或最新檔案讀取資料
def load_recipes():
    try:
        # 加上 on_bad_lines="skip" 確保格式萬一有一點小誤差也不會崩潰
        df_loaded = pd.read_csv(CSV_FILE, encoding="utf-8-sig", on_bad_lines="skip")
        expected_cols = ["name", "ingredients", "steps", "notes", "improvement"]
        for col in expected_cols:
            if col not in df_loaded.columns:
                df_loaded[col] = ""
        return df_loaded[expected_cols]
    except Exception:
        return pd.DataFrame(columns=["name", "ingredients", "steps", "notes", "improvement"])

df = load_recipes()

# 完整關鍵字清單自動排版函數
def format_text(text):
    if not pd.notna(text) or not str(text).strip():
        return ""
    
    t = str(text)
    
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
    
    for kw in ingredients_keywords:
        t = t.replace(kw, f"\n• {kw}")
        
    lines = [line.strip() for line in t.split('\n') if line.strip()]
    return "\n".join(lines)

# --- 分頁籤設計 ---
tab1, tab2 = st.tabs(["✍️ 新增烘焙配方", "🔍 搜尋與瀏覽配方"])

with tab1:
    st.subheader("🥐 新增一筆烘焙紀錄與配方")
    
    if "input_ingredients" not in st.session_state:
        st.session_state["input_ingredients"] = ""
    if "input_steps" not in st.session_state:
        st.session_state["input_steps"] = ""
    if "input_notes" not in st.session_state:
        st.session_state["input_notes"] = ""
    if "input_improvement" not in st.session_state:
        st.session_state["input_improvement"] = ""

    def handle_format():
        st.session_state["input_ingredients"] = format_text(st.session_state["input_ingredients"])

    with st.form("recipe_form"):
        recipe_name = st.text_input("📝 烘焙名稱（例如：鮮奶吐司、手作貝果）")
        
        st.markdown("⚖️ 材料與比例")
        st.session_state["input_ingredients"] = st.text_area(
            "材料內容", 
            value=st.session_state["input_ingredients"], 
            height=220, 
            placeholder="直接整段貼上後，點下方按鈕自動排版...", 
            label_visibility="collapsed"
        )
        
        if st.form_submit_button("✨ 點我自動整理材料排版"):
            handle_format()
            st.rerun()

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
            height=100, 
            placeholder="注意事項事項...", 
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
        
        submitted = st.form_submit_button("💾 儲存並寫入資料庫")
        
        if submitted:
            if recipe_name.strip():
                new_data = pd.DataFrame([{
                    "name": recipe_name,
                    "ingredients": st.session_state["input_ingredients"],
                    "steps": st.session_state["input_steps"],
                    "notes": st.session_state["input_notes"],
                    "improvement": st.session_state["input_improvement"]
                }])
                
                updated_df = pd.concat([df, new_data], ignore_index=True)
                updated_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                
                st.session_state["input_ingredients"] = ""
                st.session_state["input_steps"] = ""
                st.session_state["input_notes"] = ""
                st.session_state["input_improvement"] = ""
                
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
                    st.text(row["ingredients"])
                    
                    st.markdown("##### 📌 注意事項：")
                    st.text(row["notes"])
                    
                with col2:
                    st.markdown("##### 👩‍🍳 製作步驟：")
                    # 使用 st.text 完整呈現換行步驟
                    st.text(row["steps"])
                    
                    st.markdown("##### 💡 改良做法：")
                    st.text(row["improvement"])
