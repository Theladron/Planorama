import React, { useContext, useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
  useNavigate,
} from "react-router-dom";

import Navbar from "./components/Navbar";
import { AuthProvider, AuthContext } from "./context/AuthContext";

import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import SettingsPage from "./pages/SettingsPage";
import TripsPage from "./pages/TripsPage";

import PrivateRoute from "./components/PrivateRoute";

import { Snackbar, Alert } from "@mui/material";

// Wrapper to control Navbar layout based on current path
function Layout({ children }) {
  const location = useLocation();
  const hasSidebar = ["/dashboard", "/settings"].includes(location.pathname);

  return (
    <>
      <Navbar hasSidebar={hasSidebar} />
      {children}
    </>
  );
}

// Component to handle global auth error & redirect
function AuthErrorHandler() {
  const { authError, setAuthError, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (authError) {
      // Show snackbar
      setOpen(true);
      // Redirect to login page
      logout(); // clear auth states & token
      if (location.pathname !== "/") {
        navigate("/login");
      }
    }
  }, [authError, navigate, logout]);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") return;
    setOpen(false);
    setAuthError(null); // Clear error so message doesn't show again
  };

  return (
    <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
      <Alert severity="warning" onClose={handleClose} sx={{ width: "100%" }}>
        {authError}
      </Alert>
    </Snackbar>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AuthErrorHandler />
        <Layout>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <DashboardPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <PrivateRoute>
                  <SettingsPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/trips"
              element={
                <PrivateRoute>
                  <TripsPage />
                </PrivateRoute>
              }
            />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}
