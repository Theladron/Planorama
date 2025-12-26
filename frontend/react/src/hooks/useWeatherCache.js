import { useRef } from "react";
import { fetchWeather } from "../api/tripApi";

/**
 * Hook to manage weather data caching
 */
export const useWeatherCache = () => {
  const weatherCacheRef = useRef({});

  const getCachedWeatherForCoords = async (lat, lon) => {
    const key = `${lat.toFixed(4)}_${lon.toFixed(4)}`;
    if (weatherCacheRef.current[key]) return weatherCacheRef.current[key];
    const data = await fetchWeather(lat, lon);
    if (data) weatherCacheRef.current[key] = data;
    return data;
  };

  return { getCachedWeatherForCoords };
};

