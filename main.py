import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailMonitor:
    """
    Monitors email for job application updates
    """
    def __init__(self, email_address: str, password: str):
        self.email_address = email_address
        self.password = password
        print(f"EmailMonitor initialized for: {email_address}")


class SmartJobTracker:
    def __init__(self):
        # Get email credentials from environment variables
        email_address = os.getenv('EMAIL')
        email_password = os.getenv('PASSWORD')
        
        if not email_address or not email_password:
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env file")
        
        self.email_monitor = EmailMonitor(
            email_address=email_address,
            password=email_password
        )

    def sync_applications(self):
        """
        Sync applications from email
        """
        print("Scanning emails for Job applications...")


if __name__ == "__main__":
    tracker = SmartJobTracker()

    # sync applications from email
    tracker.sync_applications()
