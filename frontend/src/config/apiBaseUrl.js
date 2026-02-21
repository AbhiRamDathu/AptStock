// Single source of truth for API URL (local + production)
const raw = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

// Remove trailing slashes to avoid double-slash bugs
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

// Optional guardrail: warn if you forgot production env var
if (import.meta.env.PROD && API_BASE_URL.includes('localhost')) {
  console.warn(
    'VITE_API_BASE_URL is not set in production. The app is using localhost and will fail for online users.'
  );
}
