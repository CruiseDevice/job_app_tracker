import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { WebSocketProvider } from './components/Providers/WebSocketProvider';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import { ApplicationsDashboard } from './components/Applications/ApplicationsDashboard';
import Settings from './components/Settings/Settings';
import EmailAnalystDashboard from './components/Agents/EmailAnalyst/EmailAnalystDashboard';
import FollowUpAgentDashboard from './components/Agents/FollowUp/FollowUpAgentDashboard';
import ResumeWriterDashboard from './components/Agents/ResumeWriter/ResumeWriterDashboard';

function App() {
  return (
    <WebSocketProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/applications" element={<ApplicationsDashboard />} />
          <Route path="/agents/email-analyst" element={<EmailAnalystDashboard />} />
          <Route path="/agents/followup" element={<FollowUpAgentDashboard />} />
          <Route path="/agents/resume-writer" element={<ResumeWriterDashboard />} />
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