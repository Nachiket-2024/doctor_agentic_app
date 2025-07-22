// --- Import React core ---
import React from "react";
import ReactDOM from "react-dom/client";

// --- Import React Router for client-side routing ---
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

// --- Import your custom page and component files ---
import ProtectedRoute from "./components/ProtectedRoute";     // Component to guard protected routes
import Layout from "./components/Layout";                     // Layout wrapper for protected pages
import LoginPage from "./pages/LoginPage";                    // Public login screen
import Dashboard from "./pages/DashboardPage";                // Dashboard page shown after login
import PatientsPage from "./pages/PatientsPage";              // Patient management page
import DoctorsPage from "./pages/DoctorsPage";                // Doctor management page
import AppointmentsPage from "./pages/AppointmentsPage";      // Appointment management page

// --- Mount the root React app into the DOM ---
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode> {/* Enable additional checks and warnings in development */}
    <Router> {/* Set up routing with React Router */}
      <Routes>
        {/* Public login route (does not require authentication) */}
        <Route path="/login" element={<LoginPage />} />

        {/* Layout component wraps protected routes; only accessible when logged in */}
        <Route
          path="/"
          element={
            <ProtectedRoute> {/* This checks if user is authenticated */}
              <Layout />      {/* Layout provides navigation/header/sidebar */}
            </ProtectedRoute>
          }
        >
          {/* Redirect from "/" to dashboard by default */}
          <Route index element={<Navigate to="/dashboard" replace />} />

          {/* Dashboard route (inside protected layout) */}
          <Route path="dashboard" element={<Dashboard />} />

          {/* Patient management route (inside protected layout) */}
          <Route path="patients" element={<PatientsPage />} />

          {/* Doctor management route (inside protected layout) */}
          <Route path="doctors" element={<DoctorsPage />} />

          {/* Appointment management route (inside protected layout) */}
          <Route path="appointments" element={<AppointmentsPage />} />

        </Route>
      </Routes>
    </Router>
  </React.StrictMode>
);
