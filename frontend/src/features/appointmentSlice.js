// ---------------------------- External Imports ----------------------------

// Redux Toolkit utilities for creating slices and async actions
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";


// ---------------------------- Internal Imports ----------------------------

// Appointment API services
import {
    getAllAppointments,
    getAppointmentById,
    createAppointment,
    updateAppointment,
    deleteAppointment,
    getAvailableSlots,
    getAllPatients,
} from "../services/appointmentService";

// Doctor API service
import { getAllDoctors } from "../services/doctorService";


// ---------------------------- Async Thunks ----------------------------

// Fetch all appointments from backend
export const fetchAppointmentAction = createAsyncThunk(
    "appointment/fetchAll",
    async (_, { rejectWithValue }) => {
        try {
            const response = await getAllAppointments();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to fetch appointments");
        }
    }
);

// Fetch a single appointment by ID
export const fetchSingleAppointmentAction = createAsyncThunk(
    "appointment/fetchOne",
    async (id, { rejectWithValue }) => {
        try {
            const response = await getAppointmentById(id);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to fetch appointment");
        }
    }
);

// Create a new appointment
export const createAppointmentAction = createAsyncThunk(
    "appointment/create",
    async (data, { rejectWithValue }) => {
        try {
            const response = await createAppointment(data);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to create appointment");
        }
    }
);

// Update an existing appointment
export const updateAppointmentAction = createAsyncThunk(
    "appointment/update",
    async ({ id, data }, { rejectWithValue }) => {
        try {
            const response = await updateAppointment(id, data); // backend returns full updated appointment
            return response.data; // includes backend-calculated end_time
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to update appointment");
        }
    }
);

// Delete an appointment
export const deleteAppointmentAction = createAsyncThunk(
    "appointment/delete",
    async (id, { rejectWithValue }) => {
        try {
            await deleteAppointment(id);
            return id;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to delete appointment");
        }
    }
);

// Fetch available slots for a specific doctor on a date
export const fetchAvailableSlotsAction = createAsyncThunk(
    "appointment/fetchSlots",
    async ({ doctorId, dateStr }, { rejectWithValue }) => {
        try {
            const response = await getAvailableSlots(doctorId, dateStr);
            return { slots: response.data };
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to fetch available slots");
        }
    }
);

// Fetch all patients
export const fetchPatientsAction = createAsyncThunk(
    "appointment/fetchPatients",
    async (_, { rejectWithValue }) => {
        try {
            const response = await getAllPatients();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to fetch patients");
        }
    }
);

// Fetch all doctors
export const fetchDoctorsAction = createAsyncThunk(
    "appointment/fetchDoctors",
    async (_, { rejectWithValue }) => {
        try {
            const response = await getAllDoctors();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to fetch doctors");
        }
    }
);


// ---------------------------- Initial State ----------------------------

// Initial form state for appointment creation/editing
const initialFormState = {
    patient_id: "",
    doctor_id: "",
    date: "",
    start_time: "",
    reason: "",
    editingAppointmentId: null,
};

// Main initial state for appointment slice
const initialState = {
    items: [],           // List of appointments
    loading: false,      // Loading state for async operations
    error: null,         // Error message
    form: initialFormState,
    availableSlots: [],  // Slots available for selected doctor/date
    patients: [],        // List of patients
    doctors: [],         // List of doctors
};


// ---------------------------- Appointment Slice ----------------------------

const appointmentSlice = createSlice({
    name: "appointment",
    initialState,
    reducers: {
        // Reset form fields and available slots
        resetAppointmentFormAction(state) {
            state.form = { ...initialFormState };
            state.availableSlots = [];
        },

        // Update single form field
        setAppointmentFormFieldAction(state, action) {
            const { field, value } = action.payload;
            if (field in state.form) {
                state.form[field] = value;
            }
        },

        // Set form to edit a specific appointment
        setEditingAppointmentAction(state, action) {
            let startTime = action.payload.start_time || "";

            if (startTime && startTime.includes(":")) {
                startTime = startTime.slice(0, 5);
            }

            state.form = {
                editingAppointmentId: action.payload.id,
                patient_id: action.payload.patient_id || "",
                doctor_id: action.payload.doctor_id || "",
                date: action.payload.date || "",
                start_time: startTime, // show HH:MM in form
                end_time: action.payload.end_time || "", // include backend-calculated end_time
                reason: action.payload.reason || "",
            };
        },
    },
    extraReducers: (builder) => {
        builder
            // ---------------------------- Fetch All Appointments ----------------------------
            .addCase(fetchAppointmentAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchAppointmentAction.fulfilled, (state, action) => {
                state.loading = false;
                state.items = action.payload;
            })
            .addCase(fetchAppointmentAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // ---------------------------- Create Appointment ----------------------------
            .addCase(createAppointmentAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(createAppointmentAction.fulfilled, (state, action) => {
                state.loading = false;
                state.items.push(action.payload);
            })
            .addCase(createAppointmentAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // ---------------------------- Update Appointment ----------------------------
            .addCase(updateAppointmentAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(updateAppointmentAction.fulfilled, (state, action) => {
                state.loading = false;
                const updatedAppointment = action.payload; // backend returns full appointment object
                const index = state.items.findIndex((a) => a.id === updatedAppointment.id);
                if (index !== -1) state.items[index] = updatedAppointment; // ✅ includes updated end_time
            })
            .addCase(updateAppointmentAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // ---------------------------- Delete Appointment ----------------------------
            .addCase(deleteAppointmentAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(deleteAppointmentAction.fulfilled, (state, action) => {
                state.loading = false;
                state.items = state.items.filter((a) => a.id !== action.payload);
            })
            .addCase(deleteAppointmentAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // ---------------------------- Fetch Available Slots ----------------------------
            .addCase(fetchAvailableSlotsAction.fulfilled, (state, action) => {
                state.availableSlots = action.payload.slots;
            })

            // ---------------------------- Fetch Patients ----------------------------
            .addCase(fetchPatientsAction.fulfilled, (state, action) => {
                state.patients = action.payload;
            })

            // ---------------------------- Fetch Doctors ----------------------------
            .addCase(fetchDoctorsAction.fulfilled, (state, action) => {
                state.doctors = action.payload;
            });
    },
});


// ---------------------------- Export Actions and Selectors ----------------------------

export const {
    resetAppointmentFormAction,
    setAppointmentFormFieldAction,
    setEditingAppointmentAction,
} = appointmentSlice.actions;

// Selectors for components to access state
export const selectAppointments = (state) => state.appointment.items;
export const selectLoading = (state) => state.appointment.loading;
export const selectAvailableSlots = (state) => state.appointment.availableSlots;
export const selectPatients = (state) => state.appointment.patients;
export const selectDoctors = (state) => state.appointment.doctors;


// ---------------------------- Export Reducer ----------------------------

export default appointmentSlice.reducer;
