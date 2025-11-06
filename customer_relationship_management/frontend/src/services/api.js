import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }).then(res => res.data),
  
  register: (name, email, password) => 
    api.post('/auth/register', { name, email, password }).then(res => res.data),
  
  getCurrentUser: (token) => 
    api.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => res.data.user)
};

export const contactsAPI = {
  getAll: () => api.get('/contacts').then(res => res.data),
  create: (contact) => api.post('/contacts', contact).then(res => res.data),
  update: (id, contact) => api.put(`/contacts/${id}`, contact).then(res => res.data),
  delete: (id) => api.delete(`/contacts/${id}`).then(res => res.data)
};