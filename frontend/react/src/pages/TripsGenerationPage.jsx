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
      } catch (err) {
        setError("Failed to load trip data.");
      } finally {
        setLoading(false);
      }
    }
    if (tripId) {
      fetchTripData();
    } else {
      setError("No tripId specified.");
      setLoading(false);
    }
  }, [tripId]);


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
  }
});
        console.log("Route for travel", travel.id, res.data);
        return { travelId: travel.id, data: res.data };
      } catch (error){
          console.error("Error fetching route:", error);
        // No route from openrouteservice - fallback
        return {
          travelId: travel.id,
          data: {
            polyline: [
              [fromStation.latitude, fromStation.longitude],
              [toStation.latitude, toStation.longitude],
            ],
            duration: travel.time_estimated || "N/A",
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
  }, [travels, stations, token]);

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

  if (error) return <Typography color="error">{error}</Typography>;

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
        <DialogTitle>Station Info</DialogTitle>
        <DialogContent>
          <Typography>
            <strong>Town:</strong> {selectedMarker?.station_name}
          </Typography>
          <Typography>
            <strong>Day:</strong> {selectedMarker?.day_number}
          </Typography>
        </DialogContent>
      </Dialog>


      <Dialog open={!!selectedRoute} onClose={() => setSelectedRoute(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Route Info</DialogTitle>
        <DialogContent dividers>
          <Typography>
            <strong>Transport:</strong> {selectedRoute?.travel.method_of_transport}
          </Typography>
          <Typography>
            <strong>Estimated Time:</strong> {selectedRoute?.route.duration || "N/A"}
          </Typography>
          <Typography sx={{ mt: 2, mb: 1 }}>
            <strong>Directions:</strong>
          </Typography>
          {selectedRoute?.route.directions.length > 0 ? (
            <ol>
              {selectedRoute.route.directions.map((step, idx) => (
                <li key={idx}>{step.instruction}</li>
              ))}
            </ol>
          ) : (
            <Typography>No detailed directions available.</Typography>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
