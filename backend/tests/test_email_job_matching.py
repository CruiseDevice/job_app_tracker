# backend/tests/test_email_job_matching.py

"""
Test scripts to validate the email-to-job matching functionality.
Run these after implementing the matching system.
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager
from agent.smart_email_job_matcher import SmartEmailJobMatcher
from agent.email_monitor import EmailMonitor
from agent.email_processor import EmailProcessor

class EmailJobMatchingTests:
    
    def __init__(self):
        self.db = DatabaseManager()
        self.matcher = SmartEmailJobMatcher(self.db)
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })

    async def test_company_name_matching(self):
        """Test company name similarity matching"""
        print("\n🧪 Testing company name matching...")
        
        test_cases = [
            # (email_company, job_company, expected_score_range)
            ("Google", "Google", (0.95, 1.0)),
            ("Google LLC", "Google", (0.85, 0.95)),
            ("google", "Google Inc", (0.80, 0.90)),
            ("Alphabet", "Google", (0.0, 0.3)),  # Should be low unless in rules
            ("Microsoft Corporation", "Microsoft", (0.85, 0.95)),
            ("Completely Different Corp", "Google", (0.0, 0.2)),
        ]
        
        for email_company, job_company, (min_score, max_score) in test_cases:
            score = self.matcher._calculate_company_match(email_company, job_company)
            passed = min_score <= score <= max_score
            
            self.log_test(
                f"Company match: '{email_company}' vs '{job_company}'",
                passed,
                f"Score: {score:.3f}, Expected: {min_score:.1f}-{max_score:.1f}"
            )

    async def test_position_matching(self):
        """Test position title matching"""
        print("\n🧪 Testing position title matching...")
        
        test_cases = [
            ("Software Engineer", "Software Engineer", (0.95, 1.0)),
            ("Senior Software Engineer", "Software Engineer", (0.7, 0.9)),
            ("SWE", "Software Engineer", (0.0, 0.4)),  # Abbreviation might not match well
            ("Backend Engineer", "Software Engineer", (0.4, 0.7)),
            ("Data Scientist", "Software Engineer", (0.0, 0.3)),
        ]
        
        for email_pos, job_pos, (min_score, max_score) in test_cases:
            score = self.matcher._calculate_position_match(email_pos, job_pos)
            passed = min_score <= score <= max_score
            
            self.log_test(
                f"Position match: '{email_pos}' vs '{job_pos}'",
                passed,
                f"Score: {score:.3f}, Expected: {min_score:.1f}-{max_score:.1f}"
            )

    async def test_domain_matching(self):
        """Test email domain matching"""
        print("\n🧪 Testing email domain matching...")
        
        test_cases = [
            ("recruiter@google.com", "Google", 30),
            ("hiring@microsoft.com", "Microsoft", 30),
            ("noreply@greenhouse.io", "Any Company", 15),  # HR platform
            ("candidate@lever.co", "Any Company", 15),     # HR platform
            ("personal@gmail.com", "Google", 0),           # Personal email
        ]
        
        for sender_email, company, expected_score in test_cases:
            score = self.matcher._calculate_domain_match(sender_email, company)
            passed = score == expected_score
            
            self.log_test(
                f"Domain match: '{sender_email}' for '{company}'",
                passed,
                f"Score: {score}, Expected: {expected_score}"
            )

    async def test_end_to_end_matching(self):
        """Test complete email-to-job matching workflow"""
        print("\n🧪 Testing end-to-end matching...")
        
        # Create test job application
        test_job_data = {
            'company': 'Google',
            'position': 'Software Engineer',
            'status': 'applied',
            'application_date': datetime.now() - timedelta(days=3),
            'job_url': 'https://careers.google.com/jobs/12345',
            'location': 'Mountain View, CA'
        }
        
        try:
            job_id = await self.db.add_application(test_job_data)
            
            # Test email that should match
            test_email = {
                'company': 'Google',
                'position': 'Software Engineer',
                'sender': 'recruiting@google.com',
                'subject': 'Google Software Engineer - Interview Invitation',
                'received_at': datetime.now().isoformat()
            }
            
            matches = await self.matcher.find_job_matches_for_email(test_email)
            
            # Should find the match
            passed = len(matches) > 0 and matches[0]['confidence'] >= 75
            self.log_test(
                "End-to-end matching: High confidence match found",
                passed,
                f"Found {len(matches)} matches, best: {matches[0]['confidence']:.1f}%" if matches else "No matches found"
            )
            
            if passed:
                # Test that it would update the right job
                best_match = matches[0]
                passed_job = best_match['job_id'] == job_id
                self.log_test(
                    "End-to-end matching: Matched correct job",
                    passed_job,
                    f"Expected job {job_id}, got {best_match['job_id']}"
                )
            
            # Clean up test data
            await self.db.delete_application(job_id)
            
        except Exception as e:
            self.log_test(
                "End-to-end matching: Exception handling",
                False,
                f"Error: {e}"
            )

    async def test_duplicate_detection(self):
        """Test duplicate application detection"""
        print("\n🧪 Testing duplicate detection...")
        
        # Create two similar applications
        app1_data = {
            'company': 'Microsoft',
            'position': 'Product Manager',
            'status': 'applied',
            'application_date': datetime.now() - timedelta(days=2),
        }
        
        app2_data = {
            'company': 'Microsoft Corporation',  # Slightly different company name
            'position': 'Product Manager',
            'status': 'interview',
            'application_date': datetime.now() - timedelta(days=1),
        }
        
        try:
            job_id_1 = await self.db.add_application(app1_data)
            job_id_2 = await self.db.add_application(app2_data)
            
            # Check if duplicate detection works
            duplicates = self.db.get_duplicate_applications()
            
            # Should detect these as duplicates
            found_duplicate = False
            for group in duplicates:
                if group['company'].lower() in ['microsoft', 'microsoft corporation']:
                    found_duplicate = True
                    break
            
            self.log_test(
                "Duplicate detection: Found similar applications",
                found_duplicate,
                f"Found {len(duplicates)} duplicate groups"
            )
            
            # Clean up
            await self.db.delete_application(job_id_1)
            await self.db.delete_application(job_id_2)
            
        except Exception as e:
            self.log_test(
                "Duplicate detection: Exception handling",
                False,
                f"Error: {e}"
            )

    async def test_status_progression(self):
        """Test that status updates work correctly"""
        print("\n🧪 Testing status progression...")
        
        # Create test application
        test_data = {
            'company': 'Test Corp',
            'position': 'Test Engineer',
            'status': 'applied',
            'application_date': datetime.now()
        }
        
        try:
            job_id = await self.db.add_application(test_data)
            
            # Test status updates
            statuses_to_test = ['assessment', 'interview', 'offer']
            
            for status in statuses_to_test:
                updated = await self.db.update_application_status(job_id, status)
                
                self.log_test(
                    f"Status progression: Update to '{status}'",
                    updated is not None,
                    f"Status update {'successful' if updated else 'failed'}"
                )
                
                if updated:
                    # Verify the status was actually updated
                    app = self.db.get_application_by_id(job_id)
                    correct_status = app and app.get('status') == status
                    
                    self.log_test(
                        f"Status verification: Status is '{status}'",
                        correct_status,
                        f"Actual status: {app.get('status') if app else 'None'}"
                    )
            
            # Clean up
            await self.db.delete_application(job_id)
            
        except Exception as e:
            self.log_test(
                "Status progression: Exception handling",
                False,
                f"Error: {e}"
            )

    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing edge cases...")
        
        # Test empty/None inputs
        score = self.matcher._calculate_company_match("", "Google")
        self.log_test(
            "Edge case: Empty company name",
            score == 0.0,
            f"Score: {score}"
        )
        
        score = self.matcher._calculate_position_match(None, "Engineer")
        self.log_test(
            "Edge case: None position",
            score == 0.0,
            f"Score: {score}"
        )
        
        # Test with no recent applications
        empty_matches = await self.matcher.find_job_matches_for_email({
            'company': 'NonExistentCompany',
            'position': 'NonExistentPosition',
            'sender': 'test@example.com'
        })
        
        self.log_test(
            "Edge case: No matching applications",
            len(empty_matches) == 0,
            f"Found {len(empty_matches)} matches (expected 0)"
        )

    async def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Email-Job Matching Tests")
        print("=" * 50)
        
        await self.test_company_name_matching()
        await self.test_position_matching() 
        await self.test_domain_matching()
        await self.test_end_to_end_matching()
        await self.test_duplicate_detection()
        await self.test_status_progression()
        await self.test_edge_cases()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"🎯 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ {self.failed} tests failed. Please review the failures above.")
            return False
        else:
            print(f"\n🎉 All tests passed! The email-job matching system is working correctly.")
            return True

# Manual testing scenarios
class ManualTestScenarios:
    """Interactive scenarios for manual testing"""
    
    @staticmethod
    def print_test_scenario(scenario_name: str, description: str, steps: list):
        """Print a manual test scenario"""
        print(f"\n📋 Manual Test Scenario: {scenario_name}")
        print(f"Description: {description}")
        print("Steps:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
        print()

    @staticmethod
    def print_all_scenarios():
        """Print all manual test scenarios"""
        print("🧪 Manual Testing Scenarios")
        print("=" * 40)
        
        ManualTestScenarios.print_test_scenario(
            "Basic Email-to-Job Matching",
            "Test that emails get matched to existing job applications",
            [
                "Manually add a job application (e.g., 'Software Engineer at Google')",
                "Send yourself an email from a Gmail account with 'Google Software Engineer Interview' in the subject",
                "Wait for email monitoring cycle (or trigger manually)",
                "Verify that NO new application was created",
                "Verify that the existing application status was updated",
                "Check that the email is linked to the job in the database"
            ]
        )
        
        ManualTestScenarios.print_test_scenario(
            "Multiple Status Updates",
            "Test status progression through multiple emails",
            [
                "Create job application with status 'applied'",
                "Send email that should trigger 'assessment' status",
                "Verify status updated to 'assessment'",
                "Send email that should trigger 'interview' status", 
                "Verify status updated to 'interview'",
                "Send email that should trigger 'offer' status",
                "Verify final status is 'offer'",
                "Confirm timeline shows all status changes"
            ]
        )
        
        ManualTestScenarios.print_test_scenario(
            "Duplicate Prevention",
            "Test that the system doesn't create duplicates",
            [
                "Apply to the same job through extension (creates 'captured' status)",
                "Apply through website manually (creates 'applied' status)", 
                "Receive confirmation email",
                "Verify only ONE job application exists (not three)",
                "Check duplicate detection finds potential duplicates",
                "Test merge functionality"
            ]
        )
        
        ManualTestScenarios.print_test_scenario(
            "Low Confidence Matching",
            "Test behavior with uncertain matches",
            [
                "Create job for 'ACME Corp'",
                "Send email from 'ACME Corporation' (slightly different)",
                "Verify system either creates new job OR shows in pending matches",
                "Manually review and confirm/reject the match",
                "Test that decision is remembered"
            ]
        )


async def main():
    """Main test runner"""
    print("Email-Job Matching Test Suite")
    print("=" * 30)
    
    # Run automated tests
    tester = EmailJobMatchingTests()
    success = await tester.run_all_tests()
    
    # Show manual test scenarios
    print("\n" + "=" * 50)
    ManualTestScenarios.print_all_scenarios()
    
    # Final recommendation
    if success:
        print("🎉 Automated tests passed! You can now:")
        print("  1. Run the manual test scenarios above")
        print("  2. Deploy to production")
        print("  3. Monitor logs for any issues")
    else:
        print("❌ Some automated tests failed. Please:")
        print("  1. Fix the failing tests")
        print("  2. Re-run the test suite")
        print("  3. Only deploy after all tests pass")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())