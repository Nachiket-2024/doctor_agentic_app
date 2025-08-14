// ---------------------------- External Imports ----------------------------

// Import MUI components for layout, text inputs, buttons, menus, progress indicators, and containers
import {
    Box,
    Typography,
    TextField,
    Button,
    MenuItem,
    CircularProgress,
    Stack,
    Paper
} from "@mui/material";

// Import icons for calendar, save, and cancel actions
import { CalendarMonth, Save, Cancel } from "@mui/icons-material";

// Import React hooks for state and side effects
import { useEffect, useState } from "react";

// Import Redux hooks to access store state and dispatch actions
import { useSelector, useDispatch } from "react-redux";

// Import toast notifications for success/error feedback
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


// ---------------------------- Internal Imports ----------------------------

// Import Redux actions and selectors for managing appointments
import {
    fetchPatientsAction,
    fetchDoctorsAction,
    fetchAvailableSlotsAction,
    createAppointmentAction,
    updateAppointmentAction,
    resetAppointmentFormAction,
    setAppointmentFormFieldAction,
    selectLoading,
    selectAvailableSlots,
    selectPatients,
    selectDoctors,
} from "../../features/appointmentSlice";


// ---------------------------- AppointmentForm Component ----------------------------

// Component for creating or editing an appointment
export default function AppointmentForm() {
    // Initialize Redux dispatch function
    const dispatch = useDispatch();

    // ---------------------------- Redux Form State ----------------------------

    // Destructure form fields and editing state from Redux store
    const { doctor_id, patient_id, date, start_time, reason, editingAppointmentId } =
        useSelector((state) => state.appointment.form);

    // Get global loading state from Redux
    const loading = useSelector(selectLoading);

    // Get patients, doctors, and available slots from Redux
    const patients = useSelector(selectPatients);
    const doctors = useSelector(selectDoctors);
    const availableSlots = useSelector(selectAvailableSlots);

    // ---------------------------- Local State ----------------------------

    // Local state for loading indicator while fetching available slots
    const [slotsLoading, setSlotsLoading] = useState(false);

    // ---------------------------- Fetch Data on Mount ----------------------------

    // Fetch patients and doctors when component mounts
    useEffect(() => {
        // Dispatch fetchPatientsAction and handle errors
        dispatch(fetchPatientsAction())
            .unwrap()
            .catch(() => toast.error("Failed to load patients."));

        // Dispatch fetchDoctorsAction and handle errors
        dispatch(fetchDoctorsAction())
            .unwrap()
            .catch(() => toast.error("Failed to load doctors."));
    }, [dispatch]);

    // ---------------------------- Fetch Available Slots ----------------------------

    // Fetch available slots whenever doctor or date changes
    useEffect(() => {
        if (doctor_id && date) {
            setSlotsLoading(true); // Show loading indicator
            dispatch(fetchAvailableSlotsAction({ doctorId: doctor_id, dateStr: date }))
                .unwrap()
                .catch(() => toast.error("Failed to fetch available slots."))
                .finally(() => setSlotsLoading(false)); // Hide loading indicator
        }
    }, [doctor_id, date, dispatch]);

    // ---------------------------- Handlers ----------------------------

    // Handle input changes for form fields
    const handleInputChange = (field) => (e) => {
        dispatch(setAppointmentFormFieldAction({ field, value: e.target.value }));
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault(); // Prevent default form submission
        const payload = { doctor_id, patient_id, date, start_time, reason }; // Prepare payload

        try {
            if (editingAppointmentId) {
                // Update existing appointment
                await dispatch(updateAppointmentAction({ id: editingAppointmentId, data: payload })).unwrap();
                toast.success("Appointment updated successfully.");
            } else {
                // Create new appointment
                await dispatch(createAppointmentAction(payload)).unwrap();
                toast.success("Appointment created successfully.");
            }
            // Reset form after success
            dispatch(resetAppointmentFormAction());
        } catch {
            toast.error("Failed to save appointment."); // Show error on failure
        }
    };

    // Handle cancel action for editing
    const handleCancel = () => {
        dispatch(resetAppointmentFormAction()); // Reset form fields
    };

    // ---------------------------- Render ----------------------------

    return (
        // Paper container for the form
        <Paper
            elevation={2} // Slight shadow
            sx={{
                p: 2,              // Padding
                mb: 3,             // Margin bottom
                maxWidth: 400,     // Max width
                borderRadius: 2,   // Rounded corners
                backgroundColor: "#fafafa", // Light background
            }}
        >
            {/* Toast notifications container */}
            <ToastContainer position="top-right" autoClose={3000} />

            {/* Form title */}
            <Typography variant="subtitle1" fontWeight="bold" mb={1}>
                {editingAppointmentId ? "Edit Appointment" : "Create New Appointment"}
            </Typography>

            {/* Form element */}
            <Box component="form" onSubmit={handleSubmit} noValidate>
                <Stack spacing={1.5}>
                    {/* Patient selection field */}
                    <TextField
                        select
                        label="Patient"
                        value={patient_id}
                        onChange={handleInputChange("patient_id")}
                        fullWidth
                        size="small"
                        required
                    >
                        {patients.map((p) => (
                            <MenuItem key={p.id} value={p.id}>
                                {p.name}
                            </MenuItem>
                        ))}
                    </TextField>

                    {/* Doctor selection field */}
                    <TextField
                        select
                        label="Doctor"
                        value={doctor_id}
                        onChange={handleInputChange("doctor_id")}
                        fullWidth
                        size="small"
                        required
                    >
                        {doctors.map((d) => (
                            <MenuItem key={d.id} value={d.id}>
                                {d.name}
                            </MenuItem>
                        ))}
                    </TextField>

                    {/* Date picker field */}
                    <TextField
                        label="Date"
                        type="date"
                        value={date}
                        onChange={handleInputChange("date")}
                        fullWidth
                        size="small"
                        required
                        InputLabelProps={{ shrink: true }}
                    />

                    {/* Time slot selection */}
                    <TextField
                        select
                        label="Time Slot"
                        value={start_time}
                        onChange={handleInputChange("start_time")}
                        fullWidth
                        size="small"
                        required
                    >
                        {slotsLoading ? (
                            <MenuItem disabled>
                                <Box display="flex" alignItems="center" gap={1}>
                                    <CircularProgress size={16} />
                                    Loading...
                                </Box>
                            </MenuItem>
                        ) : availableSlots.length > 0 ? (
                            availableSlots.map((slot, idx) => (
                                <MenuItem key={idx} value={slot}>
                                    {slot}
                                </MenuItem>
                            ))
                        ) : (
                            <MenuItem disabled>No slots available</MenuItem>
                        )}
                    </TextField>

                    {/* Reason input (optional) */}
                    <TextField
                        label="Reason (optional)"
                        value={reason}
                        onChange={handleInputChange("reason")}
                        fullWidth
                        size="small"
                    />

                    {/* Action buttons */}
                    <Stack direction="row" spacing={1.5} mt={1}>
                        {/* Submit button */}
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            size="small"
                            startIcon={editingAppointmentId ? <Save /> : <CalendarMonth />}
                            disabled={loading}
                        >
                            {editingAppointmentId ? "Update Appointment" : "Book Appointment"}
                        </Button>

                        {/* Cancel button (shown only when editing) */}
                        {editingAppointmentId && (
                            <Button
                                type="button"
                                variant="outlined"
                                color="secondary"
                                startIcon={<Cancel />}
                                onClick={handleCancel}
                                size="small"
                            >
                                Cancel
                            </Button>
                        )}
                    </Stack>
                </Stack>
            </Box>
        </Paper>
    );
}
