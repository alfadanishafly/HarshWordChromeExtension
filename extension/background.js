// background.js
// Chrome Extension Background Service Worker

'use strict';

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background script received message:', request);

  if (request.message === 'checkHatespeech') {
    // Handle hate speech check notification
    console.log('Checking for hate speech...');
  }

  if (request.message === 'hatespeechResult' && request.isHatespeech) {
    // Show notification when hate speech is detected
    showNotification();
  }

  return true;
});

/**
 * Show a browser notification when hate speech is detected
 */
function showNotification() {
  if (!chrome.notifications) {
    console.log('Notifications not available');
    return;
  }

  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon.png',
    title: 'Hate Speech Detected',
    message: 'Potentially harmful content has been censored on this page.',
    priority: 2
  }, (notificationId) => {
    console.log('Notification created:', notificationId);
  });
}

// Optional: Listen for web requests (currently disabled - was blocking all requests)
// Uncomment and modify if you need specific request filtering
/*
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    // Add custom filtering logic here
    console.log('Web request intercepted:', details.url);
    return {}; // Don't block by default
  },
  {
    urls: ["<all_urls>"]
  },
  ["blocking"]
);
*/
