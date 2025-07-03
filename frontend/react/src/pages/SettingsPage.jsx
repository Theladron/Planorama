import React, { useContext, useState } from "react";
import {
  Box,
  Typography,
  Link as MuiLink,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
} from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import axios from "axios";

export default function SettingsPage() {
  const { logout, user } = useContext(AuthContext);
  const navigate = useNavigate();

  // Dialog state
  const [openConfirm, setOpenConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleDeleteClick = () => {
    setOpenConfirm(true);
  };

  const handleCancel = () => {
    setOpenConfirm(false);
    setError(null);
  };

  const handleConfirmDelete = async () => {
    setDeleting(true);
    setError(null);
    try {
      await axios.delete("/api/users/me");
      logout();
      navigate("/login");
    } catch (err) {
      console.error("Error deleting account:", err);
      setError("Failed to delete account. Please try again.");
    } finally {
      setDeleting(false);
      setOpenConfirm(false);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        backgroundImage: "url('/images/home_background.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        position: "relative",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.4)",
          zIndex: 0,
        },
      }}
    >
      {/* Sidebar */}
      <Box
        component="nav"
        sx={{
          width: 200,
          bgcolor: "rgba(0, 0, 0, 0.85)",
          color: "#fff",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          p: 2,
          pt: 10,
          position: "fixed",
          top: 0,
          left: 0,
          bottom: 0,
          boxShadow: "2px 0 8px rgba(0,0,0,0.8)",
          zIndex: 1100,
        }}
      >
        <Box>
          <MuiLink component={RouterLink} to="/trips" underline="none" sx={linkStyle}>
            Trips
          </MuiLink>
        </Box>

        <Box sx={{ mb: 2 }}>
          <MuiLink component={RouterLink} to="/settings" underline="none" sx={linkStyle}>
            Settings
          </MuiLink>
          <MuiLink
            component="button"
            underline="none"
            onClick={handleLogout}
            sx={{ ...linkStyle, cursor: "pointer" }}
          >
            Logout
          </MuiLink>
        </Box>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          ml: "320px",
          mt: "180px",
          pr: 4,
          pb: 4,
          flexGrow: 1,
          position: "relative",
          zIndex: 1,
          color: "#fff",
          textAlign: "left",
          maxWidth: "900px",
        }}
      >


        <Button
          variant="contained"
          color="error"
          onClick={handleDeleteClick}
          disabled={deleting}
          sx={{ mt: 3 }}
        >
          {deleting ? <CircularProgress size={24} color="inherit" /> : "Delete Profile"}
        </Button>

        {error && (
          <Typography variant="body1" color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        {/* Confirmation Dialog */}
        <Dialog open={openConfirm} onClose={handleCancel}>
          <DialogTitle>Confirm Account Deletion</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete your profile? This action is irreversible.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCancel} disabled={deleting}>
              Cancel
            </Button>
            <Button onClick={handleConfirmDelete} color="error" disabled={deleting}>
              {deleting ? <CircularProgress size={20} color="inherit" /> : "Delete"}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Box>
  );
}

const linkStyle = {
  display: "block",
  mb: 2,
  color: "#fff",
  fontWeight: "bold",
  "&:hover": { color: "#f0e6cc" },
};
