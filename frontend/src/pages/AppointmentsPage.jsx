// ---------------------------- Imports ----------------------------

// React hooks
import { useEffect, useState, useRef } from "react";

// Service functions for appointments
import {
    getAllAppointments,
    deleteAppointment,
} from "../services/appointmentService";

// Reusable form component for creating/editing appointments
import AppointmentForm from "../components/AppointmentForm";

// Service functions for fetching doctor data
import { getAllDoctors } from "../services/doctorService";

// Service functions for fetching patient data
import { getAllPatients } from "../services/patientService";

// Toast notification API and its styles
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// ---------------------------- Component ----------------------------
const AppointmentsPage = () => {
    // ---------------------------- State ----------------------------

    // All appointments
    const [appointments, setAppointments] = useState([]);

    // Selected appointment (used when editing)
    const [selectedAppointment, setSelectedAppointment] = useState(null);

    // Controls form visibility
    const [showForm, setShowForm] = useState(false);

    // Mapping doctor IDs to names
    const [doctorMap, setDoctorMap] = useState({});

    // Mapping patient IDs to names
    const [patientMap, setPatientMap] = useState({});

    // ---------------------------- StrictMode Guard ----------------------------

    // Ensures fetch logic only runs once even under React.StrictMode (dev only)
    const hasFetchedRef = useRef(false);

    // ---------------------------- useEffect for Data Load ----------------------------
    useEffect(() => {
        // Only fetch once
        if (hasFetchedRef.current) return;
        hasFetchedRef.current = true;

        // Load appointments
        fetchAllAppointments();

        // Load doctors
        getAllDoctors()
            .then((res) => {
                const map = {};
                res.data.forEach((doc) => (map[doc.id] = doc.name));
                setDoctorMap(map);
            })
            .catch((err) => {
                console.error("Error loading doctors:", err);
                toast.error("Failed to load doctors");
            });

        // Load patients
        getAllPatients()
            .then((res) => {
                const map = {};
                res.data.forEach((pat) => (map[pat.id] = pat.name));
                setPatientMap(map);
            })
            .catch((err) => {
                console.error("Error loading patients:", err);
                toast.error("Failed to load patients");
            });
    }, []);

    // ---------------------------- API Calls ----------------------------

    // Fetches all appointments from the backend
    const fetchAllAppointments = () => {
        getAllAppointments()
            .then((res) => {
                setAppointments(res.data);
                toast.success("Appointments loaded");
            })
            .catch((err) => {
                console.error("Error fetching appointments:", err);
                toast.error("Failed to load appointments");
            });
    };

    // ---------------------------- Handlers ----------------------------

    // Open form to create or edit an appointment
    const handleOpenForm = (appt = null) => {
        setSelectedAppointment(appt); // If null, it's a new appointment
        setShowForm(true);
    };

    // Delete an appointment by ID
    const handleDelete = async (id) => {
        if (window.confirm("Are you sure you want to delete this appointment?")) {
            try {
                await deleteAppointment(id);
                toast.success("Appointment deleted");
                fetchAllAppointments(); // Refresh list after deletion
            } catch (error) {
                console.error("Error deleting appointment:", error);
                const message = error.response?.data?.detail || "Error deleting appointment";
                toast.error(message);
            }
        }
    };

    // Handle successful form submission
    const handleFormSuccess = () => {
        setShowForm(false);
        setSelectedAppointment(null);
        toast.success("Appointment saved");
        fetchAllAppointments(); // Refresh list after add/edit
    };

    // ---------------------------- Render ----------------------------
    return (
        <div className="p-6">
            {/* Toast container for notifications */}
            <ToastContainer position="top-right" autoClose={3000} />

            {/* Header section */}
            <div className="flex justify-between items-center mb-4">
                <div className="flex items-center space-x-4">
                    <h2 className="text-2xl font-bold">Appointments</h2>
                    <button
                        onClick={() => (window.location.href = "/dashboard")}
                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                    >
                        Go to Dashboard
                    </button>
                </div>

                {/* Button to create a new appointment */}
                <button
                    onClick={() => handleOpenForm()}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                >
                    + New Appointment
                </button>
            </div>

            {/* Appointments table */}
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white shadow-md rounded-xl overflow-hidden">
                    <thead>
                        <tr className="bg-gray-100 text-left">
                            <th className="py-2 px-4">Doctor</th>
                            <th className="py-2 px-4">Patient</th>
                            <th className="py-2 px-4">Date</th>
                            <th className="py-2 px-4">Time</th>
                            <th className="py-2 px-4">Status</th>
                            <th className="py-2 px-4">Reason</th>
                            <th className="py-2 px-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {appointments.map((appt) => (
                            <tr key={appt.id} className="border-t hover:bg-gray-50">
                                <td className="py-2 px-4">
                                    {doctorMap[appt.doctor_id] || appt.doctor_id}
                                </td>
                                <td className="py-2 px-4">
                                    {patientMap[appt.patient_id] || appt.patient_id}
                                </td>
                                <td className="py-2 px-4">{appt.date}</td>
                                <td className="py-2 px-4">
                                    {appt.start_time} - {appt.end_time || ""}
                                </td>
                                <td className="py-2 px-4">{appt.status}</td>
                                <td className="py-2 px-4">{appt.reason}</td>
                                <td className="py-2 px-4 space-x-2">
                                    <button
                                        onClick={() => handleOpenForm(appt)}
                                        className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(appt.id)}
                                        className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {appointments.length === 0 && (
                            <tr>
                                <td colSpan="7" className="text-center py-6 text-gray-500">
                                    No appointments found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Appointment form rendered conditionally */}
            {showForm && (
                <div className="mt-6 bg-gray-100 p-4 rounded-xl border">
                    <AppointmentForm
                        selectedAppointment={selectedAppointment}
                        onSuccess={handleFormSuccess}
                    />
                </div>
            )}
        </div>
    );
};

// ---------------------------- Export ----------------------------

export default AppointmentsPage;
