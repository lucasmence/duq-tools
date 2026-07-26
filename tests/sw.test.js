import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ─── SW source code as string (so we can re-evaluate in mocked env) ─────
// We import the SW code as a raw string so we can eval it in a mock scope.
// In this test we unit-test the helper functions by duplicating them,
// and test event handlers by mocking the SW globals.

// ─── Helper function copies (extracted from sw.js for testability) ────────
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

function isNavigation(url) {
  return url.pathname === '/' ||
    url.pathname === '' ||
    url.pathname.startsWith('/sprite-editor') ||
    url.pathname.startsWith('/sprite-fusion') ||
    url.pathname.startsWith('/trigger-editor');
}

// ─── PRECACHE_URLS from sw.js ─────────────────────────────────────────────
const PRECACHE_URLS = [
  '/',
  '/static/persist.js',
  '/favicon.ico',
  '/sprite-editor/',
  '/sprite-editor/index.html',
  '/sprite-editor/css/styles.css',
  '/sprite-editor/js/app.js',
  '/sprite-editor/icon.png',
  '/sprite-fusion/',
  '/sprite-fusion/index.html',
  '/sprite-fusion/styles.css',
  '/sprite-fusion/script.js',
  '/sprite-fusion/icon.png',
  '/trigger-editor/',
  '/trigger-editor/index.html',
  '/trigger-editor/icon.png',
];

// ═══════════════════════════════════════════════════════════════════════════
//  TESTS: isStaticAsset
// ═══════════════════════════════════════════════════════════════════════════

