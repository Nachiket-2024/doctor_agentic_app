// ---------------------------- External Imports ----------------------------

// Redux Toolkit utilities for slices and async thunks
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";


// ---------------------------- Internal Imports ----------------------------

// Doctor API service functions for CRUD operations
import {
    getAllDoctors,
    deleteDoctor,
    createDoctor,
    updateDoctor,
} from "../services/doctorService";


// ---------------------------- Async Thunks ----------------------------

// Fetch all doctors from API
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

// Delete doctor by ID
export const deleteDoctorAction = createAsyncThunk(
    "doctor/delete",
    async (id, { rejectWithValue }) => {
        try {
            await deleteDoctor(id);
            return id; // return deleted doctor ID
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to delete doctor");
        }
    }
);

// Create a new doctor
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

// Update existing doctor by ID
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


// ---------------------------- Initial State ----------------------------

// Form state for creating/editing a doctor
const initialFormState = {
    name: "",
    email: "",
    specialization: "",
    availableDays: "",
    slotDuration: "",
    editingDoctorId: null,
    isListVisible: false,
};

// Overall slice state
const initialState = {
    doctors: [],       // List of doctors
    loading: false,    // Loading indicator for API calls
    error: null,       // Error messages
    form: initialFormState,
};


// ---------------------------- Slice Definition ----------------------------

const doctorSlice = createSlice({
    name: "doctor",
    initialState,
    reducers: {
        // Reset form to initial empty state
        resetDoctorFormAction(state) {
            state.form = { ...initialFormState };
        },

        // Update a specific form field
        setDoctorFormFieldAction(state, action) {
            const { field, value } = action.payload;
            if (field in state.form) {
                state.form[field] = value;
            }
        },

        // Set form for editing a doctor
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

    // Handle async thunk lifecycle actions
    extraReducers: (builder) => {
        builder
            // --- Fetch Doctors ---
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

            // --- Delete Doctor ---
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

            // --- Create Doctor ---
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

            // --- Update Doctor ---
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


// ---------------------------- Export Actions ----------------------------

export const {
    resetDoctorFormAction,
    setDoctorFormFieldAction,
    setEditingDoctorAction,
} = doctorSlice.actions;


// ---------------------------- Export Selectors ----------------------------

// Get doctors array from state
export const selectDoctors = (state) => state.doctor.doctors;

// Get loading status from state
export const selectLoading = (state) => state.doctor.loading;


// ---------------------------- Export Reducer ----------------------------

export default doctorSlice.reducer;
