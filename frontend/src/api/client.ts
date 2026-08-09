import axios, { type InternalAxiosRequestConfig } from 'axios';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor: injects the token into every request if the user is logged in
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('token')
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default apiClient;