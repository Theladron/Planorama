import { useEffect } from "react";
import { useMap } from "react-leaflet";

/**
 * Component to set up map panes for proper z-index layering
 */
export const SetupPanes = () => {
  const map = useMap();
  useEffect(() => {
    map.createPane("aiPane");
    map.getPane("aiPane").style.zIndex = 500;
    map.createPane("stationsPane");
    map.getPane("stationsPane").style.zIndex = 600;
  }, [map]);
  return null;
};

