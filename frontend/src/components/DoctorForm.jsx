// ---------------------------- Imports ----------------------------
import { useState, useEffect } from "react"; // React hooks for state and lifecycle
import {
    createDoctor,
    updateDoctor,
} from "../services/doctorService"; // Service functions for API interaction

// ---------------------------- Component ----------------------------
const DoctorForm = ({ onSuccess, existingDoctor, clearEdit }) => {
    // ---------------------------- State: Form values ----------------------------
    const [form, setForm] = useState({
        name: "", // Doctor's name
        email: "", // Doctor's email
        specialization: "", // Doctor's field
        available_days: {
            mon: "", tue: "", wed: "", thu: "", fri: "", sat: "", sun: "", // Available times per day
        },
        slot_duration: 15, // Time slot duration in minutes
    });

    // ---------------------------- Prefill form on edit ----------------------------
    useEffect(() => {
        if (existingDoctor) setForm(existingDoctor); // If editing, pre-fill form
    }, [existingDoctor]);

    // ---------------------------- Handle form submission ----------------------------
    const handleSubmit = async (e) => {
        e.preventDefault(); // Prevent page reload on form submission

        try {
            if (existingDoctor) {
                // If editing an existing doctor
                await updateDoctor(existingDoctor.id, form);
                clearEdit(); // Clear edit state after update
            } else {
                // If creating a new doctor
                await createDoctor(form);
            }

            onSuccess(); // Notify parent to refresh data
            resetForm(); // Clear the form fields
        } catch (err) {
            console.error("Error submitting form", err); // Log any error
            alert("An error occurred while submitting the form"); // Show error to user
        }
    };

    // ---------------------------- Reset form values ----------------------------
    const resetForm = () => {
        setForm({
            name: "",
            email: "",
            specialization: "",
            available_days: {
                mon: "", tue: "", wed: "", thu: "", fri: "", sat: "", sun: "",
            },
            slot_duration: 15,
        });
    };

    // ---------------------------- UI: Render form ----------------------------
    return (
        <form onSubmit={handleSubmit} className="mb-4 p-4 border rounded-md shadow-md">
            {/* Name input */}
            <input
                type="text"
                placeholder="Name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                className="p-2 mb-2 w-full"
            />

            {/* Email input */}
            <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                className="p-2 mb-2 w-full"
            />

            {/* Specialization input */}
            <input
                type="text"
                placeholder="Specialization"
                value={form.specialization}
                onChange={(e) => setForm({ ...form, specialization: e.target.value })}
                className="p-2 mb-2 w-full"
            />

            {/* Weekly availability input fields */}
            <div className="grid grid-cols-2 gap-4">
                {Object.keys(form.available_days).map((day) => (
                    <div key={day} className="flex flex-col">
                        <label>{day.charAt(0).toUpperCase() + day.slice(1)}</label>
                        <input
                            type="text"
                            placeholder="Time slot"
                            value={form.available_days[day]}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    available_days: {
                                        ...form.available_days,
                                        [day]: e.target.value,
                                    },
                                })
                            }
                            className="p-2 mb-2"
                        />
                    </div>
                ))}
            </div>

            {/* Slot duration input */}
            <input
                type="number"
                placeholder="Slot Duration (in minutes)"
                value={form.slot_duration}
                onChange={(e) => setForm({ ...form, slot_duration: e.target.value })}
                className="p-2 mb-2 w-full"
            />

            {/* Submit button */}
            <button
                type="submit"
                className="bg-blue-500 text-white px-4 py-2 rounded-md"
            >
                {existingDoctor ? "Update" : "Create"} Doctor
            </button>
        </form>
    );
};

export default DoctorForm;
