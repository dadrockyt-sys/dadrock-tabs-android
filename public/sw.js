// DadRock Tabs Service Worker v2 — auto-updating cache
// IMPORTANT: Bump this version string on every deploy to force cache refresh
const CACHE_VERSION = 'dadrock-v2-' + '20260505';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/apple-icon.png',
];

// Install: cache critical assets and immediately activate
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  // Skip waiting — activate this new SW immediately
  self.skipWaiting();
});

// Activate: delete ALL old caches so stale content is purged
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION)
          .map((key) => caches.delete(key))
      );
    })
  );
  // Claim all clients immediately so the new SW controls existing tabs/webviews
  self.clients.claim();
});

// Fetch: Network-first for EVERYTHING (ensures fresh content always)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip API requests and external URLs
  if (url.pathname.startsWith('/api/') || url.origin !== self.location.origin) return;

  // Network-first strategy for ALL requests
  // This ensures the app always gets the latest content
  // Falls back to cache only when offline
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cached) => {
          return cached || (event.request.mode === 'navigate' ? caches.match('/') : undefined);
        });
      })
  );
});

// Listen for messages to force update
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
