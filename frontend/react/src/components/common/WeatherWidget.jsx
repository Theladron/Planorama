import { backendURL } from "../../config";
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
          const response = await axios.get(`${backendURL}/api/weather`, {
            params: { lat, lon },
          });
          data = response.data;
        }
        setWeatherData(data);
      } catch {
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

      <Box
  display="flex"
  justifyContent="space-between"
  flexWrap="nowrap"
  overflowX="auto"
  gap={0.5}
  mt={2}
>
  {forecast.slice(0, 6).map((day, index) => (
    <Box
      key={index}
      sx={{
        flex: "0 0 16%", // force 6 per row
        minWidth: 0,
      }}
    >
      <Card
        sx={{
          backgroundColor: "rgba(250, 201, 72, 0.15)",
          backdropFilter: "blur(3px)",
          border: "1px solid rgba(250, 201, 72, 0.2)",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
          borderRadius: "8px",
          color: "#f0e6cc",
          height: "100%",
        }}
      >
        <CardContent sx={{ textAlign: "center", py: 1 }}>
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
    </Box>
  ))}
</Box>
    </Box>
  );
};

export default WeatherWidget;
