// --- Import necessary React hooks and services ---
import React, { useState, useEffect } from "react";
import { createDoctor, updateDoctor } from "../services/doctorService";

const DoctorForm = ({ onSuccess, existingDoctor, clearEdit }) => {
    // --- Initial form state ---
    const [form, setForm] = useState({
        name: "",
        email: "",
        specialization: "",
        available_days: { mon: "", tue: "", wed: "", thu: "", fri: "", sat: "", sun: "" },
        slot_duration: 15,
    });

    // --- On edit, set form data ---
    useEffect(() => {
        if (existingDoctor) setForm(existingDoctor);
    }, [existingDoctor]);

    // --- Handle form submission (create or update) ---
    const handleSubmit = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem("access_token");  // Get the token from localStorage

        if (!token) {
            alert("Unauthorized, please login again.");
            return;
        }

        try {
            if (existingDoctor) {
                await updateDoctor(existingDoctor.id, form);  // Update doctor
                clearEdit();
            } else {
                await createDoctor(form);  // Create doctor
            }

            onSuccess();  // Callback to refresh parent component data
            resetForm();  // Reset form after submission
        } catch (err) {
            console.error("Error submitting form", err);
            alert("An error occurred while submitting the form");
        }
    };

    // --- Reset form state ---
    const resetForm = () => {
        setForm({
            name: "",
            email: "",
            specialization: "",
            available_days: { mon: "", tue: "", wed: "", thu: "", fri: "", sat: "", sun: "" },
            slot_duration: 15,
        });
    };

    return (
        <form onSubmit={handleSubmit} className="mb-4 p-4 border rounded-md shadow-md">
            {/* Input fields */}
            <input
                type="text"
                placeholder="Name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                className="p-2 mb-2 w-full"
            />
            <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                className="p-2 mb-2 w-full"
            />
            <input
                type="text"
                placeholder="Specialization"
                value={form.specialization}
                onChange={(e) => setForm({ ...form, specialization: e.target.value })}
                className="p-2 mb-2 w-full"
            />

            {/* Dynamic available_days input (for each day) */}
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
                                    available_days: { ...form.available_days, [day]: e.target.value },
                                })
                            }
                            className="p-2 mb-2"
                        />
                    </div>
                ))}
            </div>

            {/* Slot duration */}
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
