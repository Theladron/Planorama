import React, { useContext, useEffect, useState } from "react";
import { Box, Typography, Link as MuiLink, CircularProgress } from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import axios from "axios";
import dayjs from "dayjs";

export default function DashboardPage() {
  const { logout, user } = useContext(AuthContext);
  const navigate = useNavigate();

  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const response = await axios.get("/api/trips/me");
        setTrips(response.data);
      } catch (error) {
        console.error("Error fetching trips:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTrips();
  }, []);

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
      {/* Sidebar */}
      <Box
        component="nav"
        sx={{
          width: 200,
          bgcolor: "rgba(0, 0, 0, 0.85)",
          color: "#fff",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          p: 2,
          pt: 10,
          position: "fixed",
          top: 0,
          left: 0,
          bottom: 0,
          boxShadow: "2px 0 8px rgba(0,0,0,0.8)",
          zIndex: 1100,
        }}
      >
        <Box>
          <MuiLink component={RouterLink} to="/trips" underline="none" sx={linkStyle}>
            Trips
          </MuiLink>
        </Box>

        <Box sx={{ mb: 2 }}>
            <MuiLink component={RouterLink} to="/settings" underline="none" sx={linkStyle}>
          Settings
          </MuiLink>
          <MuiLink
            component="button"
            underline="none"
            onClick={handleLogout}
            sx={{ ...linkStyle, cursor: "pointer" }}
          >
            Logout
          </MuiLink>
        </Box>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          ml: "320px", // Added margin-left more than sidebar width for breathing room
          mt: "180px",  // Top margin to push content down below navbar if needed
          pr: 4,
          pb: 4,
          flexGrow: 1,
          position: "relative",
          zIndex: 1,
          color: "#fff",
          textAlign: "left", // Align text left explicitly
          maxWidth: "900px", // Optional max width for better readability
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
          Welcome, {user?.username}.
        </Typography>

        {trips.length === 0 ? (
          <Typography variant="h6" sx={{ mt: 2 }}>
            You have not added any trips yet.{" "}
            <MuiLink
              component={RouterLink}
              to="/trips/new"
              sx={{ color: "#f0e6cc", fontWeight: "bold" }}
            >
              Do you want to plan a new vacation trip?
            </MuiLink>
          </Typography>
        ) : tripSoon ? (
          <Typography variant="h6" sx={{ mt: 2 }}>
            Your vacation trip <strong>{nextTrip.trip_name}</strong> is coming up on{" "}
            <strong>{dayjs(nextTrip.start_date).format("MMMM D, YYYY")}</strong>. Are you excited
            yet?
          </Typography>
        ) : (
          <Typography variant="h6" sx={{ mt: 2 }}>
            None of your trips are coming up soon. Still more time to plan and get excited!
          </Typography>
        )}
      </Box>
    </Box>
  );
}

const linkStyle = {
  display: "block",
  mb: 2,
  color: "#fff",
  fontWeight: "bold",
  "&:hover": { color: "#f0e6cc" },
};
