import { useState, useEffect } from "react";
import { fetchTripById } from "../api/tripApi";

/**
 * Hook to fetch a single trip by ID
 */
export const useTrip = (tripId) => {
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!tripId) {
      setLoading(false);
      return;
    }

    const loadTrip = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchTripById(tripId);
        setTrip(data);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load trip");
      } finally {
        setLoading(false);
      }
    };
    loadTrip();
  }, [tripId]);

  return { trip, loading, error };
};

