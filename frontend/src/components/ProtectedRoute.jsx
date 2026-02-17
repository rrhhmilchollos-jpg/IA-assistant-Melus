import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const { isAuthenticated, isLoading, checkAuth, user } = useAuth();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const verifyAuth = async () => {
      // Skip check if already authenticated (e.g., just registered/logged in)
      if (isAuthenticated && user) {
        setChecking(false);
        return;
      }
      
      // Skip check if user data was passed from AuthCallback
      if (location.state?.user) {
        setChecking(false);
        return;
      }

      // Check authentication status only if not already authenticated
      await checkAuth();
      setChecking(false);
    };

    verifyAuth();
  }, [checkAuth, location.state, isAuthenticated, user]);

  // Show loading while checking authentication
  if (checking || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Render protected content
  return children;
};

export default ProtectedRoute;
