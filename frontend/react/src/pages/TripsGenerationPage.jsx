import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { useLocation } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

import { MapContainer, TileLayer, Marker, Polyline, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import {
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  CircularProgress,
  Box,
} from "@mui/material";

import { useTranslation } from "react-i18next";

// Fix leaflet default icon issue in many bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

export default function TripsGenerationPage() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const tripId = searchParams.get("tripId");

  const [stations, setStations] = useState([]);
  const [travels, setTravels] = useState([]);
  const [routesData, setRoutesData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token } = useContext(AuthContext);

  const [selectedMarker, setSelectedMarker] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);

  // Fetch stations and travels
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

  // Fetch route data for each travel once travels and stations are loaded
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
        console.log("Route for travel", travel.id, res.data);
        return { travelId: travel.id, data: res.data };
      } catch (error) {
        console.error("Error fetching route:", error);
        // No route from openrouteservice - fallback
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
      if (travels.length === 0 || stations.length === 0) return;

      const promises = travels.map((travel) => fetchRouteForTravel(travel));
      const results = await Promise.all(promises);

      const newRoutes = {};
      results.forEach((result) => {
        if (result && result.travelId && result.data) {
          newRoutes[result.travelId] = result.data;
        }
      });
      setRoutesData(newRoutes);
    }

    fetchAllRoutes();
  }, [travels, stations, token, t]);

  const center = stations.length
    ? [stations[0].latitude, stations[0].longitude]
    : [20, 0]; // somewhere central

  if (loading)
    return (
      <Box
        sx={{
          display: "flex",
          height: "80vh",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <CircularProgress />
      </Box>
    );

  if (error)
    return (
      <Typography color="error" sx={{ p: 2, textAlign: "center" }}>
        {error}
      </Typography>
    );

  // Function to get station name depending on current language
  const getStationName = (station) => {
    if (!station) return "";
    if (i18n.language.startsWith("de") && station.station_name_de) {
      return station.station_name_de;
    }
    return station.station_name || "";
  };

  return (
    <>
      <MapContainer center={center} zoom={6} style={{ height: "100vh", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Stations markers */}
        {stations.map((station) => (
          <Marker
            key={station.id}
            position={[station.latitude, station.longitude]}
            eventHandlers={{
              click: () => setSelectedMarker(station),
            }}
          />
        ))}

        {/* Travel routes polylines */}
        {travels.map((travel) => {
          const route = routesData[travel.id];
          if (!route) return null;

          return (
            <Polyline
              key={travel.id}
              positions={Array.isArray(route.polyline) ? route.polyline.map(([lat, lon]) => [lat, lon]) : []}
              color="blue"
              weight={4}
              opacity={0.7}
              eventHandlers={{
                click: () => setSelectedRoute({ travel, route }),
              }}
            />
          );
        })}
      </MapContainer>

      <Dialog open={!!selectedMarker} onClose={() => setSelectedMarker(null)}>
        <DialogTitle>{t("tripsgeneration.dialog_station_info_title")}</DialogTitle>
        <DialogContent>
          <Typography>
            <strong>{t("tripsgeneration.label_town")}</strong> {getStationName(selectedMarker)}
          </Typography>
          <Typography>
            <strong>{t("tripsgeneration.label_day")}</strong> {selectedMarker?.day_number}
          </Typography>
        </DialogContent>
      </Dialog>

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
