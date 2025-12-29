import React, { useState, useContext, useEffect } from "react";
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
  TextField,
  Alert,
  Paper,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import { deleteUser, updateUsername, updatePassword } from "../api/userApi";
import Sidebar from "../components/Sidebar";

export default function SettingsPage() {
  const { logout, user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [openConfirm, setOpenConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);

  const [username, setUsername] = useState("");
  const [updatingUsername, setUpdatingUsername] = useState(false);
  const [usernameError, setUsernameError] = useState(null);
  const [usernameSuccess, setUsernameSuccess] = useState(false);

  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [updatingPassword, setUpdatingPassword] = useState(false);
  const [passwordError, setPasswordError] = useState(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  useEffect(() => {
    if (user) {
      setUsername(user.username || "");
    }
  }, [user]);

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
      await deleteUser();
      logout();
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || t("settings.error_delete"));
    } finally {
      setDeleting(false);
      setOpenConfirm(false);
    }
  };

  const handleUsernameUpdate = async (e) => {
    e.preventDefault();
    setUpdatingUsername(true);
    setUsernameError(null);
    setUsernameSuccess(false);

    if (!username.trim()) {
      setUsernameError(t("settings.error_username_empty"));
      setUpdatingUsername(false);
      return;
    }

    if (username === user?.username) {
      setUsernameError(t("settings.error_username_same"));
      setUpdatingUsername(false);
      return;
    }

    try {
      const updatedUser = await updateUsername(username.trim());
      setUser(updatedUser);
      setUsernameSuccess(true);
      setTimeout(() => setUsernameSuccess(false), 3000);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || t("settings.error_username_update_failed");
      setUsernameError(errorMessage);
    } finally {
      setUpdatingUsername(false);
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    setUpdatingPassword(true);
    setPasswordError(null);
    setPasswordSuccess(false);

    if (!password) {
      setPasswordError(t("settings.error_password_empty"));
      setUpdatingPassword(false);
      return;
    }

    if (password.length < 8) {
      setPasswordError(t("settings.error_password_length"));
      setUpdatingPassword(false);
      return;
    }

    if (password !== repeatPassword) {
      setPasswordError(t("settings.error_password_mismatch"));
      setUpdatingPassword(false);
      return;
    }

    try {
      await updatePassword(password);
      setPasswordSuccess(true);
      setPassword("");
      setRepeatPassword("");
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || t("settings.error_password_update_failed");
      setPasswordError(errorMessage);
    } finally {
      setUpdatingPassword(false);
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
        <Typography variant="h4" gutterBottom sx={{ mb: 4, textShadow: "2px 2px 4px rgba(0,0,0,0.8)" }}>
          {t("settings.title")}
        </Typography>

        <Paper
          elevation={3}
          sx={{
            p: 3,
            mb: 3,
            backgroundColor: "rgba(240, 230, 204, 0.9)",
            color: "#000",
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            {t("settings.update_username")}
          </Typography>
          <form onSubmit={handleUsernameUpdate}>
            <TextField
              fullWidth
              label={t("settings.username")}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={updatingUsername}
              sx={{ mb: 2 }}
              error={!!usernameError}
              helperText={usernameError}
            />
            {usernameSuccess && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {t("settings.username_updated")}
              </Alert>
            )}
            <Button
              type="submit"
              variant="contained"
              disabled={updatingUsername || !username.trim() || username === user?.username}
              sx={{ mb: 2 }}
            >
              {updatingUsername ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                t("settings.update_username_button")
              )}
            </Button>
          </form>
        </Paper>

        <Paper
          elevation={3}
          sx={{
            p: 3,
            mb: 3,
            backgroundColor: "rgba(240, 230, 204, 0.9)",
            color: "#000",
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            {t("settings.change_password")}
          </Typography>
          <form onSubmit={handlePasswordUpdate}>
            <TextField
              fullWidth
              type="password"
              label={t("settings.new_password")}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={updatingPassword}
              sx={{ mb: 2 }}
              error={!!passwordError && password.length > 0}
              helperText={password.length > 0 && password.length < 8 ? t("settings.error_password_length") : ""}
            />
            <TextField
              fullWidth
              type="password"
              label={t("settings.repeat_password")}
              value={repeatPassword}
              onChange={(e) => setRepeatPassword(e.target.value)}
              disabled={updatingPassword}
              sx={{ mb: 2 }}
              error={!!passwordError && repeatPassword.length > 0}
              helperText={
                repeatPassword.length > 0 && password !== repeatPassword
                  ? t("settings.error_password_mismatch")
                  : passwordError && repeatPassword.length > 0
                  ? passwordError
                  : ""
              }
            />
            {passwordSuccess && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {t("settings.password_updated")}
              </Alert>
            )}
            <Button
              type="submit"
              variant="contained"
              disabled={updatingPassword || !password || !repeatPassword || password.length < 8}
              sx={{ mb: 2 }}
            >
              {updatingPassword ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                t("settings.update_password_button")
              )}
            </Button>
          </form>
        </Paper>

        <Paper
          elevation={3}
          sx={{
            p: 3,
            mb: 3,
            backgroundColor: "rgba(200, 50, 50, 0.9)",
            color: "#fff",
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            {t("settings.danger_zone")}
          </Typography>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteClick}
            disabled={deleting}
          >
            {deleting ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              t("settings.delete_profile")
            )}
          </Button>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
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
