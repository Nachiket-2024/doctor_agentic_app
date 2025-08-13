// --- External imports ---
// Redux Toolkit for creating slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// --- Internal imports ---
// API service functions for doctor CRUD operations
import {
    getAllDoctors,
    deleteDoctor,
    createDoctor,
    updateDoctor,
} from "../services/doctorService";

// --- Async thunk to fetch all doctors ---
// Handles async fetching of doctors list
export const fetchDoctorsAction = createAsyncThunk(
    "doctor/fetchAll",
    async (_, { rejectWithValue }) => {
        try {
            const response = await getAllDoctors();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to fetch doctors");
        }
    }
);

// --- Async thunk to delete a doctor by ID ---
// Calls API to delete a doctor and returns deleted ID
export const deleteDoctorAction = createAsyncThunk(
    "doctor/delete",
    async (id, { rejectWithValue }) => {
        try {
            await deleteDoctor(id);
            return id;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to delete doctor");
        }
    }
);

// --- Async thunk to create a new doctor ---
// Calls API to create a doctor and returns created doctor data
export const createDoctorAction = createAsyncThunk(
    "doctor/create",
    async (doctorData, { rejectWithValue }) => {
        try {
            const response = await createDoctor(doctorData);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to create doctor");
        }
    }
);

// --- Async thunk to update an existing doctor ---
// Calls API to update doctor by ID with new data
export const updateDoctorAction = createAsyncThunk(
    "doctor/update",
    async ({ id, data }, { rejectWithValue }) => {
        try {
            await updateDoctor(id, data);
            return { id, data };
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to update doctor");
        }
    }
);

// --- Initial form state ---
// Holds form input values and UI state for doctor form
const initialFormState = {
    name: "",
    email: "",
    specialization: "",
    availableDays: "",
    slotDuration: "",
    editingDoctorId: null,
    isListVisible: false,
};

// --- Initial overall state ---
// Manages list, loading, error, and form state in one slice
const initialState = {
    doctors: [],
    loading: false,
    error: null,
    form: initialFormState,
};

// --- Redux slice definition ---
// Includes reducers and extraReducers to handle async actions lifecycle
const doctorSlice = createSlice({
    name: "doctor",
    initialState,
    reducers: {
        // Reset form fields to initial empty state
        resetDoctorFormAction(state) {
            state.form = { ...initialFormState };
        },

        // Set form field value by field name and value
        setDoctorFormFieldAction(state, action) {
            const { field, value } = action.payload;
            if (field in state.form) {
                state.form[field] = value;
            }
        },

        // Populate form fields for editing a doctor and set editing ID
        setEditingDoctorAction(state, action) {
            const {
                id,
                name,
                email,
                specialization,
                availableDays,
                slotDuration,
                isListVisible,
            } = action.payload;

            state.form = {
                editingDoctorId: id,
                name,
                email,
                specialization,
                availableDays,
                slotDuration,
                isListVisible: isListVisible ?? state.form.isListVisible,
            };
        },
    },

    // Handle pending, fulfilled, and rejected states of async thunks
    extraReducers: (builder) => {
        builder
            // --- Fetch doctors ---
            .addCase(fetchDoctorsAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchDoctorsAction.fulfilled, (state, action) => {
                state.loading = false;
                state.doctors = action.payload;
            })
            .addCase(fetchDoctorsAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // --- Delete doctor ---
            .addCase(deleteDoctorAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(deleteDoctorAction.fulfilled, (state, action) => {
                state.loading = false;
                state.doctors = state.doctors.filter((doc) => doc.id !== action.payload);
            })
            .addCase(deleteDoctorAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // --- Create doctor ---
            .addCase(createDoctorAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(createDoctorAction.fulfilled, (state, action) => {
                state.loading = false;
                state.doctors.push(action.payload);
            })
            .addCase(createDoctorAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // --- Update doctor ---
            .addCase(updateDoctorAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(updateDoctorAction.fulfilled, (state, action) => {
                state.loading = false;
                const { id, data } = action.payload;
                const index = state.doctors.findIndex((doc) => doc.id === id);
                if (index !== -1) {
                    state.doctors[index] = { ...state.doctors[index], ...data };
                }
            })
            .addCase(updateDoctorAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

// --- Export slice actions ---
export const {
    resetDoctorFormAction,
    setDoctorFormFieldAction,
    setEditingDoctorAction,
} = doctorSlice.actions;

// --- Export selectors ---
// Select doctors list from state
export const selectDoctors = (state) => state.doctor.doctors;
// Select loading status from state
export const selectLoading = (state) => state.doctor.loading;

// --- Export reducer as default ---
export default doctorSlice.reducer;
