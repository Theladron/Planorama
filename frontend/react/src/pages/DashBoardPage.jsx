import React from "react";
import { Box, Typography, Link as MuiLink, CircularProgress } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import dayjs from "dayjs";
import { useTranslation } from "react-i18next";
import Sidebar from "../components/Sidebar";
import { useTrips } from "../hooks/useTrips";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

export default function DashboardPage() {
  const { user } = useContext(AuthContext);
  const { t } = useTranslation();
  const { trips, loading } = useTrips();

  const nextTrip = trips
    .filter((trip) => dayjs(trip.start_date).isAfter(dayjs()))
    .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))[0];

  const tripSoon = nextTrip && dayjs(nextTrip.start_date).diff(dayjs(), "day") < 7;

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          height: "100vh",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#000000cc",
          color: "#fff",
        }}
      >
        <CircularProgress color="inherit" />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        backgroundImage: "url('/images/home_background.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        position: "relative",
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
      <Sidebar />

      <Box
        component="main"
        sx={{
          ml: "320px",
          mt: "180px",
          pr: 4,
          pb: 4,
          flexGrow: 1,
          position: "relative",
          zIndex: 1,
          color: "#fff",
          textAlign: "left",
          maxWidth: "900px",
        }}
      >
        <Typography
          variant="h3"
          sx={{
            fontFamily: "'Dancing Script', cursive",
            fontWeight: 600,
            fontSize: "3rem",
            mb: 3,
            textShadow: "2px 2px 8px rgba(0,0,0,0.6)",
          }}
        >
          {t("dashboard.welcome", { username: user.username })}
        </Typography>

        {trips.length === 0 ? (
          <Typography variant="h6" sx={{ mt: 2 }}>
            {t("dashboard.no_trips")}{" "}
            <MuiLink
              component={RouterLink}
              to="/trips/create"
              sx={{ color: "#f0e6cc", fontWeight: "bold" }}
            >
              {t("dashboard.plan_link")}
            </MuiLink>
          </Typography>
        ) : tripSoon ? (
          <Typography variant="h6" sx={{ mt: 2 }}>
            {t("dashboard.trip_soon", {
              tripName: nextTrip.trip_name,
              date: dayjs(nextTrip.start_date).format("MMMM D, YYYY"),
            })}
          </Typography>
        ) : (
          <Typography variant="h6" sx={{ mt: 2 }}>
            {t("dashboard.no_upcoming")}
          </Typography>
        )}
      </Box>
    </Box>
  );
}
