import React from 'react';

const LoadingSpinner = ({ 
  size = 'md',
  text = 'Loading...',
  theme = 'primary',
  inline = false
}) => {
  const sizeConfig = {
    sm: { spinner: '20px', text: '12px', padding: '4px 8px' },
    md: { spinner: '24px', text: '14px', padding: '8px 12px' },
    lg: { spinner: '32px', text: '16px', padding: '12px 16px' },
  };

  const themeConfig = {
    primary: { bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', text: '#667eea' },
    orange: { bg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', text: '#f59e0b' },
    green: { bg: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)', text: '#22c55e' },
    blue: { bg: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', text: '#3b82f6' },
  };

  const config = sizeConfig[size] || sizeConfig.md;
  const theme_cfg = themeConfig[theme] || themeConfig.primary;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      padding: inline ? '0' : config.padding,
      fontSize: config.text,
      fontWeight: '600',
      color: theme_cfg.text,
    }}>
      {/* Animated Spinner */}
      <svg
        width={config.spinner}
        height={config.spinner}
        viewBox="0 0 50 50"
        style={{
          animation: 'spin 1s linear infinite',
          background: 'transparent',
        }}
      >
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
        <circle
          cx="25"
          cy="25"
          r="20"
          fill="none"
          stroke={theme_cfg.text}
          strokeWidth="3"
          strokeDasharray="31.4 94.2"
          strokeLinecap="round"
        />
      </svg>

      {/* Text */}
      {text && <span>{text}</span>}
    </div>
  );
};

export default LoadingSpinner;
