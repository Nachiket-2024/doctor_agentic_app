// ---------------------------- External Imports ----------------------------

// Import MUI components for grid layout, box container, and loading spinner
import { Grid, Box, CircularProgress } from "@mui/material";


// ---------------------------- Internal Imports ----------------------------

// Import DoctorCard component to display individual doctor details
import DoctorCard from "./DoctorCard";


// ---------------------------- DoctorList Component ----------------------------

// Component to display a list of doctors or a loader when fetching
// Props:
//   - doctors: array of doctor objects
//   - loading: boolean indicating if data is being fetched
//   - isListVisible: boolean to toggle visibility of the list
//   - onEdit: callback function when a doctor is edited
//   - onDelete: callback function when a doctor is deleted
export default function DoctorList({
    doctors,
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

            {/* Render grid of doctor cards when list is visible and not loading */}
            {isListVisible && !loading && (
                <Grid container spacing={3}>
                    {doctors.map((doctor) => (
                        // Each doctor card is placed in a responsive grid item
                        <Grid item xs={12} sm={6} md={4} key={doctor.id}>
                            <DoctorCard
                                doctor={doctor}   // Pass doctor details
                                onEdit={onEdit}   // Pass edit callback
                                onDelete={onDelete} // Pass delete callback
                            />
                        </Grid>
                    ))}
                </Grid>
            )}
        </>
    );
}
