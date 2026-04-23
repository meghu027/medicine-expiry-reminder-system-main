// MedNova Service Worker - Handling Background Notifications
const CACHE_NAME = 'mednova-v1';

// 1. Install Event - App ko offline ready banane ke liye
self.addEventListener('install', (event) => {
    self.skipWaiting();
    console.log("MedNova SW: Installed & Ready");
});

// 2. Activate Event
self.addEventListener('activate', (event) => {
    console.log("MedNova SW: System Activated");
    return self.clients.claim();
});

// 3. Notification Click Handling (WhatsApp style behavior)
self.addEventListener('notificationclick', (event) => {
    const action = event.action;
    const notification = event.notification;

    // Notification band karein
    notification.close();

    if (action === 'confirm') {
        // Yahan 'Taken' wala logic handle hoga
        console.log("User confirmed: Medicine Taken");
    } else if (action === 'snooze') {
        // Yahan Snooze logic call kar sakte hain
        console.log("User requested: 5 Min Snooze");
    }

    // App open karne ke liye agar user notification body par click kare
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(windowClients => {
            // Agar tab pehle se open hai toh uspar focus karein
            for (let i = 0; i < windowClients.length; i++) {
                let client = windowClients[i];
                if ('focus' in client) return client.focus();
            }
            // Agar tab band hai toh dashboard open karein
            if (clients.openWindow) return clients.openWindow('dashboard.html');
        })
    );
});

// 4. Background Push (Agar aap server use karein toh iska kaam hota hai)
self.addEventListener('push', (event) => {
    const data = event.data ? event.data.text() : 'Time for your medication!';
    event.waitUntil(
        self.registration.showNotification('MedNova Alert', {
            body: data,
            icon: 'https://cdn-icons-png.flaticon.com/512/883/883356.png',
            vibrate: [200, 100, 200]
        })
    );
});