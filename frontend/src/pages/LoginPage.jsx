// ---------------------------- External Imports ----------------------------

// React hooks for lifecycle
import { useEffect } from "react";

// React Router hook for navigation
import { useNavigate } from "react-router-dom";

// Redux hooks for state and dispatch
import { useSelector, useDispatch } from "react-redux";

// MUI components for layout, typography, buttons, and loading
import { Box, Typography, Button, Paper, CircularProgress } from "@mui/material";

// MUI icons
import { Google } from "@mui/icons-material";


// ---------------------------- Internal Imports ----------------------------

// Redux selectors and actions for authentication
import { selectIsAuthenticated, selectAuthLoading, checkAuthState } from "../features/authSlice";


// ---------------------------- LoginPage Component ----------------------------
export default function LoginPage() {
  // ---------------------------- Navigation and Redux ----------------------------
  const navigate = useNavigate();
  const dispatch = useDispatch();

  // ---------------------------- Redux state selectors ----------------------------
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const loading = useSelector(selectAuthLoading);

  // ---------------------------- Check auth token on mount ----------------------------
  useEffect(() => {
    dispatch(checkAuthState());
  }, [dispatch]);

  // ---------------------------- Redirect if already logged in ----------------------------
  useEffect(() => {
    if (!loading && isAuthenticated) {
      navigate("/dashboard");
    }
  }, [loading, isAuthenticated, navigate]);

  // ---------------------------- Loading spinner ----------------------------
  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "50vh", // smaller height for spinner
          backgroundColor: "#f8fafc",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // ---------------------------- Main login area ----------------------------
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        py: 4,           // vertical padding
        backgroundColor: "#ffffff",
        minHeight: "50vh", // allow natural height without extra scroll
      }}
    >
      {/* Login card */}
      <Paper
        elevation={6}
        sx={{
          p: 4,
          maxWidth: 420,
          width: "100%",
          textAlign: "center",
          borderRadius: 3,
          backgroundColor: "#ffffffdd",
          backdropFilter: "blur(6px)",
        }}
      >
        {/* Title */}
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Welcome Back
        </Typography>

        {/* Description */}
        <Typography variant="body1" sx={{ mb: 3 }}>
          Login to Doctor Agentic App using your Google account.
        </Typography>

        {/* Google login button */}
        <Button
          variant="contained"
          startIcon={<Google />}
          onClick={() => { window.location.href = "http://localhost:8000/auth/login"; }}
          sx={{
            px: 3,
            py: 1.5,
            fontSize: "1rem",
            borderRadius: 2,
            backgroundColor: "#DB4437",
            "&:hover": { backgroundColor: "#c1351d" },
          }}
        >
          Login with Google
        </Button>
      </Paper>
    </Box>
  );
}
