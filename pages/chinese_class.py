import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="中文學院 - 澄玄400句成語旗艦挑戰賽", layout="wide", page_icon="📖")

@st.cache_data
def load_flagship_database():
    # 直接從 GitHub 讀取我們剛剛上傳並整理好的 idioms.csv 檔
    csv_url = "https://raw.githubusercontent.com/story66y66-ai/asset-guardian/main/idioms.csv"
    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        # 預防萬一讀取失敗時的備案
        df = pd.read_csv("idioms.csv")
    
    # 確保欄位名稱正確對應
    if "idiom" in df.columns and "meaning" in df.columns:
        df = df.rename(columns={"idiom": "成語", "meaning": "解釋"})
    
    # 嚴格過濾確保不重複
    df = df.drop_duplicates(subset=["成語"]).reset_index(drop=True)
    return df

df = load_flagship_database()

st.title(f"📖 中文學院（校長大人專屬成語庫：目前共計 {len(df)} 筆全覆蓋真題）")
st.write("---")

st.success(f"🔥 系統已成功從 GitHub 載入 **{len(df)} 筆** 完整不重複成語！支援「獨立點選」與「全自動連續朗讀（吃飯解放雙手）」！")
st.write("---")

tab1, tab2 = st.tabs(["📚 完整題庫總覽", "🎮 成語填空挑戰賽"])

with tab1:
    st.subheader(f"📚 完整成語資料庫預覽（共計 {len(df)} 筆全覆蓋，完美同步）")
    
    page_size = 20
    total_pages = (len(df) + page_size - 1) // page_size
    if total_pages < 1:
        total_pages = 1
    
    col_p1, col_p2, col_p3 = st.columns([2, 2, 3])
    with col_p1:
        current_page = st.number_input(f"跳至頁數 (共 {total_pages} 頁)：", min_value=1, max_value=total_pages, value=1, step=1)
    
    with col_p2:
        st.write("") 
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            if st.button("⬅️ 上一頁") and current_page > 1:
                current_page -= 1
        with sub_col2:
            if st.button("下一頁 ➡️") and current_page < total_pages:
                current_page += 1

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    
    st.write(f"目前顯示第 **{current_page}** 頁（第 {start_idx + 1} ~ {end_idx} 筆，總計 **{len(df)} 筆**）：")
    st.write("---")
    
    # 準備給前端 JavaScript 用的資料清單 (將當前頁面的成語包裝成 JS 陣列)
    page_data = df.iloc[start_idx:end_idx]
    
    rows_html = ""
    for idx, row in page_data.iterrows():
        idiom = row["成語"]
        meaning = row["解釋"]
        display_num = idx + 1
        text_to_speak = f"{idiom}。{meaning}"
        
        rows_html += f"""
        <tr style="border-bottom: 1px solid #ddd; height: 50px;">
            <td style="width: 10%; font-weight: bold;">#{display_num}</td>
            <td style="width: 20%;" id="idiom_cell_{idx}">{idiom}</td>
            <td style="width: 50%;">{meaning}</td>
            <td style="width: 20%;">
                <button onclick="playSingle({idx}, '{idiom}', '{text_to_speak}', {len(df)})" 
                        id="btn_{idx}" 
                        style="background-color: #f0f2f6; border: 1px solid #d6d6d6; padding: 5px 12px; border-radius: 4px; cursor: pointer;">
                    🔊 朗讀
                </button>
            </td>
        </tr>
        """
    
    full_table_html = f"""
    <div style="margin-bottom: 15px; background-color: #f9f9f9; padding: 10px; border-radius: 6px; border: 1px solid #e0e0e0;">
        <span style="font-weight: bold; margin-right: 15px;">🎧 吃飯免手動控制台：</span>
        <button onclick="startAutoPlay()" id="auto_play_btn" style="background-color: #28a745; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 10px;">
            ▶ 開始本頁自動連續朗讀
        </button>
        <button onclick="stopAutoPlay()" style="background-color: #dc3545; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: bold;">
            ⏹ 停止朗讀
        </button>
        <span id="auto_status" style="margin-left: 15px; color: #555; font-size: 14px;">狀態：待命中</span>
    </div>

    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="border-bottom: 2px solid #ccc; text-align: left;">
                <th style="padding-bottom: 8px;">序號</th>
                <th style="padding-bottom: 8px;">成語</th>
                <th style="padding-bottom: 8px;">解釋</th>
                <th style="padding-bottom: 8px;">語音朗讀</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    
    <script>
    // 將當前頁面的資料打包成 JavaScript 陣列供自動連續播放使用
    const currentStartIndex = {start_idx};
    const currentEndIndex = {end_idx};
    const pageIdiomsData = [
    """
    
    for idx, row in page_data.iterrows():
        idiom = row["成語"]
        meaning = row["解釋"]
        full_text = f"{idiom}，{meaning}"
        full_table_html += f"{{ index: {idx}, idiom: '{idiom}', text: '{full_text}' }},\n"

    full_table_html += f"""
    ];

    let autoPlaying = false;
    let currentAutoIdx = 0;

    function clearAllHighlights(totalRows) {{
        for (let i = 0; i < totalRows; i++) {{
            let cell = document.getElementById('idiom_cell_' + i);
            let btn = document.getElementById('btn_' + i);
            if (cell) {{
                let cleanText = cell.innerText.replace('🎵', '').replace('⭐', '').trim();
                cell.innerHTML = cleanText;
            }}
            if (btn) {{
                btn.innerText = '🔊 朗讀';
                btn.style.backgroundColor = '#f0f2f6';
                btn.style.color = 'black';
            }}
        }}
    }}

    function playSingle(idx, idiom, textToSpeak, totalRows) {{
        stopAutoPlay();
        clearAllHighlights(totalRows);
        
        let targetCell = document.getElementById('idiom_cell_' + idx);
        let targetBtn = document.getElementById('btn_' + idx);
        
        if (targetCell) {{
            targetCell.innerHTML = '🎵 <b>' + idiom + '</b> ⭐';
        }}
        if (targetBtn) {{
            targetBtn.innerText = '🔊 朗讀中...';
            targetBtn.style.backgroundColor = '#ff4b4b';
            targetBtn.style.color = 'white';
        }}
        
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = 'zh-TW';
        utterance.rate = 0.9;
        
        utterance.onend = function() {{
            if (targetBtn) {{
                targetBtn.innerText = '🔊 朗讀';
                targetBtn.style.backgroundColor = '#f0f2f6';
                targetBtn.style.color = 'black';
            }}
        }};
        
        window.speechSynthesis.speak(utterance);
    }}

    function startAutoPlay() {{
        if (pageIdiomsData.length === 0) return;
        autoPlaying = true;
        currentAutoIdx = 0;
        document.getElementById('auto_status').innerText = '狀態：自動連續播放中...';
        document.getElementById('auto_play_btn').style.backgroundColor = '#6c757d';
        playNextInQueue();
    }}

    function playNextInQueue() {{
        if (!autoPlaying || currentAutoIdx >= pageIdiomsData.length) {{
            stopAutoPlay();
            document.getElementById('auto_status').innerText = '狀態：本頁播放完畢！';
            return;
        }}

        let item = pageIdiomsData[currentAutoIdx];
        let idx = item.index;
        let idiom = item.idiom;
        let textToSpeak = item.text;

        // 清除其他高亮
        clearAllHighlights({len(df)});

        let targetCell = document.getElementById('idiom_cell_' + idx);
        let targetBtn = document.getElementById('btn_' + idx);

        if (targetCell) {{
            targetCell.innerHTML = '🎵 <b>' + idiom + '</b> ⭐';
        }}
        if (targetBtn) {{
            targetBtn.innerText = '🔊 播放中';
            targetBtn.style.backgroundColor = '#28a745';
            targetBtn.style.color = 'white';
        }}

        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = 'zh-TW';
        utterance.rate = 0.9;

        utterance.onend = function() {{
            if (targetBtn) {{
                targetBtn.innerText = '🔊 朗讀';
                targetBtn.style.backgroundColor = '#f0f2f6';
                targetBtn.style.color = 'black';
            }}
            currentAutoIdx++;
            // 延遲 0.8 秒無縫接軌下一句
            if (autoPlaying) {{
                setTimeout(playNextInQueue, 800);
            }}
        }};

        window.speechSynthesis.speak(utterance);
    }}

    function stopAutoPlay() {{
        autoPlaying = false;
        window.speechSynthesis.cancel();
        clearAllHighlights({len(df)});
        let autoBtn = document.getElementById('auto_play_btn');
        if (autoBtn) {{
            autoBtn.style.backgroundColor = '#28a745';
        }}
        let statusElem = document.getElementById('auto_status');
        if (statusElem) {{
            statusElem.innerText = '狀態：已停止';
        }}
    }}
    </script>
    """
    
    st.components.v1.html(full_table_html, height=1150, scrolling=True)

