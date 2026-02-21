import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { authAPI } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { login, checkAuth } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Check for error in URL params
        const error = searchParams.get('error');
        if (error) {
          console.error('OAuth error:', error);
          navigate(`/?error=${error}`);
          return;
        }

        // CASE 1: Token from self-hosted OAuth (Google/Facebook)
        const token = searchParams.get('token');
        if (token) {
          // Store the token
          localStorage.setItem('session_token', token);
          
          // Fetch user data with the new token
          try {
            const userData = await authAPI.getCurrentUser();
            login(userData);
            navigate('/home', { replace: true });
          } catch (err) {
            console.error('Error fetching user after OAuth:', err);
            navigate('/?error=auth_failed');
          }
          return;
        }

        // CASE 2: Legacy session_id from Emergent OAuth (keeping for backwards compatibility)
        const hash = location.hash;
        const sessionIdMatch = hash.match(/session_id=([^&]+)/);
        
        if (sessionIdMatch) {
          const sessionId = sessionIdMatch[1];
          const response = await authAPI.createSession(sessionId);
          login(response.user);
          navigate('/home', { replace: true, state: { user: response.user } });
          return;
        }

        // No valid auth params found
        navigate('/');
      } catch (error) {
        console.error('Auth error:', error);
        navigate('/?error=auth_error');
      }
    };

    processAuth();
  }, [location, navigate, login, searchParams, checkAuth]);

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