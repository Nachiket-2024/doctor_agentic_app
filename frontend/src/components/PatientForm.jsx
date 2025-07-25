// Importing necessary React hooks
import { useState, useEffect } from "react";

// PatientForm component receives three props: onSubmit (form handler), editingPatient (data to edit), resetForm (to clear editing state)
export default function PatientForm({
    onSubmit,
    editingPatient,
    resetForm,
}) {
    // Local state to manage each form field
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [age, setAge] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");

    // useEffect hook runs when editingPatient changes
    useEffect(() => {
        // If editingPatient is passed in (edit mode), populate the form fields with their data
        if (editingPatient) {
            setName(editingPatient.name || "");
            setEmail(editingPatient.email || "");
            setAge(editingPatient.age !== "N/A" ? editingPatient.age.toString() : "");
            setPhoneNumber(
                editingPatient.phone_number !== "N/A" ? editingPatient.phone_number : ""
            );
        }
    }, [editingPatient]); // Dependency array ensures this runs when editingPatient updates

    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault(); // Prevent default form submit behavior (page reload)

        // Construct patient object and invoke onSubmit passed from parent
        onSubmit({
            name,
            email,
            age: age.trim() === "" ? null : parseInt(age), // Convert age to number if provided
            phone_number: phoneNumber.trim() === "" ? null : phoneNumber,
            role: "patient", // Add patient role explicitly
        });
    };

    return (
        // Main form container
        <form onSubmit={handleSubmit} className="mb-6 space-y-4 max-w-md">
            {/* Form title */}
            <h2 className="text-lg font-semibold">
                {editingPatient ? "Edit Patient" : "Create New Patient"}
            </h2>

            {/* Name input field */}
            <input
                type="text"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full border border-gray-300 px-3 py-2 rounded"
            />

            {/* Email input field */}
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full border border-gray-300 px-3 py-2 rounded"
            />

            {/* Age input field */}
            <input
                type="number"
                placeholder="Age"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                className="w-full border border-gray-300 px-3 py-2 rounded"
            />

            {/* Phone number input field */}
            <input
                type="text"
                placeholder="Phone Number"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="w-full border border-gray-300 px-3 py-2 rounded"
            />

            {/* Form buttons */}
            <div className="space-x-2">
                {/* Submit button */}
                <button
                    type="submit"
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                >
                    {editingPatient ? "Update" : "Create"}
                </button>

                {/* Cancel button (only shown in edit mode) */}
                {editingPatient && (
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
    );
}
