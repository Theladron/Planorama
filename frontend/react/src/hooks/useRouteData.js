import { useState, useEffect } from "react";
import { fetchFullRouteByCoords } from "../api/tripApi";
import { getStationById } from "../utils/stationUtils";

/**
 * Hook to fetch and manage route data for travels
 */
export const useRouteData = (travels, stations, t) => {
  const [routesData, setRoutesData] = useState({});

  useEffect(() => {
    async function fetchAllRoutes() {
      if (!travels.length || !stations.length) return;
      const results = await Promise.all(
        travels.map(async (travel) => {
          const from = getStationById(stations, travel.from_station_id);
          const to = getStationById(stations, travel.to_station_id);
          if (!from || !to) return null;
          try {
            const data = await fetchFullRouteByCoords({
              startLat: from.latitude,
              startLon: from.longitude,
              endLat: to.latitude,
              endLon: to.longitude,
            });
            return { travelId: travel.id, data };
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

  return routesData;
};

