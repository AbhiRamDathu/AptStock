import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/authContext.jsx';
import ProtectedRoute from './components/protectedRoute.jsx';
import Register from './components/registration.jsx';
import Login from './components/login.jsx';
import ForgotPassword from './components/forgotpassword.jsx';
import ResetPassword from './components/resetPassword.jsx';
import Dashboard from './Dashboard-smart-alerts.jsx';


function App() {
  return (
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            {/* Redirect root to dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* 404 fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
  );
}

export default App;

