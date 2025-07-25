// --- Import React and its hooks ---
import { useState, useEffect, useRef } from "react";

// --- For programmatic navigation ---
import { useNavigate } from "react-router-dom";

// --- Import API service functions (now using centralized axios instance) ---
import {
    getAllDoctors,
    deleteDoctor,
    createDoctor,
    updateDoctor,
} from "../services/doctorService";

// --- Toast notification system ---
import { toast, ToastContainer } from "react-toastify"; // Toast library
import "react-toastify/dist/ReactToastify.css"; // Toast styles

// --- DoctorsPage Component ---
const DoctorsPage = () => {
    // --- State variables for doctor list and loading status ---
    const [doctors, setDoctors] = useState([]);
    const [loading, setLoading] = useState(true);

    // --- Toggle visibility of doctor list ---
    const [isListVisible, setIsListVisible] = useState(false);

    // --- Form input states ---
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [specialization, setSpecialization] = useState("");
    const [availableDays, setAvailableDays] = useState("");
    const [slotDuration, setSlotDuration] = useState("");

    // --- Track whether we're editing an existing doctor ---
    const [editingDoctorId, setEditingDoctorId] = useState(null);

    // --- Hook to navigate to dashboard ---
    const navigate = useNavigate();

    // --- Ref to avoid double fetch in StrictMode ---
    const hasFetched = useRef(false);

    // --- Fetch all doctors from backend ---
    const fetchDoctors = async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            toast.error("Unauthorized, please login again."); // Show toast on missing token
            return;
        }

        try {
            setLoading(true); // Start loading
            const response = await getAllDoctors(); // API call
            setDoctors(response.data); // Update doctor list
            toast.success("Doctors loaded successfully."); // Success toast
        } catch (err) {
            console.error("Error fetching doctors:", err);
            toast.error("Failed to fetch doctors."); // Error toast
        } finally {
            setLoading(false); // End loading
        }
    };

    // --- Delete a doctor by ID ---
    const handleDelete = async (id) => {
        if (window.confirm("Are you sure?")) {
            try {
                await deleteDoctor(id); // Call delete API
                await fetchDoctors(); // Refresh list
                toast.success("Doctor deleted successfully."); // Success toast
            } catch (err) {
                console.error("Error deleting doctor:", err);
                toast.error("Failed to delete doctor."); // Error toast
            }
        }
    };

    // --- Create or update doctor based on editing state ---
    const handleSubmit = async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            toast.error("Unauthorized, please login again."); // Token error toast
            return;
        }

        const payload = {
            name,
            email,
            role: "doctor", // Static role
            specialization: specialization || null,
            available_days: availableDays ? JSON.parse(availableDays) : null,
            slot_duration: slotDuration || null,
        };

        try {
            if (editingDoctorId) {
                await updateDoctor(editingDoctorId, payload); // Update doctor
                toast.success("Doctor updated successfully.");
            } else {
                await createDoctor(payload); // Create new doctor
                toast.success("Doctor created successfully.");
            }
            await fetchDoctors(); // Refresh list

            // --- Reset form ---
            setName("");
            setEmail("");
            setSpecialization("");
            setAvailableDays("");
            setSlotDuration("");
            setEditingDoctorId(null);
        } catch (err) {
            console.error("Error saving doctor:", err);
            toast.error("Failed to save doctor."); // Error toast
        }
    };

    // --- Populate form fields for editing ---
    const handleEdit = (doctor) => {
        setEditingDoctorId(doctor.id);
        setName(doctor.name);
        setEmail(doctor.email);
        setSpecialization(doctor.specialization || "");
        setAvailableDays(JSON.stringify(doctor.available_days) || "");
        setSlotDuration(doctor.slot_duration || "");
    };

    // --- Initial fetch on component mount (only once, even in StrictMode) ---
    useEffect(() => {
        if (hasFetched.current) return; // Prevent double call in dev
        hasFetched.current = true;
        fetchDoctors();
    }, []);

    // --- Render UI ---
    return (
        <div className="p-4">
            {/* Toast container (must be in render tree once) */}
            <ToastContainer position="top-right" autoClose={3000} />

            <h1 className="text-xl font-bold mb-4">Doctors Management</h1>

            {/* --- Doctor Creation / Editing Form --- */}
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
                        placeholder='{"mon": "9-11", "tue": "10-12"}'
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

            {/* --- Toggle Button to Show/Hide List --- */}
            <div style={{ marginTop: "20px" }}>
                <button
                    onClick={() => setIsListVisible(!isListVisible)}
                    className="bg-gray-500 text-white px-4 py-2 rounded"
                >
                    {isListVisible ? "Hide Doctors List" : "Show Doctors List"}
                </button>
            </div>

            {/* --- Doctors List --- */}
            {loading ? (
                <p>Loading doctors...</p>
            ) : (
                isListVisible && (
                    <div>
                        {doctors.map((doctor) => (
                            <div
                                key={doctor.id}
                                style={{
                                    marginBottom: "20px",
                                    border: "1px solid #ddd",
                                    padding: "10px",
                                }}
                            >
                                <p>Name: {doctor.name}</p>
                                <p>Email: {doctor.email}</p>
                                <p>Specialization: {doctor.specialization || "N/A"}</p>
                                <p>
                                    Available Days:{" "}
                                    {doctor.available_days
                                        ? JSON.stringify(doctor.available_days)
                                        : "N/A"}
                                </p>
                                <p>Slot Duration: {doctor.slot_duration || "N/A"}</p>
                                <div>
                                    <button onClick={() => handleEdit(doctor)}>Edit</button>
                                    <button onClick={() => handleDelete(doctor.id)}>Delete</button>
                                </div>
                            </div>
                        ))}
                    </div>
                )
            )}

            {/* --- Navigation to Dashboard --- */}
            <div style={{ marginTop: "20px" }}>
                <button
                    onClick={() => navigate("/dashboard")}
                    className="bg-blue-500 text-white px-4 py-2 rounded"
                >
                    Go to Dashboard
                </button>
            </div>
        </div>
    );
};

// --- Export DoctorsPage as default ---
export default DoctorsPage;
