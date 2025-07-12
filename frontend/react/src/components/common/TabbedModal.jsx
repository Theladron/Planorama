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

const MultiTabModal = ({
  open,
  onClose,
  stationName,
  visitDay,
  weatherWidget,
  overnightOptions = [],
  activityOptions = [],
  onActivitySearch,
}) => {
  const [tabIndex, setTabIndex] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [activityInput, setActivityInput] = useState("");
  const { t } = useTranslation();

  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };

  const handleActivityInput = (e) => {
    const value = e.target.value;
    setActivityInput(value);
    onActivitySearch?.(value);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="md"
      aria-labelledby="station-details-dialog"
    >
      <DialogTitle sx={{ m: 0, p: 2 }}>
        <Typography variant="h6">{stationName}</Typography>
        <IconButton
          aria-label={t("tabbedmodal.close")}
          onClick={onClose}
          sx={{
            position: "absolute",
            right: 16,
            top: 16,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        <Tabs
          value={tabIndex}
          onChange={handleTabChange}
          aria-label={t("tabbedmodal.tabsAria")}
          variant="fullWidth"
        >
          <Tab label={t("tabbedmodal.overview")} id="tab-0" />
          <Tab label={t("tabbedmodal.overnight")} id="tab-1" />
          <Tab label={t("tabbedmodal.activities")} id="tab-2" />
        </Tabs>

        <TabPanel value={tabIndex} index={0}>
          <Typography variant="subtitle1" gutterBottom>
            {t("tabbedmodal.visitDay")} <strong>{visitDay}</strong>
          </Typography>
          <Box mt={2}>{weatherWidget}</Box>
        </TabPanel>

        <TabPanel value={tabIndex} index={1}>
          <TextField
            select
            label={t("tabbedmodal.selectStay")}
            fullWidth
            margin="normal"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <MenuItem value="hotel">{t("tabbedmodal.hotel")}</MenuItem>
            <MenuItem value="hostel">{t("tabbedmodal.hostel")}</MenuItem>
            <MenuItem value="camping">{t("tabbedmodal.camping")}</MenuItem>
          </TextField>

          {overnightOptions.map((option, index) => (
            <Box key={index} mt={2}>
              <Typography variant="subtitle2">{option.title}</Typography>
              <Typography variant="body2">{option.description}</Typography>
              <Link href={option.link} target="_blank" rel="noopener">
                {t("tabbedmodal.visitLink")}
              </Link>
            </Box>
          ))}
        </TabPanel>

        <TabPanel value={tabIndex} index={2}>
          <TextField
            label={t("tabbedmodal.interestPrompt")}
            fullWidth
            margin="normal"
            value={activityInput}
            onChange={handleActivityInput}
            placeholder={t("tabbedmodal.interestPlaceholder")}
          />
          {activityOptions.map((activity, index) => (
            <Box key={index} mt={2}>
              <Typography variant="subtitle2">{activity.title}</Typography>
              <Typography variant="body2">{activity.description}</Typography>
            </Box>
          ))}
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
};

export default MultiTabModal;
