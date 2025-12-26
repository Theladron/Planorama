import { Marker } from "react-leaflet";

/**
 * Component to render station markers on the map
 */
export const StationMarkers = ({ stations, onMarkerClick }) => {
  return (
    <>
      {stations.map((s) => (
        <Marker
          key={s.id}
          position={[s.latitude, s.longitude]}
          pane="stationsPane"
          eventHandlers={{ click: () => onMarkerClick(s) }}
        />
      ))}
    </>
  );
};

