class JobTrackerPopup {
  constructor() {
    this.elements = {
      captureBtn: document.getElementById('captureBtn'),
      openDashboard: document.getElementById('openDashboard'),
      captureLoading: document.getElementById('captureLoading'),
      statusText: document.getElementById('statusText'),
      statusDot: document.getElementById('statusDot'),
      pageType: document.getElementById('pageType'),
      pageStatus: document.getElementById('pageStatus'),
      messageText: document.getElementById('messageText'),
      messageArea: document.getElementById('messageArea'),
      lastCompany: document.getElementById('lastCompany'),
      lastPosition: document.getElementById('lastPosition'),
      lastTimestamp: document.getElementById('lastTimestamp'),
      lastCapture: document.getElementById('lastCapture'),
      todayCount: document.getElementById('todayCount'),
    }

    this.backendUrl = 'http://localhost:8000';
    this.currentPageData = null;
    this.isCapturing = false;

    this.init();
  }

  async init() {
    // Verify all elements are found
    console.log('🔍 Initializing popup, checking elements...');
    console.log('📋 todayCount element:', this.elements.todayCount);
    if (!this.elements.todayCount) {
      console.error('❌ CRITICAL: todayCount element not found!');
      console.error('📋 Available elements:', Object.keys(this.elements));
    } else {
      console.log('✅ todayCount element found:', this.elements.todayCount);
      console.log('📋 Current value:', this.elements.todayCount.textContent);
    }
    
    // set up event listeners
    this.setupEventListeners();

    // check backend connection
    await this.checkBackendConnection();

    // update today's count
    await this.updateTodayCount();

    // analyze current page
    await this.analyzeCurrentPage();
    
  }

