// content_script.js - Analyzes job pages and extracts job data

console.log('📄 Job Tracker content script loaded on:', window.location.href);

class JobPageAnalyzer {
  constructor() {
    this.jobData = null;
    this.isJobPage = false;

    this.extractors = {
      linkedin: this.extractLinkedIn.bind(this),
    }

    this.init();
  }

  init() {
    // listen for messages from popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
    });

    // auto-analyze page on load
    this.analyzePage();

    // re-analyze if page changes (for SPAs)
    this.observePageChanges();
  }

  observePageChanges () {

  }

  handleMessage(message, sender, sendResponse) {
    console.log('📨 Content script received message:', message);
    switch (message.action) {
        case 'analyzePage':
            this.analyzePage();
            sendResponse({
                isJobPage: this.isJobPage,
                jobData: this.jobData
            });
            break;
            
        case 'extractJobData':
            sendResponse({
                success: true,
                jobData: this.jobData
            });
            break;
            
        default:
            sendResponse({ success: false, error: 'Unknown action' });
    }

    return true; // Keep message channel open for async responses
  }

  cleanText(text) {
    if (!text) return '';
        
    return text
        .replace(/\s+/g, ' ')
        .replace(/\n+/g, ' ')
        .trim();
  }

  extractSalary() {
    const salaryPatterns = [
        /\$[\d,]+(?:\.\d{2})?(?:\s*-\s*\$[\d,]+(?:\.\d{2})?)?(?:\s*(?:per|\/)\s*(?:hour|hr|year|yr|annually))?/gi,
        /[\d,]+k?\s*-\s*[\d,]+k?(?:\s*(?:per|\/)\s*(?:hour|hr|year|yr|annually))?/gi
    ];

    const textToSearch = document.body.textContent || '';
    
    for (const pattern of salaryPatterns) {
        const matches = textToSearch.match(pattern);
        if (matches && matches.length > 0) {
            return matches[0].trim();
        }
    }

    return null;
  }

  extractWithSelectors(selectors) {
    const data = {};

    Object.keys(selectors).forEach(key => {
      const selectorList = selectors[key];
      let value = null;

      // try each selector until we find a match
      for(const selector of selectorList) {
        try {
          const element = document.querySelector(selector);
          if (element) {
            value = element.textContent?.trim();
            if (value && value.length > 0) {
              console.log(`✅ Found ${key}: "${value}" with selector: ${selector}`);
              break;
            }
          }
        } catch (error) {
          console.warn(`❌ Selector "${selector}" failed:`, error);
        }
      }
      if (value) {
        data[key] = this.cleanText(value);
      }
    });
    return data;
  }

  extractLinkedIn () {
    console.log('🔧 Using LinkedIn extractor');

    // wait a bit for dynamic content to load
    const selectors = {
      company: [
          '.jobs-unified-top-card__company-name a',
          '.job-details-jobs-unified-top-card__company-name a',
          '.jobs-unified-top-card__company-name',
          '.job-details-jobs-unified-top-card__company-name'
      ],
      position: [
          '.jobs-unified-top-card__job-title',
          '.job-details-jobs-unified-top-card__job-title',
          'h1.jobs-unified-top-card__job-title'
      ],
      location: [
          '.jobs-unified-top-card__bullet',
          '.job-details-jobs-unified-top-card__bullet',
          '.jobs-unified-top-card__primary-description'
      ],
      description: [
          '.jobs-description-content__text',
          '.jobs-box__html-content',
          '.jobs-description'
      ]
    };
    return this.extractWithSelectors(selectors);
  }

  getExtractorName(url) {
    if(url.includes('linkedin.com')) return 'linkedin';
    if(url.includes('indeed.com')) return 'indeed';
    if(url.includes('glassdoor.com')) return 'glassdoor';
    return 'generic';
  }

  notifyPop() {
    // try to notify popup about job data
    try {
      chrome.runtime.sendMessage({
        action: 'pageAnalyzed',
        isJobPage: this.isJobPage,
        jobData: this.jobData
      });
    } catch (error) {
      // popup might not be open, that's ok
      console.log('📢 Could not notify popup (likely not open)');
    }
  }

  analyzePage() {
    console.log('🔍 Analyzing page for job data...')

    const url = window.location.href.toLowerCase();

    let extractor = this.extractors.generic;

    // determine which extractor to use based on URL
    if (url.includes('linkedin.com')) {
      extractor = this.extractors.linkedin;
    }

    // extract job data
    try {
      const data = extractor();
      if(data && (data.company && data.position)) {
        this.jobData = {
          ...data,
          job_url: window.location.href,
          extracted_at: new Date().toISOString(),
          extractor_used: this.getExtractorName(url)
        };
        this.isJobPage = true;

        console.log('✅ Job data extracted:', this.jobData);

        // notify popup if it's open
        this.notifyPop();
      } else {
        this.isJobPage = false;
        this.jobData = null;
        console.log('❌ No job data found on this page');
      }
    } catch (error) {
      console.error('❌ Error extracting job data:', error);
      this.isJobPage = false;
      this.jobData = null; 
    }
    return {isJobPage: this.isJobPage, jobData: this.jobData};
  }
}


// initialize the analyzer
const jobAnalyzer = new JobPageAnalyzer();

// make it globally available for debugging
window.jobAnalyzer = jobAnalyzer;