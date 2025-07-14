import { backendURL } from "../config";
import React, { useContext, useState } from "react";
import { AppBar, Toolbar, Button, Box, Menu, MenuItem, IconButton } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import axios from "axios";

const flagStyles = {
  fontSize: "1.5rem",
  cursor: "pointer",
  mr: 5,
  "&:hover": { backgroundColor: "rgba(255, 255, 255, 0.1)" },
};

export default function Navbar({ hasSidebar }) {
  const { isAuthenticated, user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const username = user?.username || "User";

  // Change language locally & (if logged in) on backend
  const changeLanguage = async (lng) => {
    if (lng === i18n.language) return; // no change

    try {
      await i18n.changeLanguage(lng);

      if (isAuthenticated) {
        // Update backend user language preference
        await axios.patch(`${backendURL}/api/users/me/language`, {
          language_preference: lng,
        });
      }
    } catch (err) {
      console.error("Failed to change language:", err);
    }
  };

  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate("/login");
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        left: hasSidebar ? "200px" : 0,
        width: hasSidebar ? "calc(100% - 200px)" : "100%",
        background: `linear-gradient(to bottom, rgba(0,0,0,0.85), rgba(0,0,0,0.4))`,
        backdropFilter: "blur(4px)",
        transition: "all 0.3s ease",
      }}
    >
      <Toolbar>
        <Box sx={{ flexGrow: 1 }}>
          <Button
            component={Link}
            to="/"
            color="inherit"
            sx={{ fontWeight: "bold", fontSize: "1.2rem" }}
          >
            {t("navbar.home")}
          </Button>
        </Box>


          <>
            {/* Flags left of Register button */}
            <IconButton
              aria-label={t("navbar.language_en")}
              onClick={() => changeLanguage("en")}
              sx={{ ...flagStyles, mr: 0 }}
              size="large"
            >
              🇬🇧
            </IconButton>
            <IconButton
              aria-label={t("navbar.language_de")}
              onClick={() => changeLanguage("de")}
              sx={flagStyles}
              size="large"
            >
              🇩🇪
            </IconButton>

            {!isAuthenticated && (
  <>
    <Button component={Link} to="/login" color="inherit">
      {t("navbar.login")}
    </Button>
    <Button component={Link} to="/register" color="inherit">
      {t("navbar.register")}
    </Button>
  </>
)}
          </>


        {isAuthenticated && (
          <>
            <Button
              color="inherit"
              onClick={handleMenuOpen}
              sx={{ textTransform: "none", fontWeight: "bold", color: "#f7d425" }}
            >
              {username}
            </Button>
            <Menu
              anchorEl={anchorEl}
              open={open}
              onClose={handleMenuClose}
              PaperProps={{
                sx: {
                  bgcolor: "rgba(0,0,0,0.85)",
                  color: "#fff",
                  minWidth: 150,
                  borderRadius: 1,
                  boxShadow: "0 4px 20px rgba(0,0,0,0.7)",
                },
              }}
              anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
              transformOrigin={{ vertical: "top", horizontal: "right" }}
            >
              <MenuItem
                onClick={() => {
                  handleMenuClose();
                  navigate("/dashboard");
                }}
                sx={{ "&:hover": { bgcolor: "rgba(255, 255, 255, 0.1)" } }}
              >
                {t("navbar.dashboard")}
              </MenuItem>
              <MenuItem
                onClick={() => {
                  handleMenuClose();
                  navigate("/trips");
                }}
                sx={{ "&:hover": { bgcolor: "rgba(255, 255, 255, 0.1)" } }}
              >
                {t("navbar.trips")}
              </MenuItem>
              <MenuItem
                onClick={() => {
                  handleMenuClose();
                  navigate("/settings");
                }}
                sx={{ "&:hover": { bgcolor: "rgba(255, 255, 255, 0.1)" } }}
              >
                {t("navbar.settings")}
              </MenuItem>
              <MenuItem
                onClick={handleLogout}
                sx={{ "&:hover": { bgcolor: "rgba(255, 255, 255, 0.1)" } }}
              >
                {t("navbar.logout")}
              </MenuItem>
            </Menu>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}
