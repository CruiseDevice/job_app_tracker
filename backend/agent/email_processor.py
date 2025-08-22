# FILE: backend/agent/email_processor.py

import os
import re
import logging
import asyncio
import imaplib
import email
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from email.header import decode_header

# LLM imports (using OpenAI as example - can be swapped for other providers)
import openai
from openai import AsyncOpenAI

# Import settings
from config.settings import settings

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self):
        self.email_address = settings.email_address
        self.email_password = settings.email_password
        self.imap_server = "imap.gmail.com"  # Default to Gmail
        self.imap_port = 993
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
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
        """Initialize email connection"""
        try:
            if not self.email_address or not self.email_password:
                raise ValueError(
                    "Missing email credentials. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your .env file"
                )
            
            # Test connection
            await self._test_connection()
            logger.info("✅ Email connection initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize email connection: {e}")
            raise

    async def _test_connection(self):
        """Test IMAP connection"""
        try:
            # Use asyncio to run blocking IMAP operations
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connect_and_test)
        except Exception as e:
            raise Exception(f"Connection test failed: {e}")

    def _connect_and_test(self):
        """Blocking IMAP connection test"""
        try:
            # Connect to IMAP server
            imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # Login
            imap.login(self.email_address, self.email_password)
            
            # Test access to INBOX
            imap.select('INBOX')
            
            # Close connection
            imap.close()
            imap.logout()
            
        except Exception as e:
            raise Exception(f"IMAP connection failed: {e}")

    async def fetch_recent_emails(self, hours: int = 24, max_results: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent emails using IMAP"""
        try:
            if not self.email_address or not self.email_password:
                raise ValueError("Email credentials not configured")
            
            # Use asyncio to run blocking IMAP operations
            loop = asyncio.get_event_loop()
            emails = await loop.run_in_executor(
                None, 
                self._fetch_emails_sync, 
                hours, 
                max_results
            )
            
            logger.info(f"✅ Successfully fetched {len(emails)} emails")
            return emails
            
        except Exception as e:
            logger.error(f"❌ Error fetching emails: {e}")
            return []

    def _fetch_emails_sync(self, hours: int, max_results: int) -> List[Dict[str, Any]]:
        """Synchronous email fetching using IMAP"""
        emails = []
        
        try:
            # Connect to IMAP server
            imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            imap.login(self.email_address, self.email_password)
            
            # Select INBOX
            imap.select('INBOX')
            
            # Search for recent emails
            # Gmail supports date search: SINCE "01-Jan-2024"
            since_date = (datetime.now() - timedelta(hours=hours)).strftime("%d-%b-%Y")
            search_criteria = f'SINCE "{since_date}"'
            
            # Search for emails
            status, message_numbers = imap.search(None, search_criteria)
            
            if status != 'OK':
                logger.error("❌ IMAP search failed")
                return emails
            
            # Get message numbers
            message_list = message_numbers[0].split()
            
            # Limit results
            if len(message_list) > max_results:
                message_list = message_list[-max_results:]  # Get most recent
            
            logger.info(f"🔍 Found {len(message_list)} emails in last {hours} hours")
            
            # Fetch each email
            for num in message_list:
                try:
                    # Fetch email data
                    status, msg_data = imap.fetch(num, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email details
                    email_data = self._parse_email_message(email_message, num.decode())
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    logger.error(f"❌ Error parsing email {num}: {e}")
                    continue
            
            # Close connection
            imap.close()
            imap.logout()
            
        except Exception as e:
            logger.error(f"❌ IMAP error: {e}")
        
        return emails

    def _parse_email_message(self, email_message, message_id: str) -> Optional[Dict[str, Any]]:
        """Parse email message and extract relevant information"""
        try:
            # Extract headers
            subject = self._decode_header(email_message.get('Subject', ''))
            sender = self._decode_header(email_message.get('From', ''))
            date = email_message.get('Date', '')
            
            # Extract body
            body = self._extract_email_body(email_message)
            
            # Create email data structure
            email_data = {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body,
                'headers': {
                    'subject': subject,
                    'from': sender,
                    'date': date
                }
            }
            
            return email_data
            
        except Exception as e:
            logger.error(f"❌ Error parsing email message: {e}")
            return None

    def _decode_header(self, header_value: str) -> str:
        """Decode email header values"""
        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += str(part)
            
            return decoded_string
        except Exception:
            return str(header_value)

    def _extract_email_body(self, email_message) -> str:
        """Extract text content from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                
                # Skip attachments
                if 'attachment' in content_disposition:
                    continue
                
                if content_type == 'text/plain':
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception:
                        continue
                elif content_type == 'text/html' and not body:
                    # Use HTML if no plain text found
                    try:
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Simple HTML to text conversion
                        body += re.sub(r'<[^>]+>', ' ', html_content)
                    except Exception:
                        continue
        else:
            # Single part message
            content_type = email_message.get_content_type()
            if content_type == 'text/plain':
                try:
                    body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                except Exception:
                    body = ""
            elif content_type == 'text/html':
                try:
                    html_content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    body = re.sub(r'<[^>]+>', ' ', html_content)
                except Exception:
                    body = ""
        
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
            # Ensure we always have a valid application_date
            app_date = result.get('application_date')
            if not app_date or app_date == 'None' or app_date == '':
                app_date = datetime.now().strftime('%Y-%m-%d')
                logger.info(f"📅 No application date found, using current date: {app_date}")
            else:
                logger.info(f"📅 Using extracted application date: {app_date}")
            
            application_data = {
                'company': result.get('company', 'Unknown'),
                'position': result.get('position', 'Unknown'),
                'status': result.get('status', 'applied'),
                'application_date': app_date,
                'job_description': result.get('description', ''),
                'location': result.get('location', ''),
                'salary_range': result.get('salary', ''),
                'job_url': result.get('job_url', ''),
                'notes': result.get('notes', ''),
                'email_thread_id': email_data.get('id', ''),
                'email_subject': email_data.get('subject', ''),
                'email_sender': email_data.get('sender', '')
            }
            
            logger.info(f"📝 Prepared application data: {application_data}")
            
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
            # For IMAP, we can't easily fetch by ID, so we'll fetch recent emails instead
            emails = await self.fetch_recent_emails(hours=24, max_results=10)
            
            if not emails:
                return {"error": "No emails found"}
            
            # Process the first email as a test
            test_email = emails[0]
            result = await self.process_email(test_email)
            
            return {
                "email_id": test_email['id'],
                "subject": test_email.get('subject', ''),
                "sender": test_email.get('sender', ''),
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
