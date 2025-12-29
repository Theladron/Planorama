import { useState, useEffect } from "react";
import { fetchUserTrips } from "../api/tripApi";

/**
 * Hook to fetch and manage user's trips
 */
export const useTrips = () => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadTrips = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchUserTrips();
        setTrips(data);
      } catch (err) {
        setError(err.message || "Failed to load trips");
      } finally {
        setLoading(false);
      }
    };
    loadTrips();
  }, []);

  return { trips, loading, error, setTrips };
};

