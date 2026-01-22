import axios from 'axios';

const API_BASE_URL ='https://web-project-pvli.onrender.com';

// Store token in localStorage
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('token', token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Get token from localStorage
export const getAuthToken = () => {
  return localStorage.getItem('token');
};

// Initialize auth token on app load
export const initializeAuth = () => {
  const token = getAuthToken();
  if (token) {
    setAuthToken(token);
  }
};

// Login function
export const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      username,
      password
    });
    const { access_token, role, user_id } = response.data;
    setAuthToken(access_token);
    localStorage.setItem('userRole', role);
    localStorage.setItem('userId', user_id);
    return { success: true, role, user_id };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Login failed' 
    };
  }
};

// Logout function
export const logout = () => {
  setAuthToken(null);
  localStorage.removeItem('userRole');
  localStorage.removeItem('userId');
};

// Get current user info
export const getCurrentUser = async () => {
  try {
    const token = getAuthToken();
    if (!token) return null;
    
    const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    logout();
    return null;
  }
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!getAuthToken();
};

// Get user role
export const getUserRole = () => {
  return localStorage.getItem('userRole');
};
