import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
} from "@mui/material";
import dayjs from "dayjs";
import { useTranslation } from "react-i18next";
import { StationList } from "./StationList";

/**
 * Trip card component displaying trip information and actions
 */
export const TripCard = ({
  trip,
  editableDates,
  onDateChange,
  onUpdateDate,
  updateLoading,
  stations,
  onDeleteStation,
  onAddStation,
  onReorderStations,
  onDeleteTrip,
  onGenerateTrip,
  language,
}) => {
  const { t } = useTranslation();

  return (
    <Card
      sx={{
        maxWidth: 270,
        backgroundColor: "rgba(250, 201, 72, 0.15)",
        backdropFilter: "blur(6px)",
        border: "1px solid rgba(250, 201, 72, 0.3)",
        borderRadius: "8px",
        boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.2)",
        fontFamily: "'Pacifico', cursive",
        textShadow: "2px 2px 6px rgba(0,0,0,0.6)",
        color: "#f0e6cc",
        display: "flex",
        flexDirection: "column",
        height: "100%",
        position: "relative",
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          {trip.trip_name}
        </Typography>
        <Typography variant="body2" sx={{ mb: 1, fontWeight: "bold" }}>
          {t("trips.createdAt", {
            date: dayjs(trip.created_at).format("YYYY-MM-DD"),
          })}
        </Typography>

        <TextField
          label={t("trips.startDate")}
          type="date"
          value={editableDates[trip.id]?.start_date || ""}
          onChange={(e) => onDateChange(trip.id, "start_date", e.target.value)}
          fullWidth
          InputLabelProps={{ shrink: true }}
          sx={{
            backgroundColor: "rgba(250, 201, 72, 0.3)",
            borderRadius: 1,
            mb: 1,
            input: { color: "#f0e6cc" },
            label: { color: "#f0e6cc" },
          }}
        />
        <TextField
          label={t("trips.endDate")}
          type="date"
          value={editableDates[trip.id]?.end_date || ""}
          onChange={(e) => onDateChange(trip.id, "end_date", e.target.value)}
          fullWidth
          InputLabelProps={{ shrink: true }}
          sx={{
            backgroundColor: "rgba(250, 201, 72, 0.3)",
            borderRadius: 1,
            input: { color: "#f0e6cc" },
            label: { color: "#f0e6cc" },
          }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={() => onUpdateDate(trip.id)}
          disabled={updateLoading[trip.id]}
          sx={{ mt: 1 }}
        >
          {updateLoading[trip.id] ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            t("trips.update")
          )}
        </Button>

        <Typography variant="subtitle1" sx={{ fontWeight: "bold", mt: 2, mb: 1 }}>
          {t("trips.stations")}
        </Typography>

        <StationList
          stations={stations}
          onDeleteStation={onDeleteStation}
          tripId={trip.id}
          language={language}
        />

        <Box sx={{ mt: 2, display: "flex", flexWrap: "wrap", gap: 1 }}>
          <Button
            fullWidth
            variant="contained"
            color="info"
            onClick={() => onAddStation(trip.id)}
            sx={{ flexBasis: "48%" }}
          >
            {t("trips.addStation")}
          </Button>
          <Button
            fullWidth
            variant="contained"
            color="info"
            onClick={() => onReorderStations(trip.id)}
            sx={{ flexBasis: "48%" }}
          >
            {t("trips.reorderStations")}
          </Button>
          <Button
            fullWidth
            variant="contained"
            color="error"
            onClick={() => onDeleteTrip(trip)}
            sx={{ flexBasis: "48%" }}
          >
            {t("trips.delete")}
          </Button>
          <Button
            fullWidth
            variant="contained"
            color="success"
            onClick={() => onGenerateTrip(trip.id)}
            sx={{ flexBasis: "48%" }}
          >
            {t("trips.showTrip")}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

