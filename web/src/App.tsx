import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ui/Toast';
import LoginModal from './components/mobile/LoginModal';
import { ResponsiveLayout } from './components/desktop/ResponsiveLayout';
import HomePageResponsive from './pages/HomePageResponsive';
import DivinationPage from './pages/DivinationPage';
import TarotPage from './pages/TarotPage';
import ProfilePage from './pages/ProfilePage';
import HistoryPage from './pages/HistoryPage';
import HistoryDetailPage from './pages/HistoryDetailPage';
import AboutPage from './pages/AboutPage';
import RegisterPage from './pages/RegisterPage';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>
            {/* 使用响应式布局 */}
            <Route path="/" element={<ResponsiveLayout><HomePageResponsive /></ResponsiveLayout>} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/divination" element={<ResponsiveLayout><DivinationPage /></ResponsiveLayout>} />
            <Route path="/tarot" element={<ResponsiveLayout><TarotPage /></ResponsiveLayout>} />
            <Route path="/profile" element={<ResponsiveLayout><ProfilePage /></ResponsiveLayout>} />
            <Route path="/history" element={<ResponsiveLayout><HistoryPage /></ResponsiveLayout>} />
            <Route path="/history/:id" element={<ResponsiveLayout><HistoryDetailPage /></ResponsiveLayout>} />
            <Route path="/about" element={<ResponsiveLayout><AboutPage /></ResponsiveLayout>} />
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <LoginModal />
          <ToastContainer />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
