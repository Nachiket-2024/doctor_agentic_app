// ---------------------------- External Imports ----------------------------

// Import MUI components for card layout, typography, and buttons
import { Card, CardContent, CardActions, Typography, Button } from "@mui/material";

// Import icons for edit and delete actions
import { Edit, Delete } from "@mui/icons-material";


// ---------------------------- DoctorCard Component ----------------------------

// Component to display a single doctor with details and action buttons
// Props:
//   - doctor: object containing doctor details
//   - onEdit: callback function to handle edit action
//   - onDelete: callback function to handle delete action
export default function DoctorCard({ doctor, onEdit, onDelete }) {
    return (
        // Root Card component with hover effect
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
            {/* Card content displaying doctor details */}
            <CardContent>
                {/* Doctor name */}
                <Typography variant="h6" mb={1}>
                    {doctor.name}
                </Typography>

                {/* Doctor email */}
                <Typography variant="body2" color="text.secondary">
                    📧 {doctor.email}
                </Typography>

                {/* Doctor specialization */}
                <Typography variant="body2" color="text.secondary">
                    🩺 Specialization: {doctor.specialization || "N/A"}
                </Typography>

                {/* Available days (formatted as JSON or fallback) */}
                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ wordBreak: "break-word" }}
                >
                    📅 Available Days:{" "}
                    {doctor.available_days ? JSON.stringify(doctor.available_days) : "N/A"}
                </Typography>

                {/* Slot duration */}
                <Typography variant="body2" color="text.secondary">
                    ⏰ Slot Duration: {doctor.slot_duration || "N/A"}
                </Typography>
            </CardContent>

            {/* Action buttons for editing and deleting */}
            <CardActions sx={{ justifyContent: "flex-end", gap: 1, pr: 2, pb: 2 }}>
                {/* Edit button triggers onEdit callback */}
                <Button
                    size="small"
                    variant="contained"
                    color="warning"
                    startIcon={<Edit />}
                    onClick={() => onEdit(doctor)}
                >
                    Edit
                </Button>

                {/* Delete button triggers onDelete callback */}
                <Button
                    size="small"
                    variant="contained"
                    color="error"
                    startIcon={<Delete />}
                    onClick={() => onDelete(doctor.id)}
                >
                    Delete
                </Button>
            </CardActions>
        </Card>
    );
}
