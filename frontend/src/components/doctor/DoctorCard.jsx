// --- External imports ---
import { Card, CardContent, CardActions, Typography, Button } from "@mui/material";
import { Edit, Delete } from "@mui/icons-material";

// --- DoctorCard component ---
// Single doctor card with details and action buttons
export default function DoctorCard({ doctor, onEdit, onDelete }) {
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
                <Typography variant="h6" mb={1}>
                    {doctor.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    📧 {doctor.email}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    🩺 Specialization: {doctor.specialization || "N/A"}
                </Typography>
                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ wordBreak: "break-word" }}
                >
                    📅 Available Days:{" "}
                    {doctor.available_days ? JSON.stringify(doctor.available_days) : "N/A"}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    ⏰ Slot Duration: {doctor.slot_duration || "N/A"}
                </Typography>
            </CardContent>
            <CardActions sx={{ justifyContent: "flex-end", gap: 1, pr: 2, pb: 2 }}>
                <Button
                    size="small"
                    variant="contained"
                    color="warning"
                    startIcon={<Edit />}
                    onClick={() => onEdit(doctor)}
                >
                    Edit
                </Button>
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
