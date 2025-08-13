// External import: React hooks
import { useState, useEffect, useRef } from "react";
// External import: Router tools
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
// External import: MUI components
import {
  Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  IconButton, Toolbar, AppBar, Typography, Avatar, Button
} from "@mui/material";
// External import: MUI icons
import { Dashboard, People, LocalHospital, Event, Menu as MenuIcon, Logout } from "@mui/icons-material";
// Internal import: Axios instance
import API from "../utils/axiosInstance";

const drawerWidth = 240;

export default function Layout() {
  // Sidebar open/close state
  const [open, setOpen] = useState(true);

  // Get current path from router
  const location = useLocation();
  const navigate = useNavigate();

  // User state
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const hasFetchedRef = useRef(false);

  // Fetch user info on mount
  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;

    const fetchUserInfo = async () => {
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
  }, [navigate]);

  // Handle logout
  const handleLogout = async () => {
    try {
      await API.post("/auth/logout"); // assuming backend logout route exists
    } catch {
      // ignore errors for logout request
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("role");
    navigate("/login");
  };

  // Menu items config
  const menuItems = [
    { text: "Dashboard", icon: <Dashboard />, path: "/dashboard" },
    { text: "Patient", icon: <People />, path: "/patient" },
    { text: "Doctor", icon: <LocalHospital />, path: "/doctor" },
    { text: "Appointment", icon: <Event />, path: "/appointment" }
  ];

  return (
    <Box sx={{ display: "flex" }}>
      {/* --- Top App Bar --- */}
      <AppBar position="fixed" sx={{ zIndex: 1300 }}>
        <Toolbar>
          <IconButton color="inherit" onClick={() => setOpen(!open)} edge="start" sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap>
            Doctor Agentic App
          </Typography>
        </Toolbar>
      </AppBar>

      {/* --- Sidebar Drawer --- */}
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
            justifyContent: "space-between"
          }
        }}
      >
        <Box>
          <Toolbar />
          <List>
            {menuItems.map((item) => (
              <ListItemButton
                key={item.text}
                component={Link}
                to={item.path}
                sx={{
                  backgroundColor: location.pathname === item.path ? "rgba(255,255,255,0.2)" : "transparent",
                  "&:hover": { backgroundColor: "rgba(255,255,255,0.3)" }
                }}
              >
                <ListItemIcon sx={{ color: "white" }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            ))}
          </List>
        </Box>

        {/* --- User Profile Section --- */}
        {!loading && user && (
          <Box sx={{ p: 2, borderTop: "1px solid rgba(255,255,255,0.2)" }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
              <Avatar sx={{ bgcolor: "#90caf9", mr: 1 }}>
                {user.name?.[0] || "U"}
              </Avatar>
              <Box sx={{ overflow: "hidden" }}>
                <Typography variant="body1" noWrap>{user.name}</Typography>
                <Typography variant="body2" noWrap>{user.email}</Typography>
              </Box>
            </Box>
            <Button
              variant="outlined"
              color="inherit"
              size="small"
              startIcon={<Logout />}
              onClick={handleLogout}
              sx={{
                textTransform: "none",
                borderColor: "rgba(255,255,255,0.5)",
                "&:hover": { borderColor: "white", backgroundColor: "rgba(255,255,255,0.1)" }
              }}
            >
              Logout
            </Button>
          </Box>
        )}
      </Drawer>

      {/* --- Main Content Area --- */}
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
