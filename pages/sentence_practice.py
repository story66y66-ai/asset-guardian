import streamlit as st

st.subheader("🎵 歌詞不同速度發音播放器")

# 用 HTML/JS 透過 streamlit 元件呈現
html_code = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <style>
        textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .controls {
            margin-top: 10px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        select, button {
            padding: 8px 12px;
            font-size: 16px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button.stop {
            background-color: #f44336;
        }
    </style>
</head>
<body>
    <textarea id="lyricsInput" placeholder="在這裡貼上你的歌詞..."></textarea>
    <div class="controls">
        <label for="speedSelect">速度：</label>
        <select id="speedSelect">
            <option value="0.5">0.5x</option>
            <option value="0.75">0.75x</option>
            <option value="1.0" selected>1.0x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
        </select>
        <button onclick="playLyrics()">播放</button>
        <button class="stop" onclick="stopLyrics()">停止</button>
    </div>

    <script>
        function playLyrics() {
            const text = document.getElementById('lyricsInput').value;
            if (!text.trim()) {
                alert('請先輸入歌詞！');
                return;
            }
            if (!('speechSynthesis' in window)) {
                alert('瀏覽器不支援語音功能');
                return;
            }
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'zh-TW';
            utterance.rate = parseFloat(document.getElementById('speedSelect').value);
            window.speechSynthesis.speak(utterance);
        }
        function stopLyrics() {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        }
    </script>
</body>
</html>
"""

# 在 Streamlit 中安全嵌入 HTML
st.components.v1.html(html_code, height=250)
