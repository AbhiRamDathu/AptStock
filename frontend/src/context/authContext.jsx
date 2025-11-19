import React, { createContext, useState, useEffect, useCallback } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));

  const API_BASE_URL = 'http://localhost:8001';

  // Check authentication status on app mount
  useEffect(() => {
    const checkAuth = async () => {
      if (accessToken) {
        try {
          const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else if (refreshToken) {
            // Try to refresh token
            await handleRefreshToken();
          } else {
            // Clear invalid tokens
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setAccessToken(null);
          }
        } catch (err) {
          console.error('Auth check failed:', err);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const handleRefreshToken = useCallback(async () => {
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh-token?refresh_token=${refreshToken}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access_token);
        localStorage.setItem('access_token', data.access_token);
        setUser(data.user);
        return true;
      } else {
        logout();
        return false;
      }
    } catch (err) {
      console.error('Token refresh failed:', err);
      logout();
      return false;
    }
  }, [refreshToken]);

  const register = async (email, password, fullName, companyName) => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          company_name: companyName,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Registration failed');
        return false;
      }

      return true;
    } catch (err) {
      setError('Registration error: ' + err.message);
      return false;
    }
  };

  const login = async (email, password, stayLoggedIn = false) => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          stay_logged_in: stayLoggedIn,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Login failed');
        return false;
      }

      setAccessToken(data.access_token);
      localStorage.setItem('access_token', data.access_token);

      if (data.refresh_token) {
        setRefreshToken(data.refresh_token);
        localStorage.setItem('refresh_token', data.refresh_token);
      }

      setUser(data.user);
      return true;
    } catch (err) {
      setError('Login error: ' + err.message);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const requestPasswordReset = async (email) => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      return response.ok;
    } catch (err) {
      setError('Request error: ' + err.message);
      return false;
    }
  };

  const resetPassword = async (token, newPassword) => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Password reset failed');
        return false;
      }

      return true;
    } catch (err) {
      setError('Reset error: ' + err.message);
      return false;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        accessToken,
        isAuthenticated: !!user,
        register,
        login,
        logout,
        requestPasswordReset,
        resetPassword,
        refreshToken: handleRefreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
