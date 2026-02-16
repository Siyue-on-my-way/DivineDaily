const CACHE_NAME = 'divinedaily-v1';
const STATIC_CACHE = 'divinedaily-static-v1';
const DYNAMIC_CACHE = 'divinedaily-dynamic-v1';

// 需要缓存的静态资源
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico'
];

// 安装事件
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[Service Worker] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  
  // 强制激活新的 Service Worker
  self.skipWaiting();
});

// 激活事件
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => {
            return name !== STATIC_CACHE && name !== DYNAMIC_CACHE;
          })
          .map((name) => {
            console.log('[Service Worker] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  
  // 立即控制所有页面
  return self.clients.claim();
});

// 拦截请求
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 跳过非 GET 请求
  if (request.method !== 'GET') {
    return;
  }

  // 跳过 chrome-extension 和其他协议
  if (!url.protocol.startsWith('http')) {
    return;
  }

  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      // 如果有缓存，返回缓存
      if (cachedResponse) {
        // 同时在后台更新缓存（Stale While Revalidate）
        fetch(request).then((response) => {
          if (response && response.status === 200) {
            caches.open(DYNAMIC_CACHE).then((cache) => {
              cache.put(request, response);
            });
          }
        });
        
        return cachedResponse;
      }

      // 没有缓存，从网络获取
      return fetch(request)
        .then((response) => {
          // 检查响应是否有效
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }

          // 克隆响应
          const responseToCache = response.clone();

          // 缓存响应
          caches.open(DYNAMIC_CACHE).then((cache) => {
            // 只缓存同源请求
            if (url.origin === location.origin) {
              cache.put(request, responseToCache);
            }
          });

          return response;
        })
        .catch((error) => {
          console.error('[Service Worker] Fetch failed:', error);
          
          // 如果是导航请求，返回离线页面
          if (request.mode === 'navigate') {
            return caches.match('/index.html');
          }
          
          // 其他请求返回错误
          throw error;
        });
    })
  );
});

// 后台同步
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);
  
  if (event.tag === 'sync-divinations') {
    event.waitUntil(syncDivinations());
  }
});

// 推送通知
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received');
  
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'DivineDaily';
  const options = {
    body: data.body || '你有新的占卜结果',
    icon: '/icon-192.png',
    badge: '/badge-72.png',
    data: data.url
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// 通知点击
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked');
  
  event.notification.close();
  
  const url = event.notification.data || '/';
  
  event.waitUntil(
    clients.openWindow(url)
  );
});

// 辅助函数：同步占卜数据
async function syncDivinations() {
  try {
    // 这里实现实际的同步逻辑
    console.log('[Service Worker] Syncing divinations...');
    
    // 获取待同步的数据
    const cache = await caches.open(DYNAMIC_CACHE);
    // ... 同步逻辑
    
    return Promise.resolve();
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error);
    return Promise.reject(error);
  }
}
