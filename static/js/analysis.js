let latestSfen = ""; // 局面を記録する変数
const el = document.querySelector("shogi-player-wc")
el.addEventListener("ev_short_sfen_change", e => {
  latestSfen = e.detail[0];
});

document.addEventListener('DOMContentLoaded', function() {
  const analyzeButton = document.getElementById('analyze-button');
  let aid = null;
  let intervalId = null;
  let pollCount = 0;

  analyzeButton.addEventListener('click', function() {
    clearMessages(); // 以前のメッセージをクリア
    analyzeButton.innerText = '分析中';
    analyzeButton.disabled = true;
    alert(latestSfen);
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
          if (data.status === 'running') {
            // 何もしない
          } else if (data.status === 'complete') {
            clearInterval(intervalId);
            showResult(data.message);
            resetButton();
          }
        })
        .catch(error => {
          console.error('Error:', error);
          clearInterval(intervalId);
          resetButton();
        });
    }, 3000);
  }

  function resetButton() {
    analyzeButton.innerText = '分析開始';
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
    result.className = 'analysis-result';
    analyzeButton.parentNode.insertBefore(result, analyzeButton.nextSibling);
  }

  function clearMessages() {
    document.querySelectorAll('.analysis-error, .analysis-result').forEach(el => el.remove());
  }
});
