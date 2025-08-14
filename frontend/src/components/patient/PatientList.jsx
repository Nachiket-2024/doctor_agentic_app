// ---------------------------- External Imports ----------------------------

// Import MUI components for grid layout, box container, and loading spinner
import { Grid, Box, CircularProgress } from "@mui/material";


// ---------------------------- Internal Imports ----------------------------

// Import PatientCard component to display individual patient details
import PatientCard from "./PatientCard";


// ---------------------------- PatientList Component ----------------------------

// Component to render a list of patients or a loader while fetching
// Props:
//   - patients: array of patient objects
//   - loading: boolean indicating data fetch in progress
//   - isListVisible: boolean flag to show/hide the list
//   - onEdit: callback function for editing a patient
//   - onDelete: callback function for deleting a patient
export default function PatientList({
    patients,
    loading,
    isListVisible,
    onEdit,
    onDelete,
}) {
    return (
        <>
            {/* Display loader centered on page when loading */}
            {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {/* Render grid of patient cards when list is visible and not loading */}
            {isListVisible && !loading && (
                <Grid container spacing={3}>
                    {patients.map((patient) => (
                        // Each patient card is placed in a responsive grid item
                        <Grid item xs={12} sm={6} md={4} key={patient.id}>
                            <PatientCard
                                patient={patient}   // Pass patient data
                                onEdit={onEdit}     // Pass edit callback
                                onDelete={onDelete} // Pass delete callback
                            />
                        </Grid>
                    ))}
                </Grid>
            )}
        </>
    );
}
