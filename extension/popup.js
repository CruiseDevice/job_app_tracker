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
    console.log('🚀 Job Tracker popup initializing...');

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

    // TODO: dashboard button
    this.elements.openDashboard.addEventListener('click', () => {
      chrome.tabs.create({url: this.backendUrl});
    });

    // TODO: Listen for messages from content script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
    });
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
      const response = await fetch(`${this.backendUrl}/api/statistics`);
      if (response.ok) {
          const stats = await response.json();
          this.elements.todayCount.textContent = stats.today || 0;
      }
    } catch (error) {
      console.error('Error fetching today count:', error);
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
      //TODO: prepate job data for backend
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

      console.log('📤 Sending job data to backend:', jobData);

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
        console.log('✅ Job captured successfully:', result);
        
        this.showMessage(`Successfully captured: ${jobData.company} - ${jobData.position}`, 'success');
        this.updateLastCapture(jobData);
        await this.updateTodayCount();
        
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
      console.log('🔗 Attempting to connect to:', url);
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
        console.log('✅ Backend connection successful')
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
        console.log('📄 Content script not available, analyzing URL...');
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