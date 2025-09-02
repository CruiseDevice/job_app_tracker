import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { WebSocketProvider } from './components/Providers/WebSocketProvider';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import { ApplicationsDashboard } from './components/Applications/ApplicationsDashboard';
import Settings from './components/Settings/Settings';

function App() {
  return (
    <WebSocketProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/applications" element={<ApplicationsDashboard />} />
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