// ---------------------------- Imports ----------------------------
import axios from "axios"; // Import Axios for making HTTP requests

// ---------------------------- Axios Instance ----------------------------
// Create a preconfigured Axios instance with a base URL pointing to your FastAPI backend
const API = axios.create({
    baseURL: "http://localhost:8000",
});

// Attach the JWT token from local storage to every request for authentication
API.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token"); // Get token from local storage
    if (token) {
        config.headers.Authorization = `Bearer ${token}`; // Attach token as Bearer
    }
    return config;
});

// ---------------------------- Appointment API Calls ----------------------------

// GET all appointments
export const getAllAppointments = () => API.get("/appointments/");

// GET a specific appointment by ID
export const getAppointmentById = (id) => API.get(`/appointments/${id}`);

// POST: Create a new appointment
export const createAppointment = (data) => API.post("/appointments/", data);

// PUT: Update an existing appointment
export const updateAppointment = (id, data) => API.put(`/appointments/${id}`, data);

// DELETE: Delete an appointment by ID
export const deleteAppointment = (id) => API.delete(`/appointments/${id}`);

// GET: Fetch available slots for a doctor on a given date
export const getAvailableSlots = (doctorId, dateStr) =>
    API.get(`/doctor_slot/${doctorId}/available-slots?date_str=${dateStr}`);

// ---------------------------- Patients API (for names) ----------------------------

// GET all patients (used for mapping patient_id → patient name)
export const getAllPatients = () => API.get("/patient/");
