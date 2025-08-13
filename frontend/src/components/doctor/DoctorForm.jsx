// --- External imports ---
// MUI components for layout, form controls, and typography
import { Paper, Box, Typography, TextField, Button, Stack } from "@mui/material";

// --- Icons ---
import { MedicalServices, Save, Cancel } from "@mui/icons-material";

// --- DoctorForm component ---
// Controlled form for creating/updating a doctor
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
        <Paper
            elevation={2}
            sx={{
                p: 2, // padding
                mb: 3, // bottom margin
                maxWidth: 400, // compact width like patient form
                borderRadius: 2,
                backgroundColor: "#fafafa",
            }}
        >
            {/* --- Form title --- */}
            <Typography variant="subtitle1" fontWeight="bold" mb={1}>
                {editingDoctorId ? "Edit Doctor" : "Create New Doctor"}
            </Typography>

            {/* --- Form fields --- */}
            <Box component="form" onSubmit={onSubmit} noValidate>
                <Stack spacing={1.5}>
                    <TextField
                        label="Name"
                        value={name}
                        onChange={onInputChange("name")}
                        required
                        fullWidth
                        size="small"
                        autoFocus={!editingDoctorId}
                    />

                    <TextField
                        type="email"
                        label="Email Address"
                        value={email}
                        onChange={onInputChange("email")}
                        required
                        fullWidth
                        size="small"
                    />

                    <TextField
                        label="Specialization"
                        value={specialization}
                        onChange={onInputChange("specialization")}
                        fullWidth
                        size="small"
                    />

                    <TextField
                        label='Available Days (JSON format)'
                        placeholder='{"mon": "9-11", "tue": "10-12"}'
                        value={availableDays}
                        onChange={onInputChange("availableDays")}
                        fullWidth
                        size="small"
                    />

                    <TextField
                        type="number"
                        label="Slot Duration (minutes)"
                        value={slotDuration}
                        onChange={onInputChange("slotDuration")}
                        fullWidth
                        size="small"
                        inputProps={{ min: 0 }}
                    />

                    {/* --- Buttons --- */}
                    <Stack direction="row" spacing={1.5} mt={1}>
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            size="small"
                            startIcon={editingDoctorId ? <Save /> : <MedicalServices />}
                        >
                            {editingDoctorId ? "Update Doctor" : "Create Doctor"}
                        </Button>

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
