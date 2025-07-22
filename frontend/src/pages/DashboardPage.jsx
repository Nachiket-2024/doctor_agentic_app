// --- React core and routing utilities ---
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

// --- Axios for making API requests ---
import axios from "axios";

export default function Dashboard() {
  const navigate = useNavigate();              // For redirecting the user
  const location = useLocation();              // For accessing query params
  const [user, setUser] = useState(null);      // Stores user info
  const [loading, setLoading] = useState(true); // Tracks whether data is loading

  useEffect(() => {
    const fetchUserInfo = async () => {
      // --- Read access_token and role from URL if present ---
      const urlParams = new URLSearchParams(location.search);
      const tokenFromUrl = urlParams.get("access_token");
      const roleFromUrl = urlParams.get("role");

      // --- If token is in the URL, store it in localStorage ---
      if (tokenFromUrl) {
        localStorage.setItem("access_token", tokenFromUrl);
        if (roleFromUrl) {
          localStorage.setItem("role", roleFromUrl);
        }

        // --- Clean up URL to remove access_token & role ---
        window.history.replaceState({}, "", location.pathname);
      }

      // --- Get token from localStorage after URL cleanup ---
      const storedToken = localStorage.getItem("access_token");

      // --- If no token found, redirect to login page ---
      if (!storedToken) {
        navigate("/login");
        return;
      }

      try {
        // --- Call /auth/me to verify token and fetch user info ---
        const response = await axios.get("http://localhost:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${storedToken}`,
          },
        });

        // --- Save user info in state ---
        setUser(response.data);
      } catch (err) {
        // --- Token invalid or expired: clear storage and redirect ---
        localStorage.removeItem("access_token");
        localStorage.removeItem("role");
        navigate("/login");
      } finally {
        // --- Hide loading UI whether success or fail ---
        setLoading(false);
      }
    };

    // --- Trigger the fetch logic on mount ---
    fetchUserInfo();
  }, [navigate, location]);

  // --- Logout function: clears localStorage and calls backend logout ---
  const handleLogout = async () => {
    const token = localStorage.getItem("access_token");

    if (token) {
      try {
        await axios.post(
          "http://localhost:8000/auth/logout",
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
      } catch (err) {
      } finally {
        // --- Clear session and navigate to login ---
        localStorage.removeItem("access_token");
        localStorage.removeItem("role");
        setUser(null);
        navigate("/login?logged_out=true", { replace: true });
      }
    }
  };

  // --- Show loading indicator while fetching user info ---
  if (loading) return <p>Loading user info...</p>;

  // --- Main Dashboard UI once authenticated ---
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-2">Welcome to the Doctor Agentic App!</h1>
      <p>You are successfully logged in for Doctor Agentic App.</p>

      <div className="mt-4 space-y-1">
        <p>👤 <strong>{user.name}</strong></p>
        <p>📧 {user.email}</p>
        <p>🛡️ <strong>Role:</strong> {user.role}</p>
      </div>

      {/* --- Logout Button --- */}
      <button
        onClick={handleLogout}
        className="mt-6 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Logout
      </button>
    </div>
  );
}
