import { backendURL } from "../../config";
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
        const response = await axios.get(`${backendURL}/api/ai-suggestions`, {
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
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          bgcolor: "black",
        }}
      >
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
          <Card style={{
                backgroundColor: "rgba(250, 201, 72, 0.15)",
                backdropFilter: "blur(3px)",
                border: "1px solid rgba(250, 201, 72, 0.2)",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
                borderRadius: "8px",
                color: "#f0e6cc",
              }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {item.title}
              </Typography>
              <Typography variant="body2">
                {item.description}
              </Typography>
              {item.lat && item.lon && (
                <Typography variant="caption" display="block" mt={1}>
                  📍 {item.lat.toFixed(4)}, {item.lon.toFixed(4)}
                </Typography>
              )}
            </CardContent>
            {item.url && (
              <CardActions>
                <Button size="small" href={item.url} target="_blank" rel="noopener noreferrer">
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
