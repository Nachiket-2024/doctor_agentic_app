// ---------------------------- External Imports ----------------------------

// Import MUI components for card layout, typography, buttons, box container, and avatar
import { Card, CardContent, Typography, Button, Box, Avatar } from "@mui/material";

// Import MUI icons for edit and delete actions
import { Edit, Delete } from "@mui/icons-material";


// ---------------------------- PatientCard Component ----------------------------

// Component to display a single patient with details and action buttons
// Props:
//   - patient: object containing patient details
//   - onEdit: callback function to handle edit action
//   - onDelete: callback function to handle delete action
export default function PatientCard({ patient, onEdit, onDelete }) {
    return (
        // Root Card component with hover effect and shadow
        <Card
            sx={{
                boxShadow: 3,                     // Initial shadow
                borderRadius: 3,                   // Rounded corners
                transition: "0.3s",                // Smooth transition on hover
                "&:hover": {                       // Hover effect
                    boxShadow: 6,                  // Elevated shadow
                    transform: "translateY(-4px)"  // Slight lift
                },
            }}
        >
            {/* Card content container */}
            <CardContent>
                {/* Avatar and patient name */}
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Avatar sx={{ mr: 2 }}>
                        {patient.name.charAt(0).toUpperCase()} {/* First letter of name */}
                    </Avatar>
                    <Typography variant="h6">{patient.name}</Typography>
                </Box>

                {/* Patient email */}
                <Typography variant="body2">📧 {patient.email}</Typography>
                {/* Patient age */}
                <Typography variant="body2">🎂 Age: {patient.age}</Typography>
                {/* Patient phone number */}
                <Typography variant="body2">📞 {patient.phone_number}</Typography>

                {/* Action buttons: Edit and Delete */}
                <Box sx={{ display: "flex", gap: 1, mt: 2 }}>
                    {/* Edit button */}
                    <Button
                        size="small"
                        variant="contained"
                        color="warning"
                        startIcon={<Edit />}
                        onClick={() => onEdit(patient)}
                    >
                        Edit
                    </Button>

                    {/* Delete button */}
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
