import React, { useState, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { API_BASE_URL } from '../config/apiBaseUrl';
import '../Styles/auth.css'


/**
 * Registration Component
 * Handles user account creation with form validation
 */
const Registration = () => {
  const navigate = useNavigate();

  // ========== STATE MANAGEMENT ==========
  const [formData, setFormData] = useState({
    full_name: '',
    company_name: '',
    email: '',
    password: '',
    confirm_password: ''
  });

  const [formErrors, setFormErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // ========== VALIDATION FUNCTIONS ==========
  /**
   * Validate email format
   */
  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  /**
   * Validate password strength
   */
  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) errors.push('Password must be at least 8 characters');
    if (!/[A-Z]/.test(password)) errors.push('Must contain at least one uppercase letter');
    if (!/[a-z]/.test(password)) errors.push('Must contain at least one lowercase letter');
    if (!/[0-9]/.test(password)) errors.push('Must contain at least one number');
    if (!/[!@#$%^&*]/.test(password)) errors.push('Must contain at least one special character (!@#$%^&*)');
    return errors;
  };

  /**
   * Validate entire form
   */
  const validateForm = () => {
    const errors = {};

    // Full Name validation
    if (!formData.full_name.trim()) {
      errors.full_name = 'Full name is required';
    } else if (formData.full_name.trim().length < 2) {
      errors.full_name = 'Full name must be at least 2 characters';
    } else if (formData.full_name.trim().length > 100) {
      errors.full_name = 'Full name must not exceed 100 characters';
    }

    // Company Name validation
    if (!formData.company_name.trim()) {
      errors.company_name = 'Company name is required';
    } else if (formData.company_name.trim().length < 2) {
      errors.company_name = 'Company name must be at least 2 characters';
    } else if (formData.company_name.trim().length > 100) {
      errors.company_name = 'Company name must not exceed 100 characters';
    }

    // Email validation
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!isValidEmail(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
    } else {
      const passwordErrors = validatePassword(formData.password);
      if (passwordErrors.length > 0) {
        errors.password = passwordErrors[0]; // Show first error
      }
    }

    // Confirm Password validation
    if (!formData.confirm_password) {
      errors.confirm_password = 'Please confirm your password';
    } else if (formData.password !== formData.confirm_password) {
      errors.confirm_password = 'Passwords do not match';
    }

    return errors;
  };

  // ========== EVENT HANDLERS ==========
  /**
   * Handle input field changes
   */
  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  }, [formErrors]);

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setLoading(true);

    try {
      // Make API request to backend
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          full_name: formData.full_name.trim(),
          company_name: formData.company_name.trim(),
          email: formData.email.trim().toLowerCase(),
          password: formData.password
        })
      });

      // Handle response
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed. Please try again.');
      }

      const data = await response.json();

      // Show success message
      setSuccessMessage('✅ Registration successful! Redirecting to login...');
      
      // Clear form
      setFormData({
        full_name: '',
        company_name: '',
        email: '',
        password: '',
        confirm_password: ''
      });

      // Redirect after delay
      setTimeout(() => {
        navigate('/login', { state: { email: formData.email } });
      }, 2000);

    } catch (error) {
      console.error('Registration error:', error);
      setErrorMessage(`❌ ${error.message || 'Registration failed. Please try again.'}`);
    } finally {
      setLoading(false);
    }
  };

  // ========== RENDER COMPONENT ==========
  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">📊</div>
          <h1>ForecastAI Pro</h1>
          <p className="auth-subtitle">Create Your Account</p>
          <p className="auth-description">Start forecasting smarter inventory decisions</p>
        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="alert alert-error" role="alert">
            {errorMessage}
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="alert alert-success" role="alert">
            {successMessage}
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          
          {/* Full Name Field */}
          <div className="form-group">
            <label htmlFor="full_name" className="form-label">
              Full Name <span className="required">*</span>
            </label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              placeholder="Enter your full name"
              className={`form-input ${formErrors.full_name ? 'error' : ''}`}
              disabled={loading}
              aria-invalid={!!formErrors.full_name}
              aria-describedby={formErrors.full_name ? 'full_name-error' : undefined}
            />
            {formErrors.full_name && (
              <span id="full_name-error" className="error-message">
                {formErrors.full_name}
              </span>
            )}
          </div>

          {/* Company Name Field */}
          <div className="form-group">
            <label htmlFor="company_name" className="form-label">
              Company Name <span className="required">*</span>
            </label>
            <input
              type="text"
              id="company_name"
              name="company_name"
              value={formData.company_name}
              onChange={handleInputChange}
              placeholder="Enter your company name"
              className={`form-input ${formErrors.company_name ? 'error' : ''}`}
              disabled={loading}
              aria-invalid={!!formErrors.company_name}
              aria-describedby={formErrors.company_name ? 'company_name-error' : undefined}
            />
            {formErrors.company_name && (
              <span id="company_name-error" className="error-message">
                {formErrors.company_name}
              </span>
            )}
          </div>

          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address <span className="required">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Enter your email"
              className={`form-input ${formErrors.email ? 'error' : ''}`}
              disabled={loading}
              autoComplete="email"
              aria-invalid={!!formErrors.email}
              aria-describedby={formErrors.email ? 'email-error' : undefined}
            />
            {formErrors.email && (
              <span id="email-error" className="error-message">
                {formErrors.email}
              </span>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password <span className="required">*</span>
            </label>
            <div className="password-field">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Create a strong password"
                className={`form-input ${formErrors.password ? 'error' : ''}`}
                disabled={loading}
                autoComplete="new-password"
                aria-invalid={!!formErrors.password}
                aria-describedby={formErrors.password ? 'password-error' : undefined}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            {formErrors.password && (
              <span id="password-error" className="error-message">
                {formErrors.password}
              </span>
            )}
            <div className="password-hint">
              <small>
                Password must contain: 8+ characters, uppercase, lowercase, number, special character
              </small>
            </div>
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label htmlFor="confirm_password" className="form-label">
              Confirm Password <span className="required">*</span>
            </label>
            <div className="password-field">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirm_password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleInputChange}
                placeholder="Confirm your password"
                className={`form-input ${formErrors.confirm_password ? 'error' : ''}`}
                disabled={loading}
                autoComplete="new-password"
                aria-invalid={!!formErrors.confirm_password}
                aria-describedby={formErrors.confirm_password ? 'confirm_password-error' : undefined}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={loading}
                title={showConfirmPassword ? 'Hide password' : 'Show password'}
              >
                {showConfirmPassword ? '🙈' : '👁️'}
              </button>
            </div>
            {formErrors.confirm_password && (
              <span id="confirm_password-error" className="error-message">
                {formErrors.confirm_password}
              </span>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary btn-large"
          >
            {loading ? (
              <>
                <span className="spinner"></span> Creating Account...
              </>
            ) : (
              '✨ Create Account'
            )}
          </button>

        </form>

        {/* Footer */}
        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="auth-link">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Registration;
