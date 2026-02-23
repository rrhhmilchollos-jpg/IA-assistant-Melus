import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import AuthCallback from "./pages/AuthCallback";
import Dashboard from "./pages/Dashboard";
import HomePage from "./pages/HomePage";
import LandingPage from "./pages/LandingPageNew";
import Pricing from "./pages/Pricing";
import Success from "./pages/Success";
import AdminPanel from "./pages/AdminPanel";
import WorkspacePage from "./pages/WorkspacePage";
import MarketplacePage from "./pages/MarketplacePage";
import OrchestratorPage from "./pages/OrchestratorPage";
import LearningDashboard from "./pages/LearningDashboard";
import AgentDashboard from "./pages/AgentDashboard";
import AIBuilder from "./pages/AIBuilder";

// Landing page route - shows landing for unauthenticated, redirects to home for authenticated
function LandingPageRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  
  return isAuthenticated ? <Navigate to="/home" replace /> : <LandingPage />;
}

// AppRouter component to handle session_id detection
function AppRouter() {
  const location = useLocation();
  
  // Check URL fragment for session_id synchronously during render
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/pricing" element={<Pricing />} />
      <Route path="/success" element={
        <ProtectedRoute>
          <Success />
        </ProtectedRoute>
      } />
      {/* Home - Main page like Emergent.sh */}
      <Route path="/home" element={
        <ProtectedRoute>
          <HomePage />
        </ProtectedRoute>
      } />
      {/* Dashboard - Chat interface */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      {/* Workspace - New IDE interface */}
      <Route path="/workspace" element={
        <ProtectedRoute>
          <WorkspacePage />
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <ProtectedRoute>
          <AdminPanel />
        </ProtectedRoute>
      } />
      {/* Marketplace */}
      <Route path="/marketplace" element={
        <ProtectedRoute>
          <MarketplacePage />
        </ProtectedRoute>
      } />
      {/* Orchestrator - Multi-Agent Dashboard */}
      <Route path="/orchestrator" element={
        <ProtectedRoute>
          <OrchestratorPage />
        </ProtectedRoute>
      } />
      {/* Learning Dashboard - Continuous Learning System */}
      <Route path="/learning" element={
        <ProtectedRoute>
          <LearningDashboard />
        </ProtectedRoute>
      } />
      {/* AI Builder - Chat interface to build apps */}
      <Route path="/build" element={
        <ProtectedRoute>
          <AIBuilder />
        </ProtectedRoute>
      } />
      {/* Agent Dashboard */}
      <Route path="/agents" element={
        <ProtectedRoute>
          <AgentDashboard />
        </ProtectedRoute>
      } />
      {/* Landing page for unauthenticated users, redirect to home for authenticated */}
      <Route path="/" element={<LandingPageRoute />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
