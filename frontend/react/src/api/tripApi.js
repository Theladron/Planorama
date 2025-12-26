import axios from "axios";
import { backendURL } from "../config";

/**
 * Fetch AI suggestions for activities or overnight stays
 */
export const fetchAISuggestions = async ({ lat, lon, townName, language, contentType }) => {
  try {
    const res = await axios.get(`${backendURL}/api/ai-suggestions`, {
      params: { lat, lon, town_name: townName, language, content_type: contentType },
    });
    return res.data || [];
  } catch (err) {
    console.error("AI suggestion fetch error:", err);
    return [];
  }
};

/**
 * Fetch AI transport route suggestions
 */
export const fetchAiTransportRoutes = async ({ startLat, startLon, startCity, endLat, endLon, endCity, language }) => {
  try {
    const response = await axios.get(`${backendURL}/api/ai-transport`, {
      params: {
        start_lat: startLat,
        start_lon: startLon,
        start_city: startCity,
        end_lat: endLat,
        end_lon: endLon,
        end_city: endCity,
        language,
      },
    });
    return response.data || [];
  } catch (err) {
    console.error("AI transport fetch error:", err);
    throw err;
  }
};

/**
 * Fetch weather data for coordinates
 */
export const fetchWeather = async (lat, lon) => {
  try {
    const res = await axios.get(`${backendURL}/api/weather`, { params: { lat, lon } });
    return res.data;
  } catch (err) {
    console.error("Weather fetch error:", err);
    return null;
  }
};

/**
 * Fetch stations by trip ID
 */
export const fetchStationsByTrip = async (tripId) => {
  const res = await axios.get(`${backendURL}/api/stations/by-trip/${tripId}`);
  return res.data;
};

/**
 * Fetch travels by trip ID
 */
export const fetchTravelsByTrip = async (tripId) => {
  const res = await axios.get(`${backendURL}/api/travel/trip/${tripId}`);
  return res.data;
};

/**
 * Fetch full route by coordinates
 */
export const fetchFullRouteByCoords = async ({ startLat, startLon, endLat, endLon }) => {
  const res = await axios.get(`${backendURL}/api/full-route-by-coords`, {
    params: {
      start_lat: startLat,
      start_lon: startLon,
      end_lat: endLat,
      end_lon: endLon,
    },
  });
  return res.data;
};

/**
 * Fetch user's trips
 */
export const fetchUserTrips = async () => {
  const res = await axios.get(`${backendURL}/api/trips/me`);
  return res.data;
};

/**
 * Fetch trip by ID
 */
export const fetchTripById = async (tripId) => {
  const res = await axios.get(`${backendURL}/api/trips/${tripId}`);
  return res.data;
};

/**
 * Create a new trip
 */
export const createTrip = async (tripName, startDate, endDate) => {
  const res = await axios.post(`${backendURL}/api/trips/`, {
    trip_name: tripName,
    start_date: startDate,
    end_date: endDate,
  });
  return res.data;
};

/**
 * Update trip dates
 */
export const updateTripDates = async (tripId, startDate, endDate) => {
  const res = await axios.put(`${backendURL}/api/trips/${tripId}`, {
    start_date: startDate,
    end_date: endDate,
  });
  return res.data;
};

/**
 * Delete a trip
 */
export const deleteTrip = async (tripId) => {
  await axios.delete(`${backendURL}/api/trips/${tripId}`);
};

