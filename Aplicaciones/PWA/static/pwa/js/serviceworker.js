self.addEventListener('install', function (e) {
    console.log('✅ [SW] Instalado');
    self.skipWaiting();
});

self.addEventListener('activate', function (e) {
    console.log('✅ [SW] Activado');
    return self.clients.claim();
});

self.addEventListener('fetch', function (event) {
    console.log('📦 [SW] Interceptando: ', event.request.url);
});
