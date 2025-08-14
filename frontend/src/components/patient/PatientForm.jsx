// ---------------------------- External Imports ----------------------------

// Import React Redux hooks for dispatching actions and selecting state
import { useDispatch, useSelector } from "react-redux";

// Import MUI components for layout, form controls, typography, and paper container
import { Box, TextField, Button, Typography, Stack, Paper } from "@mui/material";

// Import icons for save and cancel actions
import { Save, Cancel } from "@mui/icons-material";


// ---------------------------- Internal Imports ----------------------------

// Import Redux actions and selector for patient form
import {
    setPatientFormFieldAction,  // Action to update a form field
    resetPatientFormAction,     // Action to reset the form
    selectPatientForm,          // Selector to get form state from Redux
} from "../../features/patientSlice";


// ---------------------------- PatientForm Component ----------------------------

// Controlled form component connected to Redux for creating or editing a patient
// Props:
//   - onSubmit: callback function to handle form submission
//   - editingPatient: boolean flag indicating edit mode
//   - resetForm: optional callback to reset parent state when canceling
export default function PatientForm({ onSubmit, editingPatient, resetForm }) {
    // Redux dispatch function
    const dispatch = useDispatch();

    // Select patient form state from Redux
    const form = useSelector(selectPatientForm);

    // --- Input change handler factory ---
    // Returns a handler to update a specific form field in Redux
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
            role: "patient", // Default role
        };

        // Call parent submission handler
        onSubmit(payload);
    };

    // --- Handle cancel editing ---
    const handleCancel = () => {
        dispatch(resetPatientFormAction()); // Reset Redux form
        if (resetForm) resetForm();         // Call optional parent reset
    };

    // --- Render form UI ---
    return (
        // Paper container for form
        <Paper
            elevation={2}
            sx={{
                p: 2,                  // Padding
                mb: 3,                 // Bottom margin
                maxWidth: 400,         // Maximum width
                borderRadius: 2,       // Rounded corners
                backgroundColor: "#fafafa", // Light background
            }}
        >
            {/* Form title */}
            <Typography variant="subtitle1" fontWeight="bold" mb={1}>
                {editingPatient ? "Edit Patient" : "Create New Patient"}
            </Typography>

            {/* Form element */}
            <Box component="form" onSubmit={handleSubmit} noValidate>
                <Stack spacing={1.5}>
                    {/* Name input field */}
                    <TextField
                        label="Full Name"
                        value={form.name}
                        onChange={handleInputChange("name")}
                        required
                        fullWidth
                        size="small"
                    />

                    {/* Email input field */}
                    <TextField
                        type="email"
                        label="Email Address"
                        value={form.email}
                        onChange={handleInputChange("email")}
                        required
                        fullWidth
                        size="small"
                    />

                    {/* Age input field */}
                    <TextField
                        type="number"
                        label="Age"
                        value={form.age}
                        onChange={handleInputChange("age")}
                        fullWidth
                        size="small"
                        inputProps={{ min: 0 }}
                    />

                    {/* Phone number input field */}
                    <TextField
                        label="Phone Number"
                        value={form.phoneNumber}
                        onChange={handleInputChange("phoneNumber")}
                        fullWidth
                        size="small"
                    />

                    {/* Action buttons */}
                    <Stack direction="row" spacing={1.5} mt={1}>
                        {/* Submit button */}
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            startIcon={<Save />}
                            size="small"
                        >
                            {editingPatient ? "Update" : "Create Patient"}
                        </Button>

                        {/* Cancel button (shown only in edit mode) */}
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
