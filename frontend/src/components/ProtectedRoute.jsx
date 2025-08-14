// ---------------------------- External Imports ----------------------------

// React hooks for side-effects
import { useEffect } from "react";

// React Router hooks and components for navigation, location, and redirection
import { useNavigate, useLocation, Navigate } from "react-router-dom";

// Redux hooks for state and actions
import { useDispatch, useSelector } from "react-redux";

// MUI components for layout and loading spinner
import { Box, CircularProgress } from "@mui/material";


// ---------------------------- Internal Imports ----------------------------

// Redux selectors and actions from auth slice
import {
  selectIsAuthenticated, // Boolean: whether the user is logged in
  selectAuthLoading,     // Boolean: whether auth-related actions are loading
  loginSuccess,          // Action: mark user as logged in
  logout,                // Action: log user out
  setLoading             // Action: set auth loading state
} from "../features/authSlice";

// Axios instance configured for API calls
import API from "../utils/axiosInstance";


// ---------------------------- ProtectedRoute Component ----------------------------

// Component that protects routes from unauthenticated access
// Props:
//   - children: JSX elements to render if authenticated
export default function ProtectedRoute({ children }) {

  // ---------------------------- Hooks ----------------------------

  // Navigate programmatically
  const navigate = useNavigate();

  // Access current URL location
  const location = useLocation();

  // Dispatch Redux actions
  const dispatch = useDispatch();

  // ---------------------------- Redux State ----------------------------

  // Get authentication status from Redux
  const isAuthenticated = useSelector(selectIsAuthenticated);

  // Get loading status from Redux
  const loading = useSelector(selectAuthLoading);


  // ---------------------------- Effect: Authentication Check ----------------------------

  useEffect(() => {

    // Set loading state to true while checking auth
    dispatch(setLoading(true));

    // Extract token and role from URL query parameters
    const urlParams = new URLSearchParams(location.search);
    const tokenFromUrl = urlParams.get("access_token");
    const roleFromUrl = urlParams.get("role");

    // If token exists in URL, store it in localStorage and remove from URL
    if (tokenFromUrl) {
      localStorage.setItem("access_token", tokenFromUrl);
      if (roleFromUrl) localStorage.setItem("role", roleFromUrl);

      // Remove token/role from URL without reloading
      window.history.replaceState({}, "", location.pathname);
    }

    // Get token from localStorage
    const storedToken = localStorage.getItem("access_token");

    // If no token, logout and stop loading
    if (!storedToken) {
      dispatch(logout());
      dispatch(setLoading(false));
      return;
    }

    // Verify token with backend API
    API.get("/auth/me")
      .then(() => dispatch(loginSuccess()))       // Valid token → mark login success
      .catch(() => {
        dispatch(logout());                     // Invalid token → logout
        navigate("/login", { replace: true }); // Redirect to login
      })
      .finally(() => dispatch(setLoading(false))); // Stop loading after check

  }, [navigate, location, dispatch]);


  // ---------------------------- Render ----------------------------

  // Show loader while checking authentication
  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <CircularProgress />
      </Box>
    );
  }

  // Redirect to login if user is not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Render children if authenticated
  return children;
}
