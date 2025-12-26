import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import { MapContainer, TileLayer } from "react-leaflet";
import { Typography, CircularProgress, Box } from "@mui/material";
import { useTranslation } from "react-i18next";
import WeatherWidget from "../components/common/WeatherWidget";
import TabbedModal from "../components/common/TabbedModal";
import TransportModal from "../components/common/TransportModal";
import { SetupPanes } from "../components/trips/SetupPanes";
import { MapLegend } from "../components/trips/MapLegend";
import { StationMarkers } from "../components/trips/StationMarkers";
import { RoutePolylines } from "../components/trips/RoutePolylines";
import { AIMarkers } from "../components/trips/AIMarkers";
import { useTripData } from "../hooks/useTripData";
import { useRouteData } from "../hooks/useRouteData";
import { useWeatherCache } from "../hooks/useWeatherCache";
import { useAISuggestions } from "../hooks/useAISuggestions";
import { useTransportSearch } from "../hooks/useTransportSearch";
import { getStationName } from "../utils/stationUtils";
import "../utils/leafletIcons"; // Initialize Leaflet icons

export default function TripsGenerationPage() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const tripId = searchParams.get("tripId");

  const [selectedMarker, setSelectedMarker] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);

  // Fetch trip data
  const { stations, travels, loading, error } = useTripData(tripId, t);

  // Fetch route data
  const routesData = useRouteData(travels, stations, t);

  // Weather caching
  const { getCachedWeatherForCoords } = useWeatherCache();

  // AI suggestions
  const {
    isActivityLoading,
    isOvernightLoading,
    aiData,
    aiOvernightMarkers,
    aiActivityMarkers,
    handleActivitySubmit,
    handleOvernightCategoryChange,
  } = useAISuggestions(i18n);

  // Transport search
  const {
    isTransportLoading,
    hasSearchedPublicTransport,
    aiTransportData,
    handleTransportSearch,
  } = useTransportSearch(travels, stations, i18n, (station) => getStationName(station, i18n.language));

  // Helper function for station name
  const getStationNameForMarker = (station) => getStationName(station, i18n.language);

  const center = stations.length ? [stations[0].latitude, stations[0].longitude] : [20, 0];
  const selectedStationAiData = aiData[selectedMarker?.id] || { activities: {}, overnight: {} };
  const selectedTransportAiData = aiTransportData[selectedRoute?.travel.id] || [];

  if (loading)
    return (
      <Box sx={{ display: "flex", height: "80vh", justifyContent: "center", alignItems: "center" }}>
        <CircularProgress />
      </Box>
    );
  if (error)
    return (
      <Typography color="error" sx={{ p: 2, textAlign: "center" }}>
        {error}
      </Typography>
    );

  return (
    <>
      <MapContainer center={center} zoom={6} style={{ height: "100vh", width: "100%" }}>
        <SetupPanes />
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <StationMarkers stations={stations} onMarkerClick={setSelectedMarker} />
        <RoutePolylines
          travels={travels}
          routesData={routesData}
          onRouteClick={setSelectedRoute}
        />
        <AIMarkers
          overnightMarkers={aiOvernightMarkers}
          activityMarkers={aiActivityMarkers}
        />
        <MapLegend />
      </MapContainer>

      <TabbedModal
        open={!!selectedMarker}
        onClose={() => setSelectedMarker(null)}
        stationName={getStationNameForMarker(selectedMarker)}
        visitDay={selectedMarker?.day_number}
        activityLoading={isActivityLoading}
        overnightLoading={isOvernightLoading}
        weatherWidget={
          <WeatherWidget
            lat={selectedMarker?.latitude}
            lon={selectedMarker?.longitude}
            fetchCachedWeather={getCachedWeatherForCoords}
          />
        }
        overnightOptions={Object.values(selectedStationAiData.overnight || {}).flat()}
        activityOptions={Object.values(selectedStationAiData.activities || {}).flat()}
        onActivitySubmit={(query) => handleActivitySubmit(query, selectedMarker, getStationNameForMarker)}
        onOvernightCategoryChange={(cat) => handleOvernightCategoryChange(cat, selectedMarker, getStationNameForMarker)}
      />

      <TransportModal
        open={!!selectedRoute}
        onClose={() => setSelectedRoute(null)}
        turnByTurnDirections={selectedRoute?.route?.directions || []}
        estimatedTime={
          selectedRoute?.route?.duration ||
          selectedRoute?.travel.time_estimated ||
          t("tripsgeneration.unknown_duration")
        }
        publicTransportRoutes={selectedTransportAiData}
        loadingPublicTransport={isTransportLoading}
        onSearchPublicTransport={() => handleTransportSearch(selectedRoute?.travel.id)}
        hasSearchedPublicTransport={hasSearchedPublicTransport}
      />
    </>
  );
}
