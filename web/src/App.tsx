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
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <MobileLayout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/divination" element={<DivinationPage />} />
              <Route path="/tarot" element={<TarotPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/history/:id" element={<HistoryDetailPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </MobileLayout>
          <LoginModal />
          <ToastContainer />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
