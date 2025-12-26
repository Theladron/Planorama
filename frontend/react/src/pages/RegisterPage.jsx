import React, { useState } from "react";
import { Box, Typography, TextField, Button, Link as MuiLink } from "@mui/material";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { validateEmail, validatePassword } from "../utils/validation";
import { useAuth } from "../hooks/useAuth";
import { BackgroundBox } from "../components/common/BackgroundBox";

export default function RegisterPage() {
  const { t } = useTranslation();
  const { register, loading, error: authError } = useAuth();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");

    if (!validateEmail(email)) {
      setError(t("register.error_invalid_email") || "Invalid email address");
      return;
    }

    if (password !== passwordRepeat) {
      setError(t("register.error_mismatch"));
      return;
    }

    const passwordError = validatePassword(password, t);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    try {
      await register(username, email, password);
      setSuccessMessage(t("register.success_message", { username }));
      setUsername("");
      setEmail("");
      setPassword("");
      setPasswordRepeat("");
    } catch (err) {
      setError(err.message || t("register.error_generic"));
    }
  };

  const displayError = error || authError;

  return (
    <BackgroundBox>
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          position: "relative",
          zIndex: 3,
          backgroundColor: "rgba(240, 230, 204, 0.75)",
          color: "#000000",
          p: 4,
          borderRadius: 2,
          boxShadow: 3,
          width: "320px",
          display: "flex",
          flexDirection: "column",
          gap: 2,
          textAlign: "center",
        }}
      >
        <Typography variant="h4" gutterBottom>
          {t("register.title")}
        </Typography>

        {displayError && (
          <Typography color="error" variant="body2">
            {displayError}
          </Typography>
        )}

        {successMessage && (
          <Typography color="success.main" variant="body2">
            {successMessage}{" "}
            <MuiLink component={Link} to="/login" underline="hover">
              {t("register.login_link_text")}
            </MuiLink>
          </Typography>
        )}

        <TextField
          label={t("register.username_label")}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
        />
        <TextField
          label={t("register.email_label")}
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
        />
        <TextField
          label={t("register.password_label")}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
        />
        <TextField
          label={t("register.repeat_password_label")}
          type="password"
          value={passwordRepeat}
          onChange={(e) => setPasswordRepeat(e.target.value)}
          required
          sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
        />

        <Button variant="contained" type="submit" disabled={loading}>
          {loading ? "Loading..." : t("register.submit_button")}
        </Button>
      </Box>
    </BackgroundBox>
  );
}
