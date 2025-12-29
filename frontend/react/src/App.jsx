import React, { useContext, useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { Auth0Provider } from "@auth0/auth0-react";

import Navbar from "./components/Navbar";
import { AuthProvider, AuthContext } from "./context/AuthContext";
import './i18n';

const auth0Domain = import.meta.env.VITE_AUTH0_DOMAIN;
const auth0ClientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
const auth0Audience = import.meta.env.VITE_AUTH0_AUDIENCE;
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashBoardPage";
import SettingsPage from "./pages/SettingsPage";
import TripsPage from "./pages/TripsPage";
import TripsGenerationPage from "./pages/TripsGenerationPage";
import TripsCreationPage from "./pages/TripsCreationPage";
import PrivateRoute from "./components/PrivateRoute";
import AddStationPage from "./pages/AddStationPage";
import ReorderStationsPage from "./pages/ReorderStationsPage";
import { Snackbar, Alert } from "@mui/material";

function Layout({ children }) {
  const location = useLocation();
  const hasSidebar = ["/dashboard", "/settings", "/trips"].includes(location.pathname);

  return (
    <>
      <Navbar hasSidebar={hasSidebar} />
      {children}
    </>
  );
}

function AuthErrorHandler() {
  const { authError, setAuthError, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (authError) {
      setOpen(true);
      logout();
      if (location.pathname !== "/") {
        navigate("/login");
      }
    }
  }, [authError, navigate, logout, location.pathname]);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") return;
    setOpen(false);
    setAuthError(null);
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
  if (!auth0Domain || !auth0ClientId || !auth0Audience) {
    return (
      <div style={{ padding: "20px", textAlign: "center" }}>
        <h1>Configuration Error</h1>
        <p>Auth0 environment variables are missing. Please set:</p>
        <ul style={{ textAlign: "left", display: "inline-block" }}>
          <li>VITE_AUTH0_DOMAIN</li>
          <li>VITE_AUTH0_CLIENT_ID</li>
          <li>VITE_AUTH0_AUDIENCE</li>
        </ul>
      </div>
    );
  }

  return (
    <Auth0Provider
      domain={auth0Domain}
      clientId={auth0ClientId}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: auth0Audience,
      }}
      useRefreshTokens={true}
      cacheLocation="localstorage"
    >
      <AuthProvider>
        <Router>
          <AuthErrorHandler />
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
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
              <Route
                path="/trips/generate"
                element={
                  <PrivateRoute>
                    <TripsGenerationPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/trips/create"
                element={
                  <PrivateRoute>
                    <TripsCreationPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/trips/:tripId/add"
                element={
                  <PrivateRoute>
                    <AddStationPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/trips/:tripId/reorder"
                element={
                  <PrivateRoute>
                    <ReorderStationsPage />
                  </PrivateRoute>
                }
              />
            </Routes>
          </Layout>
        </Router>
      </AuthProvider>
    </Auth0Provider>
  );
}
