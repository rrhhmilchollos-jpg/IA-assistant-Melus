import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import AuthCallback from "./pages/AuthCallback";
import Dashboard from "./pages/Dashboard";
import HomePage from "./pages/HomePage";
import Pricing from "./pages/Pricing";
import Success from "./pages/Success";
import AdminPanel from "./pages/AdminPanel";
import GeneratorPage from "./pages/GeneratorPage";
import WorkspacePage from "./pages/WorkspacePage";
import MarketplacePage from "./pages/MarketplacePage";

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
      <Route path="/generator" element={
        <ProtectedRoute>
          <GeneratorPage />
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
      {/* Default redirect to home */}
      <Route path="/" element={<Navigate to="/home" replace />} />
      <Route path="*" element={<Navigate to="/home" replace />} />
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
