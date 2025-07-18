import { useState, useEffect } from "react";
import axios from "axios";  // For making HTTP requests
import { useNavigate } from "react-router-dom";  // For navigation

export default function DoctorsPage() {
    const navigate = useNavigate();
    const [doctors, setDoctors] = useState([]);   // To store doctor data
    const [loading, setLoading] = useState(true);  // To track loading state
    const [error, setError] = useState(null);      // To track any errors
    const [successMessage, setSuccessMessage] = useState(null); // To track success message
    const [newDoctor, setNewDoctor] = useState({
        name: "",
        specialization: "",
        available_days: {}, // Available days with times for doctor
        slot_duration: 30,   // Default slot duration of 30 minutes
        email: "",
        phone_number: "",
    }); // State for creating a new doctor

    const [updateDoctorData, setUpdateDoctorData] = useState({
        name: "",
        specialization: "",
        available_days: {}, // Available days with times for doctor
        slot_duration: 30,   // Default slot duration of 30 minutes
        email: "",
        phone_number: "",
    }); // State for updating an existing doctor

    const [selectedDoctor, setSelectedDoctor] = useState(null); // Selected doctor for update

    // State for controlling visibility of doctors list
    const [isDoctorsListVisible, setIsDoctorsListVisible] = useState(false);

    // Fetch all doctors on component mount
    useEffect(() => {
        axios.get("http://localhost:8000/doctors", { withCredentials: true })
            .then((res) => {
                setDoctors(res.data);
                setLoading(false);
            })
            .catch((err) => {
                setError("Error fetching doctors");
                setLoading(false);
            });
    }, []);

    // Handle Create Doctor
    const createDoctor = () => {
        // Format the available_days to lowercase keys (e.g., "mon", "tue")
        const formattedDays = Object.keys(newDoctor.available_days).reduce((acc, day) => {
            const lowerCaseDay = day.toLowerCase();
            acc[lowerCaseDay] = newDoctor.available_days[day];
            return acc;
        }, {});

        const doctorData = { ...newDoctor, available_days: formattedDays };

        axios.post("http://localhost:8000/doctors", doctorData, { withCredentials: true })
            .then((res) => {
                setDoctors((prevDoctors) => [...prevDoctors, res.data]);
                setSuccessMessage("Doctor created successfully!");
                setError(null);
                setNewDoctor({
                    name: "",
                    specialization: "",
                    available_days: {},
                    slot_duration: 30,
                    email: "",
                    phone_number: "",
                });
            })
            .catch((err) => {
                console.error("Error creating doctor:", err);
                setSuccessMessage(null);
                setError("Error creating doctor.");
            });
    };

    // Handle Update Doctor
    const updateDoctor = () => {
        if (!selectedDoctor) return;

        // Only update fields that have a new value
        const updatedData = { ...selectedDoctor };

        // Check for changes in each field and only update the ones that have been filled out
        if (updateDoctorData.name !== "") updatedData.name = updateDoctorData.name;
        if (updateDoctorData.specialization !== "") updatedData.specialization = updateDoctorData.specialization;
        if (updateDoctorData.email !== "") updatedData.email = updateDoctorData.email;
        if (updateDoctorData.phone_number !== "") updatedData.phone_number = updateDoctorData.phone_number;

        // Format the available_days to lowercase keys (e.g., "mon", "tue") and only update if provided
        const formattedDays = Object.keys(updateDoctorData.available_days).reduce((acc, day) => {
            const lowerCaseDay = day.toLowerCase();
            if (updateDoctorData.available_days[day]) {
                acc[lowerCaseDay] = updateDoctorData.available_days[day];
            }
            return acc;
        }, {});

        if (Object.keys(formattedDays).length > 0) updatedData.available_days = formattedDays;

        // Handle update API request
        axios.put(`http://localhost:8000/doctors/${selectedDoctor.id}`, updatedData, { withCredentials: true })
            .then((res) => {
                setDoctors((prevDoctors) =>
                    prevDoctors.map((doctor) => (doctor.id === selectedDoctor.id ? res.data : doctor))
                );
                setSelectedDoctor(null);
                setUpdateDoctorData({
                    name: "",
                    specialization: "",
                    available_days: {},
                    slot_duration: 30,
                    email: "",
                    phone_number: "",
                });
                setSuccessMessage("Doctor updated successfully!");
            })
            .catch((err) => {
                console.error("Error updating doctor:", err);
                setSuccessMessage(null);
                setError("Error updating doctor.");
            });
    };

    // Handle Delete Doctor
    const deleteDoctor = (doctorId) => {
        axios.delete(`http://localhost:8000/doctors/${doctorId}`, { withCredentials: true })
            .then(() => {
                setDoctors((prevDoctors) => prevDoctors.filter((doctor) => doctor.id !== doctorId));
                setSelectedDoctor(null);  // Reset selected doctor
            })
            .catch((err) => {
                console.error("Error deleting doctor:", err);
            });
    };

    // Show loading or error state
    if (loading) return <p>Loading doctors...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-2">Manage Doctors</h1>

            {/* Toggle button for doctor list visibility */}
            <button
                onClick={() => setIsDoctorsListVisible(!isDoctorsListVisible)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
                {isDoctorsListVisible ? "Hide Doctors List" : "Show Doctors List"}
            </button>

            {/* List of doctors (conditionally rendered based on visibility state) */}
            {isDoctorsListVisible && (
                <div>
                    <h2 className="text-xl font-semibold mt-4">Doctors List</h2>
                    <ul>
                        {doctors.map((doctor) => (
                            <li key={doctor.id} className="mb-2">
                                <p><strong>{doctor.name}</strong></p>
                                <p>{doctor.specialization}</p>
                                <button
                                    onClick={() => setSelectedDoctor(doctor)}
                                    className="mt-1 text-blue-500"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => deleteDoctor(doctor.id)}
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

            {/* Create New Doctor Form */}
            {!selectedDoctor && (
                <div className="mt-6">
                    <h3 className="text-lg">Create New Doctor</h3>
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            createDoctor();
                        }}
                    >
                        <input
                            type="text"
                            placeholder="Doctor Name (required)"
                            value={newDoctor.name}
                            onChange={(e) => setNewDoctor({ ...newDoctor, name: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Specialization (required)"
                            value={newDoctor.specialization}
                            onChange={(e) => setNewDoctor({ ...newDoctor, specialization: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Email (required)"
                            value={newDoctor.email}
                            onChange={(e) => setNewDoctor({ ...newDoctor, email: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Phone Number (optional)"
                            value={newDoctor.phone_number}
                            onChange={(e) => setNewDoctor({ ...newDoctor, phone_number: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />

                        {/* Doctor Availability */}
                        <h4 className="mt-4">Doctor Availability</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {["mon", "tue", "wed", "thu", "fri", "sat", "sun"].map((day) => (
                                <div key={day} className="mb-2">
                                    <input
                                        type="text"
                                        placeholder={`${day} (e.g., 10:00, 14:00)`}
                                        value={newDoctor.available_days[day]?.join(", ") || ""}
                                        onChange={(e) =>
                                            setNewDoctor({
                                                ...newDoctor,
                                                available_days: {
                                                    ...newDoctor.available_days,
                                                    [day]: e.target.value.split(",").map((time) => time.trim()),
                                                },
                                            })
                                        }
                                        className="p-2 border mb-2 w-full"
                                    />
                                </div>
                            ))}

                            {/* Slot Duration */}
                            <div className="mb-2">
                                <label htmlFor="slot_duration" className="block">Slot Duration (in minutes)</label>
                                <input
                                    type="number"
                                    id="slot_duration"
                                    value={newDoctor.slot_duration}
                                    onChange={(e) => setNewDoctor({ ...newDoctor, slot_duration: e.target.value })}
                                    className="p-2 border w-full"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                            Create Doctor
                        </button>
                    </form>
                </div>
            )}

            {/* Update Doctor Form */}
            {selectedDoctor && (
                <div className="mt-6">
                    <h3 className="text-lg">Update Doctor: {selectedDoctor.name}</h3>
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            updateDoctor();
                        }}
                    >
                        <input
                            type="text"
                            placeholder="Doctor Name"
                            value={updateDoctorData.name}
                            onChange={(e) => setUpdateDoctorData({ ...updateDoctorData, name: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Specialization"
                            value={updateDoctorData.specialization}
                            onChange={(e) => setUpdateDoctorData({ ...updateDoctorData, specialization: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Email"
                            value={updateDoctorData.email}
                            onChange={(e) => setUpdateDoctorData({ ...updateDoctorData, email: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Phone Number"
                            value={updateDoctorData.phone_number}
                            onChange={(e) => setUpdateDoctorData({ ...updateDoctorData, phone_number: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />

                        {/* Doctor Availability */}
                        <h4 className="mt-4">Doctor Availability</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {["mon", "tue", "wed", "thu", "fri", "sat", "sun"].map((day) => (
                                <div key={day} className="mb-2">
                                    <input
                                        type="text"
                                        placeholder={`${day} (e.g., 10:00, 14:00)`}
                                        value={updateDoctorData.available_days[day]?.join(", ") || ""}
                                        onChange={(e) =>
                                            setUpdateDoctorData({
                                                ...updateDoctorData,
                                                available_days: {
                                                    ...updateDoctorData.available_days,
                                                    [day]: e.target.value.split(",").map((time) => time.trim()),
                                                },
                                            })
                                        }
                                        className="p-2 border mb-2 w-full"
                                    />
                                </div>
                            ))}

                            {/* Slot Duration */}
                            <div className="mb-2">
                                <label htmlFor="slot_duration" className="block">Slot Duration (in minutes)</label>
                                <input
                                    type="number"
                                    id="slot_duration"
                                    value={updateDoctorData.slot_duration}
                                    onChange={(e) => setUpdateDoctorData({ ...updateDoctorData, slot_duration: e.target.value })}
                                    className="p-2 border w-full"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                            Update Doctor
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
