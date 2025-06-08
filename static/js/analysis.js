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
    fetch('/analysis/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'position': latestSfen
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
    pollCount = 0;
    intervalId = setInterval(() => {
      pollCount++;
      if (pollCount > 20) {
        clearInterval(intervalId);
        showError('応答がありません');
        resetButton();
        return;
      }

      fetch(`/analysis/inquire/${aid}`)
        .then(response => response.json())
        .then(data => {
          console.log(data);
          if (data.status === 'running') {
            // 何もしない
          } else if (data.status === 'successed') {
            clearInterval(intervalId);
            showResult(data.message);
            resetButton();
          } else {
            clearInterval(intervalId);
            showError('解析に失敗しました');
            resetButton();
          }
        })
        .catch(error => {
          console.error('Error:', error);
          clearInterval(intervalId);
          resetButton();
        });
    }, 2000);
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
    analyzeButton.parentNode.insertBefore(errorMessage, analyzeButton);
  }

  function showResult(message) {
    const result = document.createElement('pre');
    result.innerText = message;
    result.className = 'analysis-result has-text-left';
    analyzeButton.parentNode.insertBefore(result, analyzeButton.nextSibling);
  }

  function clearMessages() {
    document.querySelectorAll('.analysis-error, .analysis-result').forEach(el => el.remove());
  }
});

const playButton = document.getElementById("play-button");
const viewButton = document.getElementById("view-button");
const viewpointButton = document.getElementById("viewpoint-button");
const viewpoint = "black"

document.getElementById("play-button").addEventListener("click", () => {
  el.setAttribute("sp_mode", "play");
  el.setAttribute("sp_turn", latestTurn.toString());
  // ボタンを強調表示
  playButton.classList.add("is-info");
  playButton.classList.remove("is-light");
  viewButton.classList.remove("is-info");
  viewButton.classList.add("is-light");
});

document.getElementById("view-button").addEventListener("click", () => {
  el.setAttribute("sp_mode", "view");
  el.setAttribute("sp_turn", latestTurn.toString());
  // ボタンを強調表示
  playButton.classList.remove("is-info");
  playButton.classList.add("is-light");
  viewButton.classList.add("is-info");
  viewButton.classList.remove("is-light");
});

document.getElementById("viewpoint-button").addEventListener("click", () => {
  if (viewpoint === "black"){
    viewpoint = "white";
    el.setAttribute("sp_viewpoint", "white");
  } else{
    viewpoint = "black";
    el.setAttribute("sp_viewpoint", "black");
  }
});