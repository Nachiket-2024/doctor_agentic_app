// --- External imports ---
// Redux Toolkit function to configure the store
import { configureStore } from "@reduxjs/toolkit";

// --- Internal imports ---
// Import the doctors slice reducer
import doctorReducer from "../features/doctorSlice";
// Import the patients slice reducer
import patientReducer from "../features/patientSlice";
// Import the appointments slice reducer
import appointmentReducer from "../features/appointmentSlice";

// --- Configure and export the Redux store ---
const store = configureStore({
    reducer: {
        doctor: doctorReducer,       // Doctor slice reducer
        patient: patientReducer,     // Patient slice reducer
        appointment: appointmentReducer, // Appointment slice reducer
    },
});

export default store;