with tab2:
    st.subheader("🎯 挑戰您的無敵成語腦力（來自 CSV 題庫）")
    difficulty = st.radio("請選擇難易度：", ["🌱 初級（提示首字）", "⭐ 中級（提示字數）", "🔥 高級（盲猜挑戰）"], horizontal=True)
    
    st.write("---")
    
    if "golden_target" not in st.session_state or st.button("🔄 點我隨機換一題"):
        st.session_state.golden_target = df.sample(1).iloc[0].to_dict()
        st.rerun()
        
    target = st.session_state.golden_target
    idiom_text = target["成語"]
    meaning_text = target["解釋"]
    
    st.markdown(f"**💡 成語解釋提示**：`{meaning_text}`")
    
    if "初級" in difficulty:
        st.info(f"【初級提示】這是一句成語，第一個字是：【**{idiom_text[0]}**】")
    elif "中級" in difficulty:
        st.info(f"【中級提示】這是一句經典成語，字數為 {len(idiom_text)} 個字，請根據解釋填入！")
    else:
        st.info(f"【高級挑戰】完全盲猜！請輸入對應的完整成語！")
        
    user_guess = st.text_input("請輸入您的答案：", key="golden_guess_input")
    
    if st.button("送出答案"):
        if user_guess.strip() == idiom_text:
            st.success(f"👑 太神啦！校長大人完美答對！這就是【{idiom_text}】！")
            st.balloons()
        else:
            st.error("❌ 哎呀，答案不太對喔，再挑戰看看吧！")

st.write("---")

if st.button("⬅️ 返回澄玄大學首頁"):
    st.switch_page("streamlit_app.py")
