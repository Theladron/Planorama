import { backendURL } from "../config";
import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
  IconButton,
  Link as MuiLink,
} from "@mui/material";

import { Link as RouterLink, useNavigate } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";
import countries from "i18n-iso-countries";
import enLocale from "i18n-iso-countries/langs/en.json";
import { useTranslation } from "react-i18next";
import Sidebar from "../components/Sidebar";

countries.registerLocale(enLocale);

function countryCodeToEmoji(countryCode) {
  if (!countryCode) return "";
  return countryCode
    .toUpperCase()
    .replace(/./g, (char) => String.fromCodePoint(127397 + char.charCodeAt()));
}

function getCountryCode(countryName) {
  return countries.getAlpha2Code(countryName, "en") || null;
}

export default function TripsPage() {
  const { t, i18n } = useTranslation();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [tripToDelete, setTripToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [updateLoading, setUpdateLoading] = useState({});
  const [editableDates, setEditableDates] = useState({});
  const [stationsByTrip, setStationsByTrip] = useState({});

  const navigate = useNavigate();

  useEffect(() => {
    const fetchTrips = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${backendURL}/api/trips/me`);
        setTrips(res.data);

        const dates = {};
        res.data.forEach((trip) => {
          dates[trip.id] = {
            start_date: dayjs(trip.start_date).format("YYYY-MM-DD"),
            end_date: dayjs(trip.end_date).format("YYYY-MM-DD"),
          };
        });
        setEditableDates(dates);

        const stationsResults = await Promise.all(
          res.data.map(async (trip) => {
            try {
              const stationsRes = await axios.get(`${backendURL}/api/stations/by-trip/${trip.id}`);
              return { tripId: trip.id, stations: stationsRes.data };
            } catch (err) {
              console.error(`Failed to fetch stations for trip ${trip.id}:`, err);
              return { tripId: trip.id, stations: [] };
            }
          })
        );

        const stationsMap = {};
        stationsResults.forEach(({ tripId, stations }) => {
          stationsMap[tripId] = stations;
        });
        setStationsByTrip(stationsMap);
      } catch (err) {
        console.error("Failed to fetch trips:", err);
        setError(t("trips.errorLoading"));
      } finally {
        setLoading(false);
      }
    };
    fetchTrips();
  }, [t]);

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
      await axios.put(`${backendURL}/api/trips/${tripId}`, {
        start_date,
        end_date,
      });

      setTrips((prevTrips) =>
        prevTrips.map((trip) =>
          trip.id === tripId ? { ...trip, start_date, end_date } : trip
        )
      );
    } catch (err) {
      console.error("Failed to update trip dates:", err);
      alert(err.response?.data?.detail || t("trips.errorLoading"));
    } finally {
      setUpdateLoading((prev) => ({ ...prev, [tripId]: false }));
    }
  };

  const handleDeleteStation = async (linkId, tripId) => {
    try {
      await axios.delete(`${backendURL}/api/stations/${linkId}`);
      setStationsByTrip((prev) => ({
        ...prev,
        [tripId]: prev[tripId].filter((station) => station.link_id !== linkId),
      }));
    } catch (err) {
      console.error("Failed to delete station:", err);
      alert("Error deleting station.");
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
      await axios.delete(`${backendURL}/api/trips/${tripToDelete.id}`);
      setTrips((prev) => prev.filter((t) => t.id !== tripToDelete.id));
      closeDeleteDialog();
    } catch (err) {
      console.error("Failed to delete trip:", err);
      alert(err.response?.data?.detail || t("trips.errorLoading"));
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleGenerateClick = (tripId) => {
    navigate(`/trips/generate?tripId=${tripId}`);
  };

  const handleAddStationClick = (tripId) => {
    navigate(`/trips/${tripId}/add`);
  };

  const handleReorderStationsClick = (tripId) => {
    navigate(`/trips/${tripId}/reorder`);
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
    <Box sx={{ display: "flex", height: "100vh", backgroundColor: "#000" }}>
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 4,
          overflowY: "auto",
          position: "relative",
          color: "#fff",
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundImage: "url('/images/home_background.jpg')",
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            backgroundAttachment: "fixed",
            zIndex: 0,
            opacity: 0.4,
          },
        }}
      >
        <Box sx={{ position: "relative", zIndex: 1, maxWidth: 1000, mx: "auto" }}>
          <Typography variant="h3" sx={{ fontWeight: 600, mt: "100px", fontSize: "4rem", mb: 3, textShadow: "2px 2px 8px rgba(0,0,0,0.6)", textAlign: "center" }}>
            {t("trips.title")}
          </Typography>

          {error && (
            <Typography color="error" sx={{ mb: 2, textAlign: "center" }}>
              {error}
            </Typography>
          )}

          {trips.length === 0 ? (
            <Typography variant="h6" sx={{ textAlign: "center" }}>
              {t("trips.noTrips")}{" "}
              <MuiLink component={RouterLink} to="/trips/create" sx={{ color: "#f0e6cc", fontWeight: "bold" }}>
                {t("trips.startNewTrip")}
              </MuiLink>
            </Typography>
          ) : (
            <Box sx={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 3, mb: 4 }}>
              {trips.map((trip) => (
                <Card
                  key={trip.id}
                  sx={{
                    maxWidth: 270,
                    backgroundColor: "rgba(250, 201, 72, 0.15)",
                    backdropFilter: "blur(6px)",
                    border: "1px solid rgba(250, 201, 72, 0.3)",
                    borderRadius: "8px",
                    boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.2)",
                    fontFamily: "'Pacifico', cursive",
                    textShadow: "2px 2px 6px rgba(0,0,0,0.6)",
                    color: "#f0e6cc",
                    display: "flex",
                    flexDirection: "column",
                    height: "100%",
                    position: "relative",
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h5" gutterBottom fontWeight="bold">
                        {trip.trip_name}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1, fontWeight: "bold" }}>
                      {t("trips.createdAt", {
                        date: dayjs(trip.created_at).format("YYYY-MM-DD"),
                      })}
                    </Typography>

                    <TextField
                      label={t("trips.startDate")}
                      type="date"
                      value={editableDates[trip.id]?.start_date || ""}
                      onChange={(e) => handleDateChange(trip.id, "start_date", e.target.value)}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      sx={{
                        backgroundColor: "rgba(250, 201, 72, 0.3)",
                        borderRadius: 1,
                        mb: 1,
                        input: { color: "#f0e6cc" },
                        label: { color: "#f0e6cc" },
                      }}
                    />
                    <TextField
                      label={t("trips.endDate")}
                      type="date"
                      value={editableDates[trip.id]?.end_date || ""}
                      onChange={(e) => handleDateChange(trip.id, "end_date", e.target.value)}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      sx={{
                        backgroundColor: "rgba(250, 201, 72, 0.3)",
                        borderRadius: 1,
                        input: { color: "#f0e6cc" },
                        label: { color: "#f0e6cc" },
                      }}
                    />
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={() => handleUpdateDate(trip.id)}
                      disabled={updateLoading[trip.id]}
                      sx={{ mt: 1 }}
                    >
                      {updateLoading[trip.id] ? (
                        <CircularProgress size={24} color="inherit" />
                      ) : (
                        t("trips.update")
                      )}
                    </Button>

                    <Typography variant="subtitle1" sx={{ fontWeight: "bold", mt: 2, mb: 1 }}>
                      {t("trips.stations")}
                    </Typography>

                    {stationsByTrip[trip.id]?.length > 0 ? (
                      stationsByTrip[trip.id].map((station) => {
                        const countryCode = getCountryCode(station.country);
                        const flagEmoji = countryCodeToEmoji(countryCode);

                        return (
                          <Box
                            key={station.link_id}
                          >
                            <Typography sx={{ flex: 1, mt: -3}}>
                              {flagEmoji}{" "}
                              {i18n.language === "de" ? station.station_name_de : station.station_name}{" "}
                              {station.city}

                            <IconButton onClick={() => handleDeleteStation(station.link_id, trip.id)} color="error">
                              🗑
                            </IconButton>
                            </Typography>
                          </Box>
                        );
                      })
                    ) : (
                      <Typography sx={{ fontStyle: "italic" }}>{t("trips.noStations")}</Typography>
                    )}

                    <Box sx={{ mt: 2, display: "flex", flexWrap: "wrap", gap: 1 }}>
                      <Button fullWidth variant="contained" color="info" onClick={() => handleAddStationClick(trip.id)} sx={{ flexBasis: "48%" }}>
                        {t("trips.addStation")}
                      </Button>
                      <Button fullWidth variant="contained" color="info" onClick={() => handleReorderStationsClick(trip.id)} sx={{ flexBasis: "48%" }}>
                        {t("trips.reorderStations")}
                      </Button>
                      <Button fullWidth variant="contained" color="error" onClick={() => openDeleteDialog(trip)} sx={{ flexBasis: "48%" }}>
                        {t("trips.delete")}
                      </Button>
                      <Button fullWidth variant="contained" color="success" onClick={() => handleGenerateClick(trip.id)} sx={{ flexBasis: "48%" }}>
                        {t("trips.showTrip")}
                      </Button>

                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Box>

        <Dialog
          open={deleteDialogOpen}
          onClose={closeDeleteDialog}
          aria-labelledby="delete-trip-dialog-title"
          aria-describedby="delete-trip-dialog-description"
        >
          <DialogTitle id="delete-trip-dialog-title">
            {t("trips.confirmDeleteTitle")}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="delete-trip-dialog-description">
              {t("trips.confirmDeleteText")}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={closeDeleteDialog} disabled={deleteLoading}>
              {t("trips.cancel")}
            </Button>
            <Button onClick={handleConfirmDelete} color="error" disabled={deleteLoading} autoFocus>
              {deleteLoading ? <CircularProgress size={20} /> : t("trips.delete")}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Box>
  );
}
