# FILE: backend/agent/email_processor.py

import os
import re
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# LLM imports (using OpenAI as example - can be swapped for other providers)
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Gmail API scopes
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Job-related keywords for initial filtering (privacy protection)
        self.JOB_KEYWORDS = [
            'application', 'interview', 'position', 'role', 'job', 'career',
            'hiring', 'recruitment', 'hr', 'human resources', 'talent',
            'opportunity', 'opening', 'vacancy', 'candidate', 'resume',
            'cv', 'application received', 'thank you for applying',
            'next steps', 'assessment', 'screening', 'offer', 'compensation'
        ]
        
        # Email domains that commonly send job-related emails
        self.JOB_DOMAINS = [
            'greenhouse.io', 'lever.co', 'workday.com', 'successfactors.com',
            'taleo.net', 'bamboohr.com', 'namely.com', 'paycom.com',
            'ultipro.com', 'adp.com', 'workable.com', 'smartrecruiters.com',
            'jobvite.com', 'icims.com', 'cornerstone.com', 'recruitee.com'
        ]

    async def initialize(self):
        """Initialize Gmail API service"""
        try:
            creds = await self._get_credentials()
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("✅ Gmail API service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gmail API: {e}")
            raise

    async def _get_credentials(self) -> Credentials:
        """Get or refresh Gmail API credentials"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # If no valid credentials, go through OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("🔄 Gmail credentials refreshed")
                except Exception as e:
                    logger.error(f"❌ Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Gmail credentials file not found: {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                logger.info("🔑 New Gmail credentials obtained")
            
            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds

    async def fetch_recent_emails(self, hours: int = 24, max_results: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent emails from Gmail"""
        if not self.service:
            await self.initialize()
        
        try:
            # Calculate date range
            after_date = datetime.now() - timedelta(hours=hours)
            after_timestamp = int(after_date.timestamp())
            
            # Build query for recent emails
            query = f'after:{after_timestamp}'
            
            logger.info(f"🔍 Fetching emails from last {hours} hours...")
            
            # Get message list
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"📧 Found {len(messages)} recent emails")
            
            # Fetch detailed email data
            emails = []
            for message in messages:
                try:
                    email_data = await self._get_email_details(message['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"❌ Error fetching email {message['id']}: {e}")
                    continue
            
            logger.info(f"✅ Successfully processed {len(emails)} emails")
            return emails
            
        except HttpError as e:
            logger.error(f"❌ Gmail API error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error fetching emails: {e}")
            return []

    async def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {
                header['name'].lower(): header['value']
                for header in message['payload'].get('headers', [])
            }
            
            # Extract email body
            body = self._extract_email_body(message['payload'])
            
            # Basic email info
            email_data = {
                'id': message_id,
                'subject': headers.get('subject', ''),
                'sender': headers.get('from', ''),
                'date': headers.get('date', ''),
                'body': body,
                'headers': headers
            }
            
            return email_data
            
        except Exception as e:
            logger.error(f"❌ Error getting email details for {message_id}: {e}")
            return None

    def _extract_email_body(self, payload: Dict) -> str:
        """Extract text content from email payload"""
        body = ""
        
        def extract_parts(parts):
            nonlocal body
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        import base64
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html' and not body:
                    # Only use HTML if no plain text found
                    data = part['body'].get('data', '')
                    if data:
                        import base64
                        html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        # Simple HTML to text conversion
                        body += re.sub(r'<[^>]+>', ' ', html_content)
                elif 'parts' in part:
                    extract_parts(part['parts'])
        
        if 'parts' in payload:
            extract_parts(payload['parts'])
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    import base64
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body.strip()

    async def process_email(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an email to determine if it's job-related and extract details"""
        try:
            # Step 1: Privacy-first filtering
            if not await self._is_potentially_job_related(email_data):
                logger.debug(f"📧 Email {email_data['id']} not job-related (filtered)")
                return None
            
            logger.info(f"🔍 Processing potentially job-related email: {email_data['subject'][:50]}...")
            
            # Step 2: LLM analysis for job application detection
            job_details = await self._analyze_with_llm(email_data)
            
            if job_details:
                logger.info(f"✅ Job application detected: {job_details.get('company', 'Unknown')} - {job_details.get('position', 'Unknown')}")
                return job_details
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error processing email {email_data.get('id', 'unknown')}: {e}")
            return None

    async def _is_potentially_job_related(self, email_data: Dict[str, Any]) -> bool:
        """First-stage filtering: Check if email might be job-related without reading full content"""
        subject = email_data.get('subject', '').lower()
        sender = email_data.get('sender', '').lower()
        
        # Check sender domain
        sender_domain = re.search(r'@([^>]*)', sender)
        if sender_domain:
            domain = sender_domain.group(1).lower()
            if any(job_domain in domain for job_domain in self.JOB_DOMAINS):
                logger.debug(f"✅ Job domain detected: {domain}")
                return True
        
        # Check subject for job keywords
        if any(keyword in subject for keyword in self.JOB_KEYWORDS):
            logger.debug(f"✅ Job keyword found in subject: {subject}")
            return True
        
        # Check first 200 characters of body for job keywords (minimal privacy intrusion)
        body_preview = email_data.get('body', '')[:200].lower()
        if any(keyword in body_preview for keyword in self.JOB_KEYWORDS):
            logger.debug("✅ Job keyword found in email preview")
            return True
        
        return False

    async def _analyze_with_llm(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to analyze email and extract job application details"""
        try:
            # Prepare email content for LLM
            email_content = f"""
Subject: {email_data.get('subject', '')}
From: {email_data.get('sender', '')}
Date: {email_data.get('date', '')}

Body:
{email_data.get('body', '')[:2000]}  # Limit to first 2000 chars
"""

            # LLM prompt for job application analysis
            prompt = """
You are an AI assistant that analyzes emails to detect job applications and extract relevant details.

Analyze the following email and determine if it's related to a job application. If it is, extract the relevant information.

Email to analyze:
{email_content}

Return your response in JSON format with the following structure:
{{
    "is_job_application": true/false,
    "company": "Company name",
    "position": "Job title/position",
    "location": "Job location (if mentioned)",
    "status": "applied/interview_scheduled/offer_received/rejected/assessment_received",
    "description": "Brief job description (if available)",
    "salary": "Salary range (if mentioned)",
    "job_url": "Job posting URL (if available)",
    "application_date": "Date applied (YYYY-MM-DD format)",
    "notes": "Any additional relevant information"
}}

Only return valid JSON. If it's not a job application email, set "is_job_application" to false.

Guidelines:
- Look for confirmation emails after submitting applications
- Interview scheduling emails
- Job assessment or test invitations  
- Offer letters or rejection emails
- Recruiter outreach emails
- Application status updates

Be accurate and only extract information that's clearly stated in the email.
""".format(email_content=email_content)

            # Call LLM API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # More cost-effective model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes emails for job application information. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse LLM response
            llm_response = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown code blocks if present)
            llm_response = re.sub(r'```json\s*', '', llm_response)
            llm_response = re.sub(r'```\s*$', '', llm_response)
            
            import json
            result = json.loads(llm_response)
            
            # Validate response
            if not result.get('is_job_application', False):
                logger.debug("🚫 LLM determined email is not job-related")
                return None
            
            # Extract and validate required fields
            application_data = {
                'company': result.get('company', 'Unknown'),
                'position': result.get('position', 'Unknown'),
                'status': result.get('status', 'applied'),
                'dateApplied': result.get('application_date', datetime.now().strftime('%Y-%m-%d')),
                'source': 'email',
                'description': result.get('description', ''),
                'location': result.get('location', ''),
                'salary': result.get('salary', ''),
                'jobUrl': result.get('job_url', ''),
                'notes': result.get('notes', ''),
                'emailId': email_data.get('id', ''),
                'emailSubject': email_data.get('subject', ''),
                'emailSender': email_data.get('sender', ''),
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            }
            
            return application_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON response from LLM: {e}")
            logger.error(f"LLM Response: {llm_response}")
            return None
        except Exception as e:
            logger.error(f"❌ Error in LLM analysis: {e}")
            return None

    async def test_email_processing(self, test_email_id: str) -> Dict[str, Any]:
        """Test email processing with a specific email ID"""
        try:
            if not self.service:
                await self.initialize()
            
            email_data = await self._get_email_details(test_email_id)
            if not email_data:
                return {"error": "Could not fetch email"}
            
            result = await self.process_email(email_data)
            
            return {
                "email_id": test_email_id,
                "subject": email_data.get('subject', ''),
                "sender": email_data.get('sender', ''),
                "is_job_related": result is not None,
                "extracted_data": result
            }
            
        except Exception as e:
            logger.error(f"❌ Error in test processing: {e}")
            return {"error": str(e)}

    async def get_email_stats(self) -> Dict[str, Any]:
        """Get statistics about recent email processing"""
        try:
            # Get emails from last 7 days
            emails = await self.fetch_recent_emails(hours=168, max_results=200)
            
            total_emails = len(emails)
            job_related_count = 0
            
            for email in emails:
                if await self._is_potentially_job_related(email):
                    job_related_count += 1
            
            return {
                "total_emails_last_week": total_emails,
                "potentially_job_related": job_related_count,
                "job_related_percentage": round((job_related_count / total_emails * 100) if total_emails > 0 else 0, 2),
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting email stats: {e}")
            return {"error": str(e)}
