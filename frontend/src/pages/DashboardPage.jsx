// --- React core and routing utilities ---
import { useEffect, useState, useRef } from "react"; // useRef added
import { useNavigate, useLocation } from "react-router-dom";

// --- Centralized Axios instance ---
import API from "../utils/axiosInstance";

// --- Dashboard Component ---
export default function Dashboard() {
  const navigate = useNavigate();                  // For redirecting the user
  const location = useLocation();                  // For accessing query params

  const [user, setUser] = useState(null);          // Stores user info
  const [loading, setLoading] = useState(true);    // Tracks whether data is loading

  const hasFetchedRef = useRef(false);             // Prevents double API calls in dev

  // --- Effect to fetch user info when component mounts ---
  useEffect(() => {
    if (hasFetchedRef.current) return;             // Guard against duplicate runs
    hasFetchedRef.current = true;                  // Set guard

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
        const response = await API.get("/auth/me");

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
  }, [navigate, location]); // Depend on navigation and location

  // --- Logout function: clears localStorage and calls backend logout ---
  const handleLogout = async () => {
    try {
      await API.post("/auth/logout");
    } catch (err) {
      // --- Silently fail on error ---
    } finally {
      // --- Clear session and navigate to login ---
      localStorage.removeItem("access_token");
      localStorage.removeItem("role");
      setUser(null);
      navigate("/login?logged_out=true", { replace: true });
    }
  };

  // --- Show loading indicator while fetching user info ---
  if (loading) return <p>Loading user info...</p>;

  // --- Main Dashboard UI once authenticated ---
  return (
    <div className="p-6 min-h-screen bg-gray-100">
      {/* --- Header --- */}
      <h1 className="text-2xl font-bold mb-2">Welcome to the Doctor Agentic App!</h1>
      <p>You are successfully logged in for Doctor Agentic App.</p>

      {/* --- User Info --- */}
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

      {/* --- Navigation Buttons --- */}
      <div className="mt-10 space-y-4">
        <h2 className="text-xl font-semibold">Go to Management Pages</h2>

        {/* --- Patient Page --- */}
        <button
          onClick={() => navigate("/patients")}
          className="w-full md:w-64 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Patient Page
        </button>

        {/* --- Doctor Page --- */}
        <button
          onClick={() => navigate("/doctors")}
          className="w-full md:w-64 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Doctor Page
        </button>

        {/* --- Appointment Page --- */}
        <button
          onClick={() => navigate("/appointments")}
          className="w-full md:w-64 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          Appointment Page
        </button>
      </div>
    </div>
  );
}
