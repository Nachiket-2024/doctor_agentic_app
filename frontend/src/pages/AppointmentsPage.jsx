// ---------------------------- Imports ----------------------------
import React, { useEffect, useState } from "react"; // React and hooks for state and lifecycle
import {
    getAllAppointments,
    deleteAppointment,
} from "../services/appointmentService"; // Appointment API functions
import AppointmentForm from "../components/AppointmentForm"; // Reusable form component
import { getAllDoctors } from "../services/doctorService"; // Doctor API call
import { getAllPatients } from "../services/patientService"; // Patient API call
import { toast, ToastContainer } from "react-toastify"; // Toast system for notifications
import "react-toastify/dist/ReactToastify.css"; // Toast CSS styles

// ---------------------------- Component ----------------------------
const AppointmentsPage = () => {
    // Appointment data state
    const [appointments, setAppointments] = useState([]);
    const [selectedAppointment, setSelectedAppointment] = useState(null); // For editing
    const [showForm, setShowForm] = useState(false); // Toggle for showing form

    // Maps to resolve doctor/patient IDs to names
    const [doctorMap, setDoctorMap] = useState({});
    const [patientMap, setPatientMap] = useState({});

    // ---------------------------- Load all necessary data ----------------------------
    useEffect(() => {
        // Load appointments and mapping data on component mount
        fetchAllAppointments();
        getAllDoctors().then((res) => {
            const map = {};
            res.data.forEach((doc) => (map[doc.id] = doc.name)); // Map id to name
            setDoctorMap(map);
        });
        getAllPatients().then((res) => {
            const map = {};
            res.data.forEach((pat) => (map[pat.id] = pat.name)); // Map id to name
            setPatientMap(map);
        });
    }, []);

    // Function to fetch all appointments and handle errors
    const fetchAllAppointments = () => {
        getAllAppointments()
            .then((res) => {
                setAppointments(res.data); // Store data in state
                toast.success("Appointments loaded"); // Show success toast
            })
            .catch((err) => {
                console.error("Error fetching appointments:", err); // Log error for debugging
                toast.error("Failed to load appointments"); // Show error toast
            });
    };

    // ---------------------------- Handlers ----------------------------

    // Open form modal for create or edit
    const handleOpenForm = (appt = null) => {
        setSelectedAppointment(appt); // Set selected appt for editing
        setShowForm(true); // Show the form
    };

    // Delete appointment by ID and handle success/error
    const handleDelete = async (id) => {
        if (window.confirm("Are you sure you want to delete this appointment?")) {
            try {
                await deleteAppointment(id); // Delete API call
                toast.success("Appointment deleted successfully!"); // Show success toast
                fetchAllAppointments(); // Refresh list
            } catch (error) {
                console.error("Error deleting appointment:", error); // Debug log
                const message =
                    error.response?.data?.detail || "Error deleting appointment."; // Extract detail if present
                toast.error(message); // Show error toast
            }
        }
    };

    // Callback when appointment form is submitted successfully
    const handleFormSuccess = () => {
        setShowForm(false); // Hide form
        setSelectedAppointment(null); // Reset selected
        toast.success("Appointment saved successfully!"); // Show success toast
        fetchAllAppointments(); // Refresh list
    };

    // ---------------------------- UI ----------------------------
    return (
        <div className="p-6">
            {/* Toast message container (only needed once in app) */}
            <ToastContainer position="top-right" autoClose={3000} />

            {/* Header section with button */}
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Appointments</h2>
                <button
                    onClick={() => handleOpenForm()}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                >
                    + New Appointment
                </button>
            </div>

            {/* Table displaying all appointments */}
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
                        {/* Render each appointment row */}
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
                                        onClick={() => handleOpenForm(appt)} // Edit
                                        className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(appt.id)} // Delete
                                        className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {/* Empty state message */}
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

            {/* Form/modal section for creating or editing appointments */}
            {showForm && (
                <div className="mt-6 bg-gray-100 p-4 rounded-xl border">
                    <AppointmentForm
                        selectedAppointment={selectedAppointment} // Pass selected appt
                        onSuccess={handleFormSuccess} // Callback on success
                    />
                </div>
            )}
        </div>
    );
};

// Export the page component
export default AppointmentsPage;
