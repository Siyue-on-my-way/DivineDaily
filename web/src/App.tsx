import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ui/Toast';
import LoginModal from './components/mobile/LoginModal';
import { ResponsiveLayout } from './components/desktop/ResponsiveLayout';
import { IdleRoutePrefetch } from './components/IdleRoutePrefetch';
import './App.css';

const HomePageResponsive = lazy(() => import('./pages/HomePageResponsive'));
const DivinationPage = lazy(() => import('./pages/DivinationPage'));
const TarotPage = lazy(() => import('./pages/TarotPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const HistoryPage = lazy(() => import('./pages/HistoryPage'));
const HistoryDetailPage = lazy(() => import('./pages/HistoryDetailPage'));
const InsightsPage = lazy(() => import('./pages/InsightsPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const SharePage = lazy(() => import('./pages/SharePage'));

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <IdleRoutePrefetch />
          <Suspense fallback={<div className="app-loading" role="status" aria-live="polite"><span className="app-loading__spinner" aria-hidden /><span className="app-loading__text">加载中…</span></div>}>
            <Routes>
              {/* 使用响应式布局 */}
              <Route path="/" element={<ResponsiveLayout><HomePageResponsive /></ResponsiveLayout>} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/divination" element={<ResponsiveLayout><DivinationPage /></ResponsiveLayout>} />
              <Route path="/tarot" element={<ResponsiveLayout><TarotPage /></ResponsiveLayout>} />
              <Route path="/profile" element={<ResponsiveLayout><ProfilePage /></ResponsiveLayout>} />
              <Route path="/history" element={<ResponsiveLayout><HistoryPage /></ResponsiveLayout>} />
              <Route path="/history/:id" element={<ResponsiveLayout><HistoryDetailPage /></ResponsiveLayout>} />
              <Route path="/insights" element={<ResponsiveLayout><InsightsPage /></ResponsiveLayout>} />
              <Route path="/about" element={<ResponsiveLayout><AboutPage /></ResponsiveLayout>} />
              
              {/* 分享页面（无需布局） */}
              <Route path="/share/:shareToken" element={<SharePage />} />
              
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
          <LoginModal />
          <ToastContainer />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
