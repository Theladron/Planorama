import { backendURL } from "../../config";
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
  TextField,
  MenuItem,
  Link,
  Button,
  Stack,
  CircularProgress,
  Paper,
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

const glassCardStyles = {
  backgroundColor: "rgba(250, 201, 72, 0.3)",
  backdropFilter: "blur(6px)",
  border: "1px solid rgba(250, 201, 72, 0.4)",
  borderRadius: "12px",
  boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.25)",
  color: "#f0e6cc",
  padding: 2,
  mb: 2,
  minWidth: 0,
};

const MultiTabModal = ({
  open,
  onClose,
  stationName,
  visitDay,
  weatherWidget,
  overnightOptions = [],
  activityOptions = [],
  overnightLoading = false,  // ✅ updated name
  activityLoading = false,   // ✅ updated name
  onActivitySubmit,
  onOvernightCategoryChange,
}) => {
  const [tabIndex, setTabIndex] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [activityInput, setActivityInput] = useState("");
  const { t } = useTranslation();

  const handleTabChange = (event, newValue) => setTabIndex(newValue);

  const handleActivitySearchClick = () => {
    if (activityInput.trim()) onActivitySubmit?.(activityInput);
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
  };

  const handleOvernightSubmit = () => {
    if (selectedCategory) {
      onOvernightCategoryChange?.(selectedCategory);
    }
  };

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
          border: "1px solid rgba(250, 201, 72, 0.3)",
          borderRadius: "12px",
          boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.2)",
          textShadow: "2px 2px 6px rgba(0,0,0,0.6)",
          color: "#f0e6cc",
        },
      }}
    >
      <DialogTitle sx={{ position: "relative", display: "flex", alignItems: "center", pr: 6 }}>
        <Typography variant="h7">
          {t("tabbedmodal.visitDay")} {visitDay}
        </Typography>
        <Typography sx={{ position: "absolute", left: "50%", transform: "translateX(-50%)" }}>
          {stationName}
        </Typography>
        <IconButton
          aria-label={t("tabbedmodal.close")}
          onClick={onClose}
          sx={{ position: "absolute", right: 16, top: 16, color: "#f0e6cc" }}
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
          TabIndicatorProps={{ sx: { backgroundColor: "#f0e6cc" } }}
          sx={{
            "& .MuiTab-root": { color: "#f0e6cc" },
            "& .Mui-selected": { fontWeight: "bold" },
          }}
        >
          <Tab label={t("tabbedmodal.overview")} />
          <Tab label={t("tabbedmodal.overnight")} />
          <Tab label={t("tabbedmodal.activities")} />
        </Tabs>

        <TabPanel value={tabIndex} index={0}>
          <Box mt={2}>{weatherWidget}</Box>
        </TabPanel>

        <TabPanel value={tabIndex} index={1}>
          <Stack direction="row" spacing={2} alignItems="center" mt={1} mb={2}>
            <TextField
              select
              label={t("tabbedmodal.selectStay")}
              value={selectedCategory}
              onChange={handleCategoryChange}
              sx={{ flexGrow: 1 }}
              InputLabelProps={{ sx: { color: "#f0e6cc" } }}
              InputProps={{
                sx: {
                  color: "#f0e6cc",
                  "& .MuiSelect-icon": { color: "#f0e6cc" },
                },
              }}
            >
              <MenuItem value="hotel">{t("tabbedmodal.hotel")}</MenuItem>
              <MenuItem value="hostel">{t("tabbedmodal.hostel")}</MenuItem>
              <MenuItem value="camping">{t("tabbedmodal.camping")}</MenuItem>
              <MenuItem value="rbnb">{t("tabbedmodal.rbnb")}</MenuItem>
            </TextField>
            <Button
              variant="contained"
              onClick={handleOvernightSubmit}
              disabled={!selectedCategory || overnightLoading}
            >
              {overnightLoading ? <CircularProgress size={20} color="inherit" /> : t("tabbedmodal.search")}
            </Button>
          </Stack>

          {overnightLoading ? (
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              mt={4}
              mb={2}
            >
              <Typography variant="body2" sx={{ color: "#f0e6cc", mb: 2 }}>
                {t("tabbedmodal.loadingSuggestions")}
              </Typography>
              <CircularProgress color="inherit" />
            </Box>
          ) : (
            overnightOptions.map((option, idx) => (
              <Paper key={idx} sx={{ ...glassCardStyles, mt: 2 }}>
                <Link href={option.url} target="_blank" rel="noopener" underline="hover" color="#f0e6cc" sx={{ fontSize: '1.2rem' }}>
                  {option.title}
                </Link>
                <Typography variant="body2" sx={{ mb: 1 }}>{option.description}</Typography>

              </Paper>
            ))
          )}
        </TabPanel>

        <TabPanel value={tabIndex} index={2}>
          <Stack direction="row" spacing={1}>
            <TextField
              label={t("tabbedmodal.interestPrompt")}
              fullWidth
              value={activityInput}
              onChange={(e) => setActivityInput(e.target.value)}
              placeholder={t("tabbedmodal.interestPlaceholder")}
              InputLabelProps={{ sx: { color: "#f0e6cc" } }}
              InputProps={{ sx: { color: "#f0e6cc" } }}
            />
            <Button
              variant="contained"
              onClick={handleActivitySearchClick}
              disabled={activityLoading}
            >
              {activityLoading ? <CircularProgress size={20} color="inherit" /> : t("tabbedmodal.search")}
            </Button>
          </Stack>

          {activityLoading ? (
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              mt={4}
              mb={2}
            >
              <Typography variant="body2" sx={{ color: "#f0e6cc", mb: 2 }}>
                {t("tabbedmodal.loadingSuggestions")}
              </Typography>
              <CircularProgress color="inherit" />
            </Box>
          ) : (
            activityOptions.map((activity, idx) => (
              <Paper key={idx} sx={{ ...glassCardStyles, mt: 2 }}>
                <Link href={activity.url} target="_blank" rel="noopener" underline="hover" color="#f0e6cc" sx={{ fontSize: '1.2rem' }}>
                  {activity.title}
                </Link>

                <Typography variant="body2" sx={{ mb: 1 }}>{activity.description}</Typography>

              </Paper>
            ))
          )}
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
};

export default MultiTabModal;
