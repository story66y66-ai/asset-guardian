<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>澄玄的訓練農場</title>
    <style>
        body { background-color: #f0f7f4; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: 'Segoe UI', sans-serif; }
        #farm-card { width: 80%; max-width: 500px; padding: 40px; background: white; border-radius: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.15); text-align: center; cursor: pointer; }
        .word { font-size: 3rem; color: #2c3e50; margin-bottom: 10px; }
        .translation { font-size: 1.8rem; color: #27ae60; margin-top: 20px; display: none; border-top: 2px solid #eee; padding-top: 20px; }
        .hint { margin-top: 30px; color: #7f8c8d; font-size: 1rem; }
    </style>
</head>
<body>

    <div id="farm-card" onclick="toggle()">
        <div class="word" id="word">Loading...</div>
        <div class="translation" id="translation"></div>
    </div>
    <div class="hint">點擊卡片，翻開農場作物</div>

    <script>
        // 這裡就是您農場的單字庫，Sister 會幫您整理
        const farmData = [
            { word: "Seed", trans: "種子" },
            { word: "Harvest", trans: "收穫" }
        ];

        let index = 0;
        function update() {
            document.getElementById('word').innerText = farmData[index].word;
            document.getElementById('translation').innerText = farmData[index].trans;
            document.getElementById('translation').style.display = 'none';
        }
        function toggle() {
            const trans = document.getElementById('translation');
            if (trans.style.display === 'none') {
                trans.style.display = 'block';
            } else {
                index = (index + 1) % farmData.length;
                update();
            }
        }
        update();
    </script>
</body>
</html>
