// --- Axios config for interacting with doctor-related backend routes ---
import axios from "axios";

// Create Axios instance with base URL
const API = axios.create({
    baseURL: "http://localhost:8000", //
});

// Attach JWT token to every request
API.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token"); // Fetch token from localStorage
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ---- Doctor API calls ----

// GET all doctors
export const getAllDoctors = () => API.get("/doctor/");

// GET a doctor by ID
export const getDoctorById = (id) => API.get(`/doctor/${id}`);

// POST create a new doctor
export const createDoctor = (data) => API.post("/doctor/", data);

// PUT update an existing doctor
export const updateDoctor = (id, data) => API.put(`/doctor/${id}`, data);

// DELETE a doctor by ID
export const deleteDoctor = (id) => API.delete(`/doctor/${id}`);
