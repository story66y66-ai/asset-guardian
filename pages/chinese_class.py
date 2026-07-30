import streamlit as st
import pandas as pd

st.set_page_config(page_title="中文學院 - 澄玄400句成語旗艦挑戰賽", layout="wide", page_icon="📖")

@st.cache_data
def load_flagship_database():
    csv_url = "https://raw.githubusercontent.com/story66y66-ai/asset-guardian/main/idioms.csv"
    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        df = pd.read_csv("idioms.csv")
    
    if "idiom" in df.columns and "meaning" in df.columns:
        df = df.rename(columns={"idiom": "成語", "meaning": "解釋"})
    
    df = df.drop_duplicates(subset=["成語"]).reset_index(drop=True)
    return df

df = load_flagship_database()

st.title(f"📖 中文學院（校長大人專屬成語庫：目前共計 {len(df)} 筆全覆蓋真題）")
st.write("---")

st.success(f"🔥 系統已成功載入 **{len(df)} 筆** 完整成語！支援全書自動換頁與動態擴充 `.csv`！")
st.write("---")

tab1, tab2 = st.tabs(["📚 完整題庫總覽", "🎮 成語填空挑戰賽"])

with tab1:
    st.subheader(f"📚 完整成語資料庫預覽（動態對應共計 {len(df)} 筆）")
    
    page_size = 20
    total_pages = (len(df) + page_size - 1) // page_size
    if total_pages < 1:
        total_pages = 1
    
    query_params = st.query_params
    auto_mode_param = query_params.get("auto_mode", "false")
    
    if "current_page" not in st.session_state:
        if "page" in query_params:
            try:
                st.session_state.current_page = int(query_params["page"])
            except:
                st.session_state.current_page = 1
        else:
            st.session_state.current_page = 1

    col_p1, col_p2 = st.columns([2, 3])
    with col_p1:
        new_page = st.number_input(f"跳至頁數 (共 {total_pages} 頁)：", min_value=1, max_value=total_pages, value=st.session_state.current_page, step=1)
        if new_page != st.session_state.current_page:
            st.session_state.current_page = new_page
            st.query_params.clear()
            st.rerun()
    
    with col_p2:
        st.write("")
        sub1, sub2 = st.columns(2)
        with sub1:
            if st.button("⬅️ 上一頁") and st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.query_params.clear()
                st.rerun()
        with sub2:
            if st.button("下一頁 ➡️") and st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.query_params.clear()
                st.rerun()

    current_page = st.session_state.current_page
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    
    st.write(f"目前顯示第 **{current_page}** 頁（第 {start_idx + 1} ~ {end_idx} 筆）：")
    st.write("---")
    
    page_data = df.iloc[start_idx:end_idx]
    
    js_idioms_array = ""
    for idx, row in page_data.iterrows():
        idiom = row["成語"]
        meaning = row["解釋"]
        full_text = f"{idiom}，{meaning}"
        js_idioms_array += f"{{ index: {idx}, idiom: '{idiom}', text: '{full_text}' }},\n"

    rows_html = ""
    for idx, row in page_data.iterrows():
        idiom = row["成語"]
        meaning = row["解釋"]
        display_num = idx + 1
        text_to_speak = f"{idiom}。{meaning}"
        
        rows_html += f"""
        <tr style="border-bottom: 1px solid #ddd; height: 50px;" id="row_item_{idx}">
            <td style="width: 10%; font-weight: bold;">#{display_num}</td>
            <td style="width: 25%; font-weight: bold;" id="idiom_cell_{idx}">{idiom}</td>
            <td style="width: 45%;">{meaning}</td>
            <td style="width: 20%;">
                <button onclick="playSingle({idx}, '{idiom}', '{text_to_speak}', {len(df)})" 
                        id="btn_{idx}" 
                        style="background-color: #f0f2f6; border: 1px solid #d6d6d6; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-weight: bold;">
                    🔊 朗讀
                </button>
            </td>
        </tr>
        """

    audio_control_html = f"""
    <div style="margin-bottom: 15px; background-color: #f9f9f9; padding: 12px; border-radius: 6px; border: 1px solid #e0e0e0;">
        <div style="font-weight: bold; margin-bottom: 8px;">🎧 智能語音控制台：</div>
        <button onclick="startLoopPlay()" id="loop_btn" style="background-color: #17a2b8; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 8px;">
            🔁 本頁循環朗讀
        </button>
        <button onclick="startAutoNextPagePlay()" id="autonext_btn" style="background-color: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 8px;">
            📚 全書自動換頁朗讀
        </button>
        <button onclick="stopAutoPlay()" style="background-color: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold;">
            ⏹ 停止朗讀
        </button>
        <span id="auto_status" style="margin-left: 15px; color: #555; font-size: 14px; font-weight: bold;">狀態：待命中</span>
    </div>

    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="border-bottom: 2px solid #ccc; text-align: left;">
                <th style="padding-bottom: 8px;">序號</th>
                <th style="padding-bottom: 8px;">成語</th>
                <th style="padding-bottom: 8px;">解釋</th>
                <th style="padding-bottom: 8px;">語音操作</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <script>
    const totalPages = {total_pages};
    const currentPageNum = {current_page};
    const isAutoNextMode = "{auto_mode_param}" === "true";
    const totalRowsCount = {len(df)};
    
    const pageIdiomsData = [
    {js_idioms_array}
    ];

    let autoPlaying = false;
    let playMode = '';
    let currentAutoIdx = 0;

    window.addEventListener('DOMContentLoaded', (event) => {{
        if (isAutoNextMode) {{
            startAutoNextPagePlay();
        }}
    }});

    function clearAllHighlights() {{
        for (let i = 0; i < pageIdiomsData.length; i++) {{
            let item = pageIdiomsData[i];
            let cell = document.getElementById('idiom_cell_' + item.index);
            let btn = document.getElementById('btn_' + item.index);
            if (cell) {{
                cell.innerHTML = item.idiom;
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
        clearAllHighlights();
        
        let targetCell = document.getElementById('idiom_cell_' + idx);
        let targetBtn = document.getElementById('btn_' + idx);
        let targetRow = document.getElementById('row_item_' + idx);
        
        if (targetCell) {{
            targetCell.innerHTML = '🎵 <b>' + idiom + '</b> ⭐';
        }}
        if (targetBtn) {{
            targetBtn.innerText = '🔊 朗讀中...';
            targetBtn.style.backgroundColor = '#ff4b4b';
            targetBtn.style.color = 'white';
        }}
        if (targetRow) {{
            targetRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
        
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = 'zh-TW';
        utterance.rate = 0.9;
        
        utterance.onend = function() {{
            if (targetCell) {{
                targetCell.innerHTML = idiom;
            }}
            if (targetBtn) {{
                targetBtn.innerText = '🔊 朗讀';
                targetBtn.style.backgroundColor = '#f0f2f6';
                targetBtn.style.color = 'black';
            }}
        }};
        
        window.speechSynthesis.speak(utterance);
    }}

    function startLoopPlay() {{
        if (pageIdiomsData.length === 0) return;
        autoPlaying = true;
        playMode = 'loop';
        currentAutoIdx = 0;
        document.getElementById('auto_status').innerText = '狀態：[本頁循環] 播放中...';
        let btn = document.getElementById('loop_btn');
        if(btn) btn.style.backgroundColor = '#6c757d';
        playNextInQueue();
    }}

    function startAutoNextPagePlay() {{
        if (pageIdiomsData.length === 0) return;
        autoPlaying = true;
        playMode = 'autonext';
        currentAutoIdx = 0;
        document.getElementById('auto_status').innerText = '狀態：[全書換頁] 播放中...';
        let btn = document.getElementById('autonext_btn');
        if(btn) btn.style.backgroundColor = '#6c757d';
        playNextInQueue();
    }}

    function playNextInQueue() {{
        if (!autoPlaying) return;

        if (currentAutoIdx >= pageIdiomsData.length) {{
            if (playMode === 'loop') {{
                currentAutoIdx = 0;
            }} else if (playMode === 'autonext') {{
                if (currentPageNum < totalPages) {{
                    document.getElementById('auto_status').innerText = '狀態：本頁讀完，自動無縫跳至第 ' + (currentPageNum + 1) + ' 頁...';
                    setTimeout(function() {{
                        const nextUrl = window.location.pathname + '?page=' + (currentPageNum + 1) + '&auto_mode=true';
                        window.parent.location.href = nextUrl;
                    }, 800);
                    return;
                }} else {{
                    stopAutoPlay();
                    document.getElementById('auto_status').innerText = '狀態：全書所有成語已全部播畢！';
                    return;
                }}
            }}
        }}

        let item = pageIdiomsData[currentAutoIdx];
        let idx = item.index;
        let idiom = item.idiom;
        let textToSpeak = item.text;

        clearAllHighlights();

        let targetCell = document.getElementById('idiom_cell_' + idx);
        let targetBtn = document.getElementById('btn_' + idx);
        let targetRow = document.getElementById('row_item_' + idx);

        if (targetCell) {{
            targetCell.innerHTML = '🎵 <b>' + idiom + '</b> ⭐';
        }}
        if (targetBtn) {{
            targetBtn.innerText = '🔊 播放中';
            targetBtn.style.backgroundColor = '#17a2b8';
            targetBtn.style.color = 'white';
        }}
        
        if (targetRow) {{
            targetRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}

        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = 'zh-TW';
        utterance.rate = 0.9;

        utterance.onend = function() {{
            if (targetCell) {{
                targetCell.innerHTML = idiom;
            }}
            if (targetBtn) {{
                targetBtn.innerText = '🔊 朗讀';
                targetBtn.style.backgroundColor = '#f0f2f6';
                targetBtn.style.color = 'black';
            }}
            currentAutoIdx++;
            if (autoPlaying) {{
                setTimeout(playNextInQueue, 800);
            }}
        }};

        window.speechSynthesis.speak(utterance);
    }}

    function stopAutoPlay() {{
        autoPlaying = false;
        playMode = '';
        window.speechSynthesis.cancel();
        clearAllHighlights();
        
        if (window.parent.location.search.includes('auto_mode=true')) {{
            const cleanUrl = window.location.pathname;
            window.parent.history.replaceState({{}}, document.title, cleanUrl);
        }}
        
        let loopBtn = document.getElementById('loop_btn');
        let autonextBtn = document.getElementById('autonext_btn');
        if (loopBtn) loopBtn.style.backgroundColor = '#17a2b8';
        if (autonextBtn) autonextBtn.style.backgroundColor = '#28a745';
        
        let statusElem = document.getElementById('auto_status');
        if (statusElem) {{
            statusElem.innerText = '狀態：已停止';
        }}
    }}
    </script>
    """

    st.components.v1.html(audio_control_html, height=1100, scrolling=True)

with tab2:
    st.subheader("🎯 挑戰您的無敵成語腦力")
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
        st.info(f"【初級提示】第一個字是：【**{idiom_text[0]}**】")
    elif "中級" in difficulty:
        st.info(f"【中級提示】總字數為 {len(idiom_text)} 個字")
    else:
        st.info("【高級挑戰】完全盲猜！")
        
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
