// background.js - Service worker for browser extension

console.log('🚀 Job Tracker background script loaded');

class JobTrackerBackground {
  constructor() {
      this.backendUrl = 'http://localhost:8000';
      this.isMonitoring = false;
      
      this.init();
  }

  init() {
      console.log('🎯 Initializing Job Tracker background service');

      // Set up event listeners
      this.setupEventListeners();
      
      // Initialize extension state
      this.initializeState();
  }

  setupEventListeners() {
      // Extension installation/startup
      chrome.runtime.onInstalled.addListener((details) => {
          this.handleInstall(details);
      });

      // Handle messages from content scripts and popup
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
          this.handleMessage(message, sender, sendResponse);
          return true; // Keep message channel open for async responses
      });

      // Handle tab updates (when user navigates)
      chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
          this.handleTabUpdate(tabId, changeInfo, tab);
      });

      // Handle browser action (extension icon) clicks
      chrome.action.onClicked.addListener((tab) => {
          this.handleActionClick(tab);
      });

      // Handle alarms (for periodic tasks)
      chrome.alarms.onAlarm.addListener((alarm) => {
          this.handleAlarm(alarm);
      });
  }

  async initializeState() {
      try {
          // Set default title
          await chrome.action.setTitle({
              title: "Smart Job Tracker"
          });

          // Load stored settings
          const result = await chrome.storage.local.get([
              'isEnabled',
              'todayCount',
              'lastCheck'
          ]);

          console.log('💾 Loaded extension state:', result);

          // Initialize counters if not exists
          if (result.todayCount === undefined) {
              await chrome.storage.local.set({
                  todayCount: 0,
                  lastCheck: new Date().toDateString()
              });
          }

          // Reset daily counter if it's a new day
          const today = new Date().toDateString();
          if (result.lastCheck !== today) {
              await chrome.storage.local.set({
                  todayCount: 0,
                  lastCheck: today
              });
              console.log('🗓️ Reset daily counter for new day');
          }

      } catch (error) {
          console.error('❌ Error initializing state:', error);
      }
  }

  handleInstall(details) {
      console.log('🎉 Extension installed/updated:', details);

      if (details.reason === 'install') {
          // First installation
          this.showWelcomeNotification();
          this.openOnboarding();
      } else if (details.reason === 'update') {
          // Extension updated
          console.log(`📦 Extension updated to version ${chrome.runtime.getManifest().version}`);
      }
  }

  async handleMessage(message, sender, sendResponse) {
      console.log('📨 Background received message:', message);

      try {
          switch (message.action) {
              case 'captureJob':
                  await this.captureJob(message.jobData);
                  sendResponse({ success: true });
                  break;

              case 'checkBackendConnection':
                  const isConnected = await this.checkBackendConnection();
                  sendResponse({ connected: isConnected });
                  break;

              case 'getTodayCount':
                  const count = await this.getTodayCount();
                  sendResponse({ count });
                  break;

              case 'incrementTodayCount':
                  await this.incrementTodayCount();
                  const newCount = await this.getTodayCount();
                  sendResponse({ count: newCount });
                  break;

              case 'pageAnalyzed':
                  // Content script notifies about page analysis
                  // This is informational, no action needed in background
                  console.log('📄 Page analyzed:', message.isJobPage ? 'Job page detected' : 'Not a job page');
                  sendResponse({ success: true, acknowledged: true });
                  break;

              default:
                  console.warn('❓ Unknown message action:', message.action);
                  sendResponse({ success: false, error: 'Unknown action' });
          }
      } catch (error) {
          console.error('❌ Error handling message:', error);
          sendResponse({ success: false, error: error.message });
      }
  }

  async handleTabUpdate(tabId, changeInfo, tab) {
      // Only process when page is completely loaded
      if (changeInfo.status !== 'complete' || !tab.url) {
          return;
      }

      // Check if it's a job site
      const isJobSite = this.isJobSiteUrl(tab.url);
      
      if (isJobSite) {
          console.log('🔍 Job site detected:', tab.url);
          
          // Update badge to indicate job site
          await chrome.action.setBadgeText({
              tabId: tabId,
              text: '●'
          });
          
          await chrome.action.setBadgeBackgroundColor({
              tabId: tabId,
              color: '#10b981'
          });
          
          // Update title
          await chrome.action.setTitle({
              tabId: tabId,
              title: 'Job site detected - Click to capture job'
          });
      } else {
          // Clear badge for non-job sites
          await chrome.action.setBadgeText({
              tabId: tabId,
              text: ''
          });
          
          await chrome.action.setTitle({
              tabId: tabId,
              title: 'Smart Job Tracker'
          });
      }
  }

  handleActionClick(tab) {
      console.log('🖱️ Extension icon clicked on tab:', tab.url);
      
      // The popup will open automatically due to manifest.json configuration
      // This handler is mainly for cases where popup is disabled
  }

  handleAlarm(alarm) {
      console.log('⏰ Alarm triggered:', alarm.name);
      
      switch (alarm.name) {
          case 'dailyReset':
              this.resetDailyCounters();
              break;
          case 'backendSync':
              this.syncWithBackend();
              break;
      }
  }

  isJobSiteUrl(url) {
      const jobSites = [
          'linkedin.com/jobs',
          'indeed.com/viewjob',
          'glassdoor.com/job',
          'monster.com/job',
          'ziprecruiter.com/jobs',
          'careers.',
          'jobs.'
      ];

      return jobSites.some(site => url.toLowerCase().includes(site));
  }

  async checkBackendConnection() {
      try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 3000);

          const response = await fetch(`${this.backendUrl}/api/monitor/status`, {
              method: 'GET',
              signal: controller.signal
          });

          clearTimeout(timeoutId);
          return response.ok;
      } catch (error) {
          console.log('🔌 Backend connection check failed:', error.message);
          return false;
      }
  }

  async captureJob(jobData) {
      try {
          console.log('📤 Capturing job data:', jobData);

          const response = await fetch(`${this.backendUrl}/api/jobs/capture`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify(jobData)
          });

          if (response.ok) {
              const result = await response.json();
              console.log('✅ Job captured successfully:', result);
              
              await this.incrementTodayCount();
              this.showCaptureNotification(jobData);
              
              return result;
          } else {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to capture job');
          }
      } catch (error) {
          console.error('❌ Error capturing job:', error);
          throw error;
      }
  }

  async getTodayCount() {
      const result = await chrome.storage.local.get(['todayCount']);
      return result.todayCount || 0;
  }

  async incrementTodayCount() {
      const current = await this.getTodayCount();
      await chrome.storage.local.set({ 
          todayCount: current + 1,
          lastCapture: new Date().toISOString()
      });
      
      // Update badge with count
      const newCount = current + 1;
      await chrome.action.setBadgeText({
          text: newCount.toString()
      });
      
      await chrome.action.setBadgeBackgroundColor({
          color: '#3b82f6'
      });
  }

  async resetDailyCounters() {
      console.log('🗓️ Resetting daily counters');
      
      await chrome.storage.local.set({
          todayCount: 0,
          lastCheck: new Date().toDateString()
      });
      
      await chrome.action.setBadgeText({ text: '' });
  }

  async syncWithBackend() {
      console.log('🔄 Syncing with backend...');
      
      try {
          const response = await fetch(`${this.backendUrl}/api/statistics`);
          if (response.ok) {
              const stats = await response.json();
              
              // Update local storage with backend stats
              await chrome.storage.local.set({
                  backendStats: stats,
                  lastSync: new Date().toISOString()
              });
              
              console.log('✅ Backend sync successful');
          }
      } catch (error) {
          console.log('❌ Backend sync failed:', error);
      }
  }

  showWelcomeNotification() {
      if (chrome.notifications) {
          chrome.notifications.create('welcome', {
              type: 'basic',
              iconUrl: 'icons/icon48.png',
              title: 'Smart Job Tracker Installed!',
              message: 'Visit job sites and click the extension to start capturing applications.'
          });
      }
  }

  showCaptureNotification(jobData) {
      if (chrome.notifications) {
          chrome.notifications.create('capture-success', {
              type: 'basic',
              iconUrl: 'icons/icon48.png',
              title: 'Job Captured!',
              message: `${jobData.company} - ${jobData.position}`
          });
      }
  }

  openOnboarding() {
      // Open the dashboard for first-time setup
      chrome.tabs.create({
          url: this.backendUrl
      });
  }

  // Setup periodic alarms
  async setupAlarms() {
      // Daily reset at midnight
      chrome.alarms.create('dailyReset', {
          when: this.getNextMidnight(),
          periodInMinutes: 24 * 60 // Daily
      });

      // Backend sync every 15 minutes
      chrome.alarms.create('backendSync', {
          delayInMinutes: 1,
          periodInMinutes: 15
      });
  }

  getNextMidnight() {
      const now = new Date();
      const midnight = new Date(now);
      midnight.setDate(midnight.getDate() + 1);
      midnight.setHours(0, 0, 0, 0);
      return midnight.getTime();
  }
}

// Initialize background service
const jobTrackerBackground = new JobTrackerBackground();

// Setup alarms after initialization
jobTrackerBackground.setupAlarms();