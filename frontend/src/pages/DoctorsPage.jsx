import { useEffect, useState } from "react";  // Import hooks from React for managing state and lifecycle
import { useNavigate } from "react-router-dom";  // Import navigate hook for routing
import axios from "axios";  // Import axios for making API calls

export default function DoctorsPage() {
    // State variables to store doctor data, form inputs, success/error messages, etc.
    const [doctors, setDoctors] = useState([]);  // State to store the list of doctors
    const [loading, setLoading] = useState(true);  // State for loading status
    const [error, setError] = useState(null);  // State to store any error messages
    const [name, setName] = useState("");  // State for doctor's name
    const [email, setEmail] = useState("");  // State for doctor's email
    const [specialization, setSpecialization] = useState("");  // State for doctor's specialization
    const [availableDays, setAvailableDays] = useState({
        mon: "", tue: "", wed: "", thu: "", fri: "", sat: "", sun: "",
    });  // State for doctor's available days
    const [slotDuration, setSlotDuration] = useState("");  // State for slot duration
    const [editingDoctorId, setEditingDoctorId] = useState(null);  // State to track editing mode
    const [successMessage, setSuccessMessage] = useState(null);  // State for success messages
    const [errorMessage, setErrorMessage] = useState(null);  // State for error messages
    const [isDoctorsVisible, setIsDoctorsVisible] = useState(false);  // State for toggling doctor list visibility

    const navigate = useNavigate();  // Hook to navigate between pages

    // Fetch doctors on component mount
    useEffect(() => {
        const fetchDoctors = async () => {
            const token = localStorage.getItem("access_token");  // Retrieve the token from localStorage

            if (!token) {  // If no token, redirect to login page
                navigate("/login");
                return;
            }

            try {
                // Fetch doctors data from backend API with the token in headers
                const response = await axios.get("http://localhost:8000/doctor/", {
                    headers: { Authorization: `Bearer ${token}` },
                });

                // Clean and format data (e.g., ensure specialization, available_days, and slot_duration are not null)
                const cleaned = response.data.map((d) => ({
                    ...d,
                    specialization: d.specialization ?? "N/A",
                    available_days: d.available_days ?? {},
                    slot_duration: d.slot_duration ?? "N/A",
                }));

                setDoctors(cleaned);  // Update state with fetched doctors data
                setSuccessMessage("Doctors loaded successfully.");  // Set success message
                setError(null);  // Clear any error message
            } catch (err) {
                console.error("Failed to fetch doctors:", err);
                setErrorMessage("Could not load doctors.");  // Set error message on failure
            } finally {
                setLoading(false);  // Set loading to false once the request is done
            }
        };

        fetchDoctors();  // Call the fetchDoctors function
    }, [navigate]);  // Re-run useEffect only if `navigate` changes

    // Handle form submit for both creating and updating doctors
    const handleSubmit = async (e) => {
        e.preventDefault();  // Prevent default form submission behavior

        const token = localStorage.getItem("access_token");  // Retrieve token from localStorage

        // Format the availableDays object properly before sending it to the backend
        const formattedAvailableDays = {};
        Object.keys(availableDays).forEach((day) => {
            formattedAvailableDays[day] = availableDays[day]
                .split(",")  // Split time slots by commas
                .map((slot) => slot.trim())  // Trim whitespace around slots
                .filter((slot) => slot);  // Remove empty time slots
        });

        // Prepare payload for the API request
        const payload = {
            name,
            email,
            role: "doctor",  // Role is always "doctor" for this page
            specialization: specialization.trim() || null,  // If specialization is empty, set it as null
            available_days: formattedAvailableDays,  // Set formatted available days
            slot_duration: slotDuration.trim() || null,  // If slot duration is empty, set it as null
        };

        try {
            if (editingDoctorId) {
                // If editing an existing doctor, send a PUT request to update
                await axios.put(`http://localhost:8000/doctor/${editingDoctorId}`, payload, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                setDoctors((prev) =>
                    prev.map((d) => (d.id === editingDoctorId ? { ...d, ...payload } : d))  // Update the doctor in the state
                );
                setSuccessMessage("Doctor updated successfully.");  // Set success message for update
            } else {
                // If creating a new doctor, send a POST request to create
                const response = await axios.post("http://localhost:8000/doctor/", payload, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                // Clean the response data and format before adding to state
                const doctor = {
                    ...response.data,
                    specialization: response.data.specialization ?? "N/A",
                    available_days: response.data.available_days ?? {},
                    slot_duration: response.data.slot_duration ?? "N/A",
                };

                setDoctors((prev) => [...prev, doctor]);  // Add the new doctor to the state
                setSuccessMessage("Doctor created successfully.");  // Set success message for creation
            }
            resetForm();  // Reset the form after submission
        } catch (err) {
            console.error("Save failed:", err);
            setErrorMessage("Failed to save doctor.");  // Set error message if the request fails
        }
    };

    // Handle editing an existing doctor (populate form with doctor's existing data)
    const handleEditDoctor = (doctor) => {
        setEditingDoctorId(doctor.id);  // Set the doctor ID to indicate we're editing this doctor
        setName(doctor.name || "");  // Populate the name input
        setEmail(doctor.email || "");  // Populate the email input
        setSpecialization(doctor.specialization !== "N/A" ? doctor.specialization : "");  // Populate the specialization input
        setAvailableDays(doctor.available_days || {  // Populate the available days input
            mon: "", tue: "", wed: "", thu: "", fri: "", sat: "", sun: "",
        });
        setSlotDuration(doctor.slot_duration !== "N/A" ? doctor.slot_duration : "");  // Populate the slot duration input
    };

    // Handle deleting a doctor
    const handleDeleteDoctor = async (doctorId) => {
        if (!window.confirm("Are you sure you want to delete this doctor?")) return;  // Ask for confirmation before deletion
        try {
            const token = localStorage.getItem("access_token");  // Retrieve the token
            await axios.delete(`http://localhost:8000/doctor/${doctorId}`, {
                headers: { Authorization: `Bearer ${token}` },  // Pass the token in the request headers
            });
            setDoctors((prev) => prev.filter((d) => d.id !== doctorId));  // Remove the deleted doctor from the state
            setSuccessMessage("Doctor deleted successfully.");  // Set success message for deletion
        } catch (err) {
            console.error("Delete failed:", err);
            setErrorMessage("Failed to delete doctor.");  // Set error message if deletion fails
        }
    };

    // Handle changes in available days input fields
    const handleDayChange = (day) => (e) => {
        const newTimeSlot = e.target.value;  // Get the new time slot for the day
        setAvailableDays((prevDays) => {
            const updatedDays = { ...prevDays };
            updatedDays[day] = newTimeSlot;  // Update the available days state for the selected day
            return updatedDays;
        });
    };

    // Reset the form fields and state after creating or editing a doctor
    const resetForm = () => {
        setName("");
        setEmail("");
        setSpecialization("");
        setAvailableDays({
            mon: "", tue: "", wed: "", thu: "", fri: "", sat: "", sun: "",
        });
        setSlotDuration("");
        setEditingDoctorId(null);  // Reset the editing ID to indicate no doctor is being edited
    };

    // Toggle the visibility of the doctors list
    const toggleDoctorListVisibility = () => {
        setIsDoctorsVisible(!isDoctorsVisible);  // Toggle the state between true/false
    };

    // Navigate to the dashboard page
    const handleGoToDashboard = () => {
        navigate("/dashboard");  // Use the navigate hook to go to the dashboard
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Doctors</h1>

            {successMessage && <p className="text-green-500 mb-4">{successMessage}</p>}  {/* Show success message */}
            {errorMessage && <p className="text-red-500 mb-4">{errorMessage}</p>}  {/* Show error message */}

            {/* --- Create/Edit Form --- */}
            <form onSubmit={handleSubmit} className="mb-6 space-y-4 max-w-md">
                <h2 className="text-lg font-semibold">{editingDoctorId ? "Update Doctor" : "Create New Doctor"}</h2>
                <input
                    type="text"
                    placeholder="Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="w-full border border-gray-300 px-3 py-2 rounded"
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full border border-gray-300 px-3 py-2 rounded"
                />
                <input
                    type="text"
                    placeholder="Specialization"
                    value={specialization}
                    onChange={(e) => setSpecialization(e.target.value)}
                    className="w-full border border-gray-300 px-3 py-2 rounded"
                />

                {/* Available days input fields */}
                <div className="space-y-4">
                    {["mon", "tue", "wed", "thu", "fri", "sat", "sun"].map((day) => (
                        <div key={day}>
                            <label className="block font-semibold">{day.toUpperCase()}:</label>
                            <input
                                type="text"
                                placeholder="e.g. (10:00-14:00, 15:00-18:00)"
                                value={availableDays[day]}
                                onChange={handleDayChange(day)}
                                className="w-full border border-gray-300 px-3 py-2 rounded"
                            />
                        </div>
                    ))}
                </div>

                {/* Slot duration input */}
                <input
                    type="text"
                    placeholder="Slot Duration (in minutes)"
                    value={slotDuration}
                    onChange={(e) => setSlotDuration(e.target.value)}
                    className="w-full border border-gray-300 px-3 py-2 rounded"
                />
                <div className="space-x-2">
                    <button
                        type="submit"
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                    >
                        {editingDoctorId ? "Update" : "Create"}
                    </button>
                    {editingDoctorId && (
                        <button
                            type="button"
                            onClick={resetForm}
                            className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded"
                        >
                            Cancel
                        </button>
                    )}
                </div>
            </form>

            {/* Navigation and toggle visibility buttons */}
            <div className="mb-4">
                <button
                    onClick={handleGoToDashboard}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded mr-4"
                >
                    Go to Dashboard
                </button>
                <button
                    onClick={toggleDoctorListVisibility}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                >
                    {isDoctorsVisible ? "Hide" : "Show"} Doctors List
                </button>
            </div>

            {/* --- Doctors List --- */}
            {isDoctorsVisible && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {doctors.map((doctor) => (
                        <div key={doctor.id} className="border border-gray-300 rounded p-4 shadow-md">
                            <h2 className="text-lg font-semibold mb-2">{doctor.name}</h2>
                            <p>Email: {doctor.email}</p>
                            <p>Specialization: {doctor.specialization}</p>
                            <p>Available Days: {JSON.stringify(doctor.available_days)}</p>
                            <p>Slot Duration: {doctor.slot_duration}</p>

                            <div className="mt-4 space-x-2">
                                <button
                                    onClick={() => handleEditDoctor(doctor)}
                                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded"
                                >
                                    Update Doctor
                                </button>
                                <button
                                    onClick={() => handleDeleteDoctor(doctor.id)}
                                    className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
