import axios from "axios";

// ================== AXIOS INSTANCE ==================
const API_BASE_URL = import.meta.env.VITE_API_URL;

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// ================== REQUEST INTERCEPTOR ==================
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ================== RESPONSE INTERCEPTOR ==================
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Global 402 Trial Expired handler
    if (error.response?.status === 402) {
      const data = error.response.data;

      console.error("⏰ TRIAL EXPIRED:", data);

      localStorage.setItem(
        "paywall_error",
        JSON.stringify({
          status: 402,
          message: data.message || "Your free trial has ended",
          upgrade_url: data.upgrade_url || "/pricing",
        })
      );

      window.dispatchEvent(
        new CustomEvent("trial_expired", { detail: data })
      );
    }

    return Promise.reject(error);
  }
);

// ================== AUTH API ==================
export const authAPI = {
  login: (email, password, stayLoggedIn = false) =>
    api.post("/auth/login", {
      email,
      password,
      stay_logged_in: stayLoggedIn,
    }),

  register: (userData) =>
    api.post("/auth/register", userData),

  getCurrentUser: () =>
    api.get("/auth/me"),

  refreshToken: (token) =>
    api.post("/auth/refresh-token", {
      refresh_token: token,
    }),
};

// ================== FORECAST API ==================
export const forecastAPI = {
  previewCSV: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/api/forecast/preview", formData);
  },

  loadSampleData: () =>
    api.post("/api/forecast/upload-and-process-sample"),

  getSampleCSVContent: () =>
    api.get("/api/forecast/sample-data"),

  uploadAndProcess: (
    file,
    fromDate,
    toDate,
    selectedStore = "Store A",
    thresholds = {},
    costData = {}
  ) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("filter_from_date", fromDate);
    formData.append("filter_to_date", toDate);
    formData.append("store", selectedStore);

    if (thresholds && Object.keys(thresholds).length > 0) {
      formData.append("thresholds", JSON.stringify(thresholds));
    }

    if (costData) {
      Object.entries(costData).forEach(([key, value]) => {
        formData.append(key, JSON.stringify(value));
      });
    }

    return api.post("/api/forecast/upload-and-process", formData);
  },
};

// ================== TRIAL / BILLING API ==================
export const trialAPI = {
  getTrialInfo: () =>
    api.get("/api/trial/info"),

  upgradeSubscription: (planTier) =>
    api.post("/api/trial/upgrade", {
      plan_tier: planTier,
    }),
};

// ================== DEFAULT EXPORT ==================
export default {
  auth: authAPI,
  forecast: forecastAPI,
  trial: trialAPI,
};
