import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authAPI } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Extract session_id from URL fragment
        const hash = location.hash;
        const sessionIdMatch = hash.match(/session_id=([^&]+)/);
        
        if (!sessionIdMatch) {
          navigate('/login');
          return;
        }

        const sessionId = sessionIdMatch[1];

        // Exchange session_id for session_token
        const response = await authAPI.createSession(sessionId);
        
        // Set user in context
        login(response.user);

        // Redirect to dashboard
        navigate('/dashboard', { replace: true, state: { user: response.user } });
      } catch (error) {
        console.error('Auth error:', error);
        navigate('/login');
      }
    };

    processAuth();
  }, [location, navigate, login]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <Loader2 className="w-12 h-12 animate-spin text-purple-600 mx-auto mb-4" />
        <p className="text-gray-600">Autenticando...</p>
      </div>
    </div>
  );
};

export default AuthCallback;