// Axios config and Patient API endpoints

import axios from "axios";

// Base URL config
const API = axios.create({
    baseURL: "http://localhost:8000",
});

// Add JWT token to headers
API.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// API methods
export const getAllPatients = () => API.get("/patient/");
export const getPatientById = (id) => API.get(`/patient/${id}`);
export const createPatient = (data) => API.post("/patient/", data);
export const updatePatient = (id, data) => API.put(`/patient/${id}`, data);
export const deletePatient = (id) => API.delete(`/patient/${id}`);
