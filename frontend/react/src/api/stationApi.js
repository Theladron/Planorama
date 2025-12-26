import axios from "axios";
import { backendURL } from "../config";

/**
 * Fetch stations by trip ID
 */
export const fetchStationsByTrip = async (tripId) => {
  const res = await axios.get(`${backendURL}/api/stations/by-trip/${tripId}`);
  return res.data;
};

/**
 * Create a new station
 */
export const createStation = async (tripId, stationName, dayNumber) => {
  const res = await axios.post(`${backendURL}/api/stations/`, {
    trip_id: Number(tripId),
    station_name: stationName.trim(),
    day_number: Number(dayNumber),
  });
  return res.data;
};

/**
 * Delete a station
 */
export const deleteStation = async (linkId) => {
  await axios.delete(`${backendURL}/api/stations/${linkId}`);
};

/**
 * Reorder stations
 */
export const reorderStations = async (tripId, stations) => {
  const res = await axios.put(`${backendURL}/api/stations/reorder`, {
    trip_id: Number(tripId),
    stations: stations.map(({ link_id, day_number }) => ({
      link_id: Number(link_id),
      day_number: Number(day_number),
    })),
  });
  return res.data;
};

