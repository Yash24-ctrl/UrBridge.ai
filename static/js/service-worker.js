// Service Worker for Push Notifications
// This service worker handles push notifications for the web application

const CACHE_NAME = 'push-notifications-v1';
const urlsToCache = [
  '/static/js/service-worker.js',
  '/static/css/styles.css'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  console.log('Service Worker: Installed');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activated');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache');
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});

// Push event - handle incoming push notifications
self.addEventListener('push', event => {
  console.log('Push event received:', event);
  
  let data = {};
  if (event.data) {
    data = event.data.json();
  }
  
  const title = data.title || 'Notification';
  const options = {
    body: data.message || 'You have a new notification',
    icon: '/static/neuronet-white-logo.jpg',
    badge: '/static/neuronet-white-logo.jpg',
    tag: 'push-notification',
    data: {
      url: data.url || '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click event - handle when user clicks on notification
self.addEventListener('notificationclick', event => {
  console.log('Notification clicked:', event);
  
  event.notification.close();
  
  // Open the URL associated with the notification
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});

// Message event - handle messages from the main application
self.addEventListener('message', event => {
  console.log('Message received in service worker:', event.data);
  
  if (event.data && event.data.command === 'skipWaiting') {
    self.skipWaiting();
  }
});