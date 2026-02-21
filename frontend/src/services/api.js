import axios from 'axios';
import { API_BASE_URL } from '../config/apiBaseUrl';
axios.defaults.baseURL = API_BASE_URL;




// Helper to get auth token
const getAuthToken = () => {
  return localStorage.getItem('token');
};


// Helper for API calls with auth
const apiCall = async (url, options = {}) => {
  const token = getAuthToken();
  
  const headers = {
    ...options.headers,
  };

  // Add auth header if token exists and not already set
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (options.body && !(options.body instanceof FormData))  {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(new URL(url, API_BASE_URL).toString(), {
      ...options,
      headers,
    });

    // ✅ NEW: Handle 402 Payment Required (Trial Expired)
    if (response.status === 402) {
      const errorData = await response.json();
      console.error('⏰ TRIAL EXPIRED:', errorData);
      
      // ✅ IMPORTANT: Store error in global state or localStorage
      // so Dashboard can show paywall modal
      localStorage.setItem('paywall_error', JSON.stringify({
        status: 402,
        message: errorData.message || 'Your free trial has ended',
        upgrade_url: errorData.upgrade_url || '/pricing'
      }));
      
      // Dispatch event for Dashboard to listen
      window.dispatchEvent(new CustomEvent('trial_expired', {
        detail: errorData
      }));
      
      throw {
        status: 402,
        error: 'TRIAL_EXPIRED',
        data: errorData
      };
    }

    // Handle other errors normally
    if (!response.ok) {
      const error = await response.json().catch(() => ({ 
        error: 'Connect to the Internet' 
      }));
      throw new Error(error.error || error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
    
  } catch (error) {
    console.error(`❌ API Error [${url}]:`, error);
    throw error;
  }
};


// Auth API
export const authAPI = {
  login: async (email, password, stayLoggedIn = false) => {
    return apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, stay_logged_in: stayLoggedIn }),
    });
  },


  register: async (userData) => {
    return apiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },


  getCurrentUser: async () => {
    return apiCall('/auth/me', {
      method: 'GET',
    });
  },


  refreshToken: async (token) => {
    return apiCall('/auth/refresh-token', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: token }),
    });
  },
};


// Forecast API
export const forecastAPI = {

  previewCSV: async (file) => {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(
            `/api/forecast/preview`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${localStorage.getItem('token')}`
                }
            }
        );

        return response.data;
    } catch (error) {
        console.error('❌ CSV preview error:', error);
        throw error;
    }
},

// Add inside your forecastAPI = { ... } object

loadSampleData: async () => {
  try {
    const token = localStorage.getItem('token');
    console.log("Loading sample data from backend...");
    
    const response = await axios.post(
      `/api/forecast/upload-and-process-sample`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log("Sample data loaded:", response.data);
    return response.data;
    
  } catch (error) {
    console.error("Sample data error:", error);
    throw error;
  }
},

getSampleCSVContent: async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(
      `/api/forecast/sample-data`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    return response.data.csv_content;
  } catch (error) {
    console.error("Error getting sample CSV:", error);
    throw error;
  }
},


uploadAndProcess: async (file, fromDate, toDate, selectedStore = 'Store A', thresholds = {}, costData = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('filter_from_date', fromDate);  // ✅ ADD THIS
    formData.append('filter_to_date', toDate);


    if (costData) {
      formData.append('unit_cost_dict', JSON.stringify(costData.unit_cost_dict || {}));
      formData.append('unit_price_dict', JSON.stringify(costData.unit_price_dict || {}));
      formData.append('current_stock_dict', JSON.stringify(costData.current_stock_dict || {}));
      formData.append('lead_time_dict', JSON.stringify(costData.lead_time_dict || {}));
    }


    // Thresholds for risk classification
    if (thresholds && Object.keys(thresholds).length > 0) {
      formData.append('thresholds', JSON.stringify(thresholds));
    }
   
    // Build query string
    const params = new URLSearchParams();
    if (fromDate) params.append('filter_from_date', fromDate);
    if (toDate) params.append('filter_to_date', toDate);
    if (selectedStore) params.append('store', selectedStore);


    console.log('📤 API Query Params:', { fromDate, toDate, selectedStore });


    const queryString = params.toString();
    const url = `/api/forecast/upload-and-process${queryString ? `?${queryString}` : ''}`;

try {
    return await apiCall(url, {
      method: 'POST',
      body: formData,
    });
  } catch (error) {
    // ✅ Handle 402 Payment Required
    if (error.status === 402) {
      console.warn('⏰ Trial expired - showing paywall');
      // Show paywall modal in Dashboard
      window.dispatchEvent(new CustomEvent('show_paywall', {
        detail: error.data
      }));
      throw error;
    }
    throw error;
  }
},
};

export const trialAPI = {
  // Get current trial/subscription info
  getTrialInfo: async () => {
    try {
      return await apiCall('/api/trial/info', {
        method: 'GET',
      });
    } catch (error) {
      console.error('Error fetching trial info:', error);
      return null;
    }
  },

  // Upgrade subscription
  upgradeSubscription: async (planTier) => {
    try {
      return await apiCall('/api/trial/upgrade', {
        method: 'POST',
        body: JSON.stringify({ plan_tier: planTier }),
      });
    } catch (error) {
      console.error('Error upgrading:', error);
      throw error;
    }
  }
};


  export default {
    auth: authAPI,
    forecast: forecastAPI,
  }