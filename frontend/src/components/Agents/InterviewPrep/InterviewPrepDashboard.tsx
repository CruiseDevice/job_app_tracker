import React, { useState } from 'react';
import './InterviewPrepDashboard.css';

interface InterviewPrepState {
  activeTab: 'prepare' | 'questions' | 'star' | 'mock' | 'tips' | 'checklist';
  loading: boolean;
  error: string | null;
  result: any;
}

const InterviewPrepDashboard: React.FC = () => {
  const [state, setState] = useState<InterviewPrepState>({
    activeTab: 'prepare',
    loading: false,
    error: null,
    result: null
  });

  // Comprehensive Interview Preparation
  const [prepForm, setPrepForm] = useState({
    company_name: '',
    job_title: '',
    job_description: '',
    interview_date: '',
    interview_type: 'general'
  });

  // Question Generation
  const [questionForm, setQuestionForm] = useState({
    job_title: '',
    job_description: '',
    company_name: '',
    question_type: 'mixed'
  });

  // STAR Answer
  const [starForm, setStarForm] = useState({
    question: '',
    experience_context: ''
  });

  // Mock Interview
  const [mockForm, setMockForm] = useState({
    job_title: '',
    focus_area: 'general',
    difficulty: 'medium'
  });

  // Tips
  const [tipsForm, setTipsForm] = useState({
    interview_stage: 'general',
    role_level: 'mid'
  });

  // Checklist
  const [checklistForm, setChecklistForm] = useState({
    interview_date: '',
    interview_type: 'general'
  });

  const handlePrepareForInterview = async () => {
    setState({ ...state, loading: true, error: null, result: null });

    try {
      const response = await fetch('http://localhost:8000/api/agents/interview-prep/prepare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(prepForm)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setState({ ...state, loading: false, result: data });
      } else {
        setState({ ...state, loading: false, error: data.error || 'Preparation failed' });
      }
    } catch (err) {
      setState({
        ...state,
        loading: false,
        error: err instanceof Error ? err.message : 'Unknown error'
      });
    }
  };

  const handleGenerateQuestions = async () => {
    setState({ ...state, loading: true, error: null, result: null });

    try {
      const response = await fetch('http://localhost:8000/api/agents/interview-prep/generate-questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(questionForm)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setState({ ...state, loading: false, result: data });
      } else {
        setState({ ...state, loading: false, error: data.error || 'Question generation failed' });
      }
    } catch (err) {
      setState({
        ...state,
        loading: false,
        error: err instanceof Error ? err.message : 'Unknown error'
      });
    }
  };

  const handlePrepareSTAR = async () => {
    setState({ ...state, loading: true, error: null, result: null });

    try {
      const response = await fetch('http://localhost:8000/api/agents/interview-prep/star-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(starForm)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setState({ ...state, loading: false, result: data });
      } else {
        setState({ ...state, loading: false, error: data.error || 'STAR preparation failed' });
      }
    } catch (err) {
      setState({
        ...state,
        loading: false,
        error: err instanceof Error ? err.message : 'Unknown error'
      });
    }
  };

  const handleStartMockInterview = async () => {
    setState({ ...state, loading: true, error: null, result: null });

    try {
      const response = await fetch('http://localhost:8000/api/agents/interview-prep/mock-interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockForm)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setState({ ...state, loading: false, result: data });
      } else {
        setState({ ...state, loading: false, error: data.error || 'Mock interview failed' });
      }
    } catch (err) {
      setState({
        ...state,
        loading: false,
        error: err instanceof Error ? err.message : 'Unknown error'
      });
    }
  };

  const handleGetTips = async () => {
    setState({ ...state, loading: true, error: null, result: null });

    try {
      const response = await fetch('http://localhost:8000/api/agents/interview-prep/tips', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tipsForm)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setState({ ...state, loading: false, result: data });
      } else {
        setState({ ...state, loading: false, error: data.error || 'Tips retrieval failed' });
      }
    } catch (err) {
      setState({
        ...state,
        loading: false,
        error: err instanceof Error ? err.message : 'Unknown error'
      });
    }
  };

  const handleGetChecklist = async () => {
    setState({ ...state, loading: true, error: null, result: null });

    try {
      const response = await fetch('http://localhost:8000/api/agents/interview-prep/checklist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(checklistForm)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setState({ ...state, loading: false, result: data });
      } else {
        setState({ ...state, loading: false, error: data.error || 'Checklist generation failed' });
      }
    } catch (err) {
      setState({
        ...state,
        loading: false,
        error: err instanceof Error ? err.message : 'Unknown error'
      });
    }
  };

  const loadSampleData = (tab: string) => {
    switch(tab) {
      case 'prepare':
        setPrepForm({
          company_name: 'Google',
          job_title: 'Senior Software Engineer',
          job_description: 'We are looking for an experienced software engineer to join our team...',
          interview_date: '2025-12-15',
          interview_type: 'technical'
        });
        break;
      case 'questions':
        setQuestionForm({
          job_title: 'Product Manager',
          job_description: 'Lead product strategy and development for our flagship products...',
          company_name: 'Microsoft',
          question_type: 'mixed'
        });
        break;
      case 'star':
        setStarForm({
          question: 'Tell me about a time when you faced a significant challenge at work. How did you handle it?',
          experience_context: 'I led a complex microservices migration project'
        });
        break;
      case 'mock':
        setMockForm({
          job_title: 'Data Scientist',
          focus_area: 'technical',
          difficulty: 'senior'
        });
        break;
      case 'tips':
        setTipsForm({
          interview_stage: 'technical',
          role_level: 'senior'
        });
        break;
      case 'checklist':
        setChecklistForm({
          interview_date: '2025-12-20',
          interview_type: 'video'
        });
        break;
    }
  };

  const renderTabContent = () => {
    switch(state.activeTab) {
      case 'prepare':
        return (
          <div className="tab-content">
            <h2>🎯 Comprehensive Interview Preparation</h2>
            <p>Get a complete preparation plan including company research, questions, and checklist.</p>

            <div className="form-group">
              <label>Company Name *</label>
              <input
                type="text"
                value={prepForm.company_name}
                onChange={(e) => setPrepForm({...prepForm, company_name: e.target.value})}
                placeholder="e.g., Google, Microsoft, Startup Inc."
              />
            </div>

            <div className="form-group">
              <label>Job Title *</label>
              <input
                type="text"
                value={prepForm.job_title}
                onChange={(e) => setPrepForm({...prepForm, job_title: e.target.value})}
                placeholder="e.g., Senior Software Engineer"
              />
            </div>

            <div className="form-group">
              <label>Job Description</label>
              <textarea
                value={prepForm.job_description}
                onChange={(e) => setPrepForm({...prepForm, job_description: e.target.value})}
                placeholder="Paste the job description here..."
                rows={6}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Interview Date</label>
                <input
                  type="date"
                  value={prepForm.interview_date}
                  onChange={(e) => setPrepForm({...prepForm, interview_date: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Interview Type</label>
                <select
                  value={prepForm.interview_type}
                  onChange={(e) => setPrepForm({...prepForm, interview_type: e.target.value})}
                >
                  <option value="general">General</option>
                  <option value="phone">Phone Screen</option>
                  <option value="video">Video</option>
                  <option value="in-person">In-Person</option>
                  <option value="technical">Technical</option>
                  <option value="behavioral">Behavioral</option>
                  <option value="panel">Panel</option>
                  <option value="final">Final</option>
                </select>
              </div>
            </div>

            <div className="button-group">
              <button onClick={handlePrepareForInterview} disabled={state.loading || !prepForm.company_name || !prepForm.job_title}>
                {state.loading ? 'Preparing...' : 'Prepare for Interview'}
              </button>
              <button onClick={() => loadSampleData('prepare')} className="secondary">
                Load Sample Data
              </button>
            </div>
          </div>
        );

      case 'questions':
        return (
          <div className="tab-content">
            <h2>❓ Generate Interview Questions</h2>
            <p>Get relevant questions for your role and company.</p>

            <div className="form-group">
              <label>Job Title *</label>
              <input
                type="text"
                value={questionForm.job_title}
                onChange={(e) => setQuestionForm({...questionForm, job_title: e.target.value})}
                placeholder="e.g., Product Manager"
              />
            </div>

            <div className="form-group">
              <label>Company Name</label>
              <input
                type="text"
                value={questionForm.company_name}
                onChange={(e) => setQuestionForm({...questionForm, company_name: e.target.value})}
                placeholder="e.g., Amazon"
              />
            </div>

            <div className="form-group">
              <label>Job Description</label>
              <textarea
                value={questionForm.job_description}
                onChange={(e) => setQuestionForm({...questionForm, job_description: e.target.value})}
                placeholder="Optional: Paste job description for more relevant questions"
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Question Type</label>
              <select
                value={questionForm.question_type}
                onChange={(e) => setQuestionForm({...questionForm, question_type: e.target.value})}
              >
                <option value="mixed">Mixed (Recommended)</option>
                <option value="behavioral">Behavioral (STAR)</option>
                <option value="technical">Technical</option>
                <option value="situational">Situational</option>
              </select>
            </div>

            <div className="button-group">
              <button onClick={handleGenerateQuestions} disabled={state.loading || !questionForm.job_title}>
                {state.loading ? 'Generating...' : 'Generate Questions'}
              </button>
              <button onClick={() => loadSampleData('questions')} className="secondary">
                Load Sample Data
              </button>
            </div>
          </div>
        );

      case 'star':
        return (
          <div className="tab-content">
            <h2>⭐ STAR Format Answer Preparation</h2>
            <p>Structure your answers using Situation, Task, Action, Result format.</p>

            <div className="form-group">
              <label>Interview Question *</label>
              <textarea
                value={starForm.question}
                onChange={(e) => setStarForm({...starForm, question: e.target.value})}
                placeholder="Enter the interview question you want to prepare for..."
                rows={3}
              />
            </div>

            <div className="form-group">
              <label>Your Experience Context</label>
              <textarea
                value={starForm.experience_context}
                onChange={(e) => setStarForm({...starForm, experience_context: e.target.value})}
                placeholder="Optional: Brief context about relevant experience or project..."
                rows={3}
              />
            </div>

            <div className="button-group">
              <button onClick={handlePrepareSTAR} disabled={state.loading || !starForm.question}>
                {state.loading ? 'Preparing...' : 'Prepare STAR Answer'}
              </button>
              <button onClick={() => loadSampleData('star')} className="secondary">
                Load Sample Data
              </button>
            </div>
          </div>
        );

      case 'mock':
        return (
          <div className="tab-content">
            <h2>🎭 Mock Interview Practice</h2>
            <p>Practice with realistic interview questions and self-evaluation.</p>

            <div className="form-group">
              <label>Job Title *</label>
              <input
                type="text"
                value={mockForm.job_title}
                onChange={(e) => setMockForm({...mockForm, job_title: e.target.value})}
                placeholder="e.g., Data Scientist"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Focus Area</label>
                <select
                  value={mockForm.focus_area}
                  onChange={(e) => setMockForm({...mockForm, focus_area: e.target.value})}
                >
                  <option value="general">General</option>
                  <option value="behavioral">Behavioral</option>
                  <option value="technical">Technical</option>
                  <option value="company-fit">Company Fit</option>
                </select>
              </div>

              <div className="form-group">
                <label>Difficulty Level</label>
                <select
                  value={mockForm.difficulty}
                  onChange={(e) => setMockForm({...mockForm, difficulty: e.target.value})}
                >
                  <option value="entry">Entry Level</option>
                  <option value="medium">Mid Level</option>
                  <option value="senior">Senior Level</option>
                </select>
              </div>
            </div>

            <div className="button-group">
              <button onClick={handleStartMockInterview} disabled={state.loading || !mockForm.job_title}>
                {state.loading ? 'Starting...' : 'Start Mock Interview'}
              </button>
              <button onClick={() => loadSampleData('mock')} className="secondary">
                Load Sample Data
              </button>
            </div>
          </div>
        );

      case 'tips':
        return (
          <div className="tab-content">
            <h2>💡 Interview Tips & Strategies</h2>
            <p>Get expert tips based on interview stage and role level.</p>

            <div className="form-row">
              <div className="form-group">
                <label>Interview Stage</label>
                <select
                  value={tipsForm.interview_stage}
                  onChange={(e) => setTipsForm({...tipsForm, interview_stage: e.target.value})}
                >
                  <option value="general">General</option>
                  <option value="phone-screen">Phone Screen</option>
                  <option value="technical">Technical</option>
                  <option value="behavioral">Behavioral</option>
                  <option value="panel">Panel</option>
                  <option value="final">Final Round</option>
                </select>
              </div>

              <div className="form-group">
                <label>Role Level</label>
                <select
                  value={tipsForm.role_level}
                  onChange={(e) => setTipsForm({...tipsForm, role_level: e.target.value})}
                >
                  <option value="entry">Entry Level</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior Level</option>
                  <option value="executive">Executive</option>
                </select>
              </div>
            </div>

            <div className="button-group">
              <button onClick={handleGetTips} disabled={state.loading}>
                {state.loading ? 'Loading...' : 'Get Interview Tips'}
              </button>
              <button onClick={() => loadSampleData('tips')} className="secondary">
                Load Sample Data
              </button>
            </div>
          </div>
        );

      case 'checklist':
        return (
          <div className="tab-content">
            <h2>📋 Preparation Checklist</h2>
            <p>Get a comprehensive timeline-based preparation checklist.</p>

            <div className="form-row">
              <div className="form-group">
                <label>Interview Date</label>
                <input
                  type="date"
                  value={checklistForm.interview_date}
                  onChange={(e) => setChecklistForm({...checklistForm, interview_date: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Interview Type</label>
                <select
                  value={checklistForm.interview_type}
                  onChange={(e) => setChecklistForm({...checklistForm, interview_type: e.target.value})}
                >
                  <option value="general">General</option>
                  <option value="phone">Phone</option>
                  <option value="video">Video</option>
                  <option value="in-person">In-Person</option>
                  <option value="technical">Technical</option>
                </select>
              </div>
            </div>

            <div className="button-group">
              <button onClick={handleGetChecklist} disabled={state.loading}>
                {state.loading ? 'Generating...' : 'Get Checklist'}
              </button>
              <button onClick={() => loadSampleData('checklist')} className="secondary">
                Load Sample Data
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const renderResult = () => {
    if (!state.result) return null;

    const output = state.result.preparation_plan || state.result.questions ||
                   state.result.star_framework || state.result.mock_interview ||
                   state.result.tips || state.result.checklist || state.result.output;

    return (
      <div className="result-container">
        <h3>Results</h3>
        <div className="result-content">
          <pre>{output}</pre>
        </div>
      </div>
    );
  };

  return (
    <div className="interview-prep-dashboard">
      <div className="dashboard-header">
        <h1>🎯 Interview Prep Agent</h1>
        <p>AI-powered interview preparation to help you ace your next interview</p>
      </div>

      <div className="tab-navigation">
        <button
          className={state.activeTab === 'prepare' ? 'active' : ''}
          onClick={() => setState({...state, activeTab: 'prepare', result: null, error: null})}
        >
          🎯 Prepare
        </button>
        <button
          className={state.activeTab === 'questions' ? 'active' : ''}
          onClick={() => setState({...state, activeTab: 'questions', result: null, error: null})}
        >
          ❓ Questions
        </button>
        <button
          className={state.activeTab === 'star' ? 'active' : ''}
          onClick={() => setState({...state, activeTab: 'star', result: null, error: null})}
        >
          ⭐ STAR
        </button>
        <button
          className={state.activeTab === 'mock' ? 'active' : ''}
          onClick={() => setState({...state, activeTab: 'mock', result: null, error: null})}
        >
          🎭 Mock
        </button>
        <button
          className={state.activeTab === 'tips' ? 'active' : ''}
          onClick={() => setState({...state, activeTab: 'tips', result: null, error: null})}
        >
          💡 Tips
        </button>
        <button
          className={state.activeTab === 'checklist' ? 'active' : ''}
          onClick={() => setState({...state, activeTab: 'checklist', result: null, error: null})}
        >
          📋 Checklist
        </button>
      </div>

      <div className="dashboard-content">
        {renderTabContent()}

        {state.loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Processing your request...</p>
          </div>
        )}

        {state.error && (
          <div className="error-message">
            <strong>Error:</strong> {state.error}
          </div>
        )}

        {renderResult()}
      </div>
    </div>
  );
};

export default InterviewPrepDashboard;
