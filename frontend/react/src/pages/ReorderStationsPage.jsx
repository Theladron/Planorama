import { backendURL } from "../config";
import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Card,
  CircularProgress,
  Alert,
  TextField,
  MenuItem,
  Button,
  Snackbar,
} from "@mui/material";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";
import { useTranslation } from "react-i18next";

export default function ReorderStationsPage() {
  const { t } = useTranslation();
  const { tripId } = useParams();
  const [trip, setTrip] = useState(null);
  const [stations, setStations] = useState([]);
  const [dayAssignments, setDayAssignments] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, [tripId]);

  async function fetchData() {
    setLoading(true);
    try {
      const tripRes = await axios.get(`${backendURL}/api/trips/${tripId}`);
      const stationsRes = await axios.get(`${backendURL}/api/stations/by-trip/${tripId}`);
      setTrip(tripRes.data);
      setStations(stationsRes.data);

      const initialAssignments = {};
      stationsRes.data.forEach((s) => {
        initialAssignments[s.link_id] = String(s.day_number);
      });
      setDayAssignments(initialAssignments);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          t("reorderstations.error_load")
      );
    } finally {
      setLoading(false);
    }
  }

  function getTripDays() {
    if (!trip) return [];
    const start = dayjs(trip.start_date);
    const end = dayjs(trip.end_date);
    const days = [];
    for (let i = 1; i <= end.diff(start, "day") + 1; i++) {
      days.push(i);
    }
    return days;
  }

  function hasDuplicates(values) {
    const seen = new Set();
    for (const val of values) {
      if (seen.has(val)) return true;
      seen.add(val);
    }
    return false;
  }

  const handleSubmit = async () => {
    setSubmitError(null);
    setSubmitSuccess(false);

    const selectedDays = Object.values(dayAssignments);
    if (hasDuplicates(selectedDays)) {
      setSubmitError(t("reorderstations.error_unique_day"));
      return;
    }

    setSubmitLoading(true);

    try {
      const response = await axios.put(`${backendURL}/api/stations/reorder`, {
        trip_id: Number(tripId),
        stations: Object.entries(dayAssignments).map(([link_id, day]) => ({
          link_id: Number(link_id),
          day_number: Number(day),
        })),
      });

      // Use updated stations from backend
      setStations(response.data);

      setSubmitSuccess(true);
    } catch (err) {
      console.error(err);
      setSubmitError(
        err.response?.data?.detail ||
          t("reorderstations.error_generic")
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

  const tripDays = getTripDays();

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
          width: 420,
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
      >
        <Typography
          variant="h4"
          fontWeight="bold"
          mb={3}
          textAlign="center"
          sx={{ userSelect: "none" }}
        >
          {t("reorderstations.title", { tripName: trip.trip_name })}
        </Typography>

        {stations.map((station) => (
          <TextField
            key={station.link_id}
            select
            fullWidth
            label={t("reorderstations.station_label", {
              stationName: station.station_name,
            })}
            value={dayAssignments[station.link_id] || ""}
            onChange={(e) =>
              setDayAssignments({
                ...dayAssignments,
                [station.link_id]: e.target.value,
              })
            }
            margin="normal"
            variant="standard"
            sx={{
              mb: 2,
              input: { color: "#fdfae5" },
              "& .MuiInputLabel-root": { color: "#fac948" },
              "& .MuiInput-underline:before": { borderBottomColor: "#fac948" },
              "& .MuiInputBase-input": { color: "#fdfae5" },
            }}
            InputLabelProps={{ shrink: true }}
          >
            {tripDays.map((day) => (
              <MenuItem
                key={day}
                value={String(day)}
                sx={{ color: "#fdfae5", backgroundColor: "rgba(0,0,0,0.3)" }}
              >
                {t("reorderstations.day_option", { day })}
              </MenuItem>
            ))}
          </TextField>
        ))}

        {submitError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {submitError}
          </Alert>
        )}

        <Button
          variant="contained"
          fullWidth
          onClick={handleSubmit}
          disabled={submitLoading}
          sx={{ fontWeight: "bold" }}
        >
          {submitLoading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            t("reorderstations.submit_button")
          )}
        </Button>

        <Snackbar
          open={submitSuccess}
          autoHideDuration={1200}
          onClose={() => setSubmitSuccess(false)}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={() => setSubmitSuccess(false)}
            severity="success"
            sx={{ width: "100%" }}
          >
            {t("reorderstations.success_message")}
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
          {t("reorderstations.back_button")}
        </Button>
      </Box>
    </Box>
  );
}
