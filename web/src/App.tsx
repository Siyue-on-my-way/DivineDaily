import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ui/Toast';
import LoginModal from './components/mobile/LoginModal';
import { MobileLayout } from './components/mobile/MobileLayout';
import HomePage from './pages/HomePage';
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
            {/* 普通用户路由 - 使用 MobileLayout */}
            <Route path="/" element={<MobileLayout><HomePage /></MobileLayout>} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/divination" element={<MobileLayout><DivinationPage /></MobileLayout>} />
            <Route path="/tarot" element={<MobileLayout><TarotPage /></MobileLayout>} />
            <Route path="/profile" element={<MobileLayout><ProfilePage /></MobileLayout>} />
            <Route path="/history" element={<MobileLayout><HistoryPage /></MobileLayout>} />
            <Route path="/history/:id" element={<MobileLayout><HistoryDetailPage /></MobileLayout>} />
            <Route path="/about" element={<MobileLayout><AboutPage /></MobileLayout>} />
            
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
