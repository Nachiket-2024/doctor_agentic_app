// --- External imports ---
// Redux Toolkit utilities for slice and async thunk creation
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// --- Internal imports ---
// Patient API functions for CRUD operations
import {
    getAllPatients,
    createPatient,
    updatePatient,
    deletePatient,
} from "../services/patientService";

// --- Async thunk to fetch all patients ---
// Fetches the full patients list from the server
export const fetchPatientsAction = createAsyncThunk(
    "patient/fetchAll",
    async (_, { rejectWithValue }) => {
        try {
            const response = await getAllPatients();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to fetch patients");
        }
    }
);

// --- Async thunk to create a new patient ---
// Calls API to add a new patient, returns created patient data
export const createPatientAction = createAsyncThunk(
    "patient/create",
    async (patientData, { rejectWithValue }) => {
        try {
            const response = await createPatient(patientData);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to create patient");
        }
    }
);

// --- Async thunk to update an existing patient ---
// Calls API to update patient by ID with new data
export const updatePatientAction = createAsyncThunk(
    "patient/update",
    async ({ id, data }, { rejectWithValue }) => {
        try {
            await updatePatient(id, data);
            return { id, data };
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to update patient");
        }
    }
);

// --- Async thunk to delete a patient by ID ---
// Calls API to delete patient and returns deleted ID
export const deletePatientAction = createAsyncThunk(
    "patient/delete",
    async (id, { rejectWithValue }) => {
        try {
            await deletePatient(id);
            return id;
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to delete patient");
        }
    }
);

// --- Initial form state ---
// Holds the controlled input values for patient form
const initialFormState = {
    name: "",
    email: "",
    age: "",
    phoneNumber: "",
    editingPatientId: null,
    isListVisible: false,
};

// --- Initial overall state ---
// Manages list, loading, error, and form state in one slice
const initialState = {
    patients: [],
    loading: false,
    error: null,
    form: initialFormState,
};

// --- Redux slice ---
// Contains reducers and async lifecycle handlers for patients
const patientSlice = createSlice({
    name: "patient",
    initialState,
    reducers: {
        // Reset form to initial empty state
        resetPatientFormAction(state) {
            state.form = { ...initialFormState };
        },

        // Set a specific form field to a given value
        setPatientFormFieldAction(state, action) {
            const { field, value } = action.payload;
            if (field in state.form) {
                state.form[field] = value;
            }
        },

        // Populate form fields for editing a patient, and set editing ID
        setEditingPatientAction(state, action) {
            const {
                id,
                name,
                email,
                age,
                phoneNumber,
                isListVisible,
            } = action.payload;

            state.form = {
                editingPatientId: id,
                name,
                email,
                age: age !== null && age !== undefined ? age.toString() : "",
                phoneNumber: phoneNumber || "",
                isListVisible: isListVisible ?? state.form.isListVisible,
            };
        },
    },

    // Handle async thunk lifecycle for fetch, create, update, delete
    extraReducers: (builder) => {
        builder
            // --- Fetch patients ---
            .addCase(fetchPatientsAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchPatientsAction.fulfilled, (state, action) => {
                state.loading = false;
                state.patients = action.payload;
            })
            .addCase(fetchPatientsAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // --- Create patient ---
            .addCase(createPatientAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(createPatientAction.fulfilled, (state, action) => {
                state.loading = false;
                state.patients.push(action.payload);
            })
            .addCase(createPatientAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // --- Update patient ---
            .addCase(updatePatientAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(updatePatientAction.fulfilled, (state, action) => {
                state.loading = false;
                const { id, data } = action.payload;
                const index = state.patients.findIndex((p) => p.id === id);
                if (index !== -1) {
                    state.patients[index] = { ...state.patients[index], ...data };
                }
            })
            .addCase(updatePatientAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })

            // --- Delete patient ---
            .addCase(deletePatientAction.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(deletePatientAction.fulfilled, (state, action) => {
                state.loading = false;
                state.patients = state.patients.filter((p) => p.id !== action.payload);
            })
            .addCase(deletePatientAction.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

// --- Export slice actions ---
export const {
    resetPatientFormAction,
    setPatientFormFieldAction,
    setEditingPatientAction,
} = patientSlice.actions;

// --- Export selectors ---
// Get patients list from state
export const selectPatients = (state) => state.patient.patients;
// Get loading state from state
export const selectLoading = (state) => state.patient.loading;
// Get patient form state from state
export const selectPatientForm = (state) => state.patient.form;

// --- Export reducer as default ---
export default patientSlice.reducer;
