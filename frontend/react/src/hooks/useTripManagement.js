import { useState, useEffect } from "react";
import dayjs from "dayjs";
import { fetchUserTrips, updateTripDates, deleteTrip } from "../api/tripApi";
import { fetchStationsByTrip, deleteStation } from "../api/stationApi";

/**
 * Hook to manage trips with stations and date editing
 */
export const useTripManagement = (t) => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updateLoading, setUpdateLoading] = useState({});
  const [editableDates, setEditableDates] = useState({});
  const [stationsByTrip, setStationsByTrip] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const tripsData = await fetchUserTrips();
        setTrips(tripsData);

        const dates = {};
        tripsData.forEach((trip) => {
          dates[trip.id] = {
            start_date: dayjs(trip.start_date).format("YYYY-MM-DD"),
            end_date: dayjs(trip.end_date).format("YYYY-MM-DD"),
          };
        });
        setEditableDates(dates);

        const stationsResults = await Promise.all(
          tripsData.map(async (trip) => {
            try {
              const stations = await fetchStationsByTrip(trip.id);
              return { tripId: trip.id, stations };
            } catch (err) {
              console.error(`Failed to fetch stations for trip ${trip.id}:`, err);
              return { tripId: trip.id, stations: [] };
            }
          })
        );

        const stationsMap = {};
        stationsResults.forEach(({ tripId, stations }) => {
          stationsMap[tripId] = stations;
        });
        setStationsByTrip(stationsMap);
      } catch (err) {
        console.error("Failed to fetch trips:", err);
        setError(t("trips.errorLoading"));
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [t]);

  const handleDateChange = (tripId, field, value) => {
    setEditableDates((prev) => ({
      ...prev,
      [tripId]: {
        ...prev[tripId],
        [field]: value,
      },
    }));
  };

  const handleUpdateDate = async (tripId) => {
    if (!editableDates[tripId]) return;

    const { start_date, end_date } = editableDates[tripId];
    setUpdateLoading((prev) => ({ ...prev, [tripId]: true }));

    try {
      await updateTripDates(tripId, start_date, end_date);
      setTrips((prevTrips) =>
        prevTrips.map((trip) =>
          trip.id === tripId ? { ...trip, start_date, end_date } : trip
        )
      );
    } catch (err) {
      console.error("Failed to update trip dates:", err);
      throw err;
    } finally {
      setUpdateLoading((prev) => ({ ...prev, [tripId]: false }));
    }
  };

  const handleDeleteStation = async (linkId, tripId) => {
    try {
      await deleteStation(linkId);
      setStationsByTrip((prev) => ({
        ...prev,
        [tripId]: prev[tripId].filter((station) => station.link_id !== linkId),
      }));
    } catch (err) {
      console.error("Failed to delete station:", err);
      throw err;
    }
  };

  const handleDeleteTrip = async (tripId) => {
    try {
      await deleteTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
      setStationsByTrip((prev) => {
        const updated = { ...prev };
        delete updated[tripId];
        return updated;
      });
    } catch (err) {
      console.error("Failed to delete trip:", err);
      throw err;
    }
  };

  return {
    trips,
    loading,
    error,
    updateLoading,
    editableDates,
    stationsByTrip,
    handleDateChange,
    handleUpdateDate,
    handleDeleteStation,
    handleDeleteTrip,
  };
};

