# backend/config/matching_config.py

"""
Configuration for the email-to-job matching system.
Adjust these settings based on your specific needs.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import os

@dataclass
class MatchingConfig:
    """Configuration for email-job matching algorithm"""
    
    # Time window for matching (how far back to look)
    time_window_days: int = 45
    
    # Confidence thresholds
    auto_update_threshold: float = 75.0  # Auto-update existing job if confidence >= this
    manual_review_threshold: float = 50.0  # Show as potential match if >= this
    
    # Company name matching
    company_exact_match_score: int = 50
    company_fuzzy_threshold: float = 0.7
    company_containment_score: int = 45  # When one company name contains another
    
    # Position matching  
    position_exact_match_score: int = 40
    position_fuzzy_threshold: float = 0.6
    position_keyword_bonus: int = 3  # Points per matching keyword
    
    # Email domain matching
    domain_exact_match_score: int = 30
    domain_hr_platforms_score: int = 15  # For known HR platforms
    
    # Subject line matching
    subject_company_bonus: int = 10
    subject_keyword_bonus: int = 2
    subject_max_score: int = 20
    
    # Recency bonuses
    recency_1_week: int = 10
    recency_2_weeks: int = 7
    recency_1_month: int = 5
    recency_older: int = 2
    
    # Known HR/recruitment platforms
    hr_domains: List[str] = None
    
    # Company name normalization rules
    company_suffixes_to_remove: List[str] = None
    
    # Position title noise words to ignore
    position_noise_words: List[str] = None
    
    # Status progression rules
    status_progression: List[str] = None
    terminal_statuses: List[str] = None
    
    def __post_init__(self):
        """Initialize default lists if not provided"""
        if self.hr_domains is None:
            self.hr_domains = [
                'greenhouse.io',
                'lever.co', 
                'workday.com',
                'bamboohr.com',
                'jobvite.com',
                'smartrecruiters.com',
                'recruiterbox.com',
                'breezy.hr',
                'ashbyhq.com',
                'teamtailor.com'
            ]
        
        if self.company_suffixes_to_remove is None:
            self.company_suffixes_to_remove = [
                'inc', 'llc', 'corp', 'corporation', 'company', 
                'ltd', 'limited', 'co', 'technologies', 'tech',
                'systems', 'solutions', 'services', 'group'
            ]
        
        if self.position_noise_words is None:
            self.position_noise_words = [
                'position', 'role', 'job', 'opening', 'opportunity',
                'candidate', 'professional', 'specialist', 'expert'
            ]
        
        if self.status_progression is None:
            self.status_progression = [
                'captured', 'applied', 'assessment', 'interview', 'offer', 'accepted'
            ]
        
        if self.terminal_statuses is None:
            self.terminal_statuses = ['rejected', 'withdrawn', 'accepted']

    def get_confidence_level(self, score: float) -> str:
        """Get human-readable confidence level"""
        if score >= self.auto_update_threshold:
            return "high"
        elif score >= self.manual_review_threshold:
            return "medium"
        else:
            return "low"
    
    def should_auto_update(self, score: float) -> bool:
        """Check if score is high enough for automatic update"""
        return score >= self.auto_update_threshold
    
    def should_suggest_match(self, score: float) -> bool:
        """Check if score warrants manual review"""
        return score >= self.manual_review_threshold


# Environment-based configuration
def get_matching_config() -> MatchingConfig:
    """Get configuration based on environment variables"""
    config = MatchingConfig()
    
    # Override from environment variables
    config.time_window_days = int(os.getenv('MATCHING_TIME_WINDOW_DAYS', 45))
    config.auto_update_threshold = float(os.getenv('MATCHING_AUTO_THRESHOLD', 75.0))
    config.manual_review_threshold = float(os.getenv('MATCHING_MANUAL_THRESHOLD', 50.0))
    
    # Debug mode - lower thresholds for testing
    if os.getenv('MATCHING_DEBUG_MODE', 'false').lower() == 'true':
        config.auto_update_threshold = 60.0
        config.manual_review_threshold = 30.0
        print("🐛 Debug mode: Using lower matching thresholds")
    
    return config


# Pre-configured setups for different use cases
class MatchingPresets:
    """Pre-configured matching settings for different scenarios"""
    
    @staticmethod
    def conservative() -> MatchingConfig:
        """Conservative matching - fewer false positives"""
        config = MatchingConfig()
        config.auto_update_threshold = 85.0
        config.manual_review_threshold = 65.0
        config.company_fuzzy_threshold = 0.8
        config.position_fuzzy_threshold = 0.7
        return config
    
    @staticmethod
    def aggressive() -> MatchingConfig:
        """Aggressive matching - more matches, potentially more false positives"""
        config = MatchingConfig()
        config.auto_update_threshold = 65.0
        config.manual_review_threshold = 40.0
        config.company_fuzzy_threshold = 0.6
        config.position_fuzzy_threshold = 0.5
        return config
    
    @staticmethod
    def balanced() -> MatchingConfig:
        """Balanced matching - default settings"""
        return MatchingConfig()


# Company-specific matching rules
COMPANY_MATCHING_RULES = {
    # Handle common company name variations
    'google': ['google', 'google llc', 'alphabet', 'alphabet inc'],
    'microsoft': ['microsoft', 'microsoft corporation', 'msft'],
    'amazon': ['amazon', 'amazon.com', 'amazon web services', 'aws'],
    'meta': ['meta', 'facebook', 'meta platforms'],
    'apple': ['apple', 'apple inc'],
    
    # Consulting firms
    'mckinsey': ['mckinsey', 'mckinsey & company', 'mckinsey & co'],
    'bain': ['bain', 'bain & company', 'bain & co'],
    'bcg': ['bcg', 'boston consulting group', 'boston consulting'],
    
    # Banks
    'goldman sachs': ['goldman sachs', 'goldman', 'gs'],
    'morgan stanley': ['morgan stanley', 'ms'],
    'jp morgan': ['jp morgan', 'jpmorgan', 'jpmorgan chase'],
}

# Position title standardization
POSITION_STANDARDIZATION = {
    'software engineer': [
        'software engineer', 'software developer', 'swe', 
        'backend engineer', 'frontend engineer', 'full stack engineer',
        'senior software engineer', 'staff software engineer'
    ],
    'data scientist': [
        'data scientist', 'ds', 'senior data scientist',
        'machine learning engineer', 'ml engineer'
    ],
    'product manager': [
        'product manager', 'pm', 'senior product manager', 
        'associate product manager', 'apm'
    ],
    'business analyst': [
        'business analyst', 'ba', 'senior business analyst'
    ]
}

# Email patterns that indicate job communications
JOB_EMAIL_PATTERNS = {
    'application_confirmation': [
        'application received', 'thank you for applying', 'application confirmation',
        'we have received your application', 'application submitted'
    ],
    'assessment_invitation': [
        'coding challenge', 'technical assessment', 'online assessment',
        'take home assignment', 'coding test', 'technical test'
    ],
    'interview_invitation': [
        'interview', 'phone screen', 'video call', 'meeting request',
        'schedule', 'calendar', 'interview invitation'
    ],
    'offer': [
        'offer', 'congratulations', 'job offer', 'offer letter',
        'welcome to', 'we are pleased to offer'
    ],
    'rejection': [
        'regret to inform', 'not moving forward', 'other candidates',
        'decision not to proceed', 'thank you for your interest',
        'will not be moving forward'
    ]
}

# Load configuration
matching_config = get_matching_config()