// --- External imports ---
// React core imports
import React from "react";
import ReactDOM from "react-dom/client";
// React Router imports for routing
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
// Redux imports for providing store
import { Provider } from "react-redux";

// --- Internal imports ---
// Redux store
import store from "./app/store";
// Auth action to check token at startup
import { checkAuthState } from "./features/authSlice";
// App components and pages
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/DashboardPage";
import PatientPage from "./pages/PatientPage";
import DoctorPage from "./pages/DoctorPage";
import AppointmentPage from "./pages/AppointmentPage";

// --- Run initial auth check before rendering the app ---
store.dispatch(checkAuthState());

// --- Mount root React app with Redux Provider and routing ---
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {/* Provide Redux store to React app */}
    <Provider store={store}>
      <Router>
        <Routes>
          {/* Public login route */}
          <Route path="/login" element={<Layout><LoginPage /></Layout>} />

          {/* Protected routes wrapped by Layout */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            {/* Redirect root to dashboard */}
            <Route index element={<Navigate to="/dashboard" replace />} />

            {/* Protected routes */}
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="patient" element={<PatientPage />} />
            <Route path="doctor" element={<DoctorPage />} />
            <Route path="appointment" element={<AppointmentPage />} />
          </Route>
        </Routes>
      </Router>
    </Provider>
  </React.StrictMode>
);
