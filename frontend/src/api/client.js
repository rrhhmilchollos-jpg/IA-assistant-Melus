import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Helper function to clear session
export const clearSessionToken = () => {
  localStorage.removeItem('session_token');
  localStorage.removeItem('user');
};

// Request interceptor to add session token
api.interceptors.request.use((config) => {
  const sessionToken = localStorage.getItem('session_token');
  if (sessionToken) {
    config.headers['X-Session-Token'] = sessionToken;
  }
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearSessionToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (email, password, name) => {
    const response = await api.post('/api/auth/register', { email, password, name });
    if (response.data.session_token) {
      localStorage.setItem('session_token', response.data.session_token);
    }
    return response.data;
  },
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    if (response.data.session_token) {
      localStorage.setItem('session_token', response.data.session_token);
    }
    return response.data;
  },
  logout: async () => {
    await api.post('/api/auth/logout');
    localStorage.removeItem('session_token');
    localStorage.removeItem('user');
  },
  getMe: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  createSession: async (sessionId) => {
    const response = await api.post('/api/auth/session', { session_id: sessionId });
    if (response.data.session_token) {
      localStorage.setItem('session_token', response.data.session_token);
    }
    return response.data;
  }
};

// Conversations API
export const conversationsAPI = {
  getAll: async () => {
    const response = await api.get('/api/conversations');
    return response.data;
  },
  create: async (title, model) => {
    const response = await api.post('/api/conversations', { title, model });
    return response.data;
  },
  delete: async (conversationId) => {
    const response = await api.delete(`/api/conversations/${conversationId}`);
    return response.data;
  },
  getMessages: async (conversationId) => {
    const response = await api.get(`/api/conversations/${conversationId}/messages`);
    return response.data;
  },
  sendMessage: async (conversationId, content) => {
    const response = await api.post(`/api/conversations/${conversationId}/messages`, { content });
    return response.data;
  },
  fork: async (conversationId) => {
    const response = await api.post('/api/conversations', { fork_from: conversationId });
    return response.data;
  },
  summarize: async (conversationId) => {
    const response = await api.post(`/api/conversations/${conversationId}/summarize`);
    return response.data;
  },
  save: async (conversationId) => {
    const response = await api.post(`/api/conversations/${conversationId}/save`);
    return response.data;
  },
  getCode: async (conversationId) => {
    const response = await api.get(`/api/conversations/${conversationId}/code`);
    return response.data;
  },
  getPreview: async (conversationId) => {
    const response = await api.get(`/api/conversations/${conversationId}/preview`);
    return response.data;
  }
};

// Messages API
export const messagesAPI = {
  edit: async (messageId, content) => {
    const response = await api.put(`/api/messages/${messageId}`, { content });
    return response.data;
  },
  regenerate: async (messageId) => {
    const response = await api.post(`/api/messages/${messageId}/regenerate`);
    return response.data;
  },
  rollback: async (messageId) => {
    const response = await api.post(`/api/messages/${messageId}/rollback`);
    return response.data;
  }
};

// Models API
export const modelsAPI = {
  getAll: async () => {
    const response = await api.get('/api/models');
    return response.data;
  }
};

// Credits API
export const creditsAPI = {
  getBalance: async () => {
    const response = await api.get('/api/credits');
    return response.data;
  },
  getPackages: async () => {
    const response = await api.get('/api/credits/packages');
    return response.data;
  },
  getSubscriptions: async () => {
    const response = await api.get('/api/credits/subscriptions');
    return response.data;
  },
  checkout: async (packageId, originUrl, promoCode = null, customAmount = null) => {
    const response = await api.post('/api/credits/checkout', {
      package_id: packageId,
      custom_amount: customAmount,
      promo_code: promoCode,
      origin_url: originUrl
    });
    return response.data;
  },
  subscribe: async (planId, originUrl) => {
    const response = await api.post('/api/credits/subscribe', {
      plan_id: planId,
      origin_url: originUrl
    });
    return response.data;
  },
  checkStatus: async (sessionId) => {
    const response = await api.get(`/api/credits/checkout/status/${sessionId}`);
    return response.data;
  },
  getTransactions: async () => {
    const response = await api.get('/api/credits/transactions');
    return response.data;
  },
  validatePromo: async (promoCode, amount) => {
    const response = await api.post('/api/credits/validate-promo', { promo_code: promoCode, amount });
    return response.data;
  },
  getUsage: async () => {
    const response = await api.get('/api/credits/usage');
    return response.data;
  }
};

