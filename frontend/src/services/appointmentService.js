// ---------------------------- External Imports ----------------------------

// Centralized Axios instance for API requests
import API from "../utils/axiosInstance";


// ---------------------------- Appointment API Calls ----------------------------

// GET: Fetch all appointments
export const getAllAppointments = () => API.get("/appointments/");

// GET: Fetch a specific appointment by ID
export const getAppointmentById = (id) => API.get(`/appointments/${id}`);

// POST: Create a new appointment
export const createAppointment = (data) => API.post("/appointments/", data);

// PUT: Update an existing appointment by ID
export const updateAppointment = (id, data) => API.put(`/appointments/${id}`, data);

// DELETE: Remove an appointment by ID
export const deleteAppointment = (id) => API.delete(`/appointments/${id}`);

// GET: Fetch available slots for a specific doctor on a given date
export const getAvailableSlots = (doctorId, dateStr) =>
    API.get(`/doctor_slot/${doctorId}/available-slots?date_str=${dateStr}`);

// GET: Fetch all patients (used to map patient_id → patient name)
export const getAllPatients = () => API.get("/patient/");
