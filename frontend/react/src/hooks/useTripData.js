import { useState, useEffect } from "react";
import { fetchStationsByTrip, fetchTravelsByTrip } from "../api/tripApi";

/**
 * Hook to fetch and manage trip data (stations and travels)
 */
export const useTripData = (tripId, t) => {
  const [stations, setStations] = useState([]);
  const [travels, setTravels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchTripData() {
      try {
        setLoading(true);
        const [stationsRes, travelsRes] = await Promise.all([
          fetchStationsByTrip(tripId),
          fetchTravelsByTrip(tripId),
        ]);
        setStations(stationsRes);
        setTravels(travelsRes);
        setError(null);
      } catch {
        setError(t("tripsgeneration.error_load_failed"));
      } finally {
        setLoading(false);
      }
    }
    if (tripId) {
      fetchTripData();
    } else {
      setError(t("tripsgeneration.error_no_trip_id"));
      setLoading(false);
    }
  }, [tripId, t]);

  return { stations, travels, loading, error };
};

