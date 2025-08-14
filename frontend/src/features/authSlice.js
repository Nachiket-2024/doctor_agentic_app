// ---------------------------- External Imports ----------------------------

// Redux Toolkit utility for creating slices
import { createSlice } from "@reduxjs/toolkit";


// ---------------------------- Initial State ----------------------------

// Defines default authentication state
const initialState = {
    isAuthenticated: false, // Tracks if user is logged in
    loading: false,         // Indicates auth state check or login/logout in progress
};


// ---------------------------- Auth Slice ----------------------------

const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        // Set user as authenticated after successful login
        loginSuccess: (state) => {
            state.isAuthenticated = true;
            state.loading = false;
        },

        // Log out user and clear token
        logout: (state) => {
            state.isAuthenticated = false;
            state.loading = false;
            localStorage.removeItem("access_token");
        },

        // Manually set loading state (e.g., during token verification)
        setLoading: (state, action) => {
            state.loading = action.payload;
        },

        // Check localStorage for access token at app start
        checkAuthState: (state) => {
            const token = localStorage.getItem("access_token");
            state.isAuthenticated = !!token;
            state.loading = false;
        },
    },
});


// ---------------------------- Export Actions ----------------------------

export const { loginSuccess, logout, setLoading, checkAuthState } = authSlice.actions;


// ---------------------------- Export Selectors ----------------------------

// Selector to get authentication status
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;

// Selector to get loading state of authentication
export const selectAuthLoading = (state) => state.auth.loading;


// ---------------------------- Export Reducer ----------------------------

export default authSlice.reducer;
