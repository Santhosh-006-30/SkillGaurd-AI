import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import DashboardLayout from './layouts/DashboardLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CentresPage from './pages/CentresPage';
import CentreDetailPage from './pages/CentreDetailPage';
import AlertsPage from './pages/AlertsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import EvaluationPage from './pages/EvaluationPage';
import ReportsPage from './pages/ReportsPage';
import PrivacyPage from './pages/PrivacyPage';
import SystemPage from './pages/SystemPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0F19] flex items-center justify-center text-slate-400 font-mono text-sm">
        Authenticating session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="centres" element={<CentresPage />} />
            <Route path="centres/:id" element={<CentreDetailPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="evaluation" element={<EvaluationPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="privacy" element={<PrivacyPage />} />
            <Route path="system" element={<SystemPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
