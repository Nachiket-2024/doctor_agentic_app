// --- External imports ---
// React hooks for lifecycle and refs
import { useEffect, useRef } from "react";
// Redux hooks for state and dispatch
import { useSelector, useDispatch } from "react-redux";
// React Router hook for navigation
import { useNavigate } from "react-router-dom";
// MUI components for layout and UI
import { Box, Typography, Button } from "@mui/material";
// MUI icons
import { Dashboard, People } from "@mui/icons-material";
// Toast notifications
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// --- Internal imports ---
// Doctor form component
import DoctorForm from "../components/doctor/DoctorForm";
// Doctor list component
import DoctorList from "../components/doctor/DoctorList";
// Redux actions and selectors for doctors
import {
    fetchDoctorsAction,
    deleteDoctorAction,
    createDoctorAction,
    updateDoctorAction,
    selectDoctors,
    selectLoading,
    resetDoctorFormAction,
    setEditingDoctorAction,
    setDoctorFormFieldAction,
} from "../features/doctorSlice";

// --- DoctorPage component ---
export default function DoctorPage() {
    // --- Redux selectors ---
    const doctors = useSelector(selectDoctors);
    const loading = useSelector(selectLoading);

    // --- Redux dispatch ---
    const dispatch = useDispatch();

    // --- Navigation hook ---
    const navigate = useNavigate();

    // --- Ref to avoid double fetch on StrictMode ---
    const hasFetched = useRef(false);

    // --- Form state from Redux store ---
    const {
        name,
        email,
        specialization,
        availableDays,
        slotDuration,
        editingDoctorId,
        isListVisible,
    } = useSelector((state) => state.doctor.form);

    // --- Fetch doctors once on mount ---
    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;

        dispatch(fetchDoctorsAction())
            .unwrap()
            .then(() => toast.success("Doctors loaded successfully."))
            .catch(() => toast.error("Failed to fetch doctors."));
    }, [dispatch]);

    // --- Delete handler ---
    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this doctor?")) return;

        try {
            await dispatch(deleteDoctorAction(id)).unwrap();
            toast.success("Doctor deleted successfully.");
        } catch {
            toast.error("Failed to delete doctor.");
        }
    };

    // --- Submit handler for create/update ---
    const handleSubmit = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem("access_token");
        if (!token) {
            toast.error("Unauthorized, please login again.");
            return;
        }

        let parsedAvailableDays = null;
        try {
            parsedAvailableDays = availableDays ? JSON.parse(availableDays) : null;
        } catch {
            toast.error("Available Days must be valid JSON.");
            return;
        }

        const payload = {
            name,
            email,
            role: "doctor",
            specialization: specialization || null,
            available_days: parsedAvailableDays,
            slot_duration: slotDuration || null,
        };

        try {
            if (editingDoctorId) {
                await dispatch(updateDoctorAction({ id: editingDoctorId, data: payload })).unwrap();
                toast.success("Doctor updated successfully.");
            } else {
                await dispatch(createDoctorAction(payload)).unwrap();
                toast.success("Doctor created successfully.");
            }
            dispatch(resetDoctorFormAction());
        } catch {
            toast.error("Failed to save doctor.");
        }
    };

    // --- Edit handler populates form ---
    const handleEdit = (doctor) => {
        dispatch(
            setEditingDoctorAction({
                id: doctor.id,
                name: doctor.name,
                email: doctor.email,
                specialization: doctor.specialization || "",
                availableDays: doctor.available_days ? JSON.stringify(doctor.available_days) : "",
                slotDuration: doctor.slot_duration || "",
                isListVisible: true,
            })
        );
    };

    // --- Input change handler ---
    const handleInputChange = (field) => (e) => {
        dispatch(setDoctorFormFieldAction({ field, value: e.target.value }));
    };

    // --- Cancel editing handler ---
    const handleCancel = () => {
        dispatch(resetDoctorFormAction());
    };

    // --- Toggle list visibility ---
    const toggleListVisibility = () => {
        dispatch(setDoctorFormFieldAction({ field: "isListVisible", value: !isListVisible }));
    };

    // --- Render ---
    return (
        <Box sx={{ p: 4, backgroundColor: "#f8fafc", minHeight: "100vh" }}>
            <ToastContainer position="top-right" autoClose={3000} />

            {/* Page title */}
            <Typography variant="h4" fontWeight="bold" gutterBottom>
                Doctors
            </Typography>

            {/* Doctor form */}
            <Box sx={{ mb: 4 }}>
                <DoctorForm
                    name={name}
                    email={email}
                    specialization={specialization}
                    availableDays={availableDays}
                    slotDuration={slotDuration}
                    editingDoctorId={editingDoctorId}
                    onInputChange={handleInputChange}
                    onSubmit={handleSubmit}
                    onCancel={handleCancel}
                />
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
                    startIcon={<People />}
                    onClick={toggleListVisibility}
                >
                    {isListVisible ? "Hide" : "Show"} Doctors List
                </Button>
            </Box>

            {/* Doctor list */}
            <DoctorList
                doctors={doctors}
                loading={loading}
                isListVisible={isListVisible}
                onEdit={handleEdit}
                onDelete={handleDelete}
                toggleListVisibility={toggleListVisibility}
            />
        </Box>
    );
}
