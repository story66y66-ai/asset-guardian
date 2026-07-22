<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>歌詞語音播放器</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f7f9fc;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        h2 {
            color: #333;
            text-align: center;
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 16px;
            resize: vertical;
            box-sizing: border-box;
        }
        .controls {
            margin-top: 15px;
            display: flex;
            gap: 15px;
            align-items: center;
            justify-content: space-between;
        }
        select, button {
            padding: 10px 15px;
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
            flex-grow: 1;
        }
        button:hover {
            background-color: #45a049;
        }
        button.stop {
            background-color: #f44336;
            flex-grow: 0;
        }
        button.stop:hover {
            background-color: #d32f2f;
        }
    </style>
</head>
<body>

    <h2>🎵 歌詞不同速度發音播放器</h2>
    
    <label for="lyricsInput">請在下方貼上你的歌詞：</label>
    <textarea id="lyricsInput" placeholder="在這裡貼上歌詞..."></textarea>

    <div class="controls">
        <div>
            <label for="speedSelect">速度：</label>
            <select id="speedSelect">
                <option value="0.5">0.5x (慢速)</option>
                <option value="0.75">0.75x (稍慢)</option>
                <option value="1.0" selected>1.0x (正常)</option>
                <option value="1.25">1.25x (稍快)</option>
                <option value="1.5">1.5x (快速)</option>
            </select>
        </div>
        
        <button onclick="playLyrics()">播放發音</button>
        <button class="stop" onclick="stopLyrics()">停止</button>
    </div>

    <script>
        function playLyrics() {
            const text = document.getElementById('lyricsInput').value;
            if (!text.trim()) {
                alert('請先輸入或貼上歌詞！');
                return;
            }

            // 檢查瀏覽器是否支援語音合成
            if (!('speechSynthesis' in window)) {
                alert('很抱歉，你的瀏覽器不支援語音功能。');
                return;
            }

            // 如果正在播放，先停止
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            
            // 設定語言為中文
            utterance.lang = 'zh-TW';

            // 取得選取的速度
            const speed = document.getElementById('speedSelect').value;
            utterance.rate = parseFloat(speed);

            // 開始播放
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
