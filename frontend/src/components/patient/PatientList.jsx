// --- External imports ---
// MUI components for layout and button
import { Grid, Box, CircularProgress } from "@mui/material";

// --- Internal imports ---
// PatientCard component to render individual patients
import PatientCard from "./PatientCard";

// --- PatientList component ---
// Shows the list of PatientCard components only (no toggle button)
export default function PatientList({
    patients,
    loading,
    isListVisible,
    onEdit,
    onDelete,
}) {
    return (
        <>
            {/* Loading spinner */}
            {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {/* Patients grid list */}
            {isListVisible && !loading && (
                <Grid container spacing={3}>
                    {patients.map((patient) => (
                        <Grid item xs={12} sm={6} md={4} key={patient.id}>
                            <PatientCard
                                patient={patient}
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
