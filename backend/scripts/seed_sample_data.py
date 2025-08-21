# FILE: backend/scripts/seed_sample_data.py

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager

def create_sample_data():
    """Create sample job applications for development/testing"""
    
    db_manager = DatabaseManager()
    db_manager.init_db()
    
    # Sample companies and positions
    companies = [
        {"name": "Google", "positions": ["Software Engineer", "Senior Software Engineer", "Tech Lead"]},
        {"name": "Microsoft", "positions": ["Software Developer", "Senior Developer", "Principal Engineer"]},
        {"name": "Amazon", "positions": ["SDE I", "SDE II", "Senior SDE"]},
        {"name": "Apple", "positions": ["Software Engineer", "iOS Developer", "Backend Engineer"]},
        {"name": "Meta", "positions": ["Software Engineer", "Frontend Engineer", "Full Stack Engineer"]},
        {"name": "Netflix", "positions": ["Senior Software Engineer", "Staff Engineer", "Principal Engineer"]},
        {"name": "Uber", "positions": ["Backend Engineer", "Mobile Engineer", "Data Engineer"]},
        {"name": "Airbnb", "positions": ["Software Engineer", "Senior Engineer", "Staff Engineer"]},
        {"name": "Stripe", "positions": ["Software Engineer", "Backend Engineer", "Infrastructure Engineer"]},
        {"name": "Spotify", "positions": ["Backend Developer", "Full Stack Developer", "Platform Engineer"]}
    ]
    
    locations = [
        "San Francisco, CA", "Seattle, WA", "New York, NY", "Austin, TX", 
        "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Remote", 
        "Denver, CO", "Portland, OR"
    ]
    
    statuses = ["applied", "interview", "assessment", "rejected", "offer"]
    status_weights = [0.5, 0.2, 0.1, 0.15, 0.05]  # Most applications are "applied"
    
    salary_ranges = [
        "$80k - $120k", "$100k - $150k", "$120k - $180k", "$150k - $220k",
        "$180k - $250k", "$200k - $300k", "$220k - $350k", "$250k - $400k"
    ]
    
    sample_descriptions = [
        "We are looking for a passionate software engineer to join our team and help build the next generation of our platform.",
        "Join our engineering team to work on cutting-edge technology and solve complex problems at scale.",
        "We're seeking a talented developer to contribute to our mission of connecting people through technology.",
        "Work with a team of experienced engineers to build products that impact millions of users worldwide.",
        "Help us revolutionize the industry with innovative solutions and clean, maintainable code.",
        "Be part of a fast-growing team working on exciting projects with modern technologies and best practices.",
        "Collaborate with cross-functional teams to deliver high-quality software solutions that delight our customers.",
        "Join us in building the future of technology with a focus on scalability, performance, and user experience."
    ]
    
    # Generate sample applications
    applications = []
    for i in range(25):  # Create 25 sample applications
        company_data = random.choice(companies)
        company = company_data["name"]
        position = random.choice(company_data["positions"])
        
        # Generate application date (within last 90 days)
        days_ago = random.randint(0, 90)
        application_date = datetime.now() - timedelta(days=days_ago)
        
        # Assign status with weights
        status = random.choices(statuses, weights=status_weights)[0]
        
        application_data = {
            "company": company,
            "position": position,
            "application_date": application_date,
            "status": status,
            "location": random.choice(locations),
            "salary_range": random.choice(salary_ranges),
            "job_description": random.choice(sample_descriptions),
            "job_url": f"https://jobs.{company.lower()}.com/position/{i+1}",
            "email_sender": f"recruiting@{company.lower().replace(' ', '')}.com",
            "email_subject": f"Application for {position} position",
            "notes": f"Applied via company website. {random.choice(['Great company culture.', 'Interesting tech stack.', 'Good growth opportunities.', 'Competitive benefits.'])}" if random.random() > 0.7 else None
        }
        
        try:
            app_id = db_manager.add_application(application_data)
            applications.append(app_id)
            print(f"Added application {app_id}: {company} - {position}")
        except Exception as e:
            print(f"Error adding application for {company}: {e}")
    
    print(f"\nSuccessfully created {len(applications)} sample applications!")
    
    # Print statistics
    stats = db_manager.get_statistics()
    print(f"\nDatabase Statistics:")
    print(f"Total applications: {stats['total']}")
    print(f"Applications by status:")
    for status, count in stats['byStatus'].items():
        print(f"  {status}: {count}")
    print(f"Interview rate: {stats['interviewRate']}%")
    print(f"Response rate: {stats['responseRate']}%")

if __name__ == "__main__":
    create_sample_data()