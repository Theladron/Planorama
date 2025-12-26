/**
 * Tests for utility functions
 */
import { validateEmail, validatePassword, validateDateRange } from '../src/utils/validation';
import { getAvailableDays, getTripDays, hasDuplicates } from '../src/utils/dateUtils';
import { countryCodeToEmoji, getCountryCode } from '../src/utils/countryUtils';
import { getStationById, getStationName } from '../src/utils/stationUtils';

describe('Validation Utilities', () => {
  describe('validateEmail', () => {
    it('should return true for valid email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('user+tag@example.com')).toBe(true);
      expect(validateEmail('user123@example-domain.com')).toBe(true);
    });

    it('should return false for invalid email addresses', () => {
      expect(validateEmail('invalid')).toBe(false);
      expect(validateEmail('invalid@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('invalid@.com')).toBe(false);
      expect(validateEmail('')).toBe(false);
      expect(validateEmail('invalid@domain')).toBe(false);
      expect(validateEmail('invalid space@example.com')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    const mockT = (key) => key; // Mock translation function

    it('should return null for valid passwords', () => {
      expect(validatePassword('ValidPass123!', mockT)).toBeNull();
      expect(validatePassword('Another1@Pass', mockT)).toBeNull();
      expect(validatePassword('My$ecure1Pass', mockT)).toBeNull();
    });

    it('should return error for password shorter than 8 characters', () => {
      expect(validatePassword('Short1!', mockT)).toBe('register.error_password_length');
      expect(validatePassword('Abc12!', mockT)).toBe('register.error_password_length');
    });

    it('should return error for password without uppercase', () => {
      expect(validatePassword('lowercase123!', mockT)).toBe('register.error_password_uppercase');
      expect(validatePassword('alllower123!', mockT)).toBe('register.error_password_uppercase');
    });

    it('should return error for password without lowercase', () => {
      expect(validatePassword('UPPERCASE123!', mockT)).toBe('register.error_password_lowercase');
      expect(validatePassword('ALLUPPER123!', mockT)).toBe('register.error_password_lowercase');
    });

    it('should return error for password without number', () => {
      expect(validatePassword('NoNumber!', mockT)).toBe('register.error_password_number');
      expect(validatePassword('NoNum$ber', mockT)).toBe('register.error_password_number');
    });

    it('should return error for password without symbol', () => {
      expect(validatePassword('NoSymbol123', mockT)).toBe('register.error_password_symbol');
      expect(validatePassword('NoSym123', mockT)).toBe('register.error_password_symbol');
    });
  });

  describe('validateDateRange', () => {
    it('should return true when start date is before end date', () => {
      expect(validateDateRange('2025-06-01', '2025-06-10')).toBe(true);
      expect(validateDateRange('2025-01-01', '2025-12-31')).toBe(true);
    });

    it('should return true when start date equals end date', () => {
      expect(validateDateRange('2025-06-01', '2025-06-01')).toBe(true);
    });

    it('should return false when start date is after end date', () => {
      expect(validateDateRange('2025-06-10', '2025-06-01')).toBe(false);
      expect(validateDateRange('2025-12-31', '2025-01-01')).toBe(false);
    });

    it('should return false when dates are missing', () => {
      expect(validateDateRange('', '2025-06-10')).toBe(false);
      expect(validateDateRange('2025-06-01', '')).toBe(false);
      expect(validateDateRange(null, '2025-06-10')).toBe(false);
      expect(validateDateRange('2025-06-01', null)).toBe(false);
      expect(validateDateRange(undefined, '2025-06-10')).toBe(false);
    });
  });
});

describe('Date Utilities', () => {
  describe('getTripDays', () => {
    it('should return array of days for a trip', () => {
      const trip = {
        start_date: '2025-06-01',
        end_date: '2025-06-05',
      };
      const days = getTripDays(trip);
      expect(days).toEqual([1, 2, 3, 4, 5]);
    });

    it('should return single day for same start and end date', () => {
      const trip = {
        start_date: '2025-06-01',
        end_date: '2025-06-01',
      };
      const days = getTripDays(trip);
      expect(days).toEqual([1]);
    });

    it('should return empty array for null/undefined trip', () => {
      expect(getTripDays(null)).toEqual([]);
      expect(getTripDays(undefined)).toEqual([]);
    });
  });

  describe('getAvailableDays', () => {
    it('should return all days when no stations are assigned', () => {
      const trip = {
        start_date: '2025-06-01',
        end_date: '2025-06-05',
      };
      const stations = [];
      const available = getAvailableDays(trip, stations);
      expect(available).toEqual([1, 2, 3, 4, 5]);
    });

    it('should exclude assigned days', () => {
      const trip = {
        start_date: '2025-06-01',
        end_date: '2025-06-05',
      };
      const stations = [
        { day_number: 1 },
        { day_number: 3 },
        { day_number: 5 },
      ];
      const available = getAvailableDays(trip, stations);
      expect(available).toEqual([2, 4]);
    });

    it('should return empty array when all days are assigned', () => {
      const trip = {
        start_date: '2025-06-01',
        end_date: '2025-06-03',
      };
      const stations = [
        { day_number: 1 },
        { day_number: 2 },
        { day_number: 3 },
      ];
      const available = getAvailableDays(trip, stations);
      expect(available).toEqual([]);
    });

    it('should return empty array for null/undefined trip', () => {
      expect(getAvailableDays(null, [])).toEqual([]);
      expect(getAvailableDays(undefined, [])).toEqual([]);
    });
  });

  describe('hasDuplicates', () => {
    it('should return false for array without duplicates', () => {
      expect(hasDuplicates([1, 2, 3, 4, 5])).toBe(false);
      expect(hasDuplicates(['a', 'b', 'c'])).toBe(false);
      expect(hasDuplicates([])).toBe(false);
    });

    it('should return true for array with duplicates', () => {
      expect(hasDuplicates([1, 2, 2, 3])).toBe(true);
      expect(hasDuplicates(['a', 'b', 'a'])).toBe(true);
      expect(hasDuplicates([1, 1])).toBe(true);
    });

    it('should handle mixed types', () => {
      expect(hasDuplicates([1, '1', 2])).toBe(false); // Different types
      expect(hasDuplicates([1, 1, '1'])).toBe(true); // Duplicate number
    });
  });
});

describe('Country Utilities', () => {
  describe('countryCodeToEmoji', () => {
    it('should convert country code to flag emoji', () => {
      const result = countryCodeToEmoji('US');
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThan(0);
    });

    it('should handle lowercase country codes', () => {
      const result = countryCodeToEmoji('us');
      expect(result).toBeTruthy();
    });

    it('should return empty string for null/undefined', () => {
      expect(countryCodeToEmoji(null)).toBe('');
      expect(countryCodeToEmoji(undefined)).toBe('');
      expect(countryCodeToEmoji('')).toBe('');
    });
  });

  describe('getCountryCode', () => {
    it('should return country code for valid country name', () => {
      const code = getCountryCode('United States');
      expect(code).toBeTruthy();
      expect(typeof code).toBe('string');
      expect(code.length).toBe(2);
    });

    it('should return null for invalid country name', () => {
      expect(getCountryCode('InvalidCountry')).toBeNull();
      expect(getCountryCode('')).toBeNull();
    });
  });
});

describe('Station Utilities', () => {
  describe('getStationById', () => {
    const stations = [
      { id: 1, station_name: 'Station 1' },
      { id: 2, station_name: 'Station 2' },
      { id: 3, station_name: 'Station 3' },
    ];

    it('should return station with matching id', () => {
      const station = getStationById(stations, 2);
      expect(station).toEqual({ id: 2, station_name: 'Station 2' });
    });

    it('should return undefined for non-existent id', () => {
      const station = getStationById(stations, 999);
      expect(station).toBeUndefined();
    });

    it('should handle empty array', () => {
      const station = getStationById([], 1);
      expect(station).toBeUndefined();
    });
  });

  describe('getStationName', () => {
    it('should return German name when language starts with "de"', () => {
      const station = {
        station_name: 'Berlin',
        station_name_de: 'Berlin (DE)',
      };
      expect(getStationName(station, 'de')).toBe('Berlin (DE)');
      expect(getStationName(station, 'de-DE')).toBe('Berlin (DE)');
    });

    it('should return English name for non-German languages', () => {
      const station = {
        station_name: 'Berlin',
        station_name_de: 'Berlin (DE)',
      };
      expect(getStationName(station, 'en')).toBe('Berlin');
      expect(getStationName(station, 'fr')).toBe('Berlin');
    });

    it('should return station_name when station_name_de is missing', () => {
      const station = {
        station_name: 'Berlin',
      };
      expect(getStationName(station, 'de')).toBe('Berlin');
    });

    it('should return empty string for null/undefined station', () => {
      expect(getStationName(null, 'en')).toBe('');
      expect(getStationName(undefined, 'en')).toBe('');
    });

    it('should return empty string when station_name is missing', () => {
      const station = {};
      expect(getStationName(station, 'en')).toBe('');
    });
  });
});
