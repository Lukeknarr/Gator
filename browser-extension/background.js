// Background service worker for Gator browser extension
class GatorTracker {
  constructor() {
    this.apiUrl = 'https://gator-backend.railway.app';
    this.userToken = null;
    this.isEnabled = true;
    this.trackedPages = new Map();
    this.init();
  }

  async init() {
    // Load user token from storage
    const result = await chrome.storage.local.get(['gatorToken', 'gatorEnabled']);
    this.userToken = result.gatorToken;
    this.isEnabled = result.gatorEnabled !== false;

    // Set up event listeners
    this.setupEventListeners();
    
    // Start periodic sync
    this.startPeriodicSync();
  }

  setupEventListeners() {
    // Track tab updates
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && tab.url) {
        this.trackPageVisit(tab.url, tab.title);
      }
    });

    // Track tab activation
    chrome.tabs.onActivated.addListener(async (activeInfo) => {
      const tab = await chrome.tabs.get(activeInfo.tabId);
      if (tab.url) {
        this.trackPageFocus(tab.url);
      }
    });

    // Track extension installation/update
    chrome.runtime.onInstalled.addListener((details) => {
      if (details.reason === 'install') {
        this.showWelcomePage();
      }
    });

    // Handle messages from popup and content scripts
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
      return true; // Keep message channel open for async response
    });
  }

  async trackPageVisit(url, title) {
    if (!this.isEnabled || !this.userToken) return;

    const pageData = {
      url,
      title,
      timestamp: Date.now(),
      duration: 0,
      scrollDepth: 0,
      readingTime: 0
    };

    this.trackedPages.set(url, pageData);
    
    // Send to backend
    this.sendPageData(pageData);
  }

  async trackPageFocus(url) {
    if (!this.isEnabled || !this.userToken) return;

    const pageData = this.trackedPages.get(url);
    if (pageData) {
      pageData.lastFocus = Date.now();
      this.trackedPages.set(url, pageData);
    }
  }

  async sendPageData(pageData) {
    try {
      const response = await fetch(`${this.apiUrl}/passive-tracking`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.userToken}`
        },
        body: JSON.stringify({
          url: pageData.url,
          title: pageData.title,
          duration: pageData.duration,
          scroll_depth: pageData.scrollDepth,
          reading_time: pageData.readingTime,
          timestamp: pageData.timestamp
        })
      });

      if (!response.ok) {
        console.error('Failed to send page data:', response.status);
      }
    } catch (error) {
      console.error('Error sending page data:', error);
    }
  }

  async handleMessage(request, sender, sendResponse) {
    switch (request.type) {
      case 'AUTHENTICATE':
        await this.authenticateUser(request.token);
        sendResponse({ success: true });
        break;

      case 'TOGGLE_TRACKING':
        this.isEnabled = request.enabled;
        await chrome.storage.local.set({ gatorEnabled: this.isEnabled });
        sendResponse({ success: true });
        break;

      case 'GET_STATUS':
        sendResponse({
          isEnabled: this.isEnabled,
          isAuthenticated: !!this.userToken,
          trackedPagesCount: this.trackedPages.size
        });
        break;

      case 'UPDATE_PAGE_DATA':
        const pageData = this.trackedPages.get(request.url);
        if (pageData) {
          Object.assign(pageData, request.data);
          this.trackedPages.set(request.url, pageData);
          this.sendPageData(pageData);
        }
        sendResponse({ success: true });
        break;

      default:
        sendResponse({ error: 'Unknown message type' });
    }
  }

  async authenticateUser(token) {
    this.userToken = token;
    await chrome.storage.local.set({ gatorToken: token });
    
    // Test the token
    try {
      const response = await fetch(`${this.apiUrl}/user/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        console.log('User authenticated successfully');
      } else {
        console.error('Authentication failed');
        this.userToken = null;
        await chrome.storage.local.remove('gatorToken');
      }
    } catch (error) {
      console.error('Authentication error:', error);
    }
  }

  startPeriodicSync() {
    // Sync tracked pages every 5 minutes
    setInterval(() => {
      if (this.isEnabled && this.userToken) {
        this.syncTrackedPages();
      }
    }, 5 * 60 * 1000);
  }

  async syncTrackedPages() {
    const pages = Array.from(this.trackedPages.values());
    if (pages.length === 0) return;

    try {
      const response = await fetch(`${this.apiUrl}/passive-tracking/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.userToken}`
        },
        body: JSON.stringify({ pages })
      });

      if (response.ok) {
        // Clear synced pages
        this.trackedPages.clear();
      }
    } catch (error) {
      console.error('Error syncing pages:', error);
    }
  }

  showWelcomePage() {
    chrome.tabs.create({
      url: 'https://gator-app.vercel.app/welcome'
    });
  }
}

// Initialize the tracker
const tracker = new GatorTracker(); 