import React, { createContext, useState, useEffect, useCallback, useContext } from 'react';
import { authAPI } from '../services/api';
import { use } from 'react';


const AuthContext = createContext(null);


export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));


  const API_BASE_URL = 'http://localhost:8001';


  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData.user);
        } catch (err) {
          console.error('Auth check failed:', err);
          localStorage.removeItem('token');
          setUser(null);
        }
      }
      setLoading(false);
    };


    checkAuth();
  }, []);


   const login = async (email, password, stayLoggedIn = false) => {
    try {
      setError(null);
      const response = await authAPI.login(email, password, stayLoggedIn);

      if (response.success) {
        // ✅ Store access_token
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('access_token', response.access_token);
        
        // ✅ Store refresh_token only if "Stay logged in" is checked
        if (stayLoggedIn && response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
          setRefreshToken(response.refresh_token);
          console.log('✅ Refresh token stored (7-day login enabled)');
        }
        
        // ✅ Set access token in state
        setAccessToken(response.access_token);
        
        // ✅ Set user in state
        setUser(response.user);
        
        return { success: true };
      } else {
        setError(response.error || 'Login failed');
        return { success: false, error: response.error };
      }
    } catch (err) {
      const errorMsg = err.message || 'Login failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    }
  };


  const logout = async () => {
  try {
    // ✅ NEW: Call backend to revoke tokens
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      } catch (err) {
        console.warn('Backend logout failed:', err);
        // Continue with client-side logout anyway
      }
    }
    
    // ✅ Clear all tokens and state
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    setError(null);
  } catch (err) {
    console.error('Logout error:', err);
  }
};



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
  }, [refreshToken, logout]);

  // Auto-refresh 1 min before expiry
useEffect(() => {
  if (!accessToken) return;
  const timer = setTimeout(() => handleRefreshToken(), 14 * 60 * 1000);
  return () => clearTimeout(timer);
}, [accessToken, handleRefreshToken]);


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
    <AuthContext.Provider value={{ user, loading, error, login, logout,
        accessToken,
        isAuthenticated: !!user,
        register,
        requestPasswordReset,
        resetPassword,
        refreshToken: handleRefreshToken, }}>
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