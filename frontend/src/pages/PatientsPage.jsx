import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

export default function PatientsPage() {
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [age, setAge] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [editingPatientId, setEditingPatientId] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null); // Success message state
    const [errorMessage, setErrorMessage] = useState(null); // Error message state
    const [isPatientsVisible, setIsPatientsVisible] = useState(false); // Toggle for patient list visibility

    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const fetchPatients = async () => {
            const token = localStorage.getItem("access_token");

            if (!token) {
                navigate("/login");
                return;
            }

            try {
                const response = await axios.get("http://localhost:8000/patient/", {
                    headers: { Authorization: `Bearer ${token}` },
                });

                const cleaned = response.data.map((p) => ({
                    ...p,
                    age: p.age ?? "N/A",
                    phone_number: p.phone_number ?? "N/A",
                    google_id: p.google_id ?? "N/A",
                    specialization: p.specialization ?? "N/A",
                    available_days: p.available_days ?? "N/A",
                    slot_duration: p.slot_duration ?? "N/A",
                }));

                setPatients(cleaned);
                setError(null);
                setSuccessMessage("Patients loaded successfully."); // Success message for fetch
            } catch (err) {
                console.error("Failed to fetch patients:", err);
                setErrorMessage("Could not load patients.");
            } finally {
                setLoading(false);
            }
        };

        fetchPatients();
    }, [navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem("access_token");

        const payload = {
            name,
            email,
            role: "patient",
            age: age.trim() === "" ? null : parseInt(age),
            phone_number: phoneNumber.trim() === "" ? null : phoneNumber,
            // Omit available_days for patients, as they aren't relevant here
        };

        try {
            if (editingPatientId) {
                await axios.put(`http://localhost:8000/patient/${editingPatientId}`, payload, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                setPatients((prev) =>
                    prev.map((p) => (p.id === editingPatientId ? { ...p, ...payload } : p))
                );
                setSuccessMessage("Patient updated successfully."); // Success message for update
            } else {
                const response = await axios.post("http://localhost:8000/patient/", payload, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                const patient = {
                    ...response.data,
                    age: response.data.age ?? "N/A",
                    phone_number: response.data.phone_number ?? "N/A",
                    google_id: response.data.google_id ?? "N/A",
                    specialization: response.data.specialization ?? "N/A",
                    available_days: response.data.available_days ?? "N/A",
                    slot_duration: response.data.slot_duration ?? "N/A",
                };

                setPatients((prev) => [...prev, patient]);
                setSuccessMessage("Patient created successfully."); // Success message for create
            }
            resetForm();
        } catch (err) {
            console.error("Save failed:", err);
            setErrorMessage("Failed to save patient.");
        }
    };

    const handleEditPatient = (patient) => {
        setEditingPatientId(patient.id);
        setName(patient.name || "");
        setEmail(patient.email || "");
        setAge(patient.age !== "N/A" ? patient.age.toString() : "");
        setPhoneNumber(patient.phone_number !== "N/A" ? patient.phone_number : "");
    };

    const handleDeletePatient = async (patientId) => {
        if (!window.confirm("Are you sure you want to delete this patient?")) return;
        try {
            const token = localStorage.getItem("access_token");
            await axios.delete(`http://localhost:8000/patient/${patientId}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setPatients((prev) => prev.filter((p) => p.id !== patientId));
            setSuccessMessage("Patient deleted successfully."); // Success message for delete
        } catch (err) {
            console.error("Delete failed:", err);
            setErrorMessage("Failed to delete patient.");
        }
    };

    const resetForm = () => {
        setName("");
        setEmail("");
        setAge("");
        setPhoneNumber("");
        setEditingPatientId(null);
    };

    // Function to toggle patient list visibility
    const togglePatientListVisibility = () => {
        setIsPatientsVisible(!isPatientsVisible);
    };

    // Navigate to Dashboard
    const handleGoToDashboard = () => {
        navigate("/dashboard");
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Patients</h1>

            {/* Success and Error Messages */}
            {successMessage && (
                <p className="text-green-500 mb-4">{successMessage}</p>
            )}
            {errorMessage && (
                <p className="text-red-500 mb-4">{errorMessage}</p>
            )}

            {/* --- Create/Edit Form --- */}
            <form onSubmit={handleSubmit} className="mb-6 space-y-4 max-w-md">
                <h2 className="text-lg font-semibold">
                    {editingPatientId ? "Edit Patient" : "Create New Patient"}
                </h2>
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
                    type="number"
                    placeholder="Age"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    className="w-full border border-gray-300 px-3 py-2 rounded"
                />
                <input
                    type="text"
                    placeholder="Phone Number"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-full border border-gray-300 px-3 py-2 rounded"
                />
                <div className="space-x-2">
                    <button
                        type="submit"
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                    >
                        {editingPatientId ? "Update" : "Create"}
                    </button>
                    {editingPatientId && (
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

            {/* --- Buttons for Navigation and Visibility Toggle --- */}
            <div className="mb-4">
                <button
                    onClick={handleGoToDashboard}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded mr-4"
                >
                    Go to Dashboard
                </button>
                <button
                    onClick={togglePatientListVisibility}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                >
                    {isPatientsVisible ? "Hide" : "Show"} Patients List
                </button>
            </div>

            {/* --- Conditional UI --- */}
            {loading && <p>Loading patients...</p>}
            {error && <p className="text-red-500">{error}</p>}
            {!loading && !error && patients.length === 0 && (
                <p className="text-gray-600">No patients found.</p>
            )}

            {/* --- List of Patients (Visible/Hidden based on state) --- */}
            {isPatientsVisible && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {patients.map((patient) => (
                        <div key={patient.id} className="border border-gray-300 rounded p-4 shadow-md">
                            <h2 className="text-lg font-semibold mb-2">{patient.name}</h2>
                            <p>Email: {patient.email}</p>
                            <p>Age: {patient.age}</p>
                            <p>Phone: {patient.phone_number}</p>

                            <div className="mt-4 space-x-2">
                                <button
                                    onClick={() => handleEditPatient(patient)}
                                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => handleDeletePatient(patient.id)}
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
