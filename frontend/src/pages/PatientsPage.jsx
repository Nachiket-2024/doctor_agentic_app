import { useState, useEffect } from "react";
import axios from "axios";  // For making HTTP requests
import { useNavigate } from "react-router-dom";  // For navigation

export default function PatientsPage() {
    const navigate = useNavigate();
    const [patients, setPatients] = useState([]);   // To store patient data
    const [loading, setLoading] = useState(true);  // To track loading state
    const [error, setError] = useState(null);      // To track any errors
    const [successMessage, setSuccessMessage] = useState(null); // To track success message
    const [newPatient, setNewPatient] = useState({
        name: "",
        email: "",
        phone: "",
        age: null,
    }); // State for creating a new patient

    const [updatePatientData, setUpdatePatientData] = useState({
        name: "",
        email: "",
        phone: "",
        age: null,
    }); // State for updating an existing patient

    const [selectedPatient, setSelectedPatient] = useState(null); // Selected patient for update

    // State for controlling visibility of patients list
    const [isPatientsListVisible, setIsPatientsListVisible] = useState(false);

    // Fetch all patients on component mount
    useEffect(() => {
        axios.get("http://localhost:8000/patients", { withCredentials: true })
            .then((res) => {
                setPatients(res.data);
                setLoading(false);
            })
            .catch((err) => {
                setError("Error fetching patients");
                setLoading(false);
            });
    }, []);

    // Handle Create Patient
    const createPatient = () => {
        if (!newPatient.name || !newPatient.email) {
            setError("Name and email are required.");
            return;
        }

        axios.post("http://localhost:8000/patients", newPatient, { withCredentials: true })
            .then((res) => {
                setPatients((prevPatients) => [...prevPatients, res.data]);
                setSuccessMessage("Patient created successfully!");
                setError(null);
                setNewPatient({
                    name: "",
                    email: "",
                    phone: "",
                    age: null,
                });
            })
            .catch((err) => {
                console.error("Error creating patient:", err);
                setSuccessMessage(null);
                setError("Error creating patient.");
            });
    };

    // Handle Update Patient
    const updatePatient = () => {
        if (!selectedPatient) return;

        const updatedData = { ...selectedPatient };

        if (updatePatientData.name !== "") updatedData.name = updatePatientData.name;
        if (updatePatientData.email !== "") updatedData.email = updatePatientData.email;
        if (updatePatientData.phone !== "") updatedData.phone = updatePatientData.phone;
        if (updatePatientData.age !== null) updatedData.age = updatePatientData.age;

        axios.put(`http://localhost:8000/patients/${selectedPatient.id}`, updatedData, { withCredentials: true })
            .then((res) => {
                setPatients((prevPatients) =>
                    prevPatients.map((patient) => (patient.id === selectedPatient.id ? res.data : patient))
                );
                setSelectedPatient(null);
                setUpdatePatientData({
                    name: "",
                    email: "",
                    phone: "",
                    age: null,
                });
                setSuccessMessage("Patient updated successfully!");
            })
            .catch((err) => {
                console.error("Error updating patient:", err);
                setSuccessMessage(null);
                setError("Error updating patient.");
            });
    };

    // Handle Delete Patient
    const deletePatient = (patientId) => {
        axios.delete(`http://localhost:8000/patients/${patientId}`, { withCredentials: true })
            .then(() => {
                setPatients((prevPatients) => prevPatients.filter((patient) => patient.id !== patientId));
                setSelectedPatient(null);  // Reset selected patient
            })
            .catch((err) => {
                console.error("Error deleting patient:", err);
            });
    };

    // Show loading or error state
    if (loading) return <p>Loading patients...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-2">Manage Patients</h1>

            {/* Toggle button for patient list visibility */}
            <button
                onClick={() => setIsPatientsListVisible(!isPatientsListVisible)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
                {isPatientsListVisible ? "Hide Patients List" : "Show Patients List"}
            </button>

            {/* List of patients (conditionally rendered based on visibility state) */}
            {isPatientsListVisible && (
                <div>
                    <h2 className="text-xl font-semibold mt-4">Patients List</h2>
                    <ul>
                        {patients.map((patient) => (
                            <li key={patient.id} className="mb-2">
                                <p><strong>{patient.name}</strong></p>
                                <p>{patient.email}</p>
                                <button
                                    onClick={() => setSelectedPatient(patient)}
                                    className="mt-1 text-blue-500"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => deletePatient(patient.id)}
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

            {/* Create New Patient Form */}
            {!selectedPatient && (
                <div className="mt-6">
                    <h3 className="text-lg">Create New Patient</h3>
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            createPatient();
                        }}
                    >
                        <input
                            type="text"
                            placeholder="Name (required)"
                            value={newPatient.name}
                            onChange={(e) => setNewPatient({ ...newPatient, name: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="email"
                            placeholder="Email (required)"
                            value={newPatient.email}
                            onChange={(e) => setNewPatient({ ...newPatient, email: e.target.value })}
                            required
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Phone Number (optional)"
                            value={newPatient.phone}
                            onChange={(e) => setNewPatient({ ...newPatient, phone: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="number"
                            placeholder="Age (optional)"
                            value={newPatient.age || ""}
                            onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <button
                            type="submit"
                            className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                            Create Patient
                        </button>
                    </form>
                </div>
            )}

            {/* Update Patient Form */}
            {selectedPatient && (
                <div className="mt-6">
                    <h3 className="text-lg">Update Patient: {selectedPatient.name}</h3>
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            updatePatient();
                        }}
                    >
                        <input
                            type="text"
                            placeholder="Name"
                            value={updatePatientData.name}
                            onChange={(e) => setUpdatePatientData({ ...updatePatientData, name: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="email"
                            placeholder="Email"
                            value={updatePatientData.email}
                            onChange={(e) => setUpdatePatientData({ ...updatePatientData, email: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="text"
                            placeholder="Phone Number"
                            value={updatePatientData.phone}
                            onChange={(e) => setUpdatePatientData({ ...updatePatientData, phone: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <input
                            type="number"
                            placeholder="Age"
                            value={updatePatientData.age || ""}
                            onChange={(e) => setUpdatePatientData({ ...updatePatientData, age: e.target.value })}
                            className="p-2 border mb-2 w-full"
                        />
                        <button
                            type="submit"
                            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                            Update Patient
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
