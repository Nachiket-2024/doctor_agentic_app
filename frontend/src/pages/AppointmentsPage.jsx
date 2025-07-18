import { useState, useEffect } from "react";
import axios from "axios";  // For making HTTP requests
import { useNavigate } from "react-router-dom";  // For navigation

export default function AppointmentsPage() {
    const navigate = useNavigate();
    const [appointments, setAppointments] = useState([]);   // To store appointment data
    const [loading, setLoading] = useState(true);  // To track loading state
    const [error, setError] = useState(null);      // To track any errors
    const [successMessage, setSuccessMessage] = useState(null); // To track success message
    const [newAppointment, setNewAppointment] = useState({
        doctor_id: "",
        patient_id: "",
        date: "",
        start_time: "",
        end_time: "",
        status: "scheduled",
        reason: "",
    }); // State for creating a new appointment

    const [updateAppointmentData, setUpdateAppointmentData] = useState({
        doctor_id: "",
        patient_id: "",
        date: "",
        start_time: "",
        end_time: "",
        status: "",
        reason: "",
    }); // State for updating an existing appointment

    const [selectedAppointment, setSelectedAppointment] = useState(null); // Selected appointment for update

    // State for controlling visibility of appointments list
    const [isAppointmentsListVisible, setIsAppointmentsListVisible] = useState(false);

    // Fetch all appointments on component mount
    useEffect(() => {
        axios.get("http://localhost:8000/appointments", { withCredentials: true })
            .then((res) => {
                setAppointments(res.data);
                setLoading(false);
            })
            .catch((err) => {
                setError("Error fetching appointments");
                setLoading(false);
            });
    }, []);

    // Handle Create Appointment
    const createAppointment = () => {
        axios.post("http://localhost:8000/appointments", newAppointment, { withCredentials: true })
            .then((res) => {
                setAppointments((prevAppointments) => [...prevAppointments, res.data]);
                setSuccessMessage("Appointment created successfully!");
                setError(null);
                setNewAppointment({
                    doctor_id: "",
                    patient_id: "",
                    date: "",
                    start_time: "",
                    end_time: "",
                    status: "scheduled",
                    reason: "",
                });
            })
            .catch((err) => {
                console.error("Error creating appointment:", err);
                setSuccessMessage(null);
                setError("Error creating appointment.");
            });
    };

    // Handle Update Appointment
    const updateAppointment = () => {
        if (!selectedAppointment) return;

        // Only update fields that have a new value
        const updatedData = { ...selectedAppointment };

        // Check for changes in each field and only update the ones that have been filled out
        if (updateAppointmentData.doctor_id !== "") updatedData.doctor_id = updateAppointmentData.doctor_id;
        if (updateAppointmentData.patient_id !== "") updatedData.patient_id = updateAppointmentData.patient_id;
        if (updateAppointmentData.date !== "") updatedData.date = updateAppointmentData.date;
        if (updateAppointmentData.start_time !== "") updatedData.start_time = updateAppointmentData.start_time;
        if (updateAppointmentData.end_time !== "") updatedData.end_time = updateAppointmentData.end_time;
        if (updateAppointmentData.status !== "") updatedData.status = updateAppointmentData.status;
        if (updateAppointmentData.reason !== "") updatedData.reason = updateAppointmentData.reason;

        // Handle update API request
        axios.put(`http://localhost:8000/appointments/${selectedAppointment.id}`, updatedData, { withCredentials: true })
            .then((res) => {
                setAppointments((prevAppointments) =>
                    prevAppointments.map((appointment) => (appointment.id === selectedAppointment.id ? res.data : appointment))
                );
                setSelectedAppointment(null);
                setUpdateAppointmentData({
                    doctor_id: "",
                    patient_id: "",
                    date: "",
                    start_time: "",
                    end_time: "",
                    status: "",
                    reason: "",
                });
                setSuccessMessage("Appointment updated successfully!");
            })
            .catch((err) => {
                console.error("Error updating appointment:", err);
                setSuccessMessage(null);
                setError("Error updating appointment.");
            });
    };

    // Handle Delete Appointment
    const deleteAppointment = (appointmentId) => {
        axios.delete(`http://localhost:8000/appointments/${appointmentId}`, { withCredentials: true })
            .then(() => {
                setAppointments((prevAppointments) => prevAppointments.filter((appointment) => appointment.id !== appointmentId));
                setSelectedAppointment(null);  // Reset selected appointment
            })
            .catch((err) => {
                console.error("Error deleting appointment:", err);
            });
    };

    // Show loading or error state
    if (loading) return <p>Loading appointments...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-2">Manage Appointments</h1>

            {/* Toggle button for appointments list visibility */}
            <button
                onClick={() => setIsAppointmentsListVisible(!isAppointmentsListVisible)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
                {isAppointmentsListVisible ? "Hide Appointments List" : "Show Appointments List"}
            </button>

            {/* List of appointments (conditionally rendered based on visibility state) */}
            {isAppointmentsListVisible && (
                <div>
                    <h2 className="text-xl font-semibold mt-4">Appointments List</h2>
                    <ul>
                        {appointments.map((appointment) => (
                            <li key={appointment.id} className="mb-2">
                                <p><strong>{appointment.patient_id}</strong> - {appointment.doctor_id}</p>
                                <p>{appointment.date}</p>
                                <button
                                    onClick={() => setSelectedAppointment(appointment)}
                                    className="mt-1 text-blue-500"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => deleteAppointment(appointment.id)}
                                    className="mt-1 ml-4 text-red-500"
                                >
                                    Delete
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Success or Error message */}
            {successMessage && <p className="text-green-500">{successMessage}</p>}
            {error && <p className="text-red-500">{error}</p>}

            {/* Create New Appointment Form */}
            {!selectedAppointment && (
                <div className="mt-6">
                    <h3 className="text-lg">Create New Appointment</h3>
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            createAppointment();
                        }}
                    >
                        <input
                            type="number"
                            placeholder="Doctor ID (required)"
                            value={newAppointment.doctor_id}
                            onChange={(e) => setNewAppointment({ ...newAppointment, doctor_id: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="number"
                            placeholder="Patient ID (required)"
                            value={newAppointment.patient_id}
                            onChange={(e) => setNewAppointment({ ...newAppointment, patient_id: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="date"
                            placeholder="Date (required)"
                            value={newAppointment.date}
                            onChange={(e) => setNewAppointment({ ...newAppointment, date: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="time"
                            placeholder="Start Time (required)"
                            value={newAppointment.start_time}
                            onChange={(e) => setNewAppointment({ ...newAppointment, start_time: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="time"
                            placeholder="End Time"
                            value={newAppointment.end_time}
                            onChange={(e) => setNewAppointment({ ...newAppointment, end_time: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Reason (optional)"
                            value={newAppointment.reason}
                            onChange={(e) => setNewAppointment({ ...newAppointment, reason: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <button
                            type="submit"
                            className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                            Create Appointment
                        </button>
                    </form>
                </div>
            )}

            {/* Update Appointment Form */}
            {selectedAppointment && (
                <div className="mt-6">
                    <h3 className="text-lg">Update Appointment</h3>
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            updateAppointment();
                        }}
                    >
                        <input
                            type="number"
                            placeholder="Doctor ID"
                            value={updateAppointmentData.doctor_id}
                            onChange={(e) => setUpdateAppointmentData({ ...updateAppointmentData, doctor_id: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="number"
                            placeholder="Patient ID"
                            value={updateAppointmentData.patient_id}
                            onChange={(e) => setUpdateAppointmentData({ ...updateAppointmentData, patient_id: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="date"
                            placeholder="Date"
                            value={updateAppointmentData.date}
                            onChange={(e) => setUpdateAppointmentData({ ...updateAppointmentData, date: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="time"
                            placeholder="Start Time"
                            value={updateAppointmentData.start_time}
                            onChange={(e) => setUpdateAppointmentData({ ...updateAppointmentData, start_time: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="time"
                            placeholder="End Time"
                            value={updateAppointmentData.end_time}
                            onChange={(e) => setUpdateAppointmentData({ ...updateAppointmentData, end_time: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Reason"
                            value={updateAppointmentData.reason}
                            onChange={(e) => setUpdateAppointmentData({ ...updateAppointmentData, reason: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <button
                            type="submit"
                            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                            Update Appointment
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
