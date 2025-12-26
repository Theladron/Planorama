import { Typography, Box, Button } from "@mui/material";
import { useTranslation } from "react-i18next";
import { countryCodeToEmoji, getCountryCode } from "../../utils/countryUtils";

/**
 * Component to display list of stations for a trip
 */
export const StationList = ({ stations, onDeleteStation, tripId, language }) => {
  const { t } = useTranslation();

  if (!stations || stations.length === 0) {
    return <Typography sx={{ fontStyle: "italic" }}>{t("trips.noStations")}</Typography>;
  }

  return (
    <>
      {stations.map((station) => {
        const countryCode = getCountryCode(station.country);
        const flagEmoji = countryCodeToEmoji(countryCode);

        return (
          <Box key={station.link_id} sx={{ mb: 0.5 }}>
            <Typography sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <span>
                {flagEmoji}{" "}
                {language === "de" ? station.station_name_de : station.station_name}{" "}
                {station.city}
              </span>
              <Button
                onClick={() => onDeleteStation(station.link_id, tripId)}
                sx={{
                  minWidth: "auto",
                  p: 0.5,
                  ml: "auto",
                  backgroundColor: "transparent",
                  "&:hover": {
                    backgroundColor: "rgba(211, 47, 47, 0.1)",
                  },
                  fontSize: "1.5rem",
                  color: "#d32f2f",
                }}
              >
                🗑
              </Button>
            </Typography>
          </Box>
        );
      })}
    </>
  );
};

