import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
  Link as MuiLink,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";
import countries from "i18n-iso-countries";
import enLocale from "i18n-iso-countries/langs/en.json";

// Register English locale for country name lookup
countries.registerLocale(enLocale);

// Helper to convert country code to emoji flag
function countryCodeToEmoji(countryCode) {
  if (!countryCode) return ""; // handle unknown
  return countryCode
    .toUpperCase()
    .replace(/./g, (char) =>
      String.fromCodePoint(127397 + char.charCodeAt())
    );
}

// Convert full country name to alpha-2 code using i18n-iso-countries
function getCountryCode(countryName) {
  return countries.getAlpha2Code(countryName, "en") || null;
}

export default function TripsPage() {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [tripToDelete, setTripToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [updateLoading, setUpdateLoading] = useState({});

  const [editableDates, setEditableDates] = useState({});

  useEffect(() => {
    const fetchTrips = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get("/api/trips/me");
        setTrips(res.data);

        const dates = {};
        res.data.forEach((trip) => {
          dates[trip.id] = {
            start_date: dayjs(trip.start_date).format("YYYY-MM-DD"),
            end_date: dayjs(trip.end_date).format("YYYY-MM-DD"),
          };
        });
        setEditableDates(dates);
      } catch (err) {
        console.error("Failed to fetch trips:", err);
        setError("Failed to load trips.");
      } finally {
        setLoading(false);
      }
    };
    fetchTrips();
  }, []);

  const handleDateChange = (tripId, field, value) => {
    setEditableDates((prev) => ({
      ...prev,
      [tripId]: {
        ...prev[tripId],
        [field]: value,
      },
    }));
  };

  const handleUpdateDate = async (tripId) => {
    if (!editableDates[tripId]) return;

    const { start_date, end_date } = editableDates[tripId];

    setUpdateLoading((prev) => ({ ...prev, [tripId]: true }));

    try {
      await axios.put(`/api/trips/${tripId}`, {
        start_date,
        end_date,
      });

      setTrips((prevTrips) =>
        prevTrips.map((trip) =>
          trip.id === tripId
            ? { ...trip, start_date, end_date }
            : trip
        )
      );
    } catch (err) {
      console.error("Failed to update trip dates:", err);
      alert(
        err.response?.data?.detail ||
          "Failed to update trip dates. Please check your inputs."
      );
    } finally {
      setUpdateLoading((prev) => ({ ...prev, [tripId]: false }));
    }
  };

  const openDeleteDialog = (trip) => {
    setTripToDelete(trip);
    setDeleteDialogOpen(true);
  };

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setTripToDelete(null);
  };

  const handleConfirmDelete = async () => {
    if (!tripToDelete) return;
    setDeleteLoading(true);

    try {
      await axios.delete(`/api/trips/${tripToDelete.id}`);

      setTrips((prev) => prev.filter((t) => t.id !== tripToDelete.id));

      closeDeleteDialog();
    } catch (err) {
      console.error("Failed to delete trip:", err);
      alert(
        err.response?.data?.detail || "Failed to delete trip. Try again later."
      );
    } finally {
      setDeleteLoading(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          height: "100vh",
          justifyContent: "center",
          alignItems: "center",
          backgroundImage: "url('/images/home_background.jpg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          WebkitBackgroundClip: "text",
          position: "relative",
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
        <CircularProgress color="inherit" />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        p: 4,
        backgroundImage: "url('/images/home_background.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "relative",
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
      <Box sx={{ position: "relative", zIndex: 1, maxWidth: 1000, mx: "auto" }}>
        <Typography
          variant="h3"
          sx={{
            fontWeight: 600,
            mt: "100px",
            fontSize: "4rem",
            mb: 3,
            textShadow: "2px 2px 8px rgba(0,0,0,0.6)",
            textAlign: "center",
          }}
        >
          Your Trips
        </Typography>

        {error && (
          <Typography color="error" sx={{ mb: 2, textAlign: "center" }}>
            {error}
          </Typography>
        )}

        {trips.length === 0 ? (
          <Typography variant="h6" sx={{ textAlign: "center" }}>
            You have not created any trips yet.{" "}
            <MuiLink
              component={RouterLink}
              to="/trips/new"
              sx={{ color: "#f0e6cc", fontWeight: "bold" }}
            >
              Start by adding a new vacation trip.
            </MuiLink>
          </Typography>
        ) : (
          trips.map((trip) => (
            <Card
              key={trip.id}
              sx={{
                mb: 4,
                maxWidth: 270,
                backgroundColor: "rgba(250, 201, 72, 0.15)",
                backdropFilter: "blur(6px)",
                border: "1px solid rgba(250, 201, 72, 0.3)",
                borderRadius: "8px",
                boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.2)",
                fontFamily: "'Pacifico', cursive",
                textShadow: "2px 2px 6px rgba(0,0,0,0.6)",
                color: "#fac948",
                position: "relative",
                zIndex: 1,
              }}
            >
              <CardContent>
                <Typography variant="h5" fontWeight="bold" gutterBottom>
                  {trip.trip_name}
                </Typography>

                {/* Country flags */}
                <Box sx={{ mb: 2 }}>
                  {trip.trip_countries.map((countryName) => {
                    const code = getCountryCode(countryName);
                    return (
                      <Typography
                        key={countryName}
                        component="span"
                        sx={{ fontSize: "1.5rem", mr: 1 }}
                        aria-label={`Flag of ${countryName}`}
                        title={countryName}
                      >
                        {code ? countryCodeToEmoji(code) : countryName}
                      </Typography>
                    );
                  })}
                </Box>

                {/* Created at */}
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Created at: {dayjs(trip.created_at).format("MMMM D, YYYY")}
                </Typography>

                {/* Start Date */}
                <Box sx={{ display: "flex",
                    alignItems: "center",
                    mb: 1,
                    ml: -2,
                    flexWrap: "wrap",
                     height: "55px"}}>
                  <TextField
                    label="Start Date"
                    type="date"
                    size="small"
                    value={editableDates[trip.id]?.start_date || ""}
                    onChange={(e) =>
                      handleDateChange(trip.id, "start_date", e.target.value)
                    }
                    InputLabelProps={{ shrink: true }}
                    sx={{ maxWidth: 160,
                        input: {
                        color: "#f0e6cc",
                        } }}
                  />
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => handleUpdateDate(trip.id)}
                    disabled={updateLoading[trip.id]}
                  >
                    {updateLoading[trip.id] ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      "Update"
                    )}
                  </Button>
                </Box>

                {/* End Date */}
                <Box sx={{ display: "flex",
                    alignItems: "center",
                    mb: 1,
                    ml: -2,
                    flexWrap: "wrap",
                    height: "55px" }}>
                  <TextField
                    label="End Date"
                    type="date"
                    size="small"
                    value={editableDates[trip.id]?.end_date || ""}
                    onChange={(e) =>
                      handleDateChange(trip.id, "end_date", e.target.value)
                    }
                    InputLabelProps={{ shrink: true }}
                    sx={{ maxWidth: 160,
                        input: {
                        color: "#f0e6cc",
                        }}}
                  />
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => handleUpdateDate(trip.id)}
                    disabled={updateLoading[trip.id]}
                  >
                    {updateLoading[trip.id] ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      "Update"
                    )}
                  </Button>
                </Box>
              </CardContent>

              <CardActions>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => openDeleteDialog(trip)}
                  disabled={deleteLoading}
                >
                  Delete
                </Button>
              </CardActions>
            </Card>
          ))
        )}

        <Dialog open={deleteDialogOpen} onClose={closeDeleteDialog}>
          <DialogTitle>Confirm Delete Trip</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete the trip{" "}
              <strong>{tripToDelete?.trip_name}</strong>? This action cannot be
              undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={closeDeleteDialog} disabled={deleteLoading}>
              Cancel
            </Button>
            <Button
              onClick={handleConfirmDelete}
              color="error"
              disabled={deleteLoading}
            >
              {deleteLoading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                "Delete"
              )}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Box>
  );
}
