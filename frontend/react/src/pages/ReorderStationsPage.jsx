import React, { useState, useEffect } from "react";
import { Typography, Button, CircularProgress, Alert, TextField, MenuItem, Snackbar } from "@mui/material";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useTrip } from "../hooks/useTrip";
import { useStations } from "../hooks/useStations";
import { reorderStations } from "../api/stationApi";
import { getTripDays, hasDuplicates } from "../utils/dateUtils";
import { BackgroundBox } from "../components/common/BackgroundBox";
import { StyledCard } from "../components/common/StyledCard";
import { BackButton } from "../components/common/BackButton";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

export default function ReorderStationsPage() {
  const { t } = useTranslation();
  const { tripId } = useParams();

  const { trip, loading: tripLoading, error: tripError } = useTrip(tripId);
  const { stations, setStations } = useStations(tripId);

  const [dayAssignments, setDayAssignments] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);

  useEffect(() => {
    if (stations.length > 0) {
      const initialAssignments = {};
      stations.forEach((s) => {
        initialAssignments[s.link_id] = String(s.day_number);
      });
      setDayAssignments(initialAssignments);
    }
  }, [stations]);

  const tripDays = trip ? getTripDays(trip) : [];

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
      const updatedStations = await reorderStations(
        tripId,
        Object.entries(dayAssignments).map(([link_id, day]) => ({
          link_id: Number(link_id),
          day_number: Number(day),
        }))
      );
      setStations(updatedStations);
      setSubmitSuccess(true);
    } catch (err) {
      setSubmitError(err.response?.data?.detail || t("reorderstations.error_generic"));
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
      <StyledCard width={420} sx={{ p: 4 }}>
        <Typography variant="h4" fontWeight="bold" mb={3} textAlign="center" sx={{ userSelect: "none" }}>
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
          <Alert onClose={() => setSubmitSuccess(false)} severity="success" sx={{ width: "100%" }}>
            {t("reorderstations.success_message")}
          </Alert>
        </Snackbar>
      </StyledCard>

      <BackButton />
    </BackgroundBox>
  );
}
