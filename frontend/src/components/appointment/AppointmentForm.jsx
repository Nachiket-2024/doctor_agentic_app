// --- External imports ---
// MUI components for layout, inputs, and feedback
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

// --- Icons ---
import { CalendarMonth, Save, Cancel } from "@mui/icons-material";

// React hooks
import { useEffect, useState } from "react";

// Redux hooks
import { useSelector, useDispatch } from "react-redux";

// Toast notifications
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// --- Internal imports ---
// Appointment Redux actions & selectors
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

// --- AppointmentForm component ---
export default function AppointmentForm() {
    const dispatch = useDispatch();

    // --- Redux form state ---
    const { doctor_id, patient_id, date, start_time, reason, editingAppointmentId } =
        useSelector((state) => state.appointment.form);
    const loading = useSelector(selectLoading);
    const patients = useSelector(selectPatients);
    const doctors = useSelector(selectDoctors);
    const availableSlots = useSelector(selectAvailableSlots);

    // --- Local loading state for slots ---
    const [slotsLoading, setSlotsLoading] = useState(false);

    // --- Fetch patients and doctors on mount ---
    useEffect(() => {
        dispatch(fetchPatientsAction())
            .unwrap()
            .catch(() => toast.error("Failed to load patients."));
        dispatch(fetchDoctorsAction())
            .unwrap()
            .catch(() => toast.error("Failed to load doctors."));
    }, [dispatch]);

    // --- Fetch available slots when doctor or date changes ---
    useEffect(() => {
        if (doctor_id && date) {
            setSlotsLoading(true);
            dispatch(fetchAvailableSlotsAction({ doctorId: doctor_id, dateStr: date }))
                .unwrap()
                .catch(() => toast.error("Failed to fetch available slots."))
                .finally(() => setSlotsLoading(false));
        }
    }, [doctor_id, date, dispatch]);

    // --- Input change handler ---
    const handleInputChange = (field) => (e) => {
        dispatch(setAppointmentFormFieldAction({ field, value: e.target.value }));
    };

    // --- Form submit handler ---
    const handleSubmit = async (e) => {
        e.preventDefault();
        const payload = { doctor_id, patient_id, date, start_time, reason };
        try {
            if (editingAppointmentId) {
                await dispatch(updateAppointmentAction({ id: editingAppointmentId, data: payload })).unwrap();
                toast.success("Appointment updated successfully.");
            } else {
                await dispatch(createAppointmentAction(payload)).unwrap();
                toast.success("Appointment created successfully.");
            }
            dispatch(resetAppointmentFormAction());
        } catch {
            toast.error("Failed to save appointment.");
        }
    };

    // --- Cancel editing handler ---
    const handleCancel = () => {
        dispatch(resetAppointmentFormAction());
    };

    // --- Render ---
    return (
        <Paper
            elevation={2}
            sx={{
                p: 2,
                mb: 3,
                maxWidth: 400,
                borderRadius: 2,
                backgroundColor: "#fafafa",
            }}
        >
            <ToastContainer position="top-right" autoClose={3000} />

            <Typography variant="subtitle1" fontWeight="bold" mb={1}>
                {editingAppointmentId ? "Edit Appointment" : "Create New Appointment"}
            </Typography>

            <Box component="form" onSubmit={handleSubmit} noValidate>
                <Stack spacing={1.5}>
                    {/* Patient */}
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

                    {/* Doctor */}
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

                    {/* Date */}
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

                    {/* Time Slot */}
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

                    {/* Reason */}
                    <TextField
                        label="Reason (optional)"
                        value={reason}
                        onChange={handleInputChange("reason")}
                        fullWidth
                        size="small"
                    />

                    {/* Buttons */}
                    <Stack direction="row" spacing={1.5} mt={1}>
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
