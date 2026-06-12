// リクエスト送信ボタンのイベントリスナー
const requestBtn = document.getElementById('btn-confirm');
requestBtn.addEventListener('click', () => {
    sendRequest();
});
// コードブロックのコピー機能
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('pre code').forEach((block) => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn btn btn-outline-primary';
        copyBtn.textContent = 'Copy';
        copyBtn.addEventListener('click', () => {
            copyToClipboard(block.innerText);
        });
        block.parentNode.appendChild(copyBtn);
    });
});