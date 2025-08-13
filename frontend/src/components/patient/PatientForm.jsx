// --- External imports ---
// React hook for dispatching Redux actions
import { useDispatch, useSelector } from "react-redux";

// --- MUI components ---
import { Box, TextField, Button, Typography, Stack, Paper } from "@mui/material";

// --- Icons ---
import { Save, Cancel } from "@mui/icons-material";

// --- Internal imports ---
// Redux slice actions and selector for patient form
import {
    setPatientFormFieldAction,
    resetPatientFormAction,
    selectPatientForm,
} from "../../features/patientSlice";

// --- PatientForm component ---
// Controlled form fully connected to Redux state for patient creation/editing
export default function PatientForm({ onSubmit, editingPatient, resetForm }) {
    // --- Redux dispatch ---
    const dispatch = useDispatch();

    // --- Select form state from Redux ---
    const form = useSelector(selectPatientForm);

    // --- Input change handler factory ---
    // Updates Redux form field on input change
    const handleInputChange = (field) => (e) => {
        dispatch(setPatientFormFieldAction({ field, value: e.target.value }));
    };

    // --- Handle form submission ---
    const handleSubmit = (e) => {
        e.preventDefault();

        // Prepare payload for submission
        const payload = {
            name: form.name,
            email: form.email,
            age: form.age.trim() === "" ? null : parseInt(form.age, 10),
            phone_number: form.phoneNumber.trim() === "" ? null : form.phoneNumber,
            role: "patient",
        };

        onSubmit(payload);
    };

    // --- Handle cancel editing ---
    const handleCancel = () => {
        dispatch(resetPatientFormAction());
        if (resetForm) resetForm();
    };

    // --- Render form UI ---
    return (
        <Paper
            elevation={2}
            sx={{
                p: 2,
                mb: 3,
                maxWidth: 400,
                borderRadius: 2,
                backgroundColor: "#fafafa",
            }}
        >
            <Typography variant="subtitle1" fontWeight="bold" mb={1}>
                {editingPatient ? "Edit Patient" : "Create New Patient"}
            </Typography>

            <Box component="form" onSubmit={handleSubmit} noValidate>
                <Stack spacing={1.5}>
                    <TextField
                        label="Full Name"
                        value={form.name}
                        onChange={handleInputChange("name")}
                        required
                        fullWidth
                        size="small"
                    />

                    <TextField
                        type="email"
                        label="Email Address"
                        value={form.email}
                        onChange={handleInputChange("email")}
                        required
                        fullWidth
                        size="small"
                    />

                    <TextField
                        type="number"
                        label="Age"
                        value={form.age}
                        onChange={handleInputChange("age")}
                        fullWidth
                        size="small"
                        inputProps={{ min: 0 }}
                    />

                    <TextField
                        label="Phone Number"
                        value={form.phoneNumber}
                        onChange={handleInputChange("phoneNumber")}
                        fullWidth
                        size="small"
                    />

                    <Stack direction="row" spacing={1.5} mt={1}>
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            startIcon={<Save />}
                            size="small"
                        >
                            {editingPatient ? "Update" : "Create Patient"}
                        </Button>

                        {editingPatient && (
                            <Button
                                type="button"
                                variant="outlined"
                                color="secondary"
                                startIcon={<Cancel />}
                                onClick={handleCancel}
                                size="small"
                            >
                                Cancel
                            </Button>
                        )}
                    </Stack>
                </Stack>
            </Box>
        </Paper>
    );
}
