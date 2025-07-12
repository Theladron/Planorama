import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Box,
  Typography,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Tooltip,
} from "@mui/material";
import { useTranslation } from "react-i18next";

const WeatherWidget = ({ lat, lon, fetchCachedWeather }) => {
  const { t } = useTranslation();
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!lat || !lon) {
      setWeatherData(null);
      setLoading(false);
      return;
    }

    const fetchWeather = async () => {
      setLoading(true);
      try {
        let data;
        if (fetchCachedWeather) {
          data = await fetchCachedWeather(lat, lon);
        } else {
          // fallback: call API directly
          const response = await axios.get("/api/weather", {
            params: { lat, lon },
          });
          data = response.data;
        }
        setWeatherData(data);
      } catch (error) {
        console.error("Failed to fetch weather:", error);
        setWeatherData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, [lat, lon, fetchCachedWeather]);

  if (loading) {
    return (
      <Box textAlign="center" mt={2}>
        <CircularProgress />
      </Box>
    );
  }

  if (!weatherData) {
    return (
      <Typography color="error" textAlign="center">
        {t("weatherwidget.error_loading")}
      </Typography>
    );
  }

  const { current, today, forecast } = weatherData;

  return (
    <Box mt={2}>
      // Current Weather
      <Box textAlign="center" mb={2}>
        <Typography variant="h6">
          {t("weatherwidget.current_weather")} {current.icon} – {current.temperature}°C
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t(`weatherwidget.codes.${current.description.toLowerCase()}`, {
            defaultValue: current.description,
          })}
        </Typography>
      </Box>

      // Today Summary
      <Box textAlign="center" mb={3}>
        <Typography variant="subtitle1">{t("weatherwidget.today")}</Typography>

        <Typography variant="subtitle2">
          {today.temp_min}°C / {today.temp_max}°C {today.icon}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t("weatherwidget.sunrise")}:{" "}
          {new Date(today.sunrise).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}{" "}
          · {t("weatherwidget.sunset")}:{" "}
          {new Date(today.sunset).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Typography>
      </Box>

      // 7-Day Forecast
      <Grid container spacing={1}>
        {forecast.map((day, index) => (
          <Grid item xs={6} sm={4} md={3} key={index}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: "center", py: 1.5 }}>
                <Typography variant="subtitle2">
                  {new Date(day.date).toLocaleDateString(undefined, {
                    weekday: "short",
                  })}
                </Typography>
                <Tooltip
                  title={t(`weatherwidget.codes.${day.description.toLowerCase()}`, {
                    defaultValue: day.description,
                  })}
                >
                  <Typography fontSize="1.5rem">{day.icon}</Typography>
                </Tooltip>
                <Typography variant="body2">
                  {day.temp_min}° / {day.temp_max}°
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default WeatherWidget;
