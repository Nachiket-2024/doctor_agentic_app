import { useEffect, useState } from "react";            // React hooks for lifecycle and state
import { useNavigate } from "react-router-dom";         // React Router hook to programmatically navigate
import axios from "axios";                              // For making HTTP requests

// Main Dashboard screen (protected, shown after login)
export default function Dashboard() {
  const navigate = useNavigate();                       // For redirecting the user (e.g., after logout)
  const [user, setUser] = useState(null);               // Holds current user info
  const [loading, setLoading] = useState(true);         // Tracks loading state for user info

  // Fix for browser back/forward caching (prevents showing stale UI)
  useEffect(() => {
    const onPageShow = (event) => {
      if (event.persisted) {
        window.location.reload();                       // Reload if navigating from bfcache
      }
    };
    window.addEventListener("pageshow", onPageShow);
    return () => window.removeEventListener("pageshow", onPageShow);
  }, []);

  // Fetch user info on component mount
  useEffect(() => {
    axios.get("http://localhost:8000/auth/me", { withCredentials: true })
      .then((res) => {
        console.log("User info:", res.data);
        setUser(res.data);                              // Store user info in state
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching user info:", err);
        setUser(null);                                  // If unauthorized or error → nullify user
        setLoading(false);
      });
  }, []);

  // Logout flow: clear cookie on server, redirect to login
  const handleLogout = () => {
    axios.post("http://localhost:8000/auth/logout", {}, { withCredentials: true })
      .then(() => {
        setUser(null);                                  // Clear local user state
        navigate("/login?logged_out=true", { replace: true });  // Redirect to login page
      })
      .catch((err) => {
        console.error("Logout failed:", err);
      });
  };

  // Show loading message while fetching user info
  if (loading) return <p>Loading user info...</p>;

  // Render dashboard after successful login
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-2">Welcome to your Dashboard!</h1>
      <p>You are successfully logged in via Google OAuth.</p>

      {/* 👤 User details */}
      <p className="mt-4">👤 <strong>{user.name}</strong></p>
      <p>{user.email}</p>

      {/* Logout button */}
      <button
        onClick={handleLogout}
        className="mt-6 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Logout
      </button>
    </div>
  );
}
