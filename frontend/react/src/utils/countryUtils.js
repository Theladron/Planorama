import countries from "i18n-iso-countries";
import enLocale from "i18n-iso-countries/langs/en.json";

countries.registerLocale(enLocale);

/**
 * Convert country code to flag emoji
 */
export const countryCodeToEmoji = (countryCode) => {
  if (!countryCode) return "";
  return countryCode
    .toUpperCase()
    .replace(/./g, (char) => String.fromCodePoint(127397 + char.charCodeAt()));
};

/**
 * Get country code from country name
 */
export const getCountryCode = (countryName) => {
  return countries.getAlpha2Code(countryName, "en") || null;
};

