import React from 'react';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { store } from './store';
import { WebSocketProvider } from './components/Providers/WebSocketProvider';
import { RealTimeStats } from './components/Dashboard/RealTimeStats';
import { MonitoringControls } from './components/Dashboard/MonitoringControls';
import { RealTimeApplicationList } from './components/Applications/RealTimeApplicationList';

function App() {
  return (
    <Provider store={store}>
      <WebSocketProvider>
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <h1 className="text-3xl font-bold text-gray-900">
                Smart Job Application Tracker
              </h1>
            </div>
          </header>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="space-y-8">
              {/* Monitoring Controls */}
              <MonitoringControls />

              {/* Real-time Statistics */}
              <RealTimeStats />

              {/* Applications List */}
              <RealTimeApplicationList />
            </div>
          </main>

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
        </div>
      </WebSocketProvider>
    </Provider>
  );
}

export default App;