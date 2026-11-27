/* Había una vez Orlando — funciona sin señal dentro del parque.
   Guarda la app la primera vez que se abre; después, si no hay conexión,
   la sirve desde el teléfono. Solo corre en el sitio propio (no en el visor de Claude). */
const CACHE = "habia-una-vez-orlando-v4-5";
const BASE = ["./", "index.html", "manifest.webmanifest", "marca/favicon.svg", "marca/logo-principal.svg", "marca/logo-invertido.svg", "marca/icono-192.png", "marca/icono-512.png", "marca/apple-touch-icon.png", "arte/primera-noche-640.webp", "arte/primera-noche-640.jpg"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  if (r.mode === "navigate"){
    // La página: primero la red (para tener lo último), y sin señal, la guardada.
    e.respondWith(fetch(r).then(res => { const c = res.clone(); caches.open(CACHE).then(k => k.put("index.html", c)); return res; }).catch(() => caches.match("index.html")));
    return;
  }
  // Imágenes, íconos y video: primero lo guardado, y se guarda lo nuevo.
  e.respondWith(caches.match(r).then(hit => hit || fetch(r).then(res => { if (res.ok && !r.headers.has("range")){ const c = res.clone(); caches.open(CACHE).then(k => k.put(r, c)); } return res; })));
});
