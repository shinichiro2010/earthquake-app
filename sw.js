// sw.js (改良版)
const CACHE_NAME = 'eq-app-cache-v1';
const DATA_CACHE = 'eq-app-data-v1';
const LAST_ID_KEY = 'last_notified_id';

// Service Worker がインストールされたとき
self.addEventListener('install', (event) => {
    console.log('Service Worker installed');
    self.skipWaiting();
});

// activate: 新しい SW をすぐに制御下に置く
self.addEventListener('activate', (event) => {
    console.log('Service Worker activated');
    event.waitUntil(clients.claim());
});

// periodicsync (対応ブラウザがある場合)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'check-earthquake') {
        event.waitUntil(checkLatestEarthquake());
    }
});

// ページからのメッセージでチェック要求を受け取る（フォールバック）
self.addEventListener('message', (event) => {
    if (!event.data) return;
    if (event.data.type === 'CHECK_EARTHQUAKE') {
        event.waitUntil(checkLatestEarthquake());
    }
});

// 通知クリック時の処理：既存クライアントをフォーカス or 新規ウィンドウを開く
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
            for (const client of windowClients) {
                // 既存タブがあればフォーカス
                if (client.url && 'focus' in client) {
                    return client.focus();
                }
            }
            // なければ新しいウィンドウを開く（ルートを開く）
            if (clients.openWindow) {
                return clients.openWindow('/');
            }
        })
    );
});

// 最新地震をチェックして通知（重複を防止）
async function checkLatestEarthquake() {
    try {
        const resp = await fetch('https://api.p2pquake.net/v2/jma/quake?limit=1', { cache: 'no-store' });
        if (!resp.ok) {
            console.warn('Fetch failed:', resp.status);
            return;
        }
        const data = await resp.json();
        if (!data || !Array.isArray(data) || data.length === 0) return;

        const latest = data[0];

        // 推定されるIDフィールドを取得（APIレスポンスの構造に依存します）
        // もし id がない場合は earthquake.id や timestamp 等にフォールバックしてください
        const latestId = latest.id || (latest.earthquake && latest.earthquake.id) || JSON.stringify(latest);

        // キャッシュから最後に通知したIDを読み出す
        const cache = await caches.open(DATA_CACHE);
        let lastId = null;
        try {
            const stored = await cache.match(LAST_ID_KEY);
            if (stored) {
                lastId = await stored.text();
            }
        } catch (err) {
            console.warn('Failed to read last id from cache:', err);
        }

        // 新しい地震なら通知を出す
        if (String(latestId) !== String(lastId)) {

            // タイトル／本文を作る（存在しないフィールドは代替）
            const hypoName = (latest.earthquake && latest.earthquake.hypocenter && latest.earthquake.hypocenter.name) || latest.earthquake?.hypocenter?.name || '不明な震源';
            const maxScale = (latest.earthquake && latest.earthquake.maxScale) || latest.earthquake?.maxScale || '';
            const title = `地震情報: ${hypoName}`;
            const body = maxScale ? `最大震度: ${maxScale}` : '新しい地震が発生しました。';

            // 通知表示
            await self.registration.showNotification(title, {
                body: body,
                tag: 'eq-noti',
                renotify: true,
                // icon を用意していれば指定
                // icon: '/icon.png',
            });

            // 最後のIDを保存
            try {
                await cache.put(LAST_ID_KEY, new Response(String(latestId)));
            } catch (err) {
                console.warn('Failed to write last id to cache:', err);
            }
        } else {
            // 同じID：何もしない
            console.log('No new earthquake (id matched).');
        }
    } catch (error) {
        console.error('checkLatestEarthquake error:', error);
    }
}
