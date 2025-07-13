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
    <Box
      sx={{
        backgroundColor: "rgba(250, 201, 72, 0.2)",
        backdropFilter: "blur(4px)",
        border: "1px solid rgba(250, 201, 72, 0.25)",
        borderRadius: "12px",
        p: 2,
        color: "#f0e6cc",
        boxShadow: "0 6px 20px rgba(250, 201, 72, 0.1)",
        fontFamily: "'Pacifico', cursive",
        textShadow: "1px 1px 4px rgba(0, 0, 0, 0.5)",
      }}
    >
      <Box textAlign="center" mb={2}>
        <Typography variant="h6">
          {t("weatherwidget.current_weather")}
        </Typography>
        <Typography variant="h6">
           {current.temperature}°C {current.icon}
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.85 }}>
          {t(`weatherwidget.codes.${current.description.toLowerCase()}`, {
            defaultValue: current.description,
          })}
        </Typography>
      </Box>

      <Box textAlign="center" mb={3}>
        <Typography variant="subtitle1">{t("weatherwidget.today")}</Typography>

        <Typography variant="subtitle2">
          {today.temp_min}°C / {today.temp_max}°C {today.icon}
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.85 }}>
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

      <Grid container spacing={0.5} justifyContent="center">
        {forecast.map((day, index) => (
          <Grid item xs={6} sm={4} md={3} key={index}>
            <Card
              sx={{
                backgroundColor: "rgba(250, 201, 72, 0.15)",
                backdropFilter: "blur(3px)",
                border: "1px solid rgba(250, 201, 72, 0.2)",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
                borderRadius: "8px",
                color: "#f0e6cc",
              }}
            >
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
                  <Typography fontSize="1.6rem">{day.icon}</Typography>
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
