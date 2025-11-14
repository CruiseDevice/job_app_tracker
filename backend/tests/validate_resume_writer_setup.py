# backend/tests/validate_resume_writer_setup.py

"""
Validation script for Resume Writer Agent setup.
Tests module imports, class structure, and tool registration without requiring API keys.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all modules can be imported"""
    print("\n🧪 Testing module imports...")

    try:
        from agents_framework.agents.resume_writer_agent import ResumeWriterAgent, create_resume_writer_agent
        print("✅ PASS: Successfully imported ResumeWriterAgent and create_resume_writer_agent")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Failed to import Resume Writer Agent: {e}")
        return False


def test_agent_class_structure():
    """Test agent class has required methods"""
    print("\n🧪 Testing agent class structure...")

    try:
        from agents_framework.agents.resume_writer_agent import ResumeWriterAgent

        required_methods = [
            '_register_tools',
            'get_system_prompt',
            'analyze_resume',
            'tailor_for_job',
            'generate_cover_letter'
        ]

        missing_methods = []
        for method in required_methods:
            if not hasattr(ResumeWriterAgent, method):
                missing_methods.append(method)

        if missing_methods:
            print(f"❌ FAIL: Missing methods: {missing_methods}")
            return False
        else:
            print(f"✅ PASS: All required methods present ({len(required_methods)} methods)")
            return True

    except Exception as e:
        print(f"❌ FAIL: Error checking class structure: {e}")
        return False


def test_api_routes():
    """Test API routes are defined"""
    print("\n🧪 Testing API routes...")

    try:
        from api.routes.agents import router

        # Check if resume writer routes exist
        routes = [route.path for route in router.routes]

        expected_routes = [
            '/resume-writer/analyze',
            '/resume-writer/tailor',
            '/resume-writer/cover-letter',
            '/resume-writer/stats',
            '/resume-writer/ws'
        ]

        missing_routes = []
        for route in expected_routes:
            if route not in routes:
                missing_routes.append(route)

        if missing_routes:
            print(f"❌ FAIL: Missing routes: {missing_routes}")
            return False
        else:
            print(f"✅ PASS: All API routes defined ({len(expected_routes)} routes)")
            return True

    except Exception as e:
        print(f"❌ FAIL: Error checking API routes: {e}")
        return False


def test_request_models():
    """Test Pydantic request models"""
    print("\n🧪 Testing request models...")

    try:
        from api.routes.agents import (
            ResumeAnalysisRequest,
            ResumeTailorRequest,
            CoverLetterRequest,
            ResumeWriterResponse
        )

        # Test model instantiation
        analysis_req = ResumeAnalysisRequest(
            resume_text="Test resume",
            metadata={}
        )

        tailor_req = ResumeTailorRequest(
            job_title="Software Engineer",
            job_requirements="Python, React",
            candidate_experience="5 years",
            keywords="Python, React"
        )

        cover_req = CoverLetterRequest(
            company="Google",
            position="Engineer",
            motivation="Passion for tech"
        )

        print("✅ PASS: All request models can be instantiated")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error with request models: {e}")
        return False


def test_frontend_components():
    """Test frontend components exist"""
    print("\n🧪 Testing frontend components...")

    component_paths = [
        '/home/user/job_app_tracker/frontend/src/components/Agents/ResumeWriter/ResumeWriterDashboard.tsx',
        '/home/user/job_app_tracker/frontend/src/components/Agents/ResumeWriter/ResumeAnalyzerCard.tsx',
        '/home/user/job_app_tracker/frontend/src/components/Agents/ResumeWriter/ResumeTailorCard.tsx',
        '/home/user/job_app_tracker/frontend/src/components/Agents/ResumeWriter/CoverLetterCard.tsx',
        '/home/user/job_app_tracker/frontend/src/components/Agents/ResumeWriter/ATSCheckerCard.tsx',
    ]

    missing_components = []
    for path in component_paths:
        if not os.path.exists(path):
            missing_components.append(path)

    if missing_components:
        print(f"❌ FAIL: Missing components:")
        for comp in missing_components:
            print(f"    - {comp}")
        return False
    else:
        print(f"✅ PASS: All frontend components exist ({len(component_paths)} components)")
        return True


def test_agent_exports():
    """Test agent is properly exported"""
    print("\n🧪 Testing agent exports...")

    try:
        from agents_framework.agents import (
            ResumeWriterAgent,
            create_resume_writer_agent
        )

        print("✅ PASS: Resume Writer Agent properly exported from __init__.py")
        return True

    except ImportError as e:
        print(f"❌ FAIL: Agent not properly exported: {e}")
        return False


def test_app_routes():
    """Test App.tsx has route for Resume Writer"""
    print("\n🧪 Testing App.tsx routes...")

    try:
        app_path = '/home/user/job_app_tracker/frontend/src/App.tsx'

        if not os.path.exists(app_path):
            print("❌ FAIL: App.tsx not found")
            return False

        with open(app_path, 'r') as f:
            content = f.read()

        has_import = 'ResumeWriterDashboard' in content
        has_route = '/agents/resume-writer' in content

        if has_import and has_route:
            print("✅ PASS: App.tsx has Resume Writer route and import")
            return True
        else:
            print(f"❌ FAIL: Missing in App.tsx - Import: {has_import}, Route: {has_route}")
            return False

    except Exception as e:
        print(f"❌ FAIL: Error checking App.tsx: {e}")
        return False


def main():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("🚀 RESUME WRITER AGENT - SETUP VALIDATION")
    print("=" * 70)

    tests = [
        ("Module Imports", test_imports),
        ("Agent Class Structure", test_agent_class_structure),
        ("API Routes", test_api_routes),
        ("Request Models", test_request_models),
        ("Frontend Components", test_frontend_components),
        ("Agent Exports", test_agent_exports),
        ("App Routes", test_app_routes),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ FAIL: {test_name} raised exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    print("=" * 70)

    # List results
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print("\n" + "=" * 70)

    if passed == total:
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("\nResume Writer Agent is properly configured and ready to use.")
        print("\nTo test with actual API calls, set OPENAI_API_KEY environment variable")
        print("and run: python tests/test_resume_writer_agent.py")
        return 0
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
        print(f"\n{total - passed} test(s) need attention")
        return 1


if __name__ == "__main__":
    exit(main())