  setupEventListeners() {
    // capture button
    this.elements.captureBtn.addEventListener('click', () => {
      this.captureJob();
    })

    // Dashboard button
    this.elements.openDashboard.addEventListener('click', () => {
      chrome.tabs.create({url: this.backendUrl});
    });

    // Listen for messages from content script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async responses
    });
  }

  handleMessage(message, sender, sendResponse) {
    // Handle messages from content script or background
    switch (message.action) {
      case 'pageAnalyzed':
        // Content script analyzed the page - update popup if open
        if (message.isJobPage && message.jobData) {
          this.currentPageData = message.jobData;
          this.updatePageStatus(`Job page detected: ${message.jobData.company || 'Unknown Company'}`, true);
          this.elements.captureBtn.disabled = false;
        }
        sendResponse({ success: true });
        break;
      default:
        // Unknown message, ignore
        sendResponse({ success: false });
    }
  }

  showMessage(text, type='info') {
    this.elements.messageText.textContent = text;
    this.elements.messageArea.className = `message ${type}`;
    this.elements.messageArea.style.display = 'block';

    // auto-hide after 5 seconds
    setTimeout(() => {
      this.elements.messageArea.style.display = 'none';
    }, 5000);
  }

  updateCaptureButton(isLoading) {
    if(isLoading) {
      this.elements.captureBtn.disabled = true;
      this.elements.captureLoading.classList.add('visible');
    } else {
      this.elements.captureBtn.disabled = !this.currentPageData;
      this.elements.captureLoading.classList.remove('visible');
    }
  }

  getJobBoard(url) {
    if(!url) return 'Unknown';

    const urlLower = url.toLowerCase();

    if(urlLower.includes('linkedin.com')) return 'LinkedIn';
    
  }

  updateLastCapture(jobData) {
    this.elements.lastCompany.textContent = jobData.company;
    this.elements.lastPosition.textContent = jobData.position;
    this.elements.lastTimestamp.textContent = new Date().toLocaleString();
    this.elements.lastCapture.style.display = 'block';

    // store in chrome storage
    chrome.storage.local.set({
      lastCapture: {
        company: jobData.company,
        position: jobData.position,
        timestamp: new Date().toISOString()
      }
    })
  }

  async updateTodayCount() {
    try {
      // Verify element exists
      if (!this.elements.todayCount) {
        console.error('❌ todayCount element not found in updateTodayCount!');
        return;
      }
      
      console.log('🔄 Fetching statistics from API...');
      const response = await fetch(`${this.backendUrl}/api/statistics`);
      if (response.ok) {
          const stats = await response.json();
          const count = stats.today || 0;
          console.log('📊 Statistics from API:', stats);
          console.log('🔢 Today count:', count);
          console.log('🎯 Element before update:', this.elements.todayCount.textContent);
          this.elements.todayCount.textContent = count.toString();
          console.log('🎯 Element after update:', this.elements.todayCount.textContent);
          console.log('✅ Updated today count to:', count);
      } else {
          console.error('❌ Failed to fetch statistics:', response.status, response.statusText);
          const errorText = await response.text();
          console.error('❌ Error response:', errorText);
      }
    } catch (error) {
      console.error('❌ Error fetching today count:', error);
    }
  }

  async captureJob () {
    if (this.isCapturing) return;

    if (!this.currentPageData) {
      this.showMessage('No job data found to capture', 'error');
      return
    }

    this.isCapturing = true;
    this.updateCaptureButton(true);

    try {
      // Prepare job data for backend
      const jobData = {
        company: this.currentPageData.company || 'Unknown Company',
        position: this.currentPageData.position || 'Unknown Position',
        job_url: this.currentPageData.job_url || window.location.href,
        location: this.currentPageData.location || '',
        job_description: this.currentPageData.description || '',
        salary_range: this.currentPageData.salary || '',
        job_board: this.getJobBoard(this.currentPageData.job_url),
        captured_at: new Date().toISOString(),
        extraction_data: JSON.stringify(this.currentPageData)
      }

      // Send to backend
      const response = await fetch(`${this.backendUrl}/api/jobs/capture`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jobData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('📥 Capture response:', result);
        console.log('📦 Full response structure:', JSON.stringify(result, null, 2));
        
        this.showMessage(`Successfully captured: ${jobData.company} - ${jobData.position}`, 'success');
        this.updateLastCapture(jobData);
        
        // Verify element exists
        if (!this.elements.todayCount) {
          console.error('❌ todayCount element not found!');
          return;
        }
        
        // Update count from response if available, otherwise fetch
        let countUpdated = false;
        if (result && result.data && result.data.statistics) {
          const count = result.data.statistics.today || 0;
          console.log('📊 Statistics from response:', result.data.statistics);
          console.log('🔢 Today count from statistics:', count);
          console.log('🎯 Element before update:', this.elements.todayCount.textContent);
          this.elements.todayCount.textContent = count.toString();
          console.log('🎯 Element after update:', this.elements.todayCount.textContent);
          console.log('✅ Updated today count from response:', count);
          countUpdated = true;
        } else {
          console.warn('⚠️ No statistics in response, checking structure...');
          console.log('📦 result:', result);
          console.log('📦 result.data:', result?.data);
          console.log('📦 result.data?.statistics:', result?.data?.statistics);
        }
        
        // Fallback: fetch statistics if not in response or update failed
        if (!countUpdated) {
          console.log('🔄 Fetching statistics separately...');
          await this.updateTodayCount();
        }
        
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to capture job');
      }


    } catch (error) {
      console.error('❌ Error capturing job:', error);
      this.showMessage(`Failed to capture job: ${error.message}`, 'error');
    } finally {
      this.isCapturing = false;
      this.updateCaptureButton(false);
    }
  }

  updateConnectionStatus(status, text) {
    this.elements.statusText.textContent = text;
    this.elements.statusDot.className = `status-dot ${status}`;
  }

  async checkBackendConnection() {
    this.updateConnectionStatus('connecting', 'Connecting...');

    try {
      const url = `${this.backendUrl}/api/monitor/status`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: AbortSignal.timeout(5000) // 5 second timeout
      }); 

      if (response.ok) {
        const data = await response.json();
        this.updateConnectionStatus('connected', 'Connected');
      }
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      this.updateConnectionStatus('disconnected', 'Disconnected')
    } 
  }

  updatePageStatus(text, isJobPage) {
    this.elements.pageType.textContent = text;
    this.elements.pageStatus.className = `page-status ${isJobPage ? 'job-page' : 'not-job-page'}`
  }

  analyzeUrlOnly(url) {
    const jobSites = [
      'linkedin.com/jobs',
      'indeed.com/viewjob',
      'glassdoor.com/job',
      'monster.com/job',
      'ziprecruiter.com/jobs'
    ];

    const isJobSite = jobSites.some(site => url.includes(site))

    if (isJobSite) {
      this.updatePageStatus('Potential job page (install complete)', true);
      this.elements.captureBtn.disabled = false;

      // set basic page data from URL
      this.currentPageData = {
        job_url: url,
        company: 'Unknown',
        position: 'Unknown Position',
        source: 'url_analysis'
      };
    } else {
      this.updatePageStatus('Not a job site', false);
      this.elements.captureBtn.disabled = true;
    }
  }

  async analyzeCurrentPage() {
    try {
      // get current active tab
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

      if (!tab) {
        this.updatePageStatus('Unknown page', false);
        return;
      }

      // send message to content script to analyze page
      try {
        const response = await chrome.tabs.sendMessage(tab.id, {
          action: 'analyzePage'
        });

        if(response && response.isJobPage) {
          this.currentPageData = response.jobData;
          this.updatePageStatus(`Job page detected: ${response.jobData.company || 'Unknown Company'}`, true);
          this.elements.captureBtn.disabled = false;
        } else {
          this.updatePageStatus('Not a job page', false);
          this.elements.captureBtn.disabled = true;
        }

      } catch (error) {
        // Fallback: analyze URL if content script not available
        this.analyzeUrlOnly(tab.url);
      }

    } catch (error) {
      console.error('❌ Error analyzing current page:', error);
      this.updatePageStatus('Error analyzing page', false);
    }
  }
}

// initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new JobTrackerPopup();
})