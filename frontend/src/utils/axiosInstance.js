// ---------------------------- External Imports ----------------------------
// Axios library for HTTP requests
import axios from "axios";

// ---------------------------- Axios Instance ----------------------------
// Create a centralized Axios instance with base URL
const axiosInstance = axios.create({
    baseURL: "http://localhost:8000", // Base URL for all API requests
});

// ---------------------------- Request Interceptor ----------------------------
// Attach access token to every outgoing request if available
axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token"); // Get token from localStorage
    if (token) {
        config.headers.Authorization = `Bearer ${token}`; // Add Authorization header
    }
    return config; // Return updated config
});

// ---------------------------- Response Interceptor ----------------------------
// Handle 401 errors and attempt token refresh
axiosInstance.interceptors.response.use(
    (response) => response, // If response is successful, return it
    async (error) => {
        const originalRequest = error.config; // Store original request
        // Check for 401 Unauthorized and prevent infinite retry loops
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refreshToken = localStorage.getItem("refresh_token"); // Get refresh token
                // Request new access token
                const response = await axios.post(
                    "http://localhost:8000/auth/refresh",
                    { refresh_token: refreshToken }
                );
                const newAccessToken = response.data.access_token; // Extract new token
                localStorage.setItem("access_token", newAccessToken); // Save new token

                // Retry the original request with updated Authorization header
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                localStorage.clear(); // Clear all tokens if refresh fails
                window.location.href = "/login"; // Redirect to login page
                return Promise.reject(refreshError); // Reject promise
            }
        }
        return Promise.reject(error); // Reject other errors
    }
);

// ---------------------------- Export Axios Instance ----------------------------
export default axiosInstance;
