// FILE: frontend/src/main.tsx

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App.tsx';
import { store } from './store';
import ErrorBoundary from './components/common/ErrorBoundary';
import { WebSocketProvider } from './components/Providers/WebSocketProvider.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <ErrorBoundary>
          <WebSocketProvider>
            <App />
          </WebSocketProvider>
        </ErrorBoundary>
      </BrowserRouter>
    </Provider>
  </StrictMode>,
);