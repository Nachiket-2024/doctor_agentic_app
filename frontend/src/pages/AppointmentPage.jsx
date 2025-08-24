// ---------------------------- External Imports ----------------------------

// React hooks for lifecycle, state, and refs
import { useEffect, useRef, useState } from "react";

// Redux hooks for state and dispatch
import { useSelector, useDispatch } from "react-redux";

// React Router hook for navigation
import { useNavigate } from "react-router-dom";

// MUI components for layout and styling
import { Box, Typography, Button } from "@mui/material";

// MUI icons for dashboard and appointment actions
import { Dashboard, EventNote } from "@mui/icons-material";

// Toast notifications
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// ---------------------------- Internal Imports ----------------------------

// Appointment form component
import AppointmentForm from "../components/appointment/AppointmentForm";

// Appointment list component
import AppointmentList from "../components/appointment/AppointmentList";

// Redux actions and selectors for appointments
import {
    fetchAppointmentAction,
    deleteAppointmentAction,
    resetAppointmentFormAction,
    setEditingAppointmentAction,
    selectAppointments,
    selectLoading,
} from "../features/appointmentSlice";

// ---------------------------- AppointmentPage Component ----------------------------

// Main page container managing appointment data and UI composition
export default function AppointmentPage() {
    // Redux dispatch function
    const dispatch = useDispatch();

    // React Router navigation hook
    const navigate = useNavigate();

    // Select appointments list from Redux state
    const appointments = useSelector(selectAppointments);

    // Select loading state from Redux state
    const loading = useSelector(selectLoading);

    // Local state for controlling list visibility
    const [isListVisible, setIsListVisible] = useState(false);

    // Ref to avoid multiple fetches in React StrictMode
    const hasFetched = useRef(false);

    // Fetch appointments on initial mount
    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;

        dispatch(fetchAppointmentAction())
            .unwrap()
            .then(() => toast.success("Appointments loaded successfully."))
            .catch(() => toast.error("Failed to fetch appointments."));
    }, [dispatch]);

    // Toggle visibility of the appointment list
    const toggleListVisibility = () => {
        setIsListVisible((prev) => !prev);
    };

    // Delete appointment by ID
    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this appointment?")) return;

        try {
            await dispatch(deleteAppointmentAction(id)).unwrap();
            toast.success("Appointment deleted successfully.");
        } catch {
            toast.error("Failed to delete appointment.");
        }
    };

    // ---------------------------- Corrected handleEdit ----------------------------
    // Populate form for editing an existing appointment
    const handleEdit = (appointment) => {
        // Pass the raw appointment object directly to the slice
        dispatch(setEditingAppointmentAction(appointment));
        setIsListVisible(true);
    };

    // Reset the appointment form
    const handleCancel = () => {
        dispatch(resetAppointmentFormAction());
    };

    // Render the appointment management page
    return (
        <Box sx={{ p: 4, backgroundColor: "#f8fafc", minHeight: "100vh" }}>
            {/* Toast notifications */}
            <ToastContainer position="top-right" autoClose={3000} />

            {/* Page title */}
            <Typography variant="h4" fontWeight="bold" gutterBottom>
                Appointment Management
            </Typography>

            {/* Appointment form */}
            <Box sx={{ mb: 4 }}>
                <AppointmentForm onCancel={handleCancel} />
            </Box>

            {/* Buttons for dashboard navigation and list toggle */}
            <Box sx={{ mb: 3, mt: 2, display: "flex", gap: 2 }}>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<Dashboard />}
                    onClick={() => navigate("/dashboard")}
                >
                    Go to Dashboard
                </Button>
                <Button
                    variant="outlined"
                    startIcon={<EventNote />}
                    onClick={toggleListVisibility}
                >
                    {isListVisible ? "Hide" : "Show"} Appointments List
                </Button>
            </Box>

            {/* Appointment list */}
            <AppointmentList
                appointments={appointments}
                loading={loading}
                isListVisible={isListVisible}
                onEdit={handleEdit}
                onDelete={handleDelete}
                toggleListVisibility={toggleListVisibility}
            />
        </Box>
    );
}
