import React, { useState } from "react";
import { Typography, Button, CircularProgress, Alert, TextField, MenuItem, Snackbar } from "@mui/material";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useTrip } from "../hooks/useTrip";
import { useStations } from "../hooks/useStations";
import { createStation } from "../api/stationApi";
import { getAvailableDays } from "../utils/dateUtils";
import { BackgroundBox } from "../components/common/BackgroundBox";
import { StyledCard } from "../components/common/StyledCard";
import { StyledTextField } from "../components/common/StyledTextField";
import { BackButton } from "../components/common/BackButton";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

export default function AddStationPage() {
  const { t } = useTranslation();
  const { tripId } = useParams();

  const { trip, loading: tripLoading, error: tripError } = useTrip(tripId);
  const { stations, refreshStations } = useStations(tripId);

  const [townName, setTownName] = useState("");
  const [selectedDay, setSelectedDay] = useState("");
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const availableDays = trip ? getAvailableDays(trip, stations) : [];

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
      await createStation(tripId, townName, selectedDay);
      setSubmitSuccess(true);
      setTownName("");
      setSelectedDay("");
      refreshStations();
    } catch (err) {
      setSubmitError(err.response?.data?.detail || t("addstation.error_submitFailed"));
    } finally {
      setSubmitLoading(false);
    }
  };

  if (tripLoading) {
    return <LoadingSpinner />;
  }

  if (tripError) {
    return (
      <BackgroundBox>
        <Alert severity="error">{tripError}</Alert>
      </BackgroundBox>
    );
  }

  return (
    <BackgroundBox>
      <StyledCard width={380} component="form" onSubmit={handleSubmit} sx={{ p: 4 }}>
        <Typography variant="h4" fontWeight="bold" mb={3} textAlign="center" sx={{ userSelect: "none" }}>
          {t("addstation.title", { tripName: trip.trip_name })}
        </Typography>

        <StyledTextField
          label={t("addstation.townName_label")}
          fullWidth
          value={townName}
          onChange={(e) => setTownName(e.target.value)}
          margin="normal"
          disabled={submitLoading}
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
          <Alert onClose={() => setSubmitSuccess(false)} severity="success" sx={{ width: "100%" }}>
            {t("addstation.success_stationAdded")}
          </Alert>
        </Snackbar>
      </StyledCard>

      <BackButton />
    </BackgroundBox>
  );
}
