// ---------------------------- React hooks and routing helpers ----------------------------
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

// ---------------------------- Centralized Axios Instance ----------------------------
import API from "../utils/axiosInstance";

export default function ProtectedRoute({ children }) {
  const navigate = useNavigate();             // For programmatic redirects
  const location = useLocation();             // To access URL query parameters
  const [checkingAuth, setCheckingAuth] = useState(true); // Flag to manage auth check loading

  useEffect(() => {
    // --- Parse URL parameters to check if access_token or role is present ---
    const urlParams = new URLSearchParams(location.search);
    const tokenFromUrl = urlParams.get("access_token");
    const roleFromUrl = urlParams.get("role");

    // --- If token is present in the URL (from OAuth redirect), store in localStorage ---
    if (tokenFromUrl) {
      localStorage.setItem("access_token", tokenFromUrl);
      if (roleFromUrl) {
        localStorage.setItem("role", roleFromUrl);
      }

      // --- Clean the URL to remove access_token and role query parameters ---
      window.history.replaceState({}, "", location.pathname);
    }

    // --- Now try to get the token from localStorage ---
    const storedToken = localStorage.getItem("access_token");
    if (!storedToken) {
      // --- No token: redirect to login ---
      navigate("/login", { replace: true });
      return;
    }

    // --- If token exists, validate it via /auth/me API using shared axios instance ---
    API.get("/auth/me") // Base URL and headers handled automatically
      .then(() => {
        setCheckingAuth(false);
      })
      .catch(() => {
        // --- Token is invalid or expired, redirect back to login ---
        localStorage.removeItem("access_token");
        localStorage.removeItem("role");
        navigate("/login", { replace: true });
      });
  }, [navigate, location]);

  // --- Show loading UI while checking auth ---
  if (checkingAuth) {
    return <p>Checking authentication...</p>;
  }

  // --- If authenticated, render protected children ---
  return children;
}
