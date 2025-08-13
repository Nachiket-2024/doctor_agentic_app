// --- External imports ---
import { Card, CardContent, CardActions, Typography, Button } from "@mui/material";
import { Edit, Delete } from "@mui/icons-material";
import { useSelector } from "react-redux";

// --- AppointmentCard component ---
// Single appointment card displaying patient/doctor names, date, slot, and action buttons
export default function AppointmentCard({ appointment, onEdit, onDelete }) {
    // --- Get patients and doctors from Redux ---
    const patients = useSelector((state) => state.appointment.patients);
    const doctors = useSelector((state) => state.appointment.doctors);

    // --- Map IDs to names ---
    const patient = patients.find((p) => p.id === appointment.patient_id);
    const doctor = doctors.find((d) => d.id === appointment.doctor_id);

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
                    Patient: {patient ? patient.name : appointment.patient_id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Doctor: {doctor ? doctor.name : appointment.doctor_id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Date: {appointment.date}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Slot: {appointment.slot}
                </Typography>
            </CardContent>

            <CardActions sx={{ justifyContent: "flex-end", gap: 1, pr: 2, pb: 2 }}>
                <Button
                    size="small"
                    variant="contained"
                    color="warning"
                    startIcon={<Edit />}
                    onClick={() => onEdit(appointment)}
                >
                    Edit
                </Button>
                <Button
                    size="small"
                    variant="contained"
                    color="error"
                    startIcon={<Delete />}
                    onClick={() => onDelete(appointment.id)}
                >
                    Delete
                </Button>
            </CardActions>
        </Card>
    );
}
