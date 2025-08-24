// ---------------------------- External Imports ----------------------------

// Import MUI components for card layout, typography, and buttons
import { Card, CardContent, CardActions, Typography, Button } from "@mui/material";

// Import icons for edit and delete actions
import { Edit, Delete } from "@mui/icons-material";

// Import Redux hook to access the store state
import { useSelector } from "react-redux";


// ---------------------------- AppointmentCard Component ----------------------------

// Define a functional component for displaying a single appointment card
export default function AppointmentCard({ appointment, onEdit, onDelete }) {

    // ---------------------------- Redux State ----------------------------

    // Get the list of patients from the Redux store
    const patients = useSelector((state) => state.appointment.patients);

    // Get the list of doctors from the Redux store
    const doctors = useSelector((state) => state.appointment.doctors);


    // ---------------------------- Map IDs to Names ----------------------------

    // Find the patient object matching the appointment's patient_id
    const patient = patients.find((p) => p.id === appointment.patient_id);

    // Find the doctor object matching the appointment's doctor_id
    const doctor = doctors.find((d) => d.id === appointment.doctor_id);


    // ---------------------------- Render Card ----------------------------

    return (
        // Root Card component with hover effect
        <Card
            sx={{
                boxShadow: 3,                    // Initial shadow for the card
                borderRadius: 3,                  // Rounded corners
                transition: "0.3s",               // Smooth hover transition
                "&:hover": {                      // On hover, increase shadow and lift card
                    boxShadow: 6,
                    transform: "translateY(-4px)"
                },
            }}
        >
            {/* Card content showing appointment details */}
            <CardContent>
                {/* Display patient name or fallback to patient ID */}
                <Typography variant="h6" mb={1}>
                    Patient: {patient ? patient.name : appointment.patient_id}
                </Typography>

                {/* Display doctor name or fallback to doctor ID */}
                <Typography variant="body2" color="text.secondary">
                    Doctor: {doctor ? doctor.name : appointment.doctor_id}
                </Typography>

                {/* Display appointment date */}
                <Typography variant="body2" color="text.secondary">
                    Date: {appointment.date}
                </Typography>

                {/* Display appointment slot */}
                <Typography variant="body2" color="text.secondary">
                    Slot: {appointment.start_time} {appointment.end_time ? `- ${appointment.end_time}` : ""}
                </Typography>
            </CardContent>

            {/* Action buttons for edit and delete */}
            <CardActions sx={{ justifyContent: "flex-end", gap: 1, pr: 2, pb: 2 }}>
                {/* Edit button triggers onEdit callback */}
                <Button
                    size="small"
                    variant="contained"
                    color="warning"
                    startIcon={<Edit />}
                    onClick={() => onEdit(appointment)}
                >
                    Edit
                </Button>

                {/* Delete button triggers onDelete callback */}
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
