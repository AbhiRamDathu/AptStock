import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config/apiBaseUrl';
import "../Styles/forgotPassword.css";

const ForgotPassword = () => {
  const [step, setStep] = useState(1); // 1: Email, 2: OTP, 3: New Password
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  // Step 1: Send OTP
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const text = await response.text();
      const data = text ? JSON.parse(text) : {};

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to send reset code');
      }

      setMessage('Reset code sent! Check your email.');
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle OTP input
  const handleOTPChange = (index, value) => {
    if (value.length > 1) return;
    
    const newOTP = [...otp];
    newOTP[index] = value;
    setOtp(newOTP);

    // Auto-focus next input
    if (value && index < 5) {
      document.getElementById(`otp-${index + 1}`).focus();
    }
  };

  // Handle OTP paste
  const handleOTPPaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, 6);
    const newOTP = pastedData.split('');
    setOtp([...newOTP, ...Array(6 - newOTP.length).fill('')]);
  };

  // Step 2: Verify OTP and go to password reset
  const handleVerifyOTP = () => {
    if (otp.join('').length === 6) {
      setStep(3);
      setError('');
    } else {
      setError('Please enter the 6-digit code');
    }
  };

  // Step 3: Reset password
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          otp: otp.join(''),
          new_password: newPassword
        })
      });

      const text = await response.text();
      const data = text ? JSON.parse(text) : {};

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to reset password');
      }

      setMessage('Password reset successful!');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fp-container">
  <div className="fp-card">

    {/* Header */}
    <div className="fp-header">
      <div className="fp-icon">📦</div>

      <h2 className="fp-title">
        ForecastAI Pro
      </h2>

      <h3 className="fp-subtitle">
        Reset Your Password
      </h3>

      <p className="fp-description">
        {step === 1 && 'Enter your email to receive reset instructions'}
        {step === 2 && 'Enter the 6-digit code sent to your email'}
        {step === 3 && 'Create your new password'}
      </p>
    </div>

    {/* Error / Success */}
    {error && (
      <div className="fp-error">
        ❌ {error}
      </div>
    )}

    {message && (
      <div className="fp-success">
        ✅ {message}
      </div>
    )}

    {/* STEP 1 */}
    {step === 1 && (
      <form onSubmit={handleSendOTP}>
        <div className="fp-group">
          <label className="fp-label">Email Address</label>

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="your@email.com"
            className="fp-input"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="fp-btn"
        >
          {loading ? '📤 Sending...' : '📧 Send Reset Link'}
        </button>
      </form>
    )}

    {/* STEP 2 */}
    {step === 2 && (
      <div>
        <div className="fp-group">

          <label className="fp-label" style={{ textAlign: 'center', marginBottom: 16 }}>
            Enter 6-Digit Code
          </label>

          <div className="fp-otp-container">
            {otp.map((digit, index) => (
              <input
                key={index}
                id={`otp-${index}`}
                type="text"
                maxLength="1"
                value={digit}
                onChange={(e) => handleOTPChange(index, e.target.value)}
                onPaste={index === 0 ? handleOTPPaste : undefined}
                className="fp-otp-input"
              />
            ))}
          </div>

          <p className="fp-otp-text">
            Sent to: <strong>{email}</strong>
          </p>

        </div>

        <button
          onClick={handleVerifyOTP}
          disabled={otp.join('').length !== 6}
          className="fp-btn fp-btn-success"
          style={{ marginBottom: 12 }}
        >
          ✓ Verify Code
        </button>

        <button
          onClick={() => setStep(1)}
          className="fp-btn-outline"
        >
          ← Change Email
        </button>
      </div>
    )}

    {/* STEP 3 */}
    {step === 3 && (
      <form onSubmit={handleResetPassword}>

        <div className="fp-group">
          <label className="fp-label">New Password</label>

          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            placeholder="Enter new password"
            className="fp-input"
          />
        </div>

        <div className="fp-group">
          <label className="fp-label">Confirm Password</label>

          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            placeholder="Confirm new password"
            className="fp-input"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="fp-btn"
        >
          {loading ? '🔄 Resetting...' : '🔐 Reset Password'}
        </button>

      </form>
    )}

    {/* Footer */}
    <div className="fp-footer">
      <a href="/login" className="fp-link">
        ← Back to login
      </a>
    </div>

  </div>
</div>
  );
};

export default ForgotPassword;
