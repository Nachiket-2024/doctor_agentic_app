// ---------------------------- Imports ----------------------------
import { useEffect, useState } from "react"; // React and hooks
import {
    createAppointment,
    updateAppointment,
    getAvailableSlots,
    getAllPatients,
} from "../services/appointmentService"; // Appointment-related API calls
import { getAllDoctors } from "../services/doctorService"; // Doctor API calls

// ---------------------------- Component ----------------------------
const AppointmentForm = ({ selectedAppointment, onSuccess }) => {
    // State for form data
    const [formData, setFormData] = useState({
        doctor_id: "",
        patient_id: "",
        date: "",
        start_time: "",
        reason: "",
    });

    // Dropdown options
    const [doctors, setDoctors] = useState([]);
    const [patients, setPatients] = useState([]);
    const [availableSlots, setAvailableSlots] = useState([]);

    // ---------------------------- Pre-fill form if editing ----------------------------
    useEffect(() => {
        if (selectedAppointment) {
            setFormData({
                doctor_id: selectedAppointment.doctor_id,
                patient_id: selectedAppointment.patient_id,
                date: selectedAppointment.date,
                start_time: selectedAppointment.start_time,
                reason: selectedAppointment.reason || "",
            });
        }
    }, [selectedAppointment]);

    // ---------------------------- Fetch doctors and patients on mount ----------------------------
    useEffect(() => {
        const fetchData = async () => {
            try {
                const doctorRes = await getAllDoctors();
                const patientRes = await getAllPatients();
                setDoctors(doctorRes.data);
                setPatients(patientRes.data);
            } catch (err) {
                console.error("Error fetching doctors or patients:", err);
            }
        };
        fetchData();
    }, []);

    // ---------------------------- Fetch available slots whenever doctor/date changes ----------------------------
    useEffect(() => {
        const fetchSlots = async () => {
            if (formData.doctor_id && formData.date) {
                try {
                    const res = await getAvailableSlots(formData.doctor_id, formData.date);
                    const now = new Date();
                    const today = new Date().toISOString().slice(0, 10);
                    const slots = res.data;

                    // Filter past slots if date is today
                    const filtered = slots.filter((slot) => {
                        if (formData.date > today) return true;
                        const [h, m] = slot.split(":");
                        const slotTime = new Date();
                        slotTime.setHours(h, m, 0, 0);
                        return slotTime > now;
                    });

                    setAvailableSlots(filtered);
                } catch (err) {
                    console.error("Error fetching slots:", err);
                }
            }
        };
        fetchSlots();
    }, [formData.doctor_id, formData.date]);

    // ---------------------------- Handle form field changes ----------------------------
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    // ---------------------------- Handle form submit ----------------------------
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (selectedAppointment) {
                await updateAppointment(selectedAppointment.id, formData);
            } else {
                await createAppointment(formData);
            }
            onSuccess(); // Refresh parent list or close modal
        } catch (err) {
            console.error("Error submitting appointment:", err);
        }
    };

    // ---------------------------- Render UI ----------------------------
    return (
        <form onSubmit={handleSubmit} className="p-4 bg-white rounded-xl shadow space-y-4">
            {/* Doctor selection */}
            <div>
                <label className="block font-semibold">Doctor</label>
                <select
                    name="doctor_id"
                    value={formData.doctor_id}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border rounded"
                >
                    <option value="">Select a doctor</option>
                    {doctors.map((doc) => (
                        <option key={doc.id} value={doc.id}>
                            {doc.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Patient selection */}
            <div>
                <label className="block font-semibold">Patient</label>
                <select
                    name="patient_id"
                    value={formData.patient_id}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border rounded"
                >
                    <option value="">Select a patient</option>
                    {patients.map((pat) => (
                        <option key={pat.id} value={pat.id}>
                            {pat.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Date input */}
            <div>
                <label className="block font-semibold">Date</label>
                <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border rounded"
                />
            </div>

            {/* Time slot dropdown */}
            <div>
                <label className="block font-semibold">Time Slot</label>
                <select
                    name="start_time"
                    value={formData.start_time}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border rounded"
                >
                    <option value="">Select a time</option>
                    {availableSlots.map((slot, idx) => (
                        <option key={idx} value={slot}>
                            {slot}
                        </option>
                    ))}
                </select>
            </div>

            {/* Reason field */}
            <div>
                <label className="block font-semibold">Reason (optional)</label>
                <input
                    type="text"
                    name="reason"
                    value={formData.reason}
                    onChange={handleChange}
                    className="w-full p-2 border rounded"
                />
            </div>

            {/* Submit button */}
            <button
                type="submit"
                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
            >
                {selectedAppointment ? "Update Appointment" : "Book Appointment"}
            </button>
        </form>
    );
};

export default AppointmentForm;
