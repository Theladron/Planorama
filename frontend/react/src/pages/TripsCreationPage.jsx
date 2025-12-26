import React, { useState } from "react";
import { Typography, Button, CircularProgress } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { createTrip } from "../api/tripApi";
import { validateDateRange } from "../utils/validation";
import { BackgroundBox } from "../components/common/BackgroundBox";
import { StyledCard } from "../components/common/StyledCard";
import { StyledTextField } from "../components/common/StyledTextField";
import { BackButton } from "../components/common/BackButton";

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

    if (!validateDateRange(startDate, endDate)) {
      setError(t("tripscreation.error_start_after_end"));
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await createTrip(tripName, startDate, endDate);
      navigate("/trips");
    } catch (err) {
      console.error("Failed to create trip:", err);
      setError(err.response?.data?.detail || t("tripscreation.error_generic"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <BackgroundBox>
      <StyledCard component="form" onSubmit={handleSubmit}>
        <Typography variant="h4" fontWeight="bold" mb={3} textAlign="center">
          {t("tripscreation.title")}
        </Typography>

        <StyledTextField
          label={t("tripscreation.label_trip_name")}
          fullWidth
          required
          value={tripName}
          onChange={(e) => setTripName(e.target.value)}
        />

        <StyledTextField
          label={t("tripscreation.label_start_date")}
          type="date"
          fullWidth
          required
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />

        <StyledTextField
          label={t("tripscreation.label_end_date")}
          type="date"
          fullWidth
          required
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          sx={{ mb: 4 }}
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
      </StyledCard>

      <BackButton />
    </BackgroundBox>
  );
}
