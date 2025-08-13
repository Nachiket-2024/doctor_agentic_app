// --- External imports ---
// MUI components for layout and loading indicator
import { Grid, Box, CircularProgress } from "@mui/material";

// --- Internal imports ---
// DoctorCard component to display individual doctor info
import DoctorCard from "./DoctorCard";

// --- DoctorList component ---
// Displays a list of doctor cards, or a loader while fetching
export default function DoctorList({
    doctors,
    loading,
    isListVisible,
    onEdit,
    onDelete,
}) {
    return (
        <>
            {/* Loader when fetching doctors */}
            {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {/* Render grid of doctor cards when visible and not loading */}
            {isListVisible && !loading && (
                <Grid container spacing={3}>
                    {doctors.map((doctor) => (
                        <Grid item xs={12} sm={6} md={4} key={doctor.id}>
                            <DoctorCard
                                doctor={doctor}
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
