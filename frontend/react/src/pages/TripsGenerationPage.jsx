// TripsGenerationPage.jsx
import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { useLocation } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Popup,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  CircularProgress,
  Box,
  Link,
} from "@mui/material";
import { useTranslation } from "react-i18next";
import WeatherWidget from "../components/common/WeatherWidget";
import TabbedModal from "../components/common/TabbedModal";

// Leaflet icon fix
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Custom icons
const greenIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  shadowSize: [41, 41],
  className: "leaflet-green-icon",
});

const redIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  shadowSize: [41, 41],
  className: "leaflet-red-icon",
});

// Create custom panes on map load
const SetupPanes = () => {
  const map = useMap();

  useEffect(() => {
    map.createPane("aiPane");
    map.getPane("aiPane").style.zIndex = 500;

    map.createPane("stationsPane");
    map.getPane("stationsPane").style.zIndex = 600;
  }, [map]);

  return null;
};

export default function TripsGenerationPage() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const tripId = searchParams.get("tripId");
  const { token } = useContext(AuthContext);

  const [stations, setStations] = useState([]);
  const [travels, setTravels] = useState([]);
  const [routesData, setRoutesData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [aiData, setAiData] = useState({});

  const weatherCacheRef = useRef({});
  const aiCacheRef = useRef({});

  const getCachedWeatherForCoords = async (lat, lon) => {
    const cacheKey = `${lat.toFixed(4)}_${lon.toFixed(4)}`;
    if (weatherCacheRef.current[cacheKey]) {
      return weatherCacheRef.current[cacheKey];
    }
    try {
      const res = await axios.get("/api/weather", { params: { lat, lon } });
      weatherCacheRef.current[cacheKey] = res.data;
      return res.data;
    } catch (error) {
      console.error("Failed to fetch weather:", error);
      return null;
    }
  };

  const fetchAISuggestions = async ({ lat, lon, townName, language, contentType }) => {
    try {
      const res = await axios.get("/api/ai-suggestions", {
        params: { lat, lon, town_name: townName, language, content_type: contentType },
      });
      return res.data || [];
    } catch (err) {
      console.error("AI suggestion fetch error:", err);
      return [];
    }
  };

  const getStationName = (station) => {
    if (!station) return "";
    if (i18n.language.startsWith("de") && station.station_name_de) {
      return station.station_name_de;
    }
    return station.station_name || "";
  };

  const handleOvernightCategoryChange = async (category) => {
    if (!selectedMarker) return;
    const stationId = selectedMarker.id;
    const cacheKey = `${stationId}_overnight_${category}`;
    if (aiCacheRef.current[cacheKey]) return;

    const data = await fetchAISuggestions({
      lat: selectedMarker.latitude,
      lon: selectedMarker.longitude,
      townName: getStationName(selectedMarker),
      language: i18n.language,
      contentType: category,
    });

    aiCacheRef.current[cacheKey] = data;
    setAiData((prev) => ({
      ...prev,
      [stationId]: {
        ...prev[stationId],
        overnight: {
          ...(prev[stationId]?.overnight || {}),
          [category]: data,
        },
        activities: {
          ...(prev[stationId]?.activities || {}),
        },
      },
    }));
  };

  const handleActivitySearch = async (query) => {
    if (!selectedMarker || !query) return;
    const stationId = selectedMarker.id;
    const label = i18n.language.startsWith("de") ? "Aktivität" : "activity";
    const contentType = `${label}: ${query}`;
    const cacheKey = `${stationId}_activity_${query.toLowerCase()}`;
    if (aiCacheRef.current[cacheKey]) return;

    const data = await fetchAISuggestions({
      lat: selectedMarker.latitude,
      lon: selectedMarker.longitude,
      townName: getStationName(selectedMarker),
      language: i18n.language,
      contentType,
    });

    aiCacheRef.current[cacheKey] = data;
    setAiData((prev) => ({
      ...prev,
      [stationId]: {
        ...prev[stationId],
        activities: {
          ...(prev[stationId]?.activities || {}),
          [query]: data,
        },
        overnight: {
          ...(prev[stationId]?.overnight || {}),
        },
      },
    }));
  };

  useEffect(() => {
    async function fetchTripData() {
      try {
        setLoading(true);
        const [stationsRes, travelsRes] = await Promise.all([
          axios.get(`/api/stations/by-trip/${tripId}`),
          axios.get(`/api/travel/trip/${tripId}`),
        ]);
        setStations(stationsRes.data);
        setTravels(travelsRes.data);
        setError(null);
      } catch (err) {
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

  useEffect(() => {
    async function fetchRouteForTravel(travel) {
      const fromStation = stations.find((s) => s.id === travel.from_station_id);
      const toStation = stations.find((s) => s.id === travel.to_station_id);
      if (!fromStation || !toStation) return null;

      try {
        const res = await axios.get("/api/full-route-by-coords", {
          params: {
            start_lat: fromStation.latitude,
            start_lon: fromStation.longitude,
            end_lat: toStation.latitude,
            end_lon: toStation.longitude,
          },
        });
        return { travelId: travel.id, data: res.data };
      } catch (error) {
        console.error("Error fetching route:", error);
        return {
          travelId: travel.id,
          data: {
            polyline: [
              [fromStation.latitude, fromStation.longitude],
              [toStation.latitude, toStation.longitude],
            ],
            duration: travel.time_estimated || t("tripsgeneration.unknown_duration"),
            directions: [],
          },
        };
      }
    }

    async function fetchAllRoutes() {
      if (!travels.length || !stations.length) return;
      const results = await Promise.all(travels.map(fetchRouteForTravel));
      const newRoutes = {};
      results.forEach((result) => {
        if (result?.travelId && result.data) {
          newRoutes[result.travelId] = result.data;
        }
      });
      setRoutesData(newRoutes);
    }
    fetchAllRoutes();
  }, [travels, stations, token, t]);

  const center = stations.length ? [stations[0].latitude, stations[0].longitude] : [20, 0];

  const aiMarkers = Object.entries(aiData).flatMap(([stationId, suggestions]) => {
    const activityMarkers = Object.values(suggestions.activities || {}).flat().map((item, idx) => ({
      ...item,
      type: "activity",
      key: `act_${stationId}_${idx}`,
    }));
    const overnightMarkers = Object.values(suggestions.overnight || {}).flat().map((item, idx) => ({
      ...item,
      type: "overnight",
      key: `overnight_${stationId}_${idx}`,
    }));
    return [...activityMarkers, ...overnightMarkers];
  });

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

  const selectedStationAiData = aiData[selectedMarker?.id] || { activities: {}, overnight: {} };

  return (
    <>
      <MapContainer center={center} zoom={6} style={{ height: "100vh", width: "100%" }}>
        <SetupPanes />
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {stations.map((station) => (
          <Marker
            key={station.id}
            position={[station.latitude, station.longitude]}
            pane="stationsPane"
            eventHandlers={{ click: () => setSelectedMarker(station) }}
          />
        ))}
        {travels.map((travel) => {
          const route = routesData[travel.id];
          if (!route) return null;
          return (
            <Polyline
              key={travel.id}
              positions={route.polyline || []}
              color="blue"
              weight={4}
              opacity={0.7}
              eventHandlers={{ click: () => setSelectedRoute({ travel, route }) }}
            />
          );
        })}
        {aiMarkers.map((item) => (
          <Marker
            key={item.key}
            position={[item.lat, item.lon]}
            pane="aiPane"
            icon={item.type === "activity" ? greenIcon : redIcon}
          >
            <Popup>
              <Typography variant="subtitle2" gutterBottom>{item.title}</Typography>
              {item.url && (
                <Link href={item.url} target="_blank" rel="noopener noreferrer">
                  Website
                </Link>
              )}
            </Popup>
          </Marker>
        ))}

        {/* Legend */}
        <div
          style={{
            position: "absolute",
            bottom: 20,
            left: 20,
            background: "white",
            padding: "8px 12px",
            borderRadius: 6,
            boxShadow: "0 2px 6px rgba(0,0,0,0.3)",
            zIndex: 1000,
            fontSize: 14,
            backgroundColor: "rgba(255, 255, 255, 0.9)",
          }}
        >
          <div><strong>{t("tripsgeneration.legend", "Legend")}</strong></div>
          <div>{t("tripsgeneration.legend_info", "Click on a route or icon to see more information.")}</div>
          <div><img
            src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"
            alt="Blue marker"
            style={{ width: 13, height: 20, marginRight: 6}}/>Station</div>
          <div><img
            src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png"
            alt="Red marker"
            style={{ width: 13, height: 20, marginRight: 6 }}/>{t("tripsgeneration.overnight", "Overnight")}</div>
          <div><img
            src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png"
            alt="Green marker"
            style={{ width: 13, height: 20, marginRight: 6 }}/>{t("tripsgeneration.activities", "Activity")}</div>
        </div>
      </MapContainer>

      <TabbedModal
        open={!!selectedMarker}
        onClose={() => setSelectedMarker(null)}
        stationName={getStationName(selectedMarker)}
        visitDay={selectedMarker?.day_number}
        weatherWidget={
          <WeatherWidget
            lat={selectedMarker?.latitude}
            lon={selectedMarker?.longitude}
            fetchCachedWeather={getCachedWeatherForCoords}
          />
        }
        overnightOptions={Object.values(selectedStationAiData.overnight || {}).flat()}
        activityOptions={Object.values(selectedStationAiData.activities || {}).flat()}
        onActivitySubmit={handleActivitySearch}
        onOvernightCategoryChange={handleOvernightCategoryChange}
      />

      <Dialog open={!!selectedRoute} onClose={() => setSelectedRoute(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{t("tripsgeneration.dialog_route_info_title")}</DialogTitle>
        <DialogContent dividers>
          <Typography>
            <strong>{t("tripsgeneration.label_transport")}</strong> {selectedRoute?.travel.method_of_transport}
          </Typography>
          <Typography>
            <strong>{t("tripsgeneration.label_estimated_time")}</strong> {selectedRoute?.route.duration || t("tripsgeneration.unknown_duration")}
          </Typography>
          <Typography sx={{ mt: 2, mb: 1 }}>
            <strong>{t("tripsgeneration.label_directions")}</strong>
          </Typography>
          {selectedRoute?.route.directions.length > 0 ? (
            <ol>
              {selectedRoute.route.directions.map((step, idx) => (
                <li key={idx}>{step.instruction}</li>
              ))}
            </ol>
          ) : (
            <Typography>{t("tripsgeneration.no_directions")}</Typography>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
