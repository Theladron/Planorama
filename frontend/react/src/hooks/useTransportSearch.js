import { useState, useRef } from "react";
import { fetchAiTransportRoutes } from "../api/tripApi";
import { getStationById } from "../utils/stationUtils";

/**
 * Hook to manage transport search with caching
 */
export const useTransportSearch = (travels, stations, i18n, getStationName) => {
  const [isTransportLoading, setIsTransportLoading] = useState(false);
  const [hasSearchedPublicTransport, setHasSearchedPublicTransport] = useState(false);
  const [aiTransportData, setAiTransportData] = useState({});
  const transportCacheRef = useRef({});

  const handleTransportSearch = async (travelId) => {
    const travel = travels.find((t) => t.id === travelId);
    setHasSearchedPublicTransport(true);
    if (!travel) return;

    const from = getStationById(stations, travel.from_station_id);
    const to = getStationById(stations, travel.to_station_id);
    if (!from || !to) return;

    const key = `${travelId}_transport`;
    if (transportCacheRef.current[key]) {
      setAiTransportData((prev) => ({ ...prev, [travelId]: transportCacheRef.current[key] }));
      return;
    }

    setIsTransportLoading(true);

    try {
      const data = await fetchAiTransportRoutes({
        startLat: from.latitude,
        startLon: from.longitude,
        startCity: getStationName(from),
        endLat: to.latitude,
        endLon: to.longitude,
        endCity: getStationName(to),
        language: i18n.language,
      });

      transportCacheRef.current[key] = data;
      setAiTransportData((prev) => ({ ...prev, [travelId]: data }));
    } catch {
      // Silently handle transport search errors
    } finally {
      setIsTransportLoading(false);
    }
  };

  return {
    isTransportLoading,
    hasSearchedPublicTransport,
    aiTransportData,
    handleTransportSearch,
  };
};

