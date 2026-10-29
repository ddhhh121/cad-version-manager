const CACHE_NAME = 'cad-manager-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
];

// 安装时缓存静态资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// 激活时清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// 拦截网络请求
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API 请求不缓存，直接走网络
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // 静态资源使用缓存优先策略
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        // 返回缓存，同时更新缓存
        fetch(event.request).then((newResponse) => {
          if (newResponse && newResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, newResponse);
            });
          }
        });
        return response;
      }
      return fetch(event.request).then((response) => {
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      });
    })
  );
});
