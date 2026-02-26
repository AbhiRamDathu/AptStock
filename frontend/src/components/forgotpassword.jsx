import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config/apiBaseUrl';

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
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '20px',
        padding: '40px',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
      }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>📦</div>
          <h2 style={{ margin: 0, fontSize: '28px', fontWeight: '800', color: '#1a202c' }}>
            ForecastAI Pro
          </h2>
          <h3 style={{ margin: '8px 0', fontSize: '22px', fontWeight: '700', color: '#667eea' }}>
            Reset Your Password
          </h3>
          <p style={{ margin: 0, fontSize: '14px', color: '#64748b' }}>
            {step === 1 && 'Enter your email to receive reset instructions'}
            {step === 2 && 'Enter the 6-digit code sent to your email'}
            {step === 3 && 'Create your new password'}
          </p>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div style={{
            padding: '12px',
            backgroundColor: '#fef2f2',
            border: '2px solid #fecaca',
            borderRadius: '10px',
            color: '#991b1b',
            fontSize: '14px',
            fontWeight: '600',
            marginBottom: '20px'
          }}>
            ❌ {error}
          </div>
        )}

        {message && (
          <div style={{
            padding: '12px',
            backgroundColor: '#f0fdf4',
            border: '2px solid #bbf7d0',
            borderRadius: '10px',
            color: '#166534',
            fontSize: '14px',
            fontWeight: '600',
            marginBottom: '20px'
          }}>
            ✅ {message}
          </div>
        )}

        {/* Step 1: Enter Email */}
        {step === 1 && (
          <form onSubmit={handleSendOTP}>
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151'
              }}>
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
                style={{
                  width: '100%',
                  padding: '14px 16px',
                  fontSize: '16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '10px',
                  outline: 'none',
                  transition: 'border 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '16px',
                fontWeight: '700',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1,
                transition: 'opacity 0.2s'
              }}
            >
              {loading ? '📤 Sending...' : '📧 Send Reset Link'}
            </button>
          </form>
        )}

        {/* Step 2: Enter OTP */}
        {step === 2 && (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '16px',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                textAlign: 'center'
              }}>
                Enter 6-Digit Code
              </label>
              
              <div style={{
                display: 'flex',
                gap: '10px',
                justifyContent: 'center'
              }}>
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    id={`otp-${index}`}
                    type="text"
                    maxLength="1"
                    value={digit}
                    onChange={(e) => handleOTPChange(index, e.target.value)}
                    onPaste={index === 0 ? handleOTPPaste : undefined}
                    style={{
                      width: '60px',
                      height: '70px',
                      fontSize: '28px',
                      fontWeight: '700',
                      textAlign: 'center',
                      border: '2px solid #667eea',
                      borderRadius: '10px',
                      outline: 'none'
                    }}
                  />
                ))}
              </div>
              
              <p style={{
                textAlign: 'center',
                marginTop: '12px',
                fontSize: '13px',
                color: '#64748b'
              }}>
                Sent to: <strong>{email}</strong>
              </p>
            </div>

            <button
              onClick={handleVerifyOTP}
              disabled={otp.join('').length !== 6}
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '16px',
                fontWeight: '700',
                cursor: otp.join('').length !== 6 ? 'not-allowed' : 'pointer',
                opacity: otp.join('').length !== 6 ? 0.6 : 1,
                marginBottom: '12px'
              }}
            >
              ✓ Verify Code
            </button>

            <button
              onClick={() => setStep(1)}
              style={{
                width: '100%',
                padding: '12px',
                background: 'none',
                color: '#667eea',
                border: '2px solid #667eea',
                borderRadius: '10px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              ← Change Email
            </button>
          </div>
        )}

        {/* Step 3: New Password */}
        {step === 3 && (
          <form onSubmit={handleResetPassword}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151'
              }}>
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                placeholder="Enter new password"
                style={{
                  width: '100%',
                  padding: '14px 16px',
                  fontSize: '16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '10px',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151'
              }}>
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                placeholder="Confirm new password"
                style={{
                  width: '100%',
                  padding: '14px 16px',
                  fontSize: '16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '10px',
                  outline: 'none'
                }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '16px',
                fontWeight: '700',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1
              }}
            >
              {loading ? '🔄 Resetting...' : '🔐 Reset Password'}
            </button>
          </form>
        )}

        {/* Back to Login Link */}
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <a
            href="/login"
            style={{
              color: '#667eea',
              fontSize: '14px',
              fontWeight: '600',
              textDecoration: 'none'
              }}
          >
            ← Back to login
          </a>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
