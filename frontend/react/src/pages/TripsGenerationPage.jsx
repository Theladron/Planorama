import { backendURL } from "../config";
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
import TransportModal from "../components/common/TransportModal";

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
  const [isActivityLoading, setIsActivityLoading] = useState(false);
  const [isOvernightLoading, setIsOvernightLoading] = useState(false);
  const [isTransportLoading, setIsTransportLoading] = useState(false);
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const tripId = searchParams.get("tripId");
  const { token } = useContext(AuthContext);
  const [hasSearchedPublicTransport, setHasSearchedPublicTransport] = useState(false)
  const [stations, setStations] = useState([]);
  const [travels, setTravels] = useState([]);
  const [routesData, setRoutesData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [aiData, setAiData] = useState({});
  const [aiTransportData, setAiTransportData] = useState({});
  const [aiOvernightMarkers, setAiOvernightMarkers] = useState([]);
  const [aiActivityMarkers, setAiActivityMarkers] = useState([]);

  const weatherCacheRef = useRef({});
  const aiCacheRef = useRef({});
  const transportCacheRef = useRef({});

  const getStationById = (id) => stations.find((s) => s.id === id);
  const getStationName = (station) => {
    if (!station) return "";
    return i18n.language.startsWith("de") && station.station_name_de
      ? station.station_name_de
      : station.station_name || "";
  };

  const fetchAISuggestions = async ({ lat, lon, townName, language, contentType }) => {
    try {
      const res = await axios.get(`${backendURL}/api/ai-suggestions`, {
        params: { lat, lon, town_name: townName, language, content_type: contentType },
      });
      return res.data || [];
    } catch (err) {
      console.error("AI suggestion fetch error:", err);
      return [];
    }
  };

  async function fetchAiTransportRoutes({ startLat, startLon, startCity, endLat, endLon, endCity, language }) {
  try {
    const response = await axios.get(`${backendURL}/api/ai-transport`, {
      params: {
        start_lat: startLat,
        start_lon: startLon,
        start_city: startCity,
        end_lat: endLat,
        end_lon: endLon,
        end_city: endCity,
        language,
      },
    });
    return response.data || [];
  } catch (err) {
    console.error("AI transport fetch error:", err);
    throw err;
  }
}

  const getCachedWeatherForCoords = async (lat, lon) => {
    const key = `${lat.toFixed(4)}_${lon.toFixed(4)}`;
    if (weatherCacheRef.current[key]) return weatherCacheRef.current[key];
    try {
      const res = await axios.get(`${backendURL}/api/weather`, { params: { lat, lon } });
      weatherCacheRef.current[key] = res.data;
      return res.data;
    } catch (err) {
      console.error("Weather fetch error:", err);
      return null;
    }
  };

  const handleTransportSearch = async (travelId) => {
  const travel = travels.find((t) => t.id === travelId);
  setHasSearchedPublicTransport(true);
  if (!travel) return;

  const from = getStationById(travel.from_station_id);
  const to = getStationById(travel.to_station_id);
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

    console.log("AI Transport suggestions (external):", data);
    transportCacheRef.current[key] = data;
    setAiTransportData((prev) => ({ ...prev, [travelId]: data }));
  } catch (err) {
    console.error("Failed to fetch AI transport suggestions:", err);
  } finally {
    setIsTransportLoading(false);
  }
};

  const handleActivitySubmit = async (query) => {
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

  const handleOvernightCategoryChange = async (cat) => {
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

  useEffect(() => {
    async function fetchTripData() {
      try {
        setLoading(true);
        const [stationsRes, travelsRes] = await Promise.all([
          axios.get(`${backendURL}/api/stations/by-trip/${tripId}`),
          axios.get(`${backendURL}/api/travel/trip/${tripId}`),
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
    if (tripId) fetchTripData();
    else {
      setError(t("tripsgeneration.error_no_trip_id"));
      setLoading(false);
    }
  }, [tripId, t]);

  useEffect(() => {
    async function fetchAllRoutes() {
      if (!travels.length || !stations.length) return;
      const results = await Promise.all(
        travels.map(async (travel) => {
          const from = getStationById(travel.from_station_id);
          const to = getStationById(travel.to_station_id);
          if (!from || !to) return null;
          try {
            const res = await axios.get(`${backendURL}/api/full-route-by-coords`, {
              params: {
                start_lat: from.latitude,
                start_lon: from.longitude,
                end_lat: to.latitude,
                end_lon: to.longitude,
              },
            });
            return { travelId: travel.id, data: res.data };
          } catch {
            return {
              travelId: travel.id,
              data: {
                polyline: [[from.latitude, from.longitude], [to.latitude, to.longitude]],
                duration: travel.time_estimated || t("tripsgeneration.unknown_duration"),
                directions: [],
              },
            };
          }
        })
      );
      const routeMap = {};
      results.forEach((r) => {
        if (r) routeMap[r.travelId] = r.data;
      });
      setRoutesData(routeMap);
    }
    fetchAllRoutes();
  }, [travels, stations, t]);

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
        {stations.map((s) => (
          <Marker
            key={s.id}
            position={[s.latitude, s.longitude]}
            pane="stationsPane"
            eventHandlers={{ click: () => setSelectedMarker(s) }}
          />
        ))}
        {travels.map((travel) =>
          routesData[travel.id] ? (
            <Polyline
              key={travel.id}
              positions={routesData[travel.id].polyline}
              color="blue"
              weight={4}
              opacity={0.7}
              eventHandlers={{ click: () => setSelectedRoute({ travel, route: routesData[travel.id] }) }}
            />
          ) : null
        )}
        {aiOvernightMarkers.map((m, idx) => (
          <Marker key={`overnight-${idx}`} position={[m.lat, m.lon]} icon={redIcon}>
            <Popup>{m.name}</Popup>
          </Marker>
        ))}
        {aiActivityMarkers.map((m, idx) => (
          <Marker key={`activity-${idx}`} position={[m.lat, m.lon]} icon={greenIcon}>
            <Popup>{m.name}</Popup>
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
            border: "1px solid rgba(250, 201, 72, 0.25)",
            borderRadius: 6,
            boxShadow: "0 6px 20px rgba(250, 201, 72, 0.1)",
            zIndex: 1000,
            fontSize: 14,
            backgroundColor: "rgba(250, 201, 72, 0.2)",
            backdropFilter: "blur(3px)",
            textShadow: "1px 1px 4px rgba(0, 0, 0, 0.5)",
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
        activityLoading={isActivityLoading}
        overnightLoading={isOvernightLoading}
        weatherWidget={<WeatherWidget lat={selectedMarker?.latitude} lon={selectedMarker?.longitude} fetchCachedWeather={getCachedWeatherForCoords} />}
        overnightOptions={Object.values(selectedStationAiData.overnight || {}).flat()}
        activityOptions={Object.values(selectedStationAiData.activities || {}).flat()}
        onActivitySubmit={handleActivitySubmit}
        onOvernightCategoryChange={handleOvernightCategoryChange}
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
        asSearchedPublicTransport={hasSearchedPublicTransport}
      />
    </>
  );
}
