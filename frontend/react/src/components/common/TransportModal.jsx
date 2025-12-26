import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Tabs,
  Tab,
  IconButton,
  Typography,
  Box,
  Button,
  Stack,
  CircularProgress,
  Card,
  CardContent,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useTranslation } from "react-i18next";

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index} id={`tabpanel-${index}`}>
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

const cardStyle = {
  backgroundColor: "rgba(250, 201, 72, 0.3)", // less transparent than before
  backdropFilter: "blur(6px)",
  border: "1px solid rgba(250, 201, 72, 0.4)",
  borderRadius: "12px",
  boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.25)",
  color: "#f0e6cc",
  mb: 2,
};

const TransportModal = ({
  open,
  onClose,
  turnByTurnDirections = [],  // Array of strings for car directions
  estimatedTime = "",         // String for estimated trip duration
  publicTransportRoutes = [],
  planeRoutes: _planeRoutes = [],
  canUsePlane: _canUsePlane = false,
  onSearchPublicTransport,
  onSearchPlane: _onSearchPlane,
  loadingPublicTransport = false,
  loadingPlane: _loadingPlane = false,
  hasSearchedPublicTransport = false,
}) => {
  const { t } = useTranslation();
  const [tabIndex, setTabIndex] = useState(0);  // Always default to car tab

  const handleTabChange = (event, newValue) => setTabIndex(newValue);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="md"
      PaperProps={{
        sx: {
          backgroundColor: "rgba(250, 201, 72, 0.15)",
          backdropFilter: "blur(6px)",
          border: "1px solid rgba(72, 201, 250, 0.3)",
          borderRadius: "12px",
          boxShadow: "0 8px 32px 0 rgba(72, 201, 250, 0.2)",
          color: "#e0f7fa",
        },
      }}
    >
      <DialogTitle sx={{ position: "relative", pr: 6 }}>
        <Typography textAlign="center" sx={{ mb: 1 }}>
          {t("transportModal.title", "Transport Options")}
        </Typography>
        <IconButton
          aria-label={t("transportModal.close", "Close")}
          onClick={onClose}
          sx={{ position: "absolute", right: 16, top: 16, color: "#e0f7fa" }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        <Tabs
          value={tabIndex}
          onChange={handleTabChange}
          variant="fullWidth"
          textColor="inherit"
          TabIndicatorProps={{ sx: { backgroundColor: "#e0f7fa" } }}
          sx={{
            "& .MuiTab-root": { color: "#e0f7fa" },
            "& .Mui-selected": { fontWeight: "bold" },
          }}
        >
          <Tab label={t("transportModal.car", "Car")} />
          <Tab label={t("transportModal.publicTransport", "Public Transport")} />
        </Tabs>

        {/* CAR ROUTES / DIRECTIONS */}
        <TabPanel value={tabIndex} index={0}>
          <Card sx={cardStyle}>
            <CardContent>
              {estimatedTime && (
                <Typography variant="body1" fontWeight="bold" textAlign="center" mb={2}>
                  {t("transportModal.estimatedTime", "Estimated Time")}: {estimatedTime}
                </Typography>
              )}

              {turnByTurnDirections.length === 0 ? (
                <Typography textAlign="center" mt={2}>
                  {t("transportModal.noCarRoutes", "No car directions available.")}
                </Typography>
              ) : (
                <Box sx={{ pl: 2 }}>
                  <Typography variant="body2" fontWeight="bold" mb={1}>
                    {t("transportModal.turnByTurn", "Turn-by-turn Directions")}:
                  </Typography>
                  {turnByTurnDirections.map((step, i) => (
                    <Typography
                      key={i}
                      variant="body2"
                      component="p"
                      sx={{ ml: 1, mb: 0.5 }}
                    >
                      {step.instruction} {step.distance ? `(${step.distance})` : ""}{" "}
                      {step.name ? `- ${step.name}` : ""}
                    </Typography>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </TabPanel>

        {/* PUBLIC TRANSPORT */}
        <TabPanel value={tabIndex} index={1}>
          <Box display="flex" justifyContent="center" mb={2}>
            <Button
              variant="contained"
              onClick={onSearchPublicTransport}
              disabled={loadingPublicTransport}
            >
              {loadingPublicTransport ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                t("transportModal.searchPublicTransport", "Search Public Transport")
              )}
            </Button>
          </Box>

          {loadingPublicTransport ? (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    mt={4}
    mb={2}
  >
    <Typography variant="body2" sx={{ mb: 2 }}>
      {t("transportModal.loading", "Loading...")}
    </Typography>
    <CircularProgress color="inherit" />
  </Box>
) : hasSearchedPublicTransport && publicTransportRoutes.length === 0 ? (
  <Typography textAlign="center" mt={2}>
    {t("transportModal.noPublicTransportRoutes", "No public transport routes available.")}
  </Typography>
          ) : (
            publicTransportRoutes.map((route, idx) => (
              <Card key={idx} sx={cardStyle}>
                <CardContent>
                  {/* Method of Transport */}
                  <Typography variant="subtitle1" fontWeight="bold">
                    {route.method_of_transport?.toUpperCase() || t("transportModal.unknownTransport", "Unknown Transport")}
                  </Typography>

                  {/* Description */}
                  {route.description && (
                    <Typography variant="body2" mt={0.5}>
                      {route.description}
                    </Typography>
                  )}

                  {/* URL */}
                  {route.url && (
                    <Typography variant="body2" mt={1}>
                      🔗{" "}
                      <a
                        href={route.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "#90caf9", textDecoration: "underline" }}
                      >
                        {t("transportModal.viewDetails", "View Details / Tickets")}
                      </a>
                    </Typography>
                  )}

                  {/* Departure Time */}
                  {route.departure_time && (
                    <Typography variant="body2" mt={1}>
                      🕒 {t("transportModal.departure", "Departure")}: {route.departure_time}
                    </Typography>
                  )}

                  {/* Price */}
                  {route.price && (
                    <Typography variant="body2" mt={1}>
                      💶 {t("transportModal.price", "Price")}: {route.price}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
};

export default TransportModal;
