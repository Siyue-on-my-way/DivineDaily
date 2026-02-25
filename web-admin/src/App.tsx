import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './lib/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ui/Toast';
import LoginPage from './pages/LoginPage';
import AdminLayout from './components/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import LLMConfigPage from './pages/admin/LLMConfigPage';
import PromptConfigPage from './pages/admin/PromptConfigPage';
import UserManagement from './pages/admin/UserManagement';
import UserDetailPage from './pages/admin/UserDetailPage';
import ConfigManagement from './pages/ConfigManagement';
import './App.css';

// 受保护的路由组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>
            {/* 登录页面 */}
            <Route path="/admin/login" element={<LoginPage />} />
            
            {/* 管理后台路由 - 需要认证 */}
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminLayout />
              </ProtectedRoute>
            }>
              <Route index element={<AdminDashboard />} />
              <Route path="llm-config" element={<LLMConfigPage />} />
              <Route path="prompt-config" element={<PromptConfigPage />} />
              <Route path="users" element={<UserManagement />} />
              <Route path="users/:userId" element={<UserDetailPage />} />
              <Route path="config" element={<ConfigManagement />} />
            </Route>
            
            {/* 404 重定向 */}
            <Route path="*" element={<Navigate to="/admin" replace />} />
          </Routes>
          <ToastContainer />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
