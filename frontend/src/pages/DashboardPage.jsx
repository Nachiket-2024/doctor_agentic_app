// --- React core and routing utilities ---
import { useEffect, useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";

// --- Centralized Axios instance ---
import API from "../utils/axiosInstance";

export default function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const hasFetchedRef = useRef(false);

  // --- Fetch user info on mount ---
  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;

    const fetchUserInfo = async () => {
      const urlParams = new URLSearchParams(location.search);
      const tokenFromUrl = urlParams.get("access_token");
      const roleFromUrl = urlParams.get("role");

      if (tokenFromUrl) {
        localStorage.setItem("access_token", tokenFromUrl);
        if (roleFromUrl) {
          localStorage.setItem("role", roleFromUrl);
        }
        window.history.replaceState({}, "", location.pathname);
      }

      const storedToken = localStorage.getItem("access_token");

      if (!storedToken) {
        navigate("/login");
        return;
      }

      try {
        const response = await API.get("/auth/me");
        setUser(response.data);
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("role");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [navigate, location]);

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

  if (loading) return <p>Loading user info...</p>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-2">
        Welcome to the Doctor Agentic App!
      </h2>
      <p className="mb-4">You are successfully logged in.</p>

      <div className="bg-white shadow rounded p-4 space-y-1">
        <p>👤 <strong>{user.name}</strong></p>
        <p>📧 {user.email}</p>
        <p>🛡️ <strong>Role:</strong> {user.role}</p>
      </div>

      <button
        onClick={handleTestMCP}
        className="mt-4 px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
      >
        Test MCP Tools Endpoint
      </button>
    </div>
  );
}
