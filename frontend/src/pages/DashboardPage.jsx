// ---------------------------- External Imports ----------------------------

// React hooks for lifecycle, state, and refs
import { useEffect, useState, useRef } from "react";

// React Router hooks for navigation and location
import { useNavigate, useLocation } from "react-router-dom";

// ---------------------------- Internal Imports ----------------------------

// Centralized Axios instance for API calls
import API from "../utils/axiosInstance";


// ---------------------------- Dashboard Component ----------------------------

// Main dashboard page showing user info and MCP test
export default function Dashboard() {
  // React Router navigation hook
  const navigate = useNavigate();

  // React Router location hook
  const location = useLocation();

  // Local state to store user info
  const [user, setUser] = useState(null);

  // Loading state while fetching user info
  const [loading, setLoading] = useState(true);

  // Ref to prevent multiple fetches in StrictMode
  const hasFetchedRef = useRef(false);

  // ---------------------------- Fetch User Info ----------------------------
  // Runs on initial mount to fetch authenticated user's info
  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;

    const fetchUserInfo = async () => {
      // Parse query parameters from URL
      const urlParams = new URLSearchParams(location.search);
      const tokenFromUrl = urlParams.get("access_token");
      const roleFromUrl = urlParams.get("role");

      // Save token and role from URL to localStorage if present
      if (tokenFromUrl) {
        localStorage.setItem("access_token", tokenFromUrl);
        if (roleFromUrl) {
          localStorage.setItem("role", roleFromUrl);
        }
        // Remove query params from URL
        window.history.replaceState({}, "", location.pathname);
      }

      // Retrieve token from localStorage
      const storedToken = localStorage.getItem("access_token");

      // Redirect to login if no token
      if (!storedToken) {
        navigate("/login");
        return;
      }

      try {
        // Fetch current user info from API
        const response = await API.get("/auth/me");
        setUser(response.data);
      } catch {
        // Clear invalid token/role and redirect
        localStorage.removeItem("access_token");
        localStorage.removeItem("role");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [navigate, location]);

  // ---------------------------- MCP Test Handler ----------------------------
  // Calls the MCP endpoint to list tools
  const handleTestMCP = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      alert("No access token found. Please login first.");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/mcp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json, text/event-stream",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: "1",
          method: "list_tools",
          params: { session_id: "frontend-test-session" },
        }),
      });

      const data = await response.json();
      alert(`MCP tools fetched:\n${JSON.stringify(data, null, 2)}`);
    } catch {
      alert("Failed to contact MCP endpoint.");
    }
  };

  // ---------------------------- Render ----------------------------
  // Show loading text while fetching user info
  if (loading) return <p>Loading user info...</p>;

  return (
    <div className="p-6">
      {/* Page header */}
      <h2 className="text-2xl font-bold mb-2">
        Welcome to the Doctor Agentic App!
      </h2>
      <p className="mb-4">You are successfully logged in.</p>

      {/* User info card */}
      <div className="bg-white shadow rounded p-4 space-y-1">
        <p>👤 <strong>{user.name}</strong></p>
        <p>📧 {user.email}</p>
        <p>🛡️ <strong>Role:</strong> {user.role}</p>
      </div>

      {/* MCP test button */}
      <button
        onClick={handleTestMCP}
        className="mt-4 px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
      >
        Test MCP Tools Endpoint
      </button>
    </div>
  );
}
