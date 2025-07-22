import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Cookies from "js-cookie"; // Import the js-cookie library

export default function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Runs once when component mounts
  useEffect(() => {
    const fetchUserInfo = async () => {
      // Get the token and role from the URL (from the redirect after login)
      const urlParams = new URLSearchParams(window.location.search);
      const tokenFromUrl = urlParams.get("access_token");
      const roleFromUrl = urlParams.get("role");

      // Store the token and role in cookies
      if (tokenFromUrl) {
        Cookies.set("access_token", tokenFromUrl, { expires: 7, path: "" }); // Store token in cookies for 7 days
        if (roleFromUrl) Cookies.set("role", roleFromUrl, { expires: 7, path: "" });
        window.history.replaceState({}, "", "/dashboard");
      }

      const storedToken = Cookies.get("access_token");
      if (!storedToken) {
        navigate("/login");
        return;
      }

      try {
        const response = await axios.get("http://localhost:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${storedToken}`,
          },
        });

        setUser(response.data);
      } catch (err) {
        Cookies.remove("access_token");
        Cookies.remove("role");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [navigate]);

  // --- Logout handler ---
  const handleLogout = async () => {
    const token = Cookies.get("access_token");

    if (token) {
      try {
        await axios.post("http://localhost:8000/auth/logout", {}, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        Cookies.remove("access_token");
        Cookies.remove("role");
        setUser(null);
        navigate("/login?logged_out=true", { replace: true });
      } catch (err) {
        console.error("Logout failed:", err);
      }
    }
  };

  // --- Show loading spinner while fetching user info ---
  if (loading) return <p>Loading user info...</p>;

  // --- Dashboard UI ---
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-2">Welcome to the Doctor Agentic App!</h1>
      <p>You are successfully logged in for Doctor Agentic App.</p>

      <div className="mt-4 space-y-1">
        <p>👤 <strong>{user.name}</strong></p>
        <p>📧 {user.email}</p>
        <p>🛡️ <strong>Role:</strong> {user.role}</p>
      </div>

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
