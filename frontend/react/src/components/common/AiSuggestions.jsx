import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import {
  Box,
  CircularProgress,
  Grid,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
} from "@mui/material";
import { useTranslation } from "react-i18next";

const AiSuggestionPage = ({ lat, lon, townName, language, contentType }) => {
  const { t } = useTranslation();
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!lat || !lon || !townName || !language || !contentType) return;

    const fetchSuggestions = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get("/api/ai-suggestions", {
          params: {
            lat,
            lon,
            town_name: townName,
            language,
            content_type: contentType,
          },
        });

        setSuggestions(response.data || []);
      } catch (err) {
        console.error("AI suggestion fetch error:", err);
        setError(t("ai_suggestions.fetch_error", { defaultValue: "Failed to fetch suggestions." }));
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
  }, [lat, lon, townName, language, contentType, t]);

  if (loading) {
    return (
      <Box textAlign="center" mt={2}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error" textAlign="center" mt={2}>
        {error}
      </Typography>
    );
  }

  if (!suggestions.length) {
    return (
      <Typography textAlign="center" mt={2}>
        {t("ai_suggestions.no_results", { defaultValue: "No suggestions found." })}
      </Typography>
    );
  }

  return (
    <Grid container spacing={2} mt={1}>
      {suggestions.map((item, index) => (
        <Grid item xs={12} sm={6} md={4} key={index}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {item.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {item.description}
              </Typography>
              {item.lat && item.lon && (
                <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                  📍 {item.lat.toFixed(4)}, {item.lon.toFixed(4)}
                </Typography>
              )}
            </CardContent>
            {item.url && (
              <CardActions>
                <Button size="small" color="primary" href={item.url} target="_blank" rel="noopener noreferrer">
                  {t("ai_suggestions.more_info", { defaultValue: "More Info" })}
                </Button>
              </CardActions>
            )}
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

AiSuggestions.propTypes = {
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  townName: PropTypes.string.isRequired,
  language: PropTypes.string.isRequired,
  contentType: PropTypes.string.isRequired,
};

export default AiSuggestions;
