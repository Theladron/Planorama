import { Marker, Popup } from "react-leaflet";
import { greenIcon, redIcon } from "../../utils/leafletIcons";

/**
 * Component to render AI suggestion markers (activities and overnight stays)
 */
export const AIMarkers = ({ overnightMarkers, activityMarkers }) => {
  return (
    <>
      {overnightMarkers.map((m, idx) => (
        <Marker key={`overnight-${idx}`} position={[m.lat, m.lon]} icon={redIcon}>
          <Popup>{m.name}</Popup>
        </Marker>
      ))}
      {activityMarkers.map((m, idx) => (
        <Marker key={`activity-${idx}`} position={[m.lat, m.lon]} icon={greenIcon}>
          <Popup>{m.name}</Popup>
        </Marker>
      ))}
    </>
  );
};

