import { useState, useEffect } from "react";

export default function PatientForm({
    onSubmit,
    editingPatient,
    resetForm,
}) {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [age, setAge] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");

    // Populate form when editing
    useEffect(() => {
        if (editingPatient) {
            setName(editingPatient.name || "");
            setEmail(editingPatient.email || "");
            setAge(editingPatient.age !== "N/A" ? editingPatient.age.toString() : "");
            setPhoneNumber(editingPatient.phone_number !== "N/A" ? editingPatient.phone_number : "");
        }
    }, [editingPatient]);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            name,
            email,
            age: age.trim() === "" ? null : parseInt(age),
            phone_number: phoneNumber.trim() === "" ? null : phoneNumber,
            role: "patient",
        });
    };

    return (
        <form onSubmit={handleSubmit} className="mb-6 space-y-4 max-w-md">
            <h2 className="text-lg font-semibold">
                {editingPatient ? "Edit Patient" : "Create New Patient"}
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
                    {editingPatient ? "Update" : "Create"}
                </button>
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
