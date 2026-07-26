/* ============================================================
   duq-tools Service Worker — Offline support via Cache-first
   ============================================================ */

const CACHE_NAME = 'duq-tools-v1';
const STATIC_CACHE = 'duq-tools-static-v1';

// ─── Assets to pre-cache on install ────────────────────────────
const PRECACHE_URLS = [
  '/',
  '/static/persist.js',
  '/favicon.ico',
  // Sprite Editor
  '/sprite-editor/',
  '/sprite-editor/index.html',
  '/sprite-editor/css/styles.css',
  '/sprite-editor/js/app.js',
  '/sprite-editor/icon.png',
  // Sprite Fusion
  '/sprite-fusion/',
  '/sprite-fusion/index.html',
  '/sprite-fusion/styles.css',
  '/sprite-fusion/script.js',
  '/sprite-fusion/icon.png',
  // Trigger Editor
  '/trigger-editor/',
  '/trigger-editor/index.html',
  '/trigger-editor/icon.png',
];

// ─── Install: pre-cache all static assets ──────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    }).then(() => {
      return self.skipWaiting();
    })
  );
});

// ─── Activate: clean up old caches ─────────────────────────────
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME, STATIC_CACHE];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// ─── Helper: is this a static asset request? ───────────────────
function isStaticAsset(url) {
  const path = url.pathname;
  return (
    path.endsWith('.js') ||
    path.endsWith('.css') ||
    path.endsWith('.png') ||
    path.endsWith('.ico') ||
    path.endsWith('.jpg') ||
    path.endsWith('.jpeg') ||
    path.endsWith('.gif') ||
    path.endsWith('.webp') ||
    path.endsWith('.svg') ||
    path.endsWith('.woff') ||
    path.endsWith('.woff2') ||
    path.endsWith('.ttf') ||
    path === '/static/persist.js'
  );
}

// ─── Helper: is this an HTML navigation request? ────────────────
function isNavigation(url) {
  return url.pathname === '/' ||
    url.pathname === '' ||
    url.pathname.startsWith('/sprite-editor') ||
    url.pathname.startsWith('/sprite-fusion') ||
    url.pathname.startsWith('/trigger-editor');
}

// ─── Fetch: cache-first for static assets, network-first for HTML ──
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Only handle same-origin requests
  if (url.origin !== self.location.origin) return;

  // ─── Static assets (JS, CSS, images) — Cache First ───
  if (isStaticAsset(url)) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached;
        // Not in cache — fetch from network and cache for next time
        return fetch(event.request).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, clone);
            });
          }
          return response;
        }).catch(() => {
          // Network failed and not in cache — show offline fallback
          return caches.match('/');
        });
      })
    );
    return;
  }

  // ─── HTML navigations — Network First, fallback to cache ───
  if (isNavigation(url)) {
    event.respondWith(
      fetch(event.request).then((response) => {
        // Cache the latest version
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
        }
        return response;
      }).catch(() => {
        // Offline — serve from cache
        return caches.match(event.request).then((cached) => {
          if (cached) return cached;
          // Fallback to homepage
          return caches.match('/');
        });
      })
    );
    return;
  }

  // ─── Everything else — Network Only ───
  // (no offline handling needed for non-essential requests)
});
