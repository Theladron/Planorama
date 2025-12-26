import dayjs from "dayjs";

/**
 * Get available days for a trip (days not yet assigned to stations)
 */
export const getAvailableDays = (trip, stations) => {
  if (!trip) return [];

  const start = dayjs(trip.start_date);
  const end = dayjs(trip.end_date);
  const totalDays = end.diff(start, "day") + 1;

  const assignedDays = new Set(stations.map((s) => s.day_number));
  const available = [];
  for (let day = 1; day <= totalDays; day++) {
    if (!assignedDays.has(day)) available.push(day);
  }
  return available;
};

/**
 * Get all days in a trip date range
 */
export const getTripDays = (trip) => {
  if (!trip) return [];
  const start = dayjs(trip.start_date);
  const end = dayjs(trip.end_date);
  const days = [];
  for (let i = 1; i <= end.diff(start, "day") + 1; i++) {
    days.push(i);
  }
  return days;
};

/**
 * Check if array has duplicate values
 */
export const hasDuplicates = (values) => {
  const seen = new Set();
  for (const val of values) {
    if (seen.has(val)) return true;
    seen.add(val);
  }
  return false;
};