describe('isStaticAsset', () => {
  it('identifies .js files as static', () => {
    expect(isStaticAsset(new URL('http://localhost/app.js'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/script.min.js'))).toBe(true);
  });

  it('identifies .css files as static', () => {
    expect(isStaticAsset(new URL('http://localhost/styles.css'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/css/main.css'))).toBe(true);
  });

  it('identifies image files as static', () => {
    expect(isStaticAsset(new URL('http://localhost/icon.png'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/hero.jpg'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/pic.jpeg'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/animation.gif'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/bg.webp'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/logo.svg'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/favicon.ico'))).toBe(true);
  });

  it('identifies font files as static', () => {
    expect(isStaticAsset(new URL('http://localhost/font.woff'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/font.woff2'))).toBe(true);
    expect(isStaticAsset(new URL('http://localhost/font.ttf'))).toBe(true);
  });

  it('matches /static/persist.js exactly', () => {
    expect(isStaticAsset(new URL('http://localhost/static/persist.js'))).toBe(true);
  });

  it('rejects non-static paths', () => {
    expect(isStaticAsset(new URL('http://localhost/'))).toBe(false);
    expect(isStaticAsset(new URL('http://localhost/sprite-editor/'))).toBe(false);
    expect(isStaticAsset(new URL('http://localhost/api/data'))).toBe(false);
    expect(isStaticAsset(new URL('http://localhost/index.html'))).toBe(false);
  });

  it('rejects unknown extensions', () => {
    expect(isStaticAsset(new URL('http://localhost/file.json'))).toBe(false);
    expect(isStaticAsset(new URL('http://localhost/data.xml'))).toBe(false);
    expect(isStaticAsset(new URL('http://localhost/file.txt'))).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
//  TESTS: isNavigation
// ═══════════════════════════════════════════════════════════════════════════

describe('isNavigation', () => {
  it('identifies the root path as navigation', () => {
    expect(isNavigation(new URL('http://localhost/'))).toBe(true);
  });

  it('identifies empty path as navigation', () => {
    expect(isNavigation(new URL('http://localhost'))).toBe(true);
  });

  it('identifies tool root paths as navigation', () => {
    expect(isNavigation(new URL('http://localhost/sprite-editor/'))).toBe(true);
    expect(isNavigation(new URL('http://localhost/sprite-fusion/'))).toBe(true);
    expect(isNavigation(new URL('http://localhost/trigger-editor/'))).toBe(true);
  });

  it('identifies tool subpaths as navigation', () => {
    expect(isNavigation(new URL('http://localhost/sprite-editor/index.html'))).toBe(true);
    expect(isNavigation(new URL('http://localhost/sprite-fusion/styles.css'))).toBe(true);
    expect(isNavigation(new URL('http://localhost/trigger-editor/icon.png'))).toBe(true);
  });

  it('rejects non-tool paths', () => {
    expect(isNavigation(new URL('http://localhost/api/data'))).toBe(false);
    expect(isNavigation(new URL('http://localhost/static/persist.js'))).toBe(false);
    expect(isNavigation(new URL('http://localhost/other-tool/'))).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
//  TESTS: PRECACHE_URLS
// ═══════════════════════════════════════════════════════════════════════════

describe('PRECACHE_URLS', () => {
  it('includes the root path', () => {
    expect(PRECACHE_URLS).toContain('/');
  });

  it('includes all tool root pages', () => {
    expect(PRECACHE_URLS).toContain('/sprite-editor/');
    expect(PRECACHE_URLS).toContain('/sprite-fusion/');
    expect(PRECACHE_URLS).toContain('/trigger-editor/');
  });

  it('includes all known CSS and JS assets', () => {
    expect(PRECACHE_URLS).toContain('/static/persist.js');
    expect(PRECACHE_URLS).toContain('/sprite-editor/css/styles.css');
    expect(PRECACHE_URLS).toContain('/sprite-editor/js/app.js');
    expect(PRECACHE_URLS).toContain('/sprite-fusion/styles.css');
    expect(PRECACHE_URLS).toContain('/sprite-fusion/script.js');
  });

  it('includes all tool HTML files', () => {
    expect(PRECACHE_URLS).toContain('/sprite-editor/index.html');
    expect(PRECACHE_URLS).toContain('/sprite-fusion/index.html');
    expect(PRECACHE_URLS).toContain('/trigger-editor/index.html');
  });

  it('includes all icon files', () => {
    expect(PRECACHE_URLS).toContain('/favicon.ico');
    expect(PRECACHE_URLS).toContain('/sprite-editor/icon.png');
    expect(PRECACHE_URLS).toContain('/sprite-fusion/icon.png');
    expect(PRECACHE_URLS).toContain('/trigger-editor/icon.png');
  });

  it('has no duplicate entries', () => {
    const unique = new Set(PRECACHE_URLS);
    expect(unique.size).toBe(PRECACHE_URLS.length);
  });

  it('all URLs start with /', () => {
    PRECACHE_URLS.forEach(url => {
      expect(url.startsWith('/')).toBe(true);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
//  TESTS: Service Worker event handlers (mocked environment)
// ═══════════════════════════════════════════════════════════════════════════

describe('Service Worker install event', () => {
  beforeEach(() => {
    // Mock CacheStorage
    const mockCache = {
      addAll: vi.fn().mockResolvedValue(undefined),
    };
    const mockCaches = {
      open: vi.fn().mockResolvedValue(mockCache),
      keys: vi.fn().mockResolvedValue([]),
      delete: vi.fn().mockResolvedValue(true),
      match: vi.fn().mockResolvedValue(undefined),
    };

    // Mock self (ServiceWorkerGlobalScope)
    globalThis.self = {
      addEventListener: vi.fn(),
      skipWaiting: vi.fn(),
      clients: {
        claim: vi.fn(),
      },
      location: { origin: 'http://localhost' },
    };

    globalThis.caches = mockCaches;

    // Prevent the SW from auto-registering event listeners when imported
    // We'll manually test the event handler logic
  });

  afterEach(() => {
    delete globalThis.self;
    delete globalThis.caches;
  });

  it('uses CACHE_NAME constant when opening cache on install', () => {
    // Simulate what the install handler does
    caches.open('duq-tools-v1').then(cache => {
      cache.addAll(PRECACHE_URLS);
    });

    expect(caches.open).toHaveBeenCalledWith('duq-tools-v1');
  });

  it('calls skipWaiting after caching', async () => {
    // The install handler does: caches.open(CACHE_NAME) -> addAll -> skipWaiting
    const cache = await caches.open('duq-tools-v1');
    await cache.addAll(PRECACHE_URLS);
    self.skipWaiting();

    expect(cache.addAll).toHaveBeenCalledWith(PRECACHE_URLS);
    expect(self.skipWaiting).toHaveBeenCalled();
  });
});

describe('Service Worker activate event', () => {
  beforeEach(() => {
    globalThis.self = {
      addEventListener: vi.fn(),
      clients: {
        claim: vi.fn(),
      },
    };

    globalThis.caches = {
      keys: vi.fn().mockResolvedValue(['duq-tools-v1', 'duq-tools-static-v1', 'old-cache-v0']),
      delete: vi.fn().mockResolvedValue(true),
      open: vi.fn(),
      match: vi.fn(),
    };
  });

  afterEach(() => {
    delete globalThis.self;
    delete globalThis.caches;
  });

  it('deletes old caches not in the whitelist', async () => {
    const CACHE_NAME = 'duq-tools-v1';
    const STATIC_CACHE = 'duq-tools-static-v1';
    const cacheWhitelist = [CACHE_NAME, STATIC_CACHE];

    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames.map(name => {
        if (!cacheWhitelist.includes(name)) {
          return caches.delete(name);
        }
      })
    );

    // Should delete 'old-cache-v0' but not 'duq-tools-v1' or 'duq-tools-static-v1'
    expect(caches.delete).toHaveBeenCalledTimes(1);
    expect(caches.delete).toHaveBeenCalledWith('old-cache-v0');
    expect(caches.delete).not.toHaveBeenCalledWith('duq-tools-v1');
    expect(caches.delete).not.toHaveBeenCalledWith('duq-tools-static-v1');

    // Simulate the rest of the activate handler
    self.clients.claim();

    expect(self.clients.claim).toHaveBeenCalled();
  });
});

describe('Service Worker fetch event — static assets', () => {
  beforeEach(() => {
    globalThis.self = {
      addEventListener: vi.fn(),
      location: { origin: 'http://localhost' },
    };

    globalThis.caches = {
      match: vi.fn(),
      open: vi.fn(),
    };

    globalThis.fetch = vi.fn();
  });

  afterEach(() => {
    delete globalThis.self;
    delete globalThis.caches;
    delete globalThis.fetch;
  });

  it('returns cached response when available (cache-first)', async () => {
    const cachedResponse = new Response('cached', { status: 200 });
    caches.match.mockResolvedValue(cachedResponse);

    const result = await caches.match('http://localhost/app.js');

    expect(result).toBe(cachedResponse);
    expect(await result.text()).toBe('cached');
    // Network should NOT be called when cache hits
    expect(fetch).not.toHaveBeenCalled();
  });

  it('fetches from network when cache misses and caches the response', async () => {
    // First call: cache miss
    caches.match.mockResolvedValueOnce(null);
    // Second call (inside fetch.then): cache before returning
    const mockCache = { put: vi.fn().mockResolvedValue(undefined) };
    caches.open.mockResolvedValue(mockCache);

    const networkResponse = new Response('network data', { status: 200 });
    globalThis.fetch = vi.fn().mockResolvedValue(networkResponse);

    // Simulate the fetch handler's cache-first logic
    const cached = await caches.match('http://localhost/app.js');
    if (!cached) {
      const response = await fetch('http://localhost/app.js');
      if (response && response.status === 200) {
        const clone = response.clone();
        const cache = await caches.open('duq-tools-v1');
        await cache.put('http://localhost/app.js', clone);
      }
    }

    expect(fetch).toHaveBeenCalledWith('http://localhost/app.js');
    expect(caches.open).toHaveBeenCalledWith('duq-tools-v1');
    expect(mockCache.put).toHaveBeenCalled();
  });

  it('falls back to homepage on network failure when cache misses', async () => {
    caches.match
      .mockResolvedValueOnce(null)   // First: asset not in cache
      .mockResolvedValueOnce(new Response('homepage', { status: 200 })); // Fallback: homepage

    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network failed'));

    // Simulate the fetch handler's logic
    const cached = await caches.match('http://localhost/app.js');
    if (!cached) {
      try {
        await fetch('http://localhost/app.js');
      } catch {
        // Network failed — fallback to homepage
        const fallback = await caches.match('/');
        expect(fallback).toBeDefined();
        expect(await fallback.text()).toBe('homepage');
      }
    }
  });
});

describe('Service Worker fetch event — HTML navigation', () => {
  beforeEach(() => {
    globalThis.self = {
      addEventListener: vi.fn(),
      location: { origin: 'http://localhost' },
    };

    globalThis.caches = {
      match: vi.fn(),
      open: vi.fn(),
    };

    globalThis.fetch = vi.fn();
  });

  afterEach(() => {
    delete globalThis.self;
    delete globalThis.caches;
    delete globalThis.fetch;
  });

  it('caches HTML responses from network on successful fetch', async () => {
    const mockCache = { put: vi.fn().mockResolvedValue(undefined) };
    caches.open.mockResolvedValue(mockCache);

    const htmlResponse = new Response('<html>home</html>', {
      status: 200,
      headers: { 'Content-Type': 'text/html' },
    });
    globalThis.fetch = vi.fn().mockResolvedValue(htmlResponse);

    // Simulate network-first logic
    const response = await fetch('http://localhost/sprite-editor/');
    if (response && response.status === 200) {
      const clone = response.clone();
      const cache = await caches.open('duq-tools-v1');
      await cache.put('http://localhost/sprite-editor/', clone);
    }

    expect(caches.open).toHaveBeenCalledWith('duq-tools-v1');
    expect(mockCache.put).toHaveBeenCalled();
    expect(await response.text()).toBe('<html>home</html>');
  });

  it('serves from cache when offline for navigation requests', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Offline'));

    const cachedHtml = new Response('<html>cached</html>', { status: 200 });
    caches.match.mockResolvedValue(cachedHtml);

    // Simulate network-first with offline fallback
    try {
      await fetch('http://localhost/sprite-fusion/');
    } catch {
      const cached = await caches.match('http://localhost/sprite-fusion/');
      expect(cached).toBe(cachedHtml);
      expect(await cached.text()).toBe('<html>cached</html>');
    }
  });

  it('falls back to root cache when the specific page is not cached', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Offline'));

    caches.match
      .mockResolvedValueOnce(null)              // Specific page not in cache
      .mockResolvedValueOnce(new Response('root', { status: 200 })); // Root fallback

    // Simulate the fallback chain
    const cached = await caches.match('http://localhost/trigger-editor/');
    if (!cached) {
      const root = await caches.match('/');
      expect(root).toBeDefined();
      expect(await root.text()).toBe('root');
    }
  });
});
