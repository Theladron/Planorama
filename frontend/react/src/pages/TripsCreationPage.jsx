import { backendURL } from "../config";
import React, { useState } from "react";
import {
  Box,
  Typography,
  Card,
  TextField,
  Button,
  CircularProgress,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useTranslation } from "react-i18next";

export default function TripsCreationPage() {
  const { t } = useTranslation();
  const [tripName, setTripName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!tripName || !startDate || !endDate) {
      setError(t("tripscreation.error_fill_all"));
      return;
    }

    if (new Date(startDate) > new Date(endDate)) {
      setError(t("tripscreation.error_start_after_end"));
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await axios.post("${backendURL}/api/trips/", {
        trip_name: tripName,
        start_date: startDate,
        end_date: endDate,
      });

      navigate("/trips");
    } catch (err) {
      console.error("Failed to create trip:", err);
      setError(
        err.response?.data?.detail || t("tripscreation.error_generic")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundImage: "url('/images/home_background.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "relative",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        p: 3,
        color: "#fff",
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
      <Card
        sx={{
          position: "relative",
          zIndex: 1,
          width: 350,
          backdropFilter: "blur(6px)",
          backgroundColor: "rgba(250, 201, 72, 0.15)",
          border: "1px solid rgba(250, 201, 72, 0.3)",
          borderRadius: "8px",
          boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.2)",
          fontFamily: "'Pacifico', cursive",
          textShadow: "2px 2px 6px rgba(0,0,0,0.6)",
          color: "#fac948",
          p: 3,
        }}
      >
        <Typography variant="h4" fontWeight="bold" mb={3} textAlign="center">
          {t("tripscreation.title")}
        </Typography>

        <form onSubmit={handleSubmit}>
          <TextField
            label={t("tripscreation.label_trip_name")}
            variant="standard"
            fullWidth
            required
            value={tripName}
            onChange={(e) => setTripName(e.target.value)}
            sx={{
              mb: 3,
              input: { color: "#f0e6cc" },
              "& .MuiInputLabel-root": { color: "#fac948" },
              "& .MuiInput-underline:before": { borderBottomColor: "#fac948" },
            }}
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            label={t("tripscreation.label_start_date")}
            type="date"
            variant="standard"
            fullWidth
            required
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            sx={{
              mb: 3,
              input: { color: "#f0e6cc" },
              "& .MuiInputLabel-root": { color: "#fac948" },
              "& .MuiInput-underline:before": { borderBottomColor: "#fac948" },
            }}
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            label={t("tripscreation.label_end_date")}
            type="date"
            variant="standard"
            fullWidth
            required
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            sx={{
              mb: 4,
              input: { color: "#f0e6cc" },
              "& .MuiInputLabel-root": { color: "#fac948" },
              "& .MuiInput-underline:before": { borderBottomColor: "#fac948" },
            }}
            InputLabelProps={{ shrink: true }}
          />

          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}

          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={loading}
            sx={{ fontWeight: "bold" }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : t("tripscreation.button_create")}
          </Button>
        </form>
      </Card>

      <Box
        sx={{
          position: "fixed",
          bottom: 24,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          zIndex: 10,
        }}
      >
        <Button
          variant="outlined"
          color="warning"
          onClick={() => navigate("/trips")}
          sx={{
            fontWeight: "bold",
            borderColor: "#fac948",
            color: "#fac948",
            "&:hover": {
              backgroundColor: "rgba(250, 201, 72, 0.15)",
              borderColor: "#fac948",
            },
          }}
        >
          {t("tripscreation.button_back_to_trips")}
        </Button>
      </Box>
    </Box>
  );
}
