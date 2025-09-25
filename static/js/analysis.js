let latestSfen = ""; // 局面を記録する変数
const el = document.querySelector("shogi-player-wc")
// 局面を記録する変数
el.addEventListener("ev_short_sfen_change", e => {
  latestSfen = e.detail[0];
});
// 手番を記録する変数
el.addEventListener("ev_turn_offset_change", e => {
  latestTurn = e.detail[0];
});

document.addEventListener('DOMContentLoaded', function() {
  const analyzeButton = document.getElementById('analyze-button');
  let aid = null;
  let intervalId = null;
  let pollCount = 0;

  analyzeButton.addEventListener('click', function() {
    clearMessages(); // 以前のメッセージをクリア
    analyzeButton.innerText = '解析中';
    analyzeButton.disabled = true;

    // プルダウンから解析時間を取得
    const analysisTimeSelect = document.getElementById('analysis-time-select');
    const analysisTime = parseInt(analysisTimeSelect.value);

    fetch('/analysis/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'position': latestSfen,
        'movetime': analysisTime
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.submit === 'reject') {
        showError('リソースを確保できませんでした');
        resetButton();
      } else if (data.submit === 'accept') {
        aid = data.aid;
        startAnalysis();
      }
    })
    .catch(error => {
      console.error('Error:', error);
      resetButton();
    });
  });

  function startAnalysis() {
    const analysisTimeSelect = document.getElementById('analysis-time-select');
    const analysisTime = parseInt(analysisTimeSelect.value);

    // 解析時間に応じた初期待機時間を設定
    let initialDelay;
    if (analysisTime <= 3000) {
      initialDelay = 2000; // 3秒の場合は2秒待機
    } else if (analysisTime <= 5000) {
      initialDelay = 4000; // 5秒の場合は4秒待機
    } else {
      initialDelay = 9000; // 10秒の場合は9秒待機
    }

    // 最初の問い合わせは1秒後に実行
    setTimeout(() => {
      checkAnalysisResult();
    }, 1000);

    // 初期待機後、0.5秒間隔でポーリング開始
    setTimeout(() => {
      pollCount = 0;
      intervalId = setInterval(() => {
        pollCount++;
        if (pollCount > 20) {
          clearInterval(intervalId);
          showError('応答がありません');
          resetButton();
          return;
        }
        checkAnalysisResult();
      }, 500);
    }, initialDelay);
  }

  function checkAnalysisResult() {
    fetch(`/analysis/inquire/${aid}`)
      .then(response => response.json())
      .then(data => {
        console.log(data);
        if (data.status === 'running') {
          // 何もしない
        } else if (data.status === 'successed') {
          if (intervalId) clearInterval(intervalId);
          showResult(data.message);
          resetButton();
        } else {
          if (intervalId) clearInterval(intervalId);
          showError('解析に失敗しました');
          resetButton();
        }
      })
      .catch(error => {
        console.error('Error:', error);
        if (intervalId) clearInterval(intervalId);
        resetButton();
      });
  }

  function resetButton() {
    analyzeButton.innerText = '解析開始';
    analyzeButton.disabled = false;
  }

  function showError(message) {
    const errorMessage = document.createElement('div');
    errorMessage.innerText = message;
    errorMessage.style.color = 'red';
    errorMessage.className = 'analysis-error';
    // analysis-controlsの親ノード（board-controls-section）の後に挿入
    const analysisControls = analyzeButton.closest('.analysis-controls');
    analysisControls.parentNode.insertBefore(errorMessage, analysisControls.nextSibling);
  }

  function showResult(message) {
    const result = document.createElement('pre');
    result.innerText = message;
    result.className = 'analysis-result has-text-left';
    // analysis-controlsの親ノード（board-controls-section）の後に挿入
    const analysisControls = analyzeButton.closest('.analysis-controls');
    analysisControls.parentNode.insertBefore(result, analysisControls.nextSibling);
  }

  function clearMessages() {
    document.querySelectorAll('.analysis-error, .analysis-result').forEach(el => el.remove());
  }
});

const playButton = document.getElementById("play-button");
const viewButton = document.getElementById("view-button");
const viewpointButton = document.getElementById("viewpoint-button");
let viewpoint = "black"

document.getElementById("play-button").addEventListener("click", () => {
  el.setAttribute("sp_mode", "play");
  el.setAttribute("sp_turn", latestTurn.toString());
  // ボタンを強調表示
  playButton.classList.add("primary");
  viewButton.classList.remove("primary");
});

document.getElementById("view-button").addEventListener("click", () => {
  el.setAttribute("sp_mode", "view");
  el.setAttribute("sp_turn", latestTurn.toString());
  // ボタンを強調表示
  playButton.classList.remove("primary");
  viewButton.classList.add("primary");
});

document.getElementById("viewpoint-button").addEventListener("click", () => {
  if (viewpoint === "black"){
    viewpoint = "white";
    el.setAttribute("sp_viewpoint", "white");
  } else {
    viewpoint = "black";
    el.setAttribute("sp_viewpoint", "black");
  }
});