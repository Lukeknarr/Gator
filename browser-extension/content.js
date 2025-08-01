// Content script for Gator browser extension
class GatorContentTracker {
  constructor() {
    this.startTime = Date.now();
    this.scrollDepth = 0;
    this.maxScrollDepth = 0;
    this.readingTime = 0;
    this.isActive = true;
    this.lastActivity = Date.now();
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.startTracking();
  }

  setupEventListeners() {
    // Track scroll depth
    window.addEventListener('scroll', () => {
      this.updateScrollDepth();
      this.updateActivity();
    });

    // Track mouse movement
    document.addEventListener('mousemove', () => {
      this.updateActivity();
    });

    // Track keyboard activity
    document.addEventListener('keydown', () => {
      this.updateActivity();
    });

    // Track clicks
    document.addEventListener('click', () => {
      this.updateActivity();
    });

    // Track page visibility
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.isActive = false;
      } else {
        this.isActive = true;
        this.updateActivity();
      }
    });

    // Track before page unload
    window.addEventListener('beforeunload', () => {
      this.sendFinalData();
    });
  }

  updateScrollDepth() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    
    if (scrollHeight > 0) {
      this.scrollDepth = Math.round((scrollTop / scrollHeight) * 100);
      this.maxScrollDepth = Math.max(this.maxScrollDepth, this.scrollDepth);
    }
  }

  updateActivity() {
    this.lastActivity = Date.now();
  }

  startTracking() {
    // Update reading time every second
    setInterval(() => {
      if (this.isActive && !document.hidden) {
        this.readingTime += 1;
      }
    }, 1000);

    // Send periodic updates
    setInterval(() => {
      this.sendPageData();
    }, 30000); // Every 30 seconds
  }

  sendPageData() {
    const pageData = {
      url: window.location.href,
      title: document.title,
      duration: Math.floor((Date.now() - this.startTime) / 1000),
      scrollDepth: this.maxScrollDepth,
      readingTime: this.readingTime,
      timestamp: Date.now()
    };

    chrome.runtime.sendMessage({
      type: 'UPDATE_PAGE_DATA',
      url: window.location.href,
      data: pageData
    });
  }

  sendFinalData() {
    const pageData = {
      url: window.location.href,
      title: document.title,
      duration: Math.floor((Date.now() - this.startTime) / 1000),
      scrollDepth: this.maxScrollDepth,
      readingTime: this.readingTime,
      timestamp: Date.now()
    };

    // Send final data before page unload
    chrome.runtime.sendMessage({
      type: 'UPDATE_PAGE_DATA',
      url: window.location.href,
      data: pageData
    });
  }

  // Extract text content for analysis
  extractPageContent() {
    const content = {
      title: document.title,
      description: this.getMetaDescription(),
      keywords: this.getMetaKeywords(),
      mainContent: this.getMainContent(),
      links: this.getLinks()
    };

    return content;
  }

  getMetaDescription() {
    const meta = document.querySelector('meta[name="description"]');
    return meta ? meta.getAttribute('content') : '';
  }

  getMetaKeywords() {
    const meta = document.querySelector('meta[name="keywords"]');
    return meta ? meta.getAttribute('content') : '';
  }

  getMainContent() {
    // Try to find main content area
    const main = document.querySelector('main, article, .content, .post, .entry');
    if (main) {
      return main.textContent.trim();
    }

    // Fallback to body content
    const body = document.body;
    if (body) {
      return body.textContent.trim();
    }

    return '';
  }

  getLinks() {
    const links = Array.from(document.querySelectorAll('a[href]'));
    return links.map(link => ({
      text: link.textContent.trim(),
      href: link.href,
      title: link.title
    })).filter(link => link.text && link.href);
  }
}

// Initialize content tracker
const tracker = new GatorContentTracker();

// Send page content for analysis
setTimeout(() => {
  const content = tracker.extractPageContent();
  chrome.runtime.sendMessage({
    type: 'PAGE_CONTENT',
    url: window.location.href,
    content: content
  });
}, 2000); // Wait 2 seconds for page to load 