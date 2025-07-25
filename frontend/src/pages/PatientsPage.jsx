import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    getAllPatients,
    createPatient,
    updatePatient,
    deletePatient
} from "../services/patientService";
import PatientForm from "../components/PatientForm";

export default function PatientsPage() {
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingPatient, setEditingPatient] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [errorMessage, setErrorMessage] = useState(null);
    const [isPatientsVisible, setIsPatientsVisible] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchPatients();
    }, []);

    const fetchPatients = async () => {
        try {
            const res = await getAllPatients();
            const cleaned = res.data.map((p) => ({
                ...p,
                age: p.age ?? "N/A",
                phone_number: p.phone_number ?? "N/A",
                google_id: p.google_id ?? "N/A",
            }));
            setPatients(cleaned);
            setSuccessMessage("Patients loaded successfully.");
        } catch (err) {
            console.error("Failed to fetch patients:", err);
            setErrorMessage("Could not load patients.");
        } finally {
            setLoading(false);
        }
    };

    const handleFormSubmit = async (payload) => {
        try {
            if (editingPatient) {
                await updatePatient(editingPatient.id, payload);
                setPatients((prev) =>
                    prev.map((p) => (p.id === editingPatient.id ? { ...p, ...payload } : p))
                );
                setSuccessMessage("Patient updated successfully.");
            } else {
                const res = await createPatient(payload);
                const newPatient = {
                    ...res.data,
                    age: res.data.age ?? "N/A",
                    phone_number: res.data.phone_number ?? "N/A",
                };
                setPatients((prev) => [...prev, newPatient]);
                setSuccessMessage("Patient created successfully.");
            }
            resetForm();
        } catch (err) {
            console.error("Save failed:", err);
            setErrorMessage("Failed to save patient.");
        }
    };

    const handleEdit = (patient) => {
        setEditingPatient(patient);
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this patient?")) return;
        try {
            await deletePatient(id);
            setPatients((prev) => prev.filter((p) => p.id !== id));
            setSuccessMessage("Patient deleted successfully.");
        } catch (err) {
            console.error("Delete failed:", err);
            setErrorMessage("Failed to delete patient.");
        }
    };

    const resetForm = () => setEditingPatient(null);
    const toggleList = () => setIsPatientsVisible(!isPatientsVisible);

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Patients</h1>

            {successMessage && <p className="text-green-500 mb-4">{successMessage}</p>}
            {errorMessage && <p className="text-red-500 mb-4">{errorMessage}</p>}

            <PatientForm
                onSubmit={handleFormSubmit}
                editingPatient={editingPatient}
                resetForm={resetForm}
            />

            <div className="mb-4">
                <button
                    onClick={() => navigate("/dashboard")}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded mr-4"
                >
                    Go to Dashboard
                </button>
                <button
                    onClick={toggleList}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                >
                    {isPatientsVisible ? "Hide" : "Show"} Patients List
                </button>
            </div>

            {loading && <p>Loading patients...</p>}
            {!loading && isPatientsVisible && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {patients.map((p) => (
                        <div key={p.id} className="border border-gray-300 rounded p-4 shadow-md">
                            <h2 className="text-lg font-semibold mb-2">{p.name}</h2>
                            <p>Email: {p.email}</p>
                            <p>Age: {p.age}</p>
                            <p>Phone: {p.phone_number}</p>
                            <div className="mt-4 space-x-2">
                                <button
                                    onClick={() => handleEdit(p)}
                                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => handleDelete(p.id)}
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
