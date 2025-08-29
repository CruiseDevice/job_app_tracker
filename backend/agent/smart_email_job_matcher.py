# backend/agent/smart_email_job_matcher.py

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class SmartEmailJobMatcher:
    """
    Enhanced matcher for linking emails to existing job applications
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.time_window_days = 45  # Look back 45 days for potential matches
        self.company_similarity_threshold = 0.7
        self.position_similarity_threshold = 0.6

    async def find_job_matches_for_email(self, email_data: dict) -> List[Dict[str, Any]]:
        """
        Find existing job applications that match this email
        
        Args:
            email_data: Dictionary containing email analysis results
            
        Returns:
            List of potential matches sorted by confidence score
        """
        try:
            company = email_data.get('company', '').strip()
            position = email_data.get('position', '').strip()
            sender = email_data.get('sender', '').strip()
            subject = email_data.get('subject', '').strip()
            
            if not company:
                logger.debug("No company found in email - cannot match")
                return []
            
            # Get recent applications within time window
            cutoff_date = datetime.now() - timedelta(days=self.time_window_days)
            recent_jobs = await self.db.get_applications_since(cutoff_date)
            
            if not recent_jobs:
                logger.debug("No recent job applications found for matching")
                return []
            
            matches = []
            for job in recent_jobs:
                confidence = 0
                match_methods = []
                match_details = {}
                
                # 1. Company Name Matching (Most Important - 50 points)
                company_score = self._calculate_company_match(company, job.company)
                if company_score > 0.7:
                    confidence += int(company_score * 50)
                    match_methods.append("company_name")
                    match_details['company_similarity'] = company_score
                
                # 2. Position Title Matching (40 points)
                if position:
                    position_score = self._calculate_position_match(position, job.position)
                    if position_score > 0.6:
                        confidence += int(position_score * 40)
                        match_methods.append("position_title")
                        match_details['position_similarity'] = position_score
                
                # 3. Email Domain Matching (30 points)
                domain_score = self._calculate_domain_match(sender, job.company)
                if domain_score > 0:
                    confidence += domain_score
                    match_methods.append("email_domain")
                    match_details['domain_match'] = True
                
                # 4. Subject Line Keywords (20 points)
                subject_score = self._calculate_subject_match(subject, job.company, job.position)
                if subject_score > 0:
                    confidence += subject_score
                    match_methods.append("subject_keywords")
                    match_details['subject_keywords'] = subject_score
                
                # 5. Recency Bonus (10 points max)
                recency_score = self._calculate_recency_bonus(job.application_date)
                confidence += recency_score
                match_details['recency_bonus'] = recency_score
                
                # Only include matches above minimum threshold
                if confidence >= 50:  # Minimum 50% confidence
                    matches.append({
                        'job_id': job.id,
                        'job': job.to_dict(),
                        'confidence': min(confidence, 100),  # Cap at 100%
                        'match_methods': match_methods,
                        'match_details': match_details,
                        'explanation': self._generate_match_explanation(
                            job, confidence, match_methods, match_details
                        )
                    })
            
            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            if matches:
                logger.info(f"🎯 Found {len(matches)} potential matches for {company} - {position}")
                for i, match in enumerate(matches[:3]):  # Log top 3
                    logger.info(f"  {i+1}. Job {match['job_id']}: {match['confidence']:.1f}% confidence")
            else:
                logger.debug(f"🤷 No matches found for {company} - {position}")
            
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error finding job matches: {e}")
            return []

    def _calculate_company_match(self, email_company: str, job_company: str) -> float:
        """Calculate company name similarity (0.0 to 1.0)"""
        if not email_company or not job_company:
            return 0.0
        
        # Normalize company names
        email_clean = self._normalize_company_name(email_company)
        job_clean = self._normalize_company_name(job_company)
        
        # Exact match
        if email_clean == job_clean:
            return 1.0
        
        # Check if one is contained in the other
        if email_clean in job_clean or job_clean in email_clean:
            return 0.9
        
        # Fuzzy similarity
        similarity = SequenceMatcher(None, email_clean, job_clean).ratio()
        return similarity if similarity > 0.7 else 0.0

    def _calculate_position_match(self, email_position: str, job_position: str) -> float:
        """Calculate position title similarity (0.0 to 1.0)"""
        if not email_position or not job_position:
            return 0.0
        
        # Normalize positions
        email_clean = self._normalize_position_title(email_position)
        job_clean = self._normalize_position_title(job_position)
        
        # Exact match
        if email_clean == job_clean:
            return 1.0
        
        # Check for keyword overlap
        email_keywords = set(email_clean.split())
        job_keywords = set(job_clean.split())
        
        if email_keywords and job_keywords:
            overlap = len(email_keywords.intersection(job_keywords))
            total = len(email_keywords.union(job_keywords))
            keyword_score = overlap / total if total > 0 else 0.0
            
            # Also check fuzzy similarity
            fuzzy_score = SequenceMatcher(None, email_clean, job_clean).ratio()
            
            # Take the higher of the two scores
            return max(keyword_score, fuzzy_score)
        
        return 0.0

    def _calculate_domain_match(self, sender_email: str, company_name: str) -> int:
        """Check if sender domain matches company (0 to 30 points)"""
        if not sender_email or not company_name:
            return 0
        
        try:
            # Extract domain from email
            domain = sender_email.split('@')[1].lower() if '@' in sender_email else ''
            company_clean = self._normalize_company_name(company_name)
            
            # Direct domain match
            if company_clean in domain or any(word in domain for word in company_clean.split() if len(word) > 3):
                return 30
            
            # Common HR/recruitment domains
            hr_domains = ['greenhouse.io', 'lever.co', 'workday.com', 'bamboohr.com', 'jobvite.com']
            if any(hr_domain in domain for hr_domain in hr_domains):
                return 15
            
            return 0
            
        except Exception:
            return 0

    def _calculate_subject_match(self, subject: str, company: str, position: str) -> int:
        """Check subject line for job-related keywords (0 to 20 points)"""
        if not subject:
            return 0
        
        subject_lower = subject.lower()
        score = 0
        
        # Company name in subject
        if company and self._normalize_company_name(company) in subject_lower:
            score += 10
        
        # Position keywords in subject
        if position:
            position_words = self._normalize_position_title(position).split()
            for word in position_words:
                if len(word) > 3 and word in subject_lower:
                    score += 3
        
        # Job-related keywords
        job_keywords = ['interview', 'assessment', 'offer', 'application', 'position', 'role', 'opportunity']
        for keyword in job_keywords:
            if keyword in subject_lower:
                score += 2
        
        return min(score, 20)  # Cap at 20 points

    def _calculate_recency_bonus(self, application_date: datetime) -> int:
        """Give bonus points for more recent applications (0 to 10 points)"""
        if not application_date:
            return 0
        
        days_ago = (datetime.now() - application_date).days
        
        if days_ago <= 7:
            return 10  # Applied within last week
        elif days_ago <= 14:
            return 7   # Applied within 2 weeks
        elif days_ago <= 30:
            return 5   # Applied within month
        else:
            return 2   # Older applications

    def _normalize_company_name(self, company: str) -> str:
        """Normalize company name for comparison"""
        if not company:
            return ''
        
        # Remove common suffixes and normalize
        normalized = re.sub(r'\b(inc|llc|corp|corporation|company|ltd|limited)\b', '', company.lower())
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', ' ', normalized).strip()  # Normalize whitespace
        
        return normalized

    def _normalize_position_title(self, position: str) -> str:
        """Normalize position title for comparison"""
        if not position:
            return ''
        
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', position.lower().strip())
        
        # Remove common words that don't affect matching
        noise_words = ['position', 'role', 'job', 'opening', 'opportunity']
        for word in noise_words:
            normalized = re.sub(rf'\b{word}\b', '', normalized)
        
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _generate_match_explanation(self, job: Any, confidence: float, methods: List[str], details: Dict[str, Any]) -> str:
        """Generate human-readable explanation for the match"""
        explanations = []
        
        if 'company_name' in methods:
            similarity = details.get('company_similarity', 0)
            explanations.append(f"Company name similarity: {similarity:.1%}")
        
        if 'position_title' in methods:
            similarity = details.get('position_similarity', 0)
            explanations.append(f"Position similarity: {similarity:.1%}")
        
        if 'email_domain' in methods:
            explanations.append("Email from company domain")
        
        if 'subject_keywords' in methods:
            explanations.append("Subject contains job-related keywords")
        
        recency_bonus = details.get('recency_bonus', 0)
        if recency_bonus > 0:
            explanations.append(f"Recent application (+{recency_bonus} pts)")
        
        explanation = f"Matched with {confidence:.1f}% confidence: " + ", ".join(explanations)
        return explanation