import axios from "axios";

const axiosInstance = axios.create({
    baseURL: "http://localhost:8000", // your API base URL
});

// Request interceptor to attach access token
axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor for refreshing token on 401
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refreshToken = localStorage.getItem("refresh_token");
                const response = await axios.post(
                    "http://localhost:8000/auth/refresh",
                    { refresh_token: refreshToken }
                );
                const newAccessToken = response.data.access_token;
                localStorage.setItem("access_token", newAccessToken);

                // Retry the original request with new token
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                localStorage.clear(); // remove tokens if refresh fails
                window.location.href = "/login"; // force logout
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
