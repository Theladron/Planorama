import React, { useContext, useState } from "react";
import { AppBar, Toolbar, Button, Box, Menu, MenuItem } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Navbar({ hasSidebar }) {
  const { isAuthenticated, user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const username = user?.username || "User";

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
            Home
          </Button>
        </Box>

        {!isAuthenticated && (
          <>
            <Button component={Link} to="/login" color="inherit">
              Login
            </Button>
            <Button component={Link} to="/register" color="inherit">
              Register
            </Button>
          </>
        )}

        {isAuthenticated && (
          <>
            <Button
              color="inherit"
              onClick={handleMenuOpen}
              sx={{ textTransform: "none", fontWeight: "bold" }}
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
                Dashboard
              </MenuItem>
              <MenuItem
                onClick={() => {
                  handleMenuClose();
                  navigate("/trips");
                }}
                sx={{ "&:hover": { bgcolor: "rgba(255, 255, 255, 0.1)" } }}
              >
                Trips
              </MenuItem>
              <MenuItem
                onClick={() => {
                  handleMenuClose();
                  navigate("/settings");
                }}
                sx={{ "&:hover": { bgcolor: "rgba(255, 255, 255, 0.1)" } }}
              >
                Settings
              </MenuItem>
              <MenuItem
                onClick={handleLogout}
                sx={{ "&:hover": { bgcolor: "rgba(255, 255, 255, 0.1)" } }}
              >
                Logout
              </MenuItem>
            </Menu>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}
