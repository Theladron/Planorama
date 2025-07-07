import React, { useState } from "react";
import { Box, Typography, TextField, Button, Link as MuiLink } from "@mui/material";
import { Link } from "react-router-dom";

export default function RegisterPage() {
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

    if (password !== passwordRepeat) {
      setError("Passwords do not match.");
      return;
    }

    // Here you would send the registration data to your backend (example below)
    try {
      const response = await fetch("/api/users/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      if (response.ok) {
        setSuccessMessage(`${username} created. You can now log in.`);
        setUsername("");
        setEmail("");
        setPassword("");
        setPasswordRepeat("");
      } else {
        const data = await response.json();
        setError(data.detail || "Registration failed.");
      }
    } catch (err) {
      setError("Network error.");
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
        '&::before': {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.4)", // dark overlay
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
    backgroundColor: "rgba(240, 230, 204, 0.75)", // dark translucent black
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
        <Typography variant="h4" gutterBottom>
          Register
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
              Log in
            </MuiLink>
          </Typography>
        )}

        <TextField
  label="Username"
  value={username}
  onChange={(e) => setUsername(e.target.value)}
  required
  sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
/>
<TextField
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  required
  sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
/>
<TextField
  label="Password"
  type="password"
  value={password}
  onChange={(e) => setPassword(e.target.value)}
  required
  sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
/>
<TextField
  label="Repeat Password"
  type="password"
  value={passwordRepeat}
  onChange={(e) => setPasswordRepeat(e.target.value)}
  required
  sx={{ backgroundColor: "#f0e6cc", borderRadius: 1 }}
/>

        <Button variant="contained" type="submit">
          Register
        </Button>
      </Box>
    </Box>
  );
}
