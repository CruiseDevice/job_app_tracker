import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { WebSocketProvider } from './components/Providers/WebSocketProvider';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import { ApplicationsDashboard } from './components/Applications/ApplicationsDashboard';
import Settings from './components/Settings/Settings';

// Agent Dashboards
import EmailAnalystDashboard from './components/Agents/EmailAnalyst/EmailAnalystDashboard';
import FollowUpAgentDashboard from './components/Agents/FollowUp/FollowUpAgentDashboard';
import ApplicationManagerDashboard from './components/Agents/ApplicationManager/ApplicationManagerDashboard';
import JobHunterDashboard from './components/Agents/JobHunter/JobHunterDashboard';
import ResumeWriterDashboard from './components/Agents/ResumeWriter/ResumeWriterDashboard';
import InterviewPrepDashboard from './components/Agents/InterviewPrep/InterviewPrepDashboard';
import AnalyticsDashboard from './components/Agents/Analytics/AnalyticsDashboard';
import OrchestratorDashboard from './components/Agents/Orchestrator/OrchestratorDashboard';

function App() {
  return (
    <WebSocketProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/applications" element={<ApplicationsDashboard />} />

          {/* Agent Routes */}
          <Route path="/agents/email-analyst" element={<EmailAnalystDashboard />} />
          <Route path="/agents/application-manager" element={<ApplicationManagerDashboard />} />
          <Route path="/agents/followup" element={<FollowUpAgentDashboard />} />
          <Route path="/agents/job-hunter" element={<JobHunterDashboard />} />
          <Route path="/agents/resume-writer" element={<ResumeWriterDashboard />} />
          <Route path="/agents/interview-prep" element={<InterviewPrepDashboard />} />
          <Route path="/agents/analytics" element={<AnalyticsDashboard />} />
          <Route path="/agents/orchestrator" element={<OrchestratorDashboard />} />

          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </WebSocketProvider>
  );
}

export default App;