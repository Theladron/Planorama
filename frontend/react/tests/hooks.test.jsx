/**
 * Tests for custom React hooks
 */
import React from 'react';
import { vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useTrips } from '../src/hooks/useTrips';

// Mock Auth0
const mockGetAccessTokenSilently = vi.fn().mockResolvedValue('mock-token');
const mockLoginWithRedirect = vi.fn().mockResolvedValue();
const mockLogout = vi.fn();

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    isAuthenticated: false,
    isLoading: false,
    getAccessTokenSilently: mockGetAccessTokenSilently,
    loginWithRedirect: mockLoginWithRedirect,
    logout: mockLogout,
    user: null,
    error: null,
  }),
}));

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: { language: 'en', changeLanguage: vi.fn() },
  }),
}));

// Mock axios
const mockAxiosGet = vi.fn();
vi.mock('axios', () => ({
  default: {
    get: (...args) => mockAxiosGet(...args),
    defaults: {
      headers: {
        common: {},
      },
    },
  },
}));

// Mock config
vi.mock('../src/config', () => ({
  backendURL: 'http://localhost:8000',
}));

// Mock i18n
vi.mock('../src/i18n', () => ({
  default: {
    changeLanguage: vi.fn(),
  },
}));

// Mock API modules
const mockFetchUserTrips = vi.fn();

vi.mock('../src/api/tripApi', () => ({
  fetchUserTrips: (...args) => mockFetchUserTrips(...args),
}));

describe('Custom Hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetAccessTokenSilently.mockResolvedValue('mock-token');
    mockLoginWithRedirect.mockResolvedValue();
    mockAxiosGet.mockResolvedValue({ data: {} });
  });

  describe('useTrips', () => {
    it('should initialize with loading true and empty trips', async () => {
      mockFetchUserTrips.mockImplementation(() => new Promise(() => {})); // Never resolves
      const { result } = renderHook(() => useTrips());
      
      // useEffect runs asynchronously, so we need to wait a bit
      await waitFor(() => {
        expect(result.current.loading).toBe(true);
      });
      
      expect(result.current.trips).toEqual([]);
      expect(result.current.error).toBe(null);
    });

    it('should fetch trips on mount', async () => {
      const mockTrips = [
        { id: 1, trip_name: 'Trip 1' },
        { id: 2, trip_name: 'Trip 2' },
      ];
      mockFetchUserTrips.mockResolvedValue(mockTrips);
      
      const { result } = renderHook(() => useTrips());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.trips).toEqual(mockTrips);
      expect(result.current.error).toBe(null);
      expect(mockFetchUserTrips).toHaveBeenCalledTimes(1);
    });

    it('should set error on fetch failure', async () => {
      const mockError = new Error('Failed to fetch trips');
      mockFetchUserTrips.mockRejectedValue(mockError);
      
      const { result } = renderHook(() => useTrips());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.error).toBe('Failed to fetch trips');
      expect(result.current.trips).toEqual([]);
    });

    it('should handle error without message', async () => {
      const mockError = {};
      mockFetchUserTrips.mockRejectedValue(mockError);
      
      const { result } = renderHook(() => useTrips());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.error).toBe('Failed to load trips');
    });

    it('should provide setTrips function', async () => {
      mockFetchUserTrips.mockImplementation(() => new Promise(() => {}));
      const { result } = renderHook(() => useTrips());
      
      expect(typeof result.current.setTrips).toBe('function');
      
      // Wait for initial loading to start
      await waitFor(() => {
        expect(result.current.loading).toBeDefined();
      });
      
      // Test that setTrips updates trips
      const newTrips = [{ id: 99, trip_name: 'New Trip' }];
      await act(async () => {
        result.current.setTrips(newTrips);
      });
      
      await waitFor(() => {
        expect(result.current.trips).toEqual(newTrips);
      });
    });
  });
});

