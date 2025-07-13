import { backendURL } from "../config";
import React from "react";
import { Box, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";


export default function HomePage() {

  const { t } = useTranslation();
  return (
    <Box
      sx={{
        height: "100vh",
        backgroundImage: "url('/images/home_background.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        fontFamily: "'Pacifico', cursive",
        px: 2,
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.4)", // semi-transparent overlay
          zIndex: 1,
        },
        zIndex: 2,
        color: "#fff",
      }}
    >
      <Box sx={{ position: "relative", zIndex: 3 }}>
        <Typography variant="h3" gutterBottom sx={{ fontFamily: "'Pacifico', cursive", textShadow: "2px 2px 8px rgba(0,0,0,0.6)", }}>
          {t('home.title')}
        </Typography>
        <Typography variant="h6" paragraph sx={{ maxWidth: "600px", textShadow: "2px 2px 8px rgba(0,0,0,0.6)", }}>
          {t('home.subtitle')}
        </Typography>
        <Typography variant="h6" paragraph>
          <Link
            to="/register"
            style={{
              textDecoration: "none",
              color: "#90caf9",
              fontWeight: "bold",
            }}
          >
            {t('home.register_link')}
          </Link>
        </Typography>
      </Box>
    </Box>
  );
}
