import React, { useState, useContext } from "react";
import { Box, Typography, TextField, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useTranslation } from "react-i18next";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("/api/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          username: email,
          password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        login(data.access_token);
        setEmail("");
        setPassword("");
        navigate("/dashboard");
      } else {
        const data = await response.json();
        setError(data.detail || "login.error_generic");
      }
    } catch (err) {
      setError("login.error_network");
    }
  };

  return (
    <Box
      sx={{
        height: "100vh",
        backgroundImage: "url('/images/home_background.jpg')",
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
          color: "#00000",
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
        <Typography variant="h4" gutterBottom sx={{ color: "#00000" }}>
          {t("login.title")}
        </Typography>

        {error && (
          <Typography color="error" variant="body2">
            {t(error)}
          </Typography>
        )}

        <TextField
          label={t("login.email_label")}
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
        />
        <TextField
          label={t("login.password_label")}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
        />

        <Button variant="contained" type="submit">
          {t("login.submit_button")}
        </Button>
      </Box>
    </Box>
  );
}
