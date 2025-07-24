import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getAllDoctors, deleteDoctor, createDoctor, updateDoctor } from "../services/doctorService";

const DoctorsPage = () => {
    const [doctors, setDoctors] = useState([]);
    const [loading, setLoading] = useState(true);  // To handle loading state
    const [isListVisible, setIsListVisible] = useState(false);  // State to toggle doctors' list visibility

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [specialization, setSpecialization] = useState("");
    const [availableDays, setAvailableDays] = useState("");
    const [slotDuration, setSlotDuration] = useState("");
    const [editingDoctorId, setEditingDoctorId] = useState(null);  // Track which doctor is being edited

    const navigate = useNavigate();  // For navigation to dashboard

    // Fetch doctors when the page loads
    const fetchDoctors = async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            alert("Unauthorized, please login again.");
            return;
        }

        try {
            setLoading(true);  // Set loading to true while fetching
            const response = await getAllDoctors();
            setDoctors(response.data);  // Set the doctors state
            setLoading(false);  // Set loading to false after data is fetched
        } catch (err) {
            setLoading(false);  // Set loading to false in case of error
            console.error("Error fetching doctors:", err);
            alert("Error fetching doctors.");
        }
    };

    // Handle deletion of doctor
    const handleDelete = async (id) => {
        if (window.confirm("Are you sure?")) {
            try {
                await deleteDoctor(id);
                fetchDoctors();  // Re-fetch doctors after update
            } catch (err) {
                console.error("Error deleting doctor:", err);
                alert("Error deleting doctor.");
            }
        }
    };

    // Handle form submission for both creating and editing doctors
    const handleSubmit = async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            alert("Unauthorized, please login again.");
            return;
        }

        const payload = {
            name,
            email,
            role: "doctor",
            specialization: specialization || null,  // Set to null if empty
            available_days: availableDays ? JSON.parse(availableDays) : null,  // Parse string to object, or null
            slot_duration: slotDuration || null,  // Set to null if empty
        };

        try {
            if (editingDoctorId) {
                // Update the doctor
                await updateDoctor(editingDoctorId, payload);
                fetchDoctors();  // Re-fetch doctors after update
            } else {
                // Create a new doctor
                await createDoctor(payload);
                fetchDoctors();  // Re-fetch doctors after creation
            }

            // Reset form after submission
            setName("");
            setEmail("");
            setSpecialization("");
            setAvailableDays("");
            setSlotDuration("");
            setEditingDoctorId(null);  // Clear editing state
        } catch (err) {
            console.error("Error saving doctor:", err);
            alert("Error saving doctor.");
        }
    };

    // Handle editing a doctor (populate the form with current values)
    const handleEdit = (doctor) => {
        setEditingDoctorId(doctor.id);
        setName(doctor.name);
        setEmail(doctor.email);
        setSpecialization(doctor.specialization || "");
        setAvailableDays(JSON.stringify(doctor.available_days) || "");
        setSlotDuration(doctor.slot_duration || "");
    };

    useEffect(() => {
        fetchDoctors();
    }, []);

    return (
        <div className="p-4">
            <h1 className="text-xl font-bold mb-4">Doctors Management</h1>

            {/* Create/Edit Doctor Form */}
            <form onSubmit={(e) => e.preventDefault()}>
                <div>
                    <label>Name:</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Specialization:</label>
                    <input
                        type="text"
                        value={specialization}
                        onChange={(e) => setSpecialization(e.target.value)}
                    />
                </div>
                <div>
                    <label>Available Days:</label>
                    <input
                        type="text"
                        value={availableDays}
                        onChange={(e) => setAvailableDays(e.target.value)}
                        placeholder='{"mon": "9-11", "tue": "10-12"}'  // Sample format
                    />
                </div>
                <div>
                    <label>Slot Duration:</label>
                    <input
                        type="number"
                        value={slotDuration}
                        onChange={(e) => setSlotDuration(e.target.value)}
                    />
                </div>
                <button onClick={handleSubmit}>
                    {editingDoctorId ? "Update Doctor" : "Create Doctor"}
                </button>
            </form>

            {/* Toggle Button to Show/Hide Doctors List */}
            <div style={{ marginTop: "20px" }}>
                <button
                    onClick={() => setIsListVisible(!isListVisible)}
                    className="bg-gray-500 text-white px-4 py-2 rounded"
                >
                    {isListVisible ? "Hide Doctors List" : "Show Doctors List"}
                </button>
            </div>

            {/* Doctors List (only visible when isListVisible is true) */}
            {loading ? (
                <p>Loading doctors...</p>
            ) : isListVisible && (
                <div>
                    {doctors.map((doctor) => (
                        <div key={doctor.id} style={{ marginBottom: "20px", border: "1px solid #ddd", padding: "10px" }}>
                            <p>Name: {doctor.name}</p>
                            <p>Email: {doctor.email}</p>
                            <p>Specialization: {doctor.specialization || "N/A"}</p>
                            <p>Available Days: {doctor.available_days ? JSON.stringify(doctor.available_days) : "N/A"}</p>
                            <p>Slot Duration: {doctor.slot_duration || "N/A"}</p>

                            <div>
                                {/* Edit Button */}
                                <button onClick={() => handleEdit(doctor)}>Edit</button>
                                {/* Delete Button */}
                                <button onClick={() => handleDelete(doctor.id)}>Delete</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Go to Dashboard Button */}
            <div style={{ marginTop: "20px" }}>
                <button onClick={() => navigate("/dashboard")} className="bg-blue-500 text-white px-4 py-2 rounded">
                    Go to Dashboard
                </button>
            </div>
        </div>
    );
};

export default DoctorsPage;
