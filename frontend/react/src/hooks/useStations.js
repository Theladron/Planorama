import { useState, useEffect } from "react";
import { fetchStationsByTrip } from "../api/stationApi";

/**
 * Hook to fetch stations for a trip
 */
export const useStations = (tripId) => {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!tripId) {
      setLoading(false);
      return;
    }

    const loadStations = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchStationsByTrip(tripId);
        setStations(data);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load stations");
      } finally {
        setLoading(false);
      }
    };
    loadStations();
  }, [tripId]);

  const refreshStations = async () => {
    if (!tripId) return;
    try {
      const data = await fetchStationsByTrip(tripId);
      setStations(data);
    } catch (err) {
    }
  };

  return { stations, loading, error, setStations, refreshStations };
};

