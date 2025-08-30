import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add JWT token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
}, error => {
  return Promise.reject(error);
});

// Handle token refresh on 401 errors and add global error handling
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Add more detailed error logging
    console.error('API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method
    });

    // Handle 401 errors (authentication)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('http://localhost:8000/api/auth/refresh/', {
            refresh: refreshToken
          });

          localStorage.setItem('access_token', response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          console.error('Token refresh failed:', refreshError);
          window.location.href = '/components/Login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/components/Login';
        return Promise.reject(error);
      }
    }

    // Enhanced error object with more details
    const enhancedError = {
      ...error,
      isAxiosError: true,
      timestamp: new Date().toISOString(),
      requestUrl: error.config?.url,
      requestMethod: error.config?.method
    };

    // For network errors, add more context
    if (!error.response) {
      enhancedError.errorType = 'NETWORK_ERROR';
      enhancedError.userMessage = 'Network connection failed. Please check your internet connection.';
    } else {
      enhancedError.errorType = 'HTTP_ERROR';
      enhancedError.userMessage = `Server returned ${error.response.status} error.`;
    }

    return Promise.reject(enhancedError);
  }
);

export default api;