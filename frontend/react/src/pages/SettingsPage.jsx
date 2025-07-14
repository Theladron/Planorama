import { backendURL } from "../config";
import React, { useContext, useState } from "react";
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import axios from "axios";
import { useTranslation } from "react-i18next";
import Sidebar from "../components/Sidebar";

export default function SettingsPage() {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const { t } = useTranslation();

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
      await axios.delete(`${backendURL}/api/users/me`);
      logout();
      navigate("/login");
    } catch (err) {
      console.error("Error deleting account:", err);
      setError(t("settings.error_delete"));
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
      <Sidebar />

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
          {deleting ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            t("settings.delete_profile")
          )}
        </Button>

        {error && (
          <Typography variant="body1" color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        <Dialog open={openConfirm} onClose={handleCancel}>
          <DialogTitle>{t("settings.confirm_title")}</DialogTitle>
          <DialogContent>
            <DialogContentText>{t("settings.confirm_text")}</DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCancel} disabled={deleting}>
              {t("settings.cancel")}
            </Button>
            <Button onClick={handleConfirmDelete} color="error" disabled={deleting}>
              {deleting ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                t("settings.delete")
              )}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Box>
  );
}
