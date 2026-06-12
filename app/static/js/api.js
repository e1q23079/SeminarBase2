const getCsrtfToken = () => {
    /*
        CSRFトークンを取得する関数
    */
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return null;
}

const getRequest = async (url) => {
    /*
        GETリクエストを送信する関数
    */
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        return { response, data };
    } catch (error) {
        return { response: { ok: false }, data: null };
    }
}

const postRequest = async (url) => {
    /*
        POSTリクエストを送信する関数
    */
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrtfToken(),
            },
        });
        const data = await response.json();
        return { response, data };
    } catch (error) {
        return { response: { ok: false }, data: null };
    }
}

const sendRequest = async () => {
    /*
        セミナー参加リクエストを送信する関数
    */
    const seminarId = window.SEMINAR_ID;
    const { response, data } = await postRequest(`/api/request/${seminarId}`);
    if (response.ok) {
        showLiveToast(data.message);
    } else {
        showLiveToast("リクエストの送信に失敗しました");
    }
}

const showLiveToast = (message) => {
    /*
        ライブトーストを表示する関数
    */
    const toastLive = document.getElementById('liveToast');
    const minutes = document.getElementById('minutes');
    minutes.textContent = message;
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLive);
    toastBootstrap.show();
}

const playNotificationSound = () => {
    /*
        通知音を再生する関数
    */
    const audio = new Audio('/static/file/notify.mp3');
    audio.play();
}

const copyToClipboard = (text) => {
    /*
        クリップボードにテキストをコピーする関数
    */
    navigator.clipboard.writeText(text).then(() => {
        return showLiveToast("コピーしました");
    }).catch(() => {
        showLiveToast("コピーに失敗しました");
    });
}