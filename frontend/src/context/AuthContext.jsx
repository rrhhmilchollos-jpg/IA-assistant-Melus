import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { authAPI, clearSessionToken } from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [initialCheckDone, setInitialCheckDone] = useState(false);

  const checkAuth = useCallback(async () => {
    // Don't check if we're already authenticated with user data
    if (isAuthenticated && user) {
      setIsLoading(false);
      return;
    }
    
    // Check if there's a session token stored
    const hasToken = localStorage.getItem('session_token');
    if (!hasToken) {
      setIsLoading(false);
      setInitialCheckDone(true);
      return;
    }
    
    setIsLoading(true);
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      // Clear invalid token
      clearSessionToken();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
      setInitialCheckDone(true);
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    // Check auth on mount only once
    if (!initialCheckDone) {
      checkAuth();
    }
  }, [checkAuth, initialCheckDone]);

  const login = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    setIsLoading(false);
    setInitialCheckDone(true);
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearSessionToken();
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const updateCredits = (newCredits) => {
    if (user) {
      setUser({ ...user, credits: newCredits });
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      isAuthenticated, 
      isLoading, 
      login, 
      logout, 
      checkAuth,
      updateCredits
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};