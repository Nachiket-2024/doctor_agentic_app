// --- External imports ---
// MUI components for card UI
import { Card, CardContent, Typography, Button, Box, Avatar } from "@mui/material";
// MUI icons for edit/delete actions
import { Edit, Delete } from "@mui/icons-material";

// --- PatientCard component ---
// Displays single patient info with Edit/Delete buttons
export default function PatientCard({ patient, onEdit, onDelete }) {
    // Return card UI with patient details and action buttons
    return (
        <Card
            sx={{
                boxShadow: 3,
                borderRadius: 3,
                transition: "0.3s",
                "&:hover": { boxShadow: 6, transform: "translateY(-4px)" },
            }}
        >
            <CardContent>
                {/* Avatar and patient name */}
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Avatar sx={{ mr: 2 }}>
                        {patient.name.charAt(0).toUpperCase()}
                    </Avatar>
                    <Typography variant="h6">{patient.name}</Typography>
                </Box>

                {/* Patient email */}
                <Typography variant="body2">📧 {patient.email}</Typography>
                {/* Patient age */}
                <Typography variant="body2">🎂 Age: {patient.age}</Typography>
                {/* Patient phone number */}
                <Typography variant="body2">📞 {patient.phone_number}</Typography>

                {/* Action buttons */}
                <Box sx={{ display: "flex", gap: 1, mt: 2 }}>
                    <Button
                        size="small"
                        variant="contained"
                        color="warning"
                        startIcon={<Edit />}
                        onClick={() => onEdit(patient)}
                    >
                        Edit
                    </Button>
                    <Button
                        size="small"
                        variant="contained"
                        color="error"
                        startIcon={<Delete />}
                        onClick={() => onDelete(patient.id)}
                    >
                        Delete
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
}
