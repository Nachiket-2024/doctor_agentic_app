// ---------------------------- External Imports ----------------------------

// Import MUI components for paper container, form layout, text fields, buttons, and stack layout
import { Paper, Box, Typography, TextField, Button, Stack } from "@mui/material";

// Import icons for medical services, save, and cancel actions
import { MedicalServices, Save, Cancel } from "@mui/icons-material";


// ---------------------------- DoctorForm Component ----------------------------

// Controlled form component for creating or updating a doctor
// Props:
//   - name, email, specialization, availableDays, slotDuration: form field values
//   - editingDoctorId: id of doctor being edited (null if creating)
//   - onInputChange: callback for input change
//   - onSubmit: callback for form submission
//   - onCancel: callback to cancel editing
export default function DoctorForm({
    name,
    email,
    specialization,
    availableDays,
    slotDuration,
    editingDoctorId,
    onInputChange,
    onSubmit,
    onCancel,
}) {
    return (
        // Paper container for form with padding, border radius, and light background
        <Paper
            elevation={2}
            sx={{
                p: 2,                   // Padding
                mb: 3,                  // Bottom margin
                maxWidth: 400,          // Maximum width
                borderRadius: 2,        // Rounded corners
                backgroundColor: "#fafafa", // Light background color
            }}
        >
            {/* Form title */}
            <Typography variant="subtitle1" fontWeight="bold" mb={1}>
                {editingDoctorId ? "Edit Doctor" : "Create New Doctor"}
            </Typography>

            {/* Form element */}
            <Box component="form" onSubmit={onSubmit} noValidate>
                <Stack spacing={1.5}>
                    {/* Name input field */}
                    <TextField
                        label="Name"
                        value={name}
                        onChange={onInputChange("name")}
                        required
                        fullWidth
                        size="small"
                        autoFocus={!editingDoctorId} // Autofocus when creating new doctor
                    />

                    {/* Email input field */}
                    <TextField
                        type="email"
                        label="Email Address"
                        value={email}
                        onChange={onInputChange("email")}
                        required
                        fullWidth
                        size="small"
                    />

                    {/* Specialization input field */}
                    <TextField
                        label="Specialization"
                        value={specialization}
                        onChange={onInputChange("specialization")}
                        fullWidth
                        size="small"
                    />

                    {/* Available Days input field */}
                    <TextField
                        label='Available Days (JSON format)'
                        placeholder='{"mon": "9-11", "tue": "10-12"}'
                        value={availableDays}
                        onChange={onInputChange("availableDays")}
                        fullWidth
                        size="small"
                    />

                    {/* Slot Duration input field */}
                    <TextField
                        type="number"
                        label="Slot Duration (minutes)"
                        value={slotDuration}
                        onChange={onInputChange("slotDuration")}
                        fullWidth
                        size="small"
                        inputProps={{ min: 0 }} // Minimum value constraint
                    />

                    {/* Form action buttons */}
                    <Stack direction="row" spacing={1.5} mt={1}>
                        {/* Submit button */}
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            size="small"
                            startIcon={editingDoctorId ? <Save /> : <MedicalServices />}
                        >
                            {editingDoctorId ? "Update Doctor" : "Create Doctor"}
                        </Button>

                        {/* Cancel button, shown only when editing */}
                        {editingDoctorId && (
                            <Button
                                type="button"
                                variant="outlined"
                                color="secondary"
                                startIcon={<Cancel />}
                                onClick={onCancel}
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
