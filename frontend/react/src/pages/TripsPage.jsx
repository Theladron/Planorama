import React, { useState } from "react";
import { Box, Typography, Link as MuiLink, CircularProgress } from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Sidebar from "../components/Sidebar";
import { useTripManagement } from "../hooks/useTripManagement";
import { TripCard } from "../components/trips/TripCard";
import { DeleteTripDialog } from "../components/trips/DeleteTripDialog";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

export default function TripsPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();

  const {
    trips,
    loading,
    error,
    updateLoading,
    editableDates,
    stationsByTrip,
    handleDateChange,
    handleUpdateDate,
    handleDeleteStation,
    handleDeleteTrip,
  } = useTripManagement(t);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [tripToDelete, setTripToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

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
      await handleDeleteTrip(tripToDelete.id);
      closeDeleteDialog();
    } catch (err) {
      alert(err.response?.data?.detail || t("trips.errorLoading"));
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleUpdateDateWithError = async (tripId) => {
    try {
      await handleUpdateDate(tripId);
    } catch (err) {
      alert(err.response?.data?.detail || t("trips.errorLoading"));
    }
  };

  const handleDeleteStationWithError = async (linkId, tripId) => {
    try {
      await handleDeleteStation(linkId, tripId);
    } catch (err) {
      alert("Error deleting station.");
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
                <TripCard
                  key={trip.id}
                  trip={trip}
                  editableDates={editableDates}
                  onDateChange={handleDateChange}
                  onUpdateDate={handleUpdateDateWithError}
                  updateLoading={updateLoading}
                  stations={stationsByTrip[trip.id] || []}
                  onDeleteStation={handleDeleteStationWithError}
                  onAddStation={(tripId) => navigate(`/trips/${tripId}/add`)}
                  onReorderStations={(tripId) => navigate(`/trips/${tripId}/reorder`)}
                  onDeleteTrip={openDeleteDialog}
                  onGenerateTrip={(tripId) => navigate(`/trips/generate?tripId=${tripId}`)}
                  language={i18n.language}
                />
              ))}
            </Box>
          )}
        </Box>

        <DeleteTripDialog
          open={deleteDialogOpen}
          onClose={closeDeleteDialog}
          onConfirm={handleConfirmDelete}
          loading={deleteLoading}
        />
      </Box>
    </Box>
  );
}
