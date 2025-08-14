// ---------------------------- External Imports ----------------------------

// Import MUI components for grid layout, box container, and loading spinner
import { Grid, Box, CircularProgress } from "@mui/material";


// ---------------------------- Internal Imports ----------------------------

// Import AppointmentCard component to display individual appointment details
import AppointmentCard from "./AppointmentCard";


// ---------------------------- AppointmentList Component ----------------------------

// Component to display a list of appointments or a loader when fetching
// Props:
//   - appointments: array of appointment objects
//   - loading: boolean indicating if data is being fetched
//   - isListVisible: boolean to toggle visibility of the list
//   - onEdit: callback function when an appointment is edited
//   - onDelete: callback function when an appointment is deleted
export default function AppointmentList({
    appointments,
    loading,
    isListVisible,
    onEdit,
    onDelete,
}) {
    return (
        <>
            {/* Display loader centered on the page when loading */}
            {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {/* Render grid of appointment cards when list is visible and not loading */}
            {isListVisible && !loading && (
                <Grid container spacing={3}>
                    {appointments.map((appt) => (
                        // Each appointment card is placed in a responsive grid item
                        <Grid item xs={12} sm={6} md={4} key={appt.id}>
                            <AppointmentCard
                                appointment={appt}   // Pass appointment details
                                onEdit={onEdit}      // Pass edit callback
                                onDelete={onDelete}  // Pass delete callback
                            />
                        </Grid>
                    ))}
                </Grid>
            )}
        </>
    );
}
