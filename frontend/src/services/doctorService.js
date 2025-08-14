// ---------------------------- External Imports ----------------------------

// Centralized Axios instance for API requests
import API from "../utils/axiosInstance";


// ---------------------------- Doctor API Calls ----------------------------

// GET: Fetch all doctors
export const getAllDoctors = () => API.get("/doctor/");

// GET: Fetch a specific doctor by ID
export const getDoctorById = (id) => API.get(`/doctor/${id}`);

// POST: Create a new doctor
export const createDoctor = (data) => API.post("/doctor/", data);

// PUT: Update an existing doctor by ID
export const updateDoctor = (id, data) => API.put(`/doctor/${id}`, data);

// DELETE: Remove a doctor by ID
export const deleteDoctor = (id) => API.delete(`/doctor/${id}`);