// Attachments API
export const attachmentsAPI = {
  upload: async (fileData, fileName, fileType, conversationId = null) => {
    const response = await api.post('/api/attachments/upload', {
      file_data: fileData,
      file_name: fileName,
      file_type: fileType,
      conversation_id: conversationId
    });
    return response.data;
  },
  get: async (attachmentId) => {
    const response = await api.get(`/api/attachments/${attachmentId}`);
    return response.data;
  }
};

// Projects API
export const projectsAPI = {
  getAll: async () => {
    const response = await api.get('/api/projects');
    return response.data;
  },
  create: async (name, description) => {
    const response = await api.post('/api/projects', { name, description });
    return response.data;
  },
  get: async (projectId) => {
    const response = await api.get(`/api/projects/${projectId}`);
    return response.data;
  },
  update: async (projectId, data) => {
    const response = await api.put(`/api/projects/${projectId}`, data);
    return response.data;
  },
  delete: async (projectId) => {
    const response = await api.delete(`/api/projects/${projectId}`);
    return response.data;
  },
  getFiles: async (projectId) => {
    const response = await api.get(`/api/projects/${projectId}/files`);
    return response.data;
  },
  download: async (projectId) => {
    const response = await api.post(`/api/projects/${projectId}/download`);
    return response.data;
  }
};

// Agents API
export const agentsAPI = {
  analyze: async (description) => {
    const response = await api.post('/api/agents/analyze', { description });
    return response.data;
  },
  execute: async (agentType, task, context = {}, projectId = null) => {
    const response = await api.post('/api/agents/execute', {
      agent_type: agentType,
      task,
      context,
      project_id: projectId
    });
    return response.data;
  },
  generateApp: async (name, description) => {
    const response = await api.post('/api/agents/generate-app', { name, description });
    return response.data;
  },
  getStatus: async (projectId) => {
    const response = await api.get(`/api/agents/status/${projectId}`);
    return response.data;
  },
  getCosts: async () => {
    const response = await api.get('/api/agents/costs');
    return response.data;
  }
};

// Admin API
export const adminAPI = {
  getDashboard: async () => {
    const response = await api.get('/api/admin/dashboard');
    return response.data;
  },
  getUsers: async (limit = 50, skip = 0) => {
    const response = await api.get(`/api/admin/users?limit=${limit}&skip=${skip}`);
    return response.data;
  },
  updateUser: async (userId, data) => {
    const response = await api.put(`/api/admin/users/${userId}`, data);
    return response.data;
  },
  deleteUser: async (userId) => {
    const response = await api.delete(`/api/admin/users/${userId}`);
    return response.data;
  },
  getTransactions: async (limit = 100, skip = 0) => {
    const response = await api.get(`/api/admin/transactions?limit=${limit}&skip=${skip}`);
    return response.data;
  },
  getProjects: async (limit = 50, skip = 0) => {
    const response = await api.get(`/api/admin/projects?limit=${limit}&skip=${skip}`);
    return response.data;
  },
  getSystemHealth: async () => {
    const response = await api.get('/api/admin/system-health');
    return response.data;
  },
  getRevenueChart: async (days = 30) => {
    const response = await api.get(`/api/admin/revenue/chart?days=${days}`);
    return response.data;
  },
  getCreditCosts: async () => {
    const response = await api.get('/api/admin/settings/credit-costs');
    return response.data;
  },
  updateCreditCosts: async (costs) => {
    const response = await api.post('/api/admin/settings/credit-costs', costs);
    return response.data;
  }
};

export default api;
