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

// Add request interceptor to include session token
apiClient.interceptors.request.use((config) => {
  const sessionToken = localStorage.getItem('session_token');
  if (sessionToken) {
    config.headers['X-Session-Token'] = sessionToken;
  }
  return config;
});

// Helper to save session token
export const saveSessionToken = (token) => {
  if (token) {
    localStorage.setItem('session_token', token);
  }
};

// Helper to clear session token
export const clearSessionToken = () => {
  localStorage.removeItem('session_token');
};

// Auth API
export const authAPI = {
  register: async (email, password, name) => {
    const response = await apiClient.post('/auth/register', { 
      email, 
      password, 
      name 
    });
    // Save session token for future requests
    if (response.data.session_token) {
      saveSessionToken(response.data.session_token);
    }
    return response.data;
  },
  
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { 
      email, 
      password 
    });
    // Save session token for future requests
    if (response.data.session_token) {
      saveSessionToken(response.data.session_token);
    }
    return response.data;
  },
  
  createSession: async (sessionId) => {
    const response = await apiClient.post('/auth/session', { session_id: sessionId });
    // Save session token for future requests
    if (response.data.session_token) {
      saveSessionToken(response.data.session_token);
    }
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
  
  logout: async () => {
    clearSessionToken();
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
};

// Models API
export const modelsAPI = {
  getAll: async () => {
    const response = await apiClient.get('/models');
    return response.data;
  },
};

// Conversations API
export const conversationsAPI = {
  getAll: async () => {
    const response = await apiClient.get('/conversations');
    return response.data;
  },
  
  create: async (title = 'Nueva Conversación', model = 'gpt-4o', forkFrom = null) => {
    const response = await apiClient.post('/conversations', { 
      title,
      model,
      fork_from: forkFrom
    });
    return response.data;
  },
  
  fork: async (conversationId) => {
    const response = await apiClient.post('/conversations', {
      title: 'Fork',
      fork_from: conversationId
    });
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
  
  exportConversation: async (conversationId) => {
    // Get messages and format for export
    const messages = await conversationsAPI.getMessages(conversationId);
    const formatted = messages.map(m => 
      `${m.role === 'user' ? 'Usuario' : 'Assistant Melus'}: ${m.content}`
    ).join('\n\n');
    
    // Create downloadable file
    const blob = new Blob([formatted], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation-${conversationId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};

// Messages API
export const messagesAPI = {
  edit: async (messageId, content) => {
    const response = await apiClient.put(`/messages/${messageId}`, { content });
    return response.data;
  },
  
  regenerate: async (messageId) => {
    const response = await apiClient.post(`/messages/${messageId}/regenerate`);
    return response.data;
  },
};

// Credits API
export const creditsAPI = {
  getBalance: async () => {
    const response = await apiClient.get('/credits');
    return response.data;
  },
  
  getTransactions: async () => {
    const response = await apiClient.get('/credits/transactions');
    return response.data;
  },
  
  getPackages: async () => {
    const response = await apiClient.get('/credits/packages');
    return response.data;
  },
  
  createCheckout: async (packageId = null, customAmount = null, promoCode = null) => {
    const originUrl = window.location.origin;
    const payload = {
      origin_url: originUrl,
    };
    
    if (packageId) {
      payload.package_id = packageId;
    }
    
    if (customAmount) {
      payload.custom_amount = customAmount;
    }
    
    if (promoCode) {
      payload.promo_code = promoCode;
    }
    
    const response = await apiClient.post('/credits/checkout', payload);
    return response.data;
  },
  
  getCheckoutStatus: async (sessionId) => {
    const response = await apiClient.get(`/credits/checkout/status/${sessionId}`);
    return response.data;
  },
};

export default apiClient;
