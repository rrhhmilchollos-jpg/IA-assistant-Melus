import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const apiClient = axios.create({
  baseURL: API,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API
export const authAPI = {
  createSession: async (sessionId) => {
    const response = await apiClient.post('/auth/session', { session_id: sessionId });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
  
  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
};

// Conversations API
export const conversationsAPI = {
  getAll: async () => {
    const response = await apiClient.get('/conversations');
    return response.data;
  },
  
  create: async (title = 'Nueva Conversación') => {
    const response = await apiClient.post('/conversations', { title });
    return response.data;
  },
  
  delete: async (conversationId) => {
    const response = await apiClient.delete(`/conversations/${conversationId}`);
    return response.data;
  },
  
  getMessages: async (conversationId) => {
    const response = await apiClient.get(`/conversations/${conversationId}/messages`);
    return response.data;
  },
  
  sendMessage: async (conversationId, content) => {
    const response = await apiClient.post(`/conversations/${conversationId}/messages`, { content });
    return response.data;
  },
};

// Credits API
export const creditsAPI = {
  getBalance: async () => {
    const response = await apiClient.get('/credits');
    return response.data;
  },
  
  getPackages: async () => {
    const response = await apiClient.get('/credits/packages');
    return response.data;
  },
  
  createCheckout: async (packageId) => {
    const originUrl = window.location.origin;
    const response = await apiClient.post('/credits/checkout', {
      package_id: packageId,
      origin_url: originUrl,
    });
    return response.data;
  },
  
  getCheckoutStatus: async (sessionId) => {
    const response = await apiClient.get(`/credits/checkout/status/${sessionId}`);
    return response.data;
  },
};

export default apiClient;