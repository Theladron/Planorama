/**
 * Get station by ID from stations array
 */
export const getStationById = (stations, id) => {
  return stations.find((s) => s.id === id);
};

/**
 * Get station name based on current language
 */
export const getStationName = (station, language) => {
  if (!station) return "";
  return language.startsWith("de") && station.station_name_de
    ? station.station_name_de
    : station.station_name || "";
};

