// ---------------------------- External Imports ----------------------------

// Centralized Axios instance for API requests
import API from "../utils/axiosInstance";


// ---------------------------- Patient API Calls ----------------------------

// GET: Fetch all patients
export const getAllPatients = () => API.get("/patient/");

// GET: Fetch a specific patient by ID
export const getPatientById = (id) => API.get(`/patient/${id}`);

// POST: Create a new patient
export const createPatient = (data) => API.post("/patient/", data);

// PUT: Update an existing patient by ID
export const updatePatient = (id, data) => API.put(`/patient/${id}`, data);

// DELETE: Remove a patient by ID
export const deletePatient = (id) => API.delete(`/patient/${id}`);
