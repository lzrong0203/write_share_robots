// Firebase Messaging Service Worker

// 添加調試信息
console.log('[firebase-messaging-sw.js] Service Worker 已加載');

// 導入 Firebase 腳本
importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-messaging.js');

// 初始化 Firebase
// 需要替換成自己的 config
firebase.initializeApp({
  apiKey: "",
  authDomain: "",
  projectId: "",
  storageBucket: "",
  messagingSenderId: "",
  appId: "",
  databaseURL: ""
});

console.log('[firebase-messaging-sw.js] Firebase 已初始化');

// 獲取 Messaging 實例
const messaging = firebase.messaging();
console.log('[firebase-messaging-sw.js] Messaging 實例已獲取');

// 設置後台通知處理
messaging.setBackgroundMessageHandler(function(payload) {
  console.log('[firebase-messaging-sw.js] 收到後台消息 ', payload);
  
  // 自定義通知選項
  const notificationTitle = payload.notification?.title || '情緒分析通知';
  const notificationOptions = {
    body: payload.notification?.body || '收到新的情緒分析數據',
    icon: '/static/img/notification-icon.png',
    data: payload.data || {}
  };

  console.log('[firebase-messaging-sw.js] 顯示通知: ', notificationTitle, notificationOptions);

  // 顯示通知
  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// 監聽通知點擊事件
self.addEventListener('notificationclick', function(event) {
  console.log('[firebase-messaging-sw.js] 通知被點擊', event);
  
  // 關閉通知
  event.notification.close();
  
  // 打開主頁面
  event.waitUntil(
    clients.openWindow('/')
  );
});

// 監聽 Service Worker 安裝事件
self.addEventListener('install', function(event) {
  console.log('[firebase-messaging-sw.js] Service Worker 已安裝');
  self.skipWaiting();
});

// 監聽 Service Worker 激活事件
self.addEventListener('activate', function(event) {
  console.log('[firebase-messaging-sw.js] Service Worker 已激活');
  event.waitUntil(clients.claim());
});

// 監聽 push 事件
self.addEventListener('push', function(event) {
  console.log('[firebase-messaging-sw.js] 收到推送事件', event);
  
  if (event.data) {
    try {
      const data = event.data.json();
      console.log('[firebase-messaging-sw.js] 推送數據:', data);
      
      // 顯示通知
      const title = data.notification?.title || '情緒分析通知';
      const options = {
        body: data.notification?.body || '收到新的情緒分析數據',
        icon: '/static/img/notification-icon.png',
        data: data.data || {}
      };
      
      event.waitUntil(
        self.registration.showNotification(title, options)
      );
    } catch (e) {
      console.error('[firebase-messaging-sw.js] 處理推送數據時出錯:', e);
      
      // 嘗試顯示一個基本通知
      event.waitUntil(
        self.registration.showNotification('情緒分析通知', {
          body: '收到新的通知，但無法解析詳細內容',
          icon: '/static/img/notification-icon.png'
        })
      );
    }
  } else {
    console.log('[firebase-messaging-sw.js] 收到空的推送事件');
    
    // 顯示一個基本通知
    event.waitUntil(
      self.registration.showNotification('情緒分析通知', {
        body: '收到新的通知',
        icon: '/static/img/notification-icon.png'
      })
    );
  }
}); 