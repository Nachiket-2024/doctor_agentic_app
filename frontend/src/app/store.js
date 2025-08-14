// ---------------------------- External Imports ----------------------------

// Import Redux Toolkit function to configure the Redux store
import { configureStore } from "@reduxjs/toolkit";


// ---------------------------- Internal Imports ----------------------------

// Import the slice reducer for managing doctors state
import doctorReducer from "../features/doctorSlice";

// Import the slice reducer for managing patients state
import patientReducer from "../features/patientSlice";

// Import the slice reducer for managing appointments state
import appointmentReducer from "../features/appointmentSlice";

// Import the slice reducer for handling authentication state
import authReducer from "../features/authSlice";


// ---------------------------- Store Configuration ----------------------------

// Configure the Redux store with all slice reducers
const store = configureStore({
    reducer: {
        doctor: doctorReducer,            // Handles doctors state
        patient: patientReducer,          // Handles patients state
        appointment: appointmentReducer,  // Handles appointments state
        auth: authReducer,                // Handles authentication state
    },
});


// ---------------------------- Export Store ----------------------------

// Export the configured Redux store for use in the app
export default store;
