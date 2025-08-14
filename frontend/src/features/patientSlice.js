// ---------------------------- External Imports ----------------------------

// Redux Toolkit utilities for slice and async thunk creation
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";


// ---------------------------- Internal Imports ----------------------------

// Patient API service functions for CRUD operations
import {
    getAllPatients,
    createPatient,
    updatePatient,
    deletePatient,
} from "../services/patientService";


// ---------------------------- Async Thunks ----------------------------

// Fetch all patients from API
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

// Create a new patient
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

// Update existing patient by ID
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

// Delete patient by ID
export const deletePatientAction = createAsyncThunk(
    "patient/delete",
    async (id, { rejectWithValue }) => {
        try {
            await deletePatient(id);
            return id; // return deleted patient ID
        } catch (err) {
            return rejectWithValue(err.response?.data || "Failed to delete patient");
        }
    }
);


// ---------------------------- Initial State ----------------------------

// Form state for creating/editing a patient
const initialFormState = {
    name: "",
    email: "",
    age: "",
    phoneNumber: "",
    editingPatientId: null,
    isListVisible: false,
};

// Overall slice state
const initialState = {
    patients: [],      // List of patients
    loading: false,    // Loading indicator for API calls
    error: null,       // Error messages
    form: initialFormState,
};


// ---------------------------- Slice Definition ----------------------------

const patientSlice = createSlice({
    name: "patient",
    initialState,
    reducers: {
        // Reset patient form to initial empty state
        resetPatientFormAction(state) {
            state.form = { ...initialFormState };
        },

        // Update a specific form field by name
        setPatientFormFieldAction(state, action) {
            const { field, value } = action.payload;
            if (field in state.form) {
                state.form[field] = value;
            }
        },

        // Set form fields for editing an existing patient
        setEditingPatientAction(state, action) {
            const { id, name, email, age, phoneNumber, isListVisible } = action.payload;

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

    // Handle async thunk lifecycle actions
    extraReducers: (builder) => {
        builder
            // --- Fetch Patients ---
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

            // --- Create Patient ---
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

            // --- Update Patient ---
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

            // --- Delete Patient ---
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


// ---------------------------- Export Actions ----------------------------

export const {
    resetPatientFormAction,
    setPatientFormFieldAction,
    setEditingPatientAction,
} = patientSlice.actions;


// ---------------------------- Export Selectors ----------------------------

// Get list of patients
export const selectPatients = (state) => state.patient.patients;

// Get loading state
export const selectLoading = (state) => state.patient.loading;

// Get patient form state
export const selectPatientForm = (state) => state.patient.form;


// ---------------------------- Export Reducer ----------------------------

export default patientSlice.reducer;
