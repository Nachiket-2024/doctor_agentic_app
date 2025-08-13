// --- External imports ---
// MUI components for layout and loading indicator
import { Grid, Box, CircularProgress } from "@mui/material";

// --- Internal imports ---
// AppointmentCard component to display individual appointment info
import AppointmentCard from "./AppointmentCard";

// --- AppointmentList component ---
// Displays a list of appointment cards or a loader while fetching
export default function AppointmentList({
    appointments,
    loading,
    isListVisible,
    onEdit,
    onDelete,
}) {
    return (
        <>
            {/* Loader when fetching appointments */}
            {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {/* Render grid of appointment cards when visible and not loading */}
            {isListVisible && !loading && (
                <Grid container spacing={3}>
                    {appointments.map((appt) => (
                        <Grid item xs={12} sm={6} md={4} key={appt.id}>
                            <AppointmentCard
                                appointment={appt}
                                onEdit={onEdit}
                                onDelete={onDelete}
                            />
                        </Grid>
                    ))}
                </Grid>
            )}
        </>
    );
}
