// ---------------------------- External Imports ----------------------------

// React hooks for state, lifecycle, and routing
import { useState, useEffect } from "react";
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";

// MUI components for layout, navigation drawer, buttons, typography, and avatar
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  AppBar,
  Typography,
  Button,
  IconButton,
  Avatar,
} from "@mui/material";

// MUI icons for menu and navigation actions
import {
  Dashboard,
  People,
  LocalHospital,
  Event,
  Menu as MenuIcon,
  Logout,
} from "@mui/icons-material";

// Redux hooks for state selection and dispatching actions
import { useSelector, useDispatch } from "react-redux";

// ---------------------------- Internal Imports ----------------------------

// Redux auth selectors and actions
import { selectIsAuthenticated, logout } from "../features/authSlice";

// API instance for backend calls
import API from "../utils/axiosInstance";


// ---------------------------- Constants ----------------------------

// Sidebar width
const drawerWidth = 240;


// ---------------------------- Layout Component ----------------------------

// Main layout component with AppBar, persistent sidebar, and content area
// Props:
//   - children: optional content to render instead of <Outlet />
export default function Layout({ children }) {
  // --- Sidebar open state ---
  const [open, setOpen] = useState(true);

  // --- Routing utilities ---
  const location = useLocation();
  const navigate = useNavigate();

  // --- Redux dispatch ---
  const dispatch = useDispatch();

  // --- Authentication state ---
  const isAuthenticated = useSelector(selectIsAuthenticated);

  // --- Logged-in user info ---
  const [user, setUser] = useState(null);

  // --- Fade-in effect state for main content ---
  const [fadeIn, setFadeIn] = useState(false);

  // --- Trigger fade-in on route change ---
  useEffect(() => {
    setFadeIn(false); // reset opacity
    const timeout = setTimeout(() => setFadeIn(true), 10); // slight delay for smooth transition
    return () => clearTimeout(timeout);
  }, [location.pathname]);

  // --- Fetch user info when authenticated ---
  useEffect(() => {
    if (!isAuthenticated) {
      setUser(null); // clear user if not logged in
      return;
    }

    const fetchUser = async () => {
      try {
        const response = await API.get("/auth/me"); // backend call for current user
        setUser(response.data);                     // store user in local state
      } catch (err) {
        console.error("Failed to fetch user info", err);
      }
    };

    fetchUser();
  }, [isAuthenticated]);

  // --- Sidebar menu items ---
  const menuItems = [
    { text: "Dashboard", icon: <Dashboard />, path: "/dashboard" },
    { text: "Patient", icon: <People />, path: "/patient" },
    { text: "Doctor", icon: <LocalHospital />, path: "/doctor" },
    { text: "Appointment", icon: <Event />, path: "/appointment" },
  ];

  // --- Logout handler ---
  const handleLogout = async () => {
    try {
      await API.post("/auth/logout"); // optional backend logout
    } catch (err) {
      console.error("Logout request failed", err);
    }
    localStorage.removeItem("access_token"); // remove token
    dispatch(logout());                       // update Redux auth state
    navigate("/login", { replace: true });    // redirect to login page
  };

  // --- Render layout ---
  return (
    <Box sx={{ display: "flex" }}>
      {/* ---------------------------- Top AppBar ---------------------------- */}
      <AppBar position="fixed" sx={{ zIndex: 1300 }}>
        <Toolbar>
          {/* Menu toggle button */}
          <IconButton
            color="inherit"
            onClick={() => setOpen(!open)}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          {/* App title */}
          <Typography variant="h6" noWrap>
            Doctor Agentic App
          </Typography>
        </Toolbar>
      </AppBar>

      {/* ---------------------------- Sidebar Drawer ---------------------------- */}
      <Drawer
        variant="persistent"
        open={open}
        sx={{
          width: drawerWidth,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            backgroundColor: "#1565c0",
            color: "white",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between", // pushes bottom section down
          },
        }}
      >
        {/* Top section: Menu items */}
        <Box>
          <Toolbar /> {/* spacing for AppBar */}
          <List>
            {menuItems.map((item) => (
              <ListItemButton
                key={item.text}
                component={Link}
                to={item.path}
                disabled={!isAuthenticated} // disable links if not logged in
                sx={{
                  backgroundColor:
                    location.pathname === item.path
                      ? "rgba(255,255,255,0.2)"
                      : "transparent",
                  "&:hover": {
                    backgroundColor: isAuthenticated
                      ? "rgba(255,255,255,0.3)"
                      : "transparent",
                  },
                  cursor: isAuthenticated ? "pointer" : "not-allowed",
                }}
              >
                <ListItemIcon sx={{ color: "white" }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            ))}
          </List>
        </Box>

        {/* Bottom section: User info + Logout */}
        {isAuthenticated && user && (
          <Box sx={{ p: 2, borderTop: "1px solid rgba(255,255,255,0.2)" }}>
            {/* User avatar and info */}
            <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
              <Avatar sx={{ bgcolor: "#90caf9", mr: 1 }}>
                {user.name?.[0] || "U"}
              </Avatar>
              <Box sx={{ overflow: "hidden" }}>
                <Typography variant="body1" noWrap>
                  {user.name}
                </Typography>
                <Typography variant="body2" noWrap>
                  {user.email}
                </Typography>
              </Box>
            </Box>

            {/* Logout button */}
            <Button
              variant="contained"
              startIcon={<Logout />}
              onClick={handleLogout}
              sx={{
                textTransform: "none",
                width: "100%",
                backgroundColor: "#e53935",           // main red shade
                "&:hover": { backgroundColor: "#d32f2f" }, // darker red
                color: "white",
              }}
            >
              Logout
            </Button>
          </Box>
        )}
      </Drawer>

      {/* ---------------------------- Main Content Area ---------------------------- */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          minHeight: "100vh",
          opacity: fadeIn ? 1 : 0,                 // fade-in effect
          transition: "opacity 0.25s ease-in-out",
        }}
      >
        <Toolbar /> {/* spacing for AppBar */}
        {children ? children : <Outlet />} {/* render children or nested routes */}
      </Box>
    </Box>
  );
}
