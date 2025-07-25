// --- React hooks ---
import { useEffect, useState, useRef } from "react"; // useRef added to guard API call
import { useNavigate } from "react-router-dom";

// --- Import API service functions for patients ---
import {
    getAllPatients,
    createPatient,
    updatePatient,
    deletePatient,
} from "../services/patientService";

// --- Import reusable PatientForm component ---
import PatientForm from "../components/PatientForm";

// --- Toast notification system ---
import { toast, ToastContainer } from "react-toastify"; // Toast API
import "react-toastify/dist/ReactToastify.css"; // Toast styles

// --- PatientsPage Component ---
export default function PatientsPage() {
    // --- State: holds all patients fetched from backend ---
    const [patients, setPatients] = useState([]);

    // --- State: indicates if patients are being loaded ---
    const [loading, setLoading] = useState(true);

    // --- State: stores patient being edited (null if none) ---
    const [editingPatient, setEditingPatient] = useState(null);

    // --- State: toggle for displaying the patients list ---
    const [isPatientsVisible, setIsPatientsVisible] = useState(false);

    // --- React Router hook for navigation ---
    const navigate = useNavigate();

    // --- Ref: ensures fetchPatients runs only once in dev mode ---
    const hasFetchedRef = useRef(false);

    // --- useEffect to run once on mount to fetch patients ---
    useEffect(() => {
        if (!hasFetchedRef.current) {
            fetchPatients(); // Call fetch logic once
            hasFetchedRef.current = true; // Set ref so it doesn't repeat
        }
    }, []); // empty dependency array ensures it only runs on mount

    // --- Fetch patient list from backend ---
    const fetchPatients = async () => {
        try {
            const res = await getAllPatients(); // API call to fetch patients

            // Normalize null/undefined values to show cleanly in UI
            const cleaned = res.data.map((p) => ({
                ...p,
                age: p.age ?? "N/A",
                phone_number: p.phone_number ?? "N/A",
                google_id: p.google_id ?? "N/A",
            }));

            setPatients(cleaned); // Save to state
            toast.success("Patients loaded successfully."); // Notify user
        } catch (err) {
            console.error("Failed to fetch patients:", err); // Log error
            toast.error("Could not load patients."); // Show error toast
        } finally {
            setLoading(false); // Hide loader regardless of result
        }
    };

    // --- Handle create or update form submission ---
    const handleFormSubmit = async (payload) => {
        try {
            if (editingPatient) {
                // If editing, update the patient record
                await updatePatient(editingPatient.id, payload);

                // Update the local state to reflect changes
                setPatients((prev) =>
                    prev.map((p) =>
                        p.id === editingPatient.id ? { ...p, ...payload } : p
                    )
                );

                toast.success("Patient updated successfully.");
            } else {
                // If not editing, create a new patient
                const res = await createPatient(payload);

                const newPatient = {
                    ...res.data,
                    age: res.data.age ?? "N/A",
                    phone_number: res.data.phone_number ?? "N/A",
                };

                setPatients((prev) => [...prev, newPatient]); // Append new patient
                toast.success("Patient created successfully.");
            }

            resetForm(); // Clear the form after submission
        } catch (err) {
            console.error("Save failed:", err); // Log error
            toast.error("Failed to save patient."); // Show error toast
        }
    };

    // --- Populate the form with existing patient details ---
    const handleEdit = (patient) => {
        setEditingPatient(patient); // Load patient data into form
    };

    // --- Delete a patient by ID ---
    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this patient?")) return;

        try {
            await deletePatient(id); // Call delete API
            setPatients((prev) => prev.filter((p) => p.id !== id)); // Remove from UI
            toast.success("Patient deleted successfully.");
        } catch (err) {
            console.error("Delete failed:", err);
            toast.error("Failed to delete patient.");
        }
    };

    // --- Reset form to initial state ---
    const resetForm = () => setEditingPatient(null);

    // --- Toggle patient list visibility ---
    const toggleList = () => setIsPatientsVisible((prev) => !prev);

    // --- Render component UI ---
    return (
        <div className="p-6">
            {/* Toast container to display notifications */}
            <ToastContainer position="top-right" autoClose={3000} />

            {/* Page title */}
            <h1 className="text-2xl font-bold mb-4">Patients</h1>

            {/* Reusable form component */}
            <PatientForm
                onSubmit={handleFormSubmit}
                editingPatient={editingPatient}
                resetForm={resetForm}
            />

            {/* Action buttons */}
            <div className="mb-4">
                {/* Navigate to Dashboard */}
                <button
                    onClick={() => navigate("/dashboard")}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded mr-4"
                >
                    Go to Dashboard
                </button>

                {/* Toggle Patient List */}
                <button
                    onClick={toggleList}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                >
                    {isPatientsVisible ? "Hide" : "Show"} Patients List
                </button>
            </div>

            {/* Conditional loading or display of patients list */}
            {loading && <p>Loading patients...</p>}

            {!loading && isPatientsVisible && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {patients.map((p) => (
                        <div
                            key={p.id}
                            className="border border-gray-300 rounded p-4 shadow-md"
                        >
                            {/* Patient details */}
                            <h2 className="text-lg font-semibold mb-2">{p.name}</h2>
                            <p>Email: {p.email}</p>
                            <p>Age: {p.age}</p>
                            <p>Phone: {p.phone_number}</p>

                            {/* Edit/Delete buttons */}
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
