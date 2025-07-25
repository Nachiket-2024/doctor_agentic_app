// --- React hooks for side effects and navigation ---
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

// --- Login Page Component ---
function LoginPage() {
  const navigate = useNavigate(); // Used to programmatically navigate routes

  // --- Redirect to dashboard if already logged in (token exists) ---
  useEffect(() => {
    const token = localStorage.getItem("access_token"); // Get token from local storage
    if (token) {
      navigate("/dashboard"); // Redirect if token exists
    }
  }, [navigate]);

  // --- Handle login button click ---
  const handleLogin = () => {
    // Redirect user to backend Google OAuth login endpoint
    window.location.href = "http://localhost:8000/auth/login";
  };

  // --- Render login UI ---
  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Login to Doctor Agentic App</h1>
      <button
        onClick={handleLogin}
        style={{
          padding: "10px 20px",
          backgroundColor: "blue",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        Login with Google
      </button>
    </div>
  );
}

export default LoginPage;
