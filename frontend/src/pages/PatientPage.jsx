// --- External imports ---
// React hooks and Redux hooks
import { useEffect, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

// --- MUI components ---
import { Box, Typography, Button } from "@mui/material";
import { Dashboard, People } from "@mui/icons-material";

// --- Toast notifications ---
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// --- Internal imports ---
// PatientForm component for create/update form
import PatientForm from "../components/patient/PatientForm";
// PatientList component for showing patients list and toggle
import PatientList from "../components/patient/PatientList";

// Redux slice actions and selectors
import {
    fetchPatientsAction,
    deletePatientAction,
    createPatientAction,
    updatePatientAction,
    selectPatients,
    selectLoading,
    resetPatientFormAction,
    setEditingPatientAction,
    setPatientFormFieldAction,
    selectPatientForm,
} from "../features/patientSlice";

// --- PatientsPage component ---
// Main page container managing patient data and UI composition
export default function PatientPage() {
    // Selectors for patients data, loading, and form state from Redux store
    const patients = useSelector(selectPatients);
    const loading = useSelector(selectLoading);
    const form = useSelector(selectPatientForm);

    // Redux dispatch function
    const dispatch = useDispatch();

    // React Router navigation
    const navigate = useNavigate();

    // Ref to avoid multiple fetches in StrictMode
    const hasFetched = useRef(false);

    // Fetch patients once on mount
    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;

        dispatch(fetchPatientsAction())
            .unwrap()
            .then(() => toast.success("Patients loaded successfully."))
            .catch(() => toast.error("Could not load patients."));
    }, [dispatch]);

    // Submit handler to create or update patient
    const handleFormSubmit = async (payload) => {
        try {
            if (form.editingPatientId) {
                await dispatch(
                    updatePatientAction({ id: form.editingPatientId, data: payload })
                ).unwrap();
                toast.success("Patient updated successfully.");
            } else {
                await dispatch(createPatientAction(payload)).unwrap();
                toast.success("Patient created successfully.");
            }
            dispatch(resetPatientFormAction());
        } catch {
            toast.error("Failed to save patient.");
        }
    };

    // Handler to populate form with selected patient for editing
    const handleEdit = (patient) => {
        dispatch(
            setEditingPatientAction({
                id: patient.id,
                name: patient.name,
                email: patient.email,
                age: patient.age !== "N/A" ? patient.age.toString() : "",
                phoneNumber: patient.phone_number !== "N/A" ? patient.phone_number : "",
                isListVisible: true,
            })
        );
    };

    // Handler to delete patient by ID
    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this patient?")) return;

        try {
            await dispatch(deletePatientAction(id)).unwrap();
            toast.success("Patient deleted successfully.");
        } catch {
            toast.error("Failed to delete patient.");
        }
    };

    // Reset the form (cancel editing)
    const resetForm = () => {
        dispatch(resetPatientFormAction());
    };

    // Toggle the visibility of the patient list
    const toggleList = () => {
        dispatch(
            setPatientFormFieldAction({
                field: "isListVisible",
                value: !form.isListVisible,
            })
        );
    };

    // Render the full page UI
    return (
        <Box sx={{ p: 4, backgroundColor: "#f8fafc", minHeight: "100vh" }}>
            <ToastContainer position="top-right" autoClose={3000} />

            {/* Page title */}
            <Typography variant="h4" fontWeight="bold" gutterBottom>
                Patients
            </Typography>

            {/* Patient form for create/update */}
            <Box sx={{ mb: 4 }}>
                <PatientForm
                    onSubmit={handleFormSubmit}
                    editingPatient={form.editingPatientId ? form : null}
                    resetForm={resetForm}
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
                <Button variant="outlined" startIcon={<People />} onClick={toggleList}>
                    {form.isListVisible ? "Hide" : "Show"} Patients List
                </Button>
            </Box>

            {/* Patient list component */}
            <PatientList
                patients={patients}
                loading={loading}
                isListVisible={form.isListVisible}
                onEdit={handleEdit}
                onDelete={handleDelete}
                toggleListVisibility={toggleList}
            />
        </Box>
    );
}
