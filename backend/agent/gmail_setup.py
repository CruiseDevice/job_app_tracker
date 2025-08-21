import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def setup_gmail_credentials():
    """Interactive setup for Gmail API credentials"""
    
    print("🔑 Gmail API Setup")
    print("=" * 50)
    
    # Check if credentials.json exists
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found!")
        print("\n📋 To set up Gmail API access:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download credentials.json to this directory")
        return False
    
    print("✅ Found credentials.json")
    
    # Set up OAuth flow
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("✅ Gmail API credentials configured successfully!")
    return True

if __name__ == "__main__":
    setup_gmail_credentials()