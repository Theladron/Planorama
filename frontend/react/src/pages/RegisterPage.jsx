import React, { useState } from "react";
import { Box, Typography, TextField, Button, Link as MuiLink } from "@mui/material";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { backendURL } from "../config";

function validatePassword(password, t) {
  if (password.length < 8) return t("register.error_password_length");
  if (!/[A-Z]/.test(password)) return t("register.error_password_uppercase");
  if (!/[a-z]/.test(password)) return t("register.error_password_lowercase");
  if (!/\d/.test(password)) return t("register.error_password_number");
  if (!/[^\w\s]/.test(password)) return t("register.error_password_symbol");
  return null; // valid
}

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export default function RegisterPage() {
  const { t } = useTranslation();

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
    const response = await fetch(`${backendURL}/api/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });

    if (response.ok) {
      setSuccessMessage(t("register.success_message", { username }));
      setUsername("");
      setEmail("");
      setPassword("");
      setPasswordRepeat("");
    } else {
      const data = await response.json();
      setError(data.detail || t("register.error_generic"));
    }
  } catch (err) {
    setError(t("register.error_network"));
  }
};


  return (
    <Box
      sx={{
        height: "100vh",
        backgroundImage: `url('${backendURL}/images/home_background.jpg')`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.4)",
          zIndex: 1,
        },
        zIndex: 2,
      }}
    >
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

        {error && (
          <Typography color="error" variant="body2">
            {error}
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

        <Button variant="contained" type="submit">
          {t("register.submit_button")}
        </Button>
      </Box>
    </Box>
  );
}
