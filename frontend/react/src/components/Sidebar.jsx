import React, { useContext } from "react";
import { Box, Link as MuiLink } from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useTranslation } from "react-i18next";

export default function Sidebar() {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
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
        <MuiLink
          component={RouterLink}
          to="/trips"
          underline="none"
          sx={linkStyle}
        >
          {t("sidebar.trips")}
        </MuiLink>
      </Box>

      <Box sx={{ mb: 2 }}>
        <MuiLink
          component={RouterLink}
          to="/settings"
          underline="none"
          sx={linkStyle}
        >
          {t("sidebar.settings")}
        </MuiLink>
        <MuiLink
          component="button"
          underline="none"
          onClick={handleLogout}
          sx={{ ...linkStyle, cursor: "pointer" }}
        >
          {t("sidebar.logout")}
        </MuiLink>
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
