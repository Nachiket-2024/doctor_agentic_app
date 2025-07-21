import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true); // Add loading state

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/dashboard"); // Redirect to dashboard if already logged in
    } else {
      setLoading(false); // Set loading to false once check is complete
    }
  }, [navigate]);

  const handleLogin = () => {
    window.location.href = "http://localhost:8000/auth/login"; // Redirect to backend login page (Google OAuth)
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", marginTop: "50px" }}>
        <h2>Checking authentication...</h2>
      </div>
    ); // Show loading state while checking authentication
  }

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
