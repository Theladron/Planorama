import { Polyline } from "react-leaflet";

/**
 * Component to render route polylines on the map
 */
export const RoutePolylines = ({ travels, routesData, onRouteClick }) => {
  return (
    <>
      {travels.map((travel) =>
        routesData[travel.id] ? (
          <Polyline
            key={travel.id}
            positions={routesData[travel.id].polyline}
            color="blue"
            weight={4}
            opacity={0.7}
            eventHandlers={{ click: () => onRouteClick({ travel, route: routesData[travel.id] }) }}
          />
        ) : null
      )}
    </>
  );
};

