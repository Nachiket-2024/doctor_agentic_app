// --- External imports ---
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// --- Internal imports ---
import {
    getAllAppointments,
    getAppointmentById,
    createAppointment,
    updateAppointment,
    deleteAppointment,
    getAvailableSlots,
    getAllPatients,
} from "../services/appointmentService";
import { getAllDoctors } from "../services/doctorService"; // Doctor API

// --- Async thunks ---

// Fetch all appointments
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

// Fetch single appointment
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

// Create appointment
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

// Update appointment
export const updateAppointmentAction = createAsyncThunk(
    "appointment/update",
    async ({ id, data }, { rejectWithValue }) => {
        try {
            await updateAppointment(id, data);
            return { id, data };
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to update appointment");
        }
    }
);

// Delete appointment
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

// Fetch available slots for a doctor on a date
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

// --- Initial state ---
const initialFormState = {
    patient_id: "",
    doctor_id: "",
    date: "",
    start_time: "",
    reason: "",
    editingAppointmentId: null,
};

const initialState = {
    items: [],
    loading: false,
    error: null,
    form: initialFormState,
    availableSlots: [],
    patients: [],
    doctors: [],
};

// --- Slice definition ---
const appointmentSlice = createSlice({
    name: "appointment",
    initialState,
    reducers: {
        resetAppointmentFormAction(state) {
            state.form = { ...initialFormState };
            state.availableSlots = [];
        },
        setAppointmentFormFieldAction(state, action) {
            const { field, value } = action.payload;
            if (field in state.form) {
                state.form[field] = value;
            }
        },
        setEditingAppointmentAction(state, action) {
            const { id, patient_id, doctor_id, date, start_time } = action.payload;
            state.form = {
                editingAppointmentId: id,
                patient_id,
                doctor_id,
                date,
                start_time,
                reason: "",
            };
        },
    },
    extraReducers: (builder) => {
        builder
            // Fetch all appointments
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

            // Create appointment
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

            // Update appointment
            .addCase(updateAppointmentAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(updateAppointmentAction.fulfilled, (state, action) => {
                state.loading = false;
                const { id, data } = action.payload;
                const index = state.items.findIndex((a) => a.id === id);
                if (index !== -1) state.items[index] = { ...state.items[index], ...data };
            })
            .addCase(updateAppointmentAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // Delete appointment
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

            // Fetch available slots
            .addCase(fetchAvailableSlotsAction.fulfilled, (state, action) => {
                state.availableSlots = action.payload.slots;
            })

            // Fetch patients
            .addCase(fetchPatientsAction.fulfilled, (state, action) => {
                state.patients = action.payload;
            })

            // Fetch doctors
            .addCase(fetchDoctorsAction.fulfilled, (state, action) => {
                state.doctors = action.payload;
            });
    },
});

// --- Export actions and selectors ---
export const {
    resetAppointmentFormAction,
    setAppointmentFormFieldAction,
    setEditingAppointmentAction,
} = appointmentSlice.actions;

export const selectAppointments = (state) => state.appointment.items;
export const selectLoading = (state) => state.appointment.loading;
export const selectAvailableSlots = (state) => state.appointment.availableSlots;
export const selectPatients = (state) => state.appointment.patients;
export const selectDoctors = (state) => state.appointment.doctors;

// --- Export reducer ---
export default appointmentSlice.reducer;
