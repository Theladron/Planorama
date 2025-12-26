import { useState, useRef } from "react";
import { fetchAISuggestions } from "../api/tripApi";

/**
 * Hook to manage AI suggestions with caching
 */
export const useAISuggestions = (i18n) => {
  const [isActivityLoading, setIsActivityLoading] = useState(false);
  const [isOvernightLoading, setIsOvernightLoading] = useState(false);
  const [aiData, setAiData] = useState({});
  const [aiOvernightMarkers, setAiOvernightMarkers] = useState([]);
  const [aiActivityMarkers, setAiActivityMarkers] = useState([]);
  const aiCacheRef = useRef({});

  const handleActivitySubmit = async (query, selectedMarker, getStationName) => {
    if (!selectedMarker) return;
    const key = `${selectedMarker.id}_activities_${query}`;
    if (aiCacheRef.current[key]) {
      const cached = aiCacheRef.current[key];
      setAiData((prev) => ({
        ...prev,
        [selectedMarker.id]: {
          ...prev[selectedMarker.id],
          activities: {
            ...prev[selectedMarker.id]?.activities,
            [query]: cached,
          },
        },
      }));
      setAiActivityMarkers((prev) => [
        ...prev,
        ...cached.map((item) => ({
          lat: item.lat,
          lon: item.lon,
          name: item.name,
        })),
      ]);
      return;
    }

    setIsActivityLoading(true);
    const result = await fetchAISuggestions({
      lat: selectedMarker.latitude,
      lon: selectedMarker.longitude,
      townName: getStationName(selectedMarker),
      language: i18n.language,
      contentType: query,
    });
    setIsActivityLoading(false);
    aiCacheRef.current[key] = result;
    setAiData((prev) => ({
      ...prev,
      [selectedMarker.id]: {
        ...prev[selectedMarker.id],
        activities: {
          ...prev[selectedMarker.id]?.activities,
          [query]: result,
        },
      },
    }));
    setAiActivityMarkers((prev) => [
      ...prev,
      ...result.map((item) => ({
        lat: item.lat,
        lon: item.lon,
        name: item.name,
      })),
    ]);
  };

  const handleOvernightCategoryChange = async (cat, selectedMarker, getStationName) => {
    if (!selectedMarker) return;
    const key = `${selectedMarker.id}_overnight_${cat}`;
    if (aiCacheRef.current[key]) {
      const cached = aiCacheRef.current[key];
      setAiData((prev) => ({
        ...prev,
        [selectedMarker.id]: {
          ...prev[selectedMarker.id],
          overnight: {
            ...prev[selectedMarker.id]?.overnight,
            [cat]: cached,
          },
        },
      }));
      setAiOvernightMarkers((prev) => [
        ...prev,
        ...cached.map((item) => ({
          lat: item.lat,
          lon: item.lon,
          name: item.name,
        })),
      ]);
      return;
    }

    setIsOvernightLoading(true);
    const result = await fetchAISuggestions({
      lat: selectedMarker.latitude,
      lon: selectedMarker.longitude,
      townName: getStationName(selectedMarker),
      language: i18n.language,
      contentType: cat,
    });
    setIsOvernightLoading(false);
    aiCacheRef.current[key] = result;
    setAiData((prev) => ({
      ...prev,
      [selectedMarker.id]: {
        ...prev[selectedMarker.id],
        overnight: {
          ...prev[selectedMarker.id]?.overnight,
          [cat]: result,
        },
      },
    }));
    setAiOvernightMarkers((prev) => [
      ...prev,
      ...result.map((item) => ({
        lat: item.lat,
        lon: item.lon,
        name: item.name,
      })),
    ]);
  };

  return {
    isActivityLoading,
    isOvernightLoading,
    aiData,
    aiOvernightMarkers,
    aiActivityMarkers,
    handleActivitySubmit,
    handleOvernightCategoryChange,
  };
};

