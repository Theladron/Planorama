import { backendURL } from "../config";
import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Card,
  TextField,
  MenuItem,
  Button,
  CircularProgress,
  Alert,
  Snackbar,
} from "@mui/material";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";
import { useTranslation } from "react-i18next";

export default function AddStationPage() {
  const { t } = useTranslation();
  const { tripId } = useParams();
  const navigate = useNavigate();

  const [trip, setTrip] = useState(null);
  const [tripStations, setTripStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [townName, setTownName] = useState("");
  const [selectedDay, setSelectedDay] = useState("");

  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const tripRes = await axios.get(`/api/trips/${tripId}`);
        setTrip(tripRes.data);

        const stationsRes = await axios.get(`/api/stations/by-trip/${tripId}`);
        setTripStations(stationsRes.data);
      } catch (err) {
        console.error(err);
        setError(
          err.response?.data?.detail || t("addstation.error_loadData")
        );
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [tripId, t]);

  const getAvailableDays = () => {
    if (!trip) return [];

    const start = dayjs(trip.start_date);
    const end = dayjs(trip.end_date);
    const totalDays = end.diff(start, "day") + 1;

    const assignedDays = new Set(tripStations.map((s) => s.day_number));
    const available = [];
    for (let day = 1; day <= totalDays; day++) {
      if (!assignedDays.has(day)) available.push(day);
    }
    return available;
  };

  const availableDays = getAvailableDays();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);
    setSubmitSuccess(false);

    if (!townName.trim()) {
      setSubmitError(t("addstation.error_enterTown"));
      return;
    }
    if (!selectedDay) {
      setSubmitError(t("addstation.error_selectDay"));
      return;
    }

    setSubmitLoading(true);

    try {
      await axios.post("/api/stations/", {
        trip_id: Number(tripId),
        station_name: townName.trim(),
        day_number: Number(selectedDay),
      });

      setSubmitSuccess(true);
      setTownName("");
      setSelectedDay("");

      const stationsRes = await axios.get(`/api/stations/by-trip/${tripId}`);
      setTripStations(stationsRes.data);
    } catch (err) {
      console.error(err);
      setSubmitError(
        err.response?.data?.detail || t("addstation.error_submitFailed")
      );
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          bgcolor: "black",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

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
          width: 380,
          backdropFilter: "blur(6px)",
          backgroundColor: "rgba(250, 201, 72, 0.15)",
          border: "1px solid rgba(250, 201, 72, 0.3)",
          borderRadius: "8px",
          boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.2)",
          fontFamily: "'Pacifico', cursive",
          textShadow: "2px 2px 6px rgba(0,0,0,0.6)",
          color: "#fac948",
          p: 4,
        }}
        component="form"
        onSubmit={handleSubmit}
      >
        <Typography
          variant="h4"
          fontWeight="bold"
          mb={3}
          textAlign="center"
          sx={{ userSelect: "none" }}
        >
          {t("addstation.title", { tripName: trip.trip_name })}
        </Typography>

        <TextField
          label={t("addstation.townName_label")}
          variant="standard"
          fullWidth
          value={townName}
          onChange={(e) => setTownName(e.target.value)}
          margin="normal"
          disabled={submitLoading}
          sx={{
            mb: 3,
            input: { color: "#f0e6cc" },
            "& .MuiInputLabel-root": { color: "#fac948" },
            "& .MuiInput-underline:before": { borderBottomColor: "#fac948" },
          }}
          InputLabelProps={{ shrink: true }}
        />

        <TextField
          select
          label={t("addstation.selectDay_label")}
          value={selectedDay}
          onChange={(e) => setSelectedDay(e.target.value)}
          fullWidth
          margin="normal"
          disabled={submitLoading || availableDays.length === 0}
          helperText={
            availableDays.length === 0
              ? t("addstation.selectDay_helper_unavailable")
              : t("addstation.selectDay_helper_available")
          }
          variant="standard"
          sx={{
            mb: 3,
            input: { color: "#f0e6cc" },
            "& .MuiInputLabel-root": { color: "#fac948" },
            "& .MuiInput-underline:before": { borderBottomColor: "#fac948" },
            "& .MuiFormHelperText-root": { color: "#ffffff" },
          }}
          InputLabelProps={{ shrink: true }}
        >
          {availableDays.map((day) => (
            <MenuItem key={day} value={day}>
              Day {day}
            </MenuItem>
          ))}
        </TextField>

        {submitError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {submitError}
          </Alert>
        )}

        <Button
          type="submit"
          variant="contained"
          fullWidth
          disabled={submitLoading || availableDays.length === 0}
          sx={{ fontWeight: "bold" }}
        >
          {submitLoading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            t("addstation.button_addStation")
          )}
        </Button>

        <Snackbar
          open={submitSuccess}
          autoHideDuration={3000}
          onClose={() => setSubmitSuccess(false)}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={() => setSubmitSuccess(false)}
            severity="success"
            sx={{ width: "100%" }}
          >
            {t("addstation.success_stationAdded")}
          </Alert>
        </Snackbar>
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
          {t("addstation.button_backToTrips")}
        </Button>
      </Box>
    </Box>
  );
}
