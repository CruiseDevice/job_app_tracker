"""
Smart Email-Job Matching System

This module implements intelligent matching between job applications (captured via browser extension)
and email communications, using multiple criteria and confidence scoring.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MatchMethod(Enum):
    """Types of matching methods used"""
    COMPANY_EXACT = "company_exact"
    COMPANY_FUZZY = "company_fuzzy"
    DOMAIN_MATCH = "domain_match"
    POSITION_MATCH = "position_match"
    URL_MATCH = "url_match"
    KEYWORD_MATCH = "keyword_match"
    TIME_PROXIMITY = "time_proximity"

@dataclass
class MatchCriteria:
    """Configuration for matching criteria and weights"""
    company_exact_weight: float = 40.0          # Exact company name match
    company_fuzzy_weight: float = 25.0          # Fuzzy company name match  
    domain_match_weight: float = 20.0           # Email domain matches company
    position_match_weight: float = 15.0         # Job position mentioned in email
    url_match_weight: float = 35.0              # Job URL found in email
    keyword_match_weight: float = 10.0          # Job-related keywords
    time_proximity_weight: float = 8.0          # Temporal proximity bonus
    
    # Matching thresholds
    fuzzy_threshold: float = 0.8                # Minimum similarity for fuzzy matching
    time_window_days: int = 14                  # Days to look for related emails
    min_confidence: float = 30.0                # Minimum confidence to suggest match
    auto_link_confidence: float = 85.0          # Auto-link above this confidence

@dataclass  
class EmailJobMatch:
    """Represents a potential match between an email and job"""
    email_id: str
    job_id: int
    confidence_score: float
    match_methods: List[MatchMethod]
    match_details: Dict[str, Any]
    created_at: datetime
    is_verified: bool = False
    is_auto_linked: bool = False

class SmartEmailJobMatcher:
    """
    Intelligent system for matching emails with job applications
    """
    
    def __init__(self, db_manager, criteria: Optional[MatchCriteria] = None):
        self.db = db_manager
        self.criteria = criteria or MatchCriteria()
        
        # Company domain mappings for better matching
        self.company_domains = {
            'google': ['google.com', 'gmail.com', 'googlemail.com'],
            'microsoft': ['microsoft.com', 'msn.com', 'outlook.com', 'hotmail.com'],
            'meta': ['meta.com', 'facebook.com', 'fb.com', 'instagram.com'],
            'amazon': ['amazon.com', 'amazonaws.com'],
            'apple': ['apple.com', 'icloud.com'],
            'netflix': ['netflix.com'],
            'uber': ['uber.com'],
            'airbnb': ['airbnb.com'],
            'linkedin': ['linkedin.com'],
            'stripe': ['stripe.com'],
            'spotify': ['spotify.com'],
        }

    def find_matches_for_email(self, email_data: Dict[str, Any]) -> List[EmailJobMatch]:
        """
        Find potential job matches for a given email
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            List of EmailJobMatch objects sorted by confidence
        """
        logger.info(f"🔍 Finding matches for email: {email_data.get('subject', 'No Subject')}")
        
        try:
            # Get candidate jobs within time window
            candidate_jobs = self._get_candidate_jobs(email_data)
            
            if not candidate_jobs:
                logger.debug("No candidate jobs found in time window")
                return []
            
            logger.info(f"📋 Found {len(candidate_jobs)} candidate jobs to match against")
            
            matches = []
            for job in candidate_jobs:
                match = self._calculate_match(email_data, job)
                if match and match.confidence_score >= self.criteria.min_confidence:
                    matches.append(match)
                    logger.debug(f"   Match found: {job['company']} - {match.confidence_score:.1f}%")
            
            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"✅ Found {len(matches)} potential matches above {self.criteria.min_confidence}% confidence")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error finding email matches: {e}", exc_info=True)
            return []

    def find_matches_for_job(self, job_id: int) -> List[EmailJobMatch]:
        """
        Find potential email matches for a given job
        
        Args:
            job_id: ID of the job application
            
        Returns:
            List of EmailJobMatch objects sorted by confidence
        """
        logger.info(f"🔍 Finding email matches for job ID: {job_id}")
        
        try:
            # Get job details
            job = self.db.get_application(job_id)
            if not job:
                logger.warning(f"Job {job_id} not found")
                return []
            
            job_data = job.to_dict()
            
            # Get candidate emails within time window
            candidate_emails = self._get_candidate_emails(job_data)
            
            if not candidate_emails:
                logger.debug("No candidate emails found in time window")
                return []
            
            logger.info(f"📧 Found {len(candidate_emails)} candidate emails to match against")
            
            matches = []
            for email in candidate_emails:
                match = self._calculate_match(email, job_data)
                if match and match.confidence_score >= self.criteria.min_confidence:
                    matches.append(match)
                    logger.debug(f"   Match found: {email.get('subject', 'No Subject')} - {match.confidence_score:.1f}%")
            
            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"✅ Found {len(matches)} potential matches above {self.criteria.min_confidence}% confidence")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error finding job matches: {e}", exc_info=True)
            return []

    def _get_candidate_jobs(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get jobs within the matching time window"""
        try:
            # Parse email date
            email_date = self._parse_email_date(email_data.get('date', ''))
            if not email_date:
                email_date = datetime.now()
            
            # Define time window (look for jobs captured recently)
            start_time = email_date - timedelta(days=self.criteria.time_window_days)
            end_time = email_date + timedelta(days=1)  # Allow emails slightly before job capture
            
            # Get extension-captured jobs (these are the ones we want to match emails to)
            all_jobs = self.db.get_extension_jobs(limit=500)
            
            # Filter by time window
            candidate_jobs = []
            for job in all_jobs:
                job_date = job.captured_at or job.created_at
                if job_date and start_time <= job_date <= end_time:
                    candidate_jobs.append(job.to_dict())
            
            return candidate_jobs
            
        except Exception as e:
            logger.error(f"❌ Error getting candidate jobs: {e}")
            return []

    def _get_candidate_emails(self, job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get emails within the matching time window for a job"""
        try:
            # This would require integration with email storage system
            # For now, return empty list - will be implemented when email storage is enhanced
            logger.debug("Email candidate retrieval not yet implemented")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting candidate emails: {e}")
            return []

    def _calculate_match(self, email_data: Dict[str, Any], job_data: Dict[str, Any]) -> Optional[EmailJobMatch]:
        """
        Calculate match confidence between an email and job
        
        Args:
            email_data: Dictionary containing email information
            job_data: Dictionary containing job application information
            
        Returns:
            EmailJobMatch object or None if no significant match
        """
        try:
            email_id = email_data.get('id', email_data.get('email_id', 'unknown'))
            job_id = job_data.get('id')
            
            if not job_id:
                return None
            
            match_methods = []
            match_details = {}
            total_score = 0.0
            
            # 1. Company Name Matching
            company_score, company_method = self._match_company(email_data, job_data)
            if company_score > 0:
                total_score += company_score
                match_methods.append(company_method)
                match_details['company_score'] = company_score
            
            # 2. Domain Matching
            domain_score = self._match_domain(email_data, job_data)
            if domain_score > 0:
                total_score += domain_score
                match_methods.append(MatchMethod.DOMAIN_MATCH)
                match_details['domain_score'] = domain_score
            
            # 3. Position/Job Title Matching
            position_score = self._match_position(email_data, job_data)
            if position_score > 0:
                total_score += position_score
                match_methods.append(MatchMethod.POSITION_MATCH)
                match_details['position_score'] = position_score
            
            # 4. URL Matching
            url_score = self._match_url(email_data, job_data)
            if url_score > 0:
                total_score += url_score
                match_methods.append(MatchMethod.URL_MATCH)
                match_details['url_score'] = url_score
            
            # 5. Keyword Matching
            keyword_score = self._match_keywords(email_data, job_data)
            if keyword_score > 0:
                total_score += keyword_score
                match_methods.append(MatchMethod.KEYWORD_MATCH)
                match_details['keyword_score'] = keyword_score
            
            # 6. Time Proximity Bonus
            time_score = self._calculate_time_proximity(email_data, job_data)
            if time_score > 0:
                total_score += time_score
                match_methods.append(MatchMethod.TIME_PROXIMITY)
                match_details['time_score'] = time_score
            
            # Cap at 100%
            confidence_score = min(total_score, 100.0)
            
            if confidence_score >= self.criteria.min_confidence and match_methods:
                return EmailJobMatch(
                    email_id=email_id,
                    job_id=job_id,
                    confidence_score=confidence_score,
                    match_methods=match_methods,
                    match_details=match_details,
                    created_at=datetime.now(),
                    is_auto_linked=(confidence_score >= self.criteria.auto_link_confidence)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error calculating match: {e}", exc_info=True)
            return None

    def _match_company(self, email_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, MatchMethod]:
        """Match company names between email and job"""
        try:
            job_company = job_data.get('company', '').strip().lower()
            if not job_company:
                return 0.0, None
            
            email_content = self._get_email_searchable_content(email_data).lower()
            
            # Exact match in email content
            if job_company in email_content:
                return self.criteria.company_exact_weight, MatchMethod.COMPANY_EXACT
            
            # Fuzzy matching with company name variations
            company_variations = self._generate_company_variations(job_company)
            
            best_similarity = 0.0
            for variation in company_variations:
                if variation in email_content:
                    return self.criteria.company_exact_weight * 0.9, MatchMethod.COMPANY_EXACT
                
                # Check similarity with words in email
                for word in email_content.split():
                    if len(word) > 3:  # Skip short words
                        similarity = SequenceMatcher(None, variation, word).ratio()
                        best_similarity = max(best_similarity, similarity)
            
            # If fuzzy similarity is above threshold
            if best_similarity >= self.criteria.fuzzy_threshold:
                score = self.criteria.company_fuzzy_weight * best_similarity
                return score, MatchMethod.COMPANY_FUZZY
            
            return 0.0, None
            
        except Exception as e:
            logger.error(f"❌ Error in company matching: {e}")
            return 0.0, None

    def _match_domain(self, email_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Match email sender domain with company"""
        try:
            job_company = job_data.get('company', '').strip().lower()
            email_sender = email_data.get('sender', email_data.get('from', '')).lower()
            
            if not job_company or not email_sender:
                return 0.0
            
            # Extract domain from email
            domain_match = re.search(r'@([^>]*)', email_sender)
            if not domain_match:
                return 0.0
            
            sender_domain = domain_match.group(1).lower()
            
            # Check if company has known domains
            company_key = job_company.replace(' ', '').replace('.', '').replace(',', '')
            
            # Direct company domain match (e.g., google.com for Google)
            if company_key in sender_domain or sender_domain.startswith(company_key):
                return self.criteria.domain_match_weight
            
            # Check predefined company-domain mappings
            for company, domains in self.company_domains.items():
                if company in job_company:
                    if any(domain in sender_domain for domain in domains):
                        return self.criteria.domain_match_weight
            
            # Check for recruiting domains that mention company
            recruiting_domains = ['greenhouse.io', 'lever.co', 'workday.com', 'successfactors.com']
            if any(domain in sender_domain for domain in recruiting_domains):
                return self.criteria.domain_match_weight * 0.8
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error in domain matching: {e}")
            return 0.0

    def _match_position(self, email_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Match job position/title in email content"""
        try:
            job_position = job_data.get('position', '').strip().lower()
            if not job_position:
                return 0.0
            
            email_content = self._get_email_searchable_content(email_data).lower()
            
            # Exact position match
            if job_position in email_content:
                return self.criteria.position_match_weight
            
            # Match key words from position
            position_words = [word for word in job_position.split() if len(word) > 2]
            matches = 0
            for word in position_words:
                if word in email_content:
                    matches += 1
            
            # Partial match scoring
            if matches > 0:
                match_ratio = matches / len(position_words)
                return self.criteria.position_match_weight * match_ratio
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error in position matching: {e}")
            return 0.0

    def _match_url(self, email_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Match job URL in email content"""
        try:
            job_url = job_data.get('job_url', '').strip()
            if not job_url:
                return 0.0
            
            email_content = self._get_email_searchable_content(email_data)
            
            # Exact URL match
            if job_url in email_content:
                return self.criteria.url_match_weight
            
            # Match domain from job URL
            try:
                from urllib.parse import urlparse
                job_domain = urlparse(job_url).netloc.lower()
                if job_domain and job_domain in email_content.lower():
                    return self.criteria.url_match_weight * 0.7
            except Exception:
                pass
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error in URL matching: {e}")
            return 0.0

    def _match_keywords(self, email_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Match job-related keywords in email"""
        try:
            email_content = self._get_email_searchable_content(email_data).lower()
            
            # Job application related keywords
            job_keywords = [
                'application', 'interview', 'position', 'role', 'job', 'opportunity',
                'hiring', 'recruitment', 'candidate', 'resume', 'cv', 'apply',
                'thank you for applying', 'next steps', 'assessment', 'screening'
            ]
            
            matches = 0
            for keyword in job_keywords:
                if keyword in email_content:
                    matches += 1
            
            if matches > 0:
                # Scale based on number of job-related keywords found
                keyword_score = min(matches * 2, self.criteria.keyword_match_weight)
                return keyword_score
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error in keyword matching: {e}")
            return 0.0

    def _calculate_time_proximity(self, email_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate time proximity bonus"""
        try:
            email_date = self._parse_email_date(email_data.get('date', ''))
            job_date = job_data.get('captured_at') or job_data.get('created_at')
            
            if not email_date or not job_date:
                return 0.0
            
            # Convert job_date string to datetime if needed
            if isinstance(job_date, str):
                job_date = datetime.fromisoformat(job_date.replace('Z', '+00:00'))
            
            # Calculate time difference in days
            time_diff = abs((email_date - job_date).days)
            
            # Closer in time = higher bonus
            if time_diff <= 1:
                return self.criteria.time_proximity_weight
            elif time_diff <= 3:
                return self.criteria.time_proximity_weight * 0.7
            elif time_diff <= 7:
                return self.criteria.time_proximity_weight * 0.5
            else:
                return self.criteria.time_proximity_weight * 0.2
                
        except Exception as e:
            logger.error(f"❌ Error calculating time proximity: {e}")
            return 0.0

    def _get_email_searchable_content(self, email_data: Dict[str, Any]) -> str:
        """Get searchable content from email (subject + body)"""
        try:
            content_parts = []
            
            # Add subject
            subject = email_data.get('subject', email_data.get('email_subject', ''))
            if subject:
                content_parts.append(subject)
            
            # Add body content
            body = email_data.get('body', email_data.get('content', ''))
            if body:
                # Limit body content to avoid performance issues
                content_parts.append(body[:2000])
            
            # Add sender for additional context
            sender = email_data.get('sender', email_data.get('from', ''))
            if sender:
                content_parts.append(sender)
            
            return ' '.join(content_parts)
            
        except Exception as e:
            logger.error(f"❌ Error getting email content: {e}")
            return ''

    def _generate_company_variations(self, company_name: str) -> List[str]:
        """Generate company name variations for better matching"""
        variations = [company_name]
        
        # Remove common suffixes
        suffixes = [' inc', ' inc.', ' corp', ' corp.', ' llc', ' llc.', ' ltd', ' ltd.', ' co', ' co.']
        for suffix in suffixes:
            if company_name.endswith(suffix):
                variations.append(company_name[:-len(suffix)].strip())
        
        # Remove common prefixes/words
        words_to_remove = ['the ', 'a ']
        for word in words_to_remove:
            if company_name.startswith(word):
                variations.append(company_name[len(word):].strip())
        
        # Add acronym if applicable
        words = company_name.split()
        if len(words) > 1:
            acronym = ''.join(word[0].upper() for word in words if word)
            if len(acronym) > 1:
                variations.append(acronym.lower())
        
        return list(set(variations))  # Remove duplicates

    def _parse_email_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date from various formats"""
        if not date_str:
            return None
        
        try:
            # Try common email date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',  # RFC 2822 format
                '%d %b %Y %H:%M:%S %z',
                '%Y-%m-%dT%H:%M:%SZ',        # ISO format
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Fallback to current time
            logger.warning(f"Could not parse email date: {date_str}")
            return datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Error parsing email date: {e}")
            return datetime.now()

    def get_match_explanation(self, match: EmailJobMatch) -> str:
        """Generate human-readable explanation of why email and job matched"""
        try:
            explanations = []
            
            for method in match.match_methods:
                if method == MatchMethod.COMPANY_EXACT:
                    explanations.append("Company name exactly matches")
                elif method == MatchMethod.COMPANY_FUZZY:
                    explanations.append("Company name closely matches")
                elif method == MatchMethod.DOMAIN_MATCH:
                    explanations.append("Email sender domain matches company")
                elif method == MatchMethod.POSITION_MATCH:
                    explanations.append("Job position mentioned in email")
                elif method == MatchMethod.URL_MATCH:
                    explanations.append("Job URL found in email")
                elif method == MatchMethod.KEYWORD_MATCH:
                    explanations.append("Job-related keywords found")
                elif method == MatchMethod.TIME_PROXIMITY:
                    explanations.append("Email and job are close in time")
            
            if explanations:
                return f"Match reasons: {', '.join(explanations)}"
            else:
                return "Match based on multiple criteria"
                
        except Exception as e:
            logger.error(f"❌ Error generating match explanation: {e}")
            return "Match detected"