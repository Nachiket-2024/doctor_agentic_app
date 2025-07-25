// ---------------------------- Imports ----------------------------
import API from "../utils/axiosInstance";

// ---------------------------- Doctor API Calls ----------------------------

// GET all doctors
export const getAllDoctors = () => API.get("/doctor/");

// GET a doctor by ID
export const getDoctorById = (id) => API.get(`/doctor/${id}`);

// POST: Create a new doctor
export const createDoctor = (data) => API.post("/doctor/", data);

// PUT: Update an existing doctor
export const updateDoctor = (id, data) => API.put(`/doctor/${id}`, data);

// DELETE: Delete a doctor by ID
export const deleteDoctor = (id) => API.delete(`/doctor/${id}`);
