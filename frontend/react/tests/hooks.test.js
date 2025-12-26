/**
 * Tests for custom React hooks
 */
import { renderHook, waitFor, act } from '@testing-library/react';
import { useAuth } from '../src/hooks/useAuth';
import { useTrips } from '../src/hooks/useTrips';

// Mock API modules
const mockLoginApi = jest.fn();
const mockRegisterApi = jest.fn();
const mockFetchUserTrips = jest.fn();

jest.mock('../src/api/authApi', () => ({
  login: (...args) => mockLoginApi(...args),
  register: (...args) => mockRegisterApi(...args),
}));

jest.mock('../src/api/tripApi', () => ({
  fetchUserTrips: (...args) => mockFetchUserTrips(...args),
}));

describe('Custom Hooks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useAuth', () => {
    it('should initialize with loading false and no error', () => {
      const { result } = renderHook(() => useAuth());
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(typeof result.current.login).toBe('function');
      expect(typeof result.current.register).toBe('function');
    });

    describe('login', () => {
      it('should set loading to true during login', async () => {
        mockLoginApi.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve('token123'), 100)));
        const { result } = renderHook(() => useAuth());
        
        let loginPromise;
        act(() => {
          loginPromise = result.current.login('test@example.com', 'password');
        });
        
        // Loading state should be set immediately after act
        expect(result.current.loading).toBe(true);
        
        await act(async () => {
          await loginPromise;
        });
        
        await waitFor(() => {
          expect(result.current.loading).toBe(false);
        });
      });

      it('should return token on successful login', async () => {
        const mockToken = 'test-token-123';
        mockLoginApi.mockResolvedValue(mockToken);
        const { result } = renderHook(() => useAuth());
        
        let token;
        await act(async () => {
          token = await result.current.login('test@example.com', 'password');
        });
        
        await waitFor(() => {
          expect(result.current.loading).toBe(false);
        });
        
        expect(token).toBe(mockToken);
        expect(result.current.error).toBe(null);
      });

      it('should set error on login failure', async () => {
        const mockError = new Error('Invalid credentials');
        mockLoginApi.mockRejectedValue(mockError);
        const { result } = renderHook(() => useAuth());
        
        await act(async () => {
          try {
            await result.current.login('test@example.com', 'wrong');
          } catch (e) {
            // Expected to throw
          }
        });
        
        await waitFor(() => {
          expect(result.current.error).toBe('Invalid credentials');
          expect(result.current.loading).toBe(false);
        });
      });

      it('should clear previous errors on new login attempt', async () => {
        // First fail
        mockLoginApi.mockRejectedValueOnce(new Error('First error'));
        const { result } = renderHook(() => useAuth());
        
        await act(async () => {
          try {
            await result.current.login('test@example.com', 'wrong');
          } catch (e) {
            // Expected to fail
          }
        });
        
        await waitFor(() => {
          expect(result.current.error).toBe('First error');
          expect(result.current.loading).toBe(false);
        });

        // Then succeed
        mockLoginApi.mockResolvedValueOnce('token');
        await act(async () => {
          await result.current.login('test@example.com', 'correct');
        });
        
        await waitFor(() => {
          expect(result.current.error).toBe(null);
          expect(result.current.loading).toBe(false);
        });
      });
    });

    describe('register', () => {
      it('should set loading to true during registration', async () => {
        mockRegisterApi.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ id: 1 }), 100)));
        const { result } = renderHook(() => useAuth());
        
        let registerPromise;
        act(() => {
          registerPromise = result.current.register('username', 'test@example.com', 'password');
        });
        
        // Loading state should be set immediately after act
        expect(result.current.loading).toBe(true);
        
        await act(async () => {
          await registerPromise;
        });
        
        await waitFor(() => {
          expect(result.current.loading).toBe(false);
        });
      });

      it('should return user on successful registration', async () => {
        const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };
        mockRegisterApi.mockResolvedValue(mockUser);
        const { result } = renderHook(() => useAuth());
        
        let user;
        await act(async () => {
          user = await result.current.register('testuser', 'test@example.com', 'password');
        });
        
        await waitFor(() => {
          expect(result.current.loading).toBe(false);
        });
        
        expect(user).toEqual(mockUser);
        expect(result.current.error).toBe(null);
      });

      it('should set error on registration failure', async () => {
        const mockError = new Error('Email already exists');
        mockRegisterApi.mockRejectedValue(mockError);
        const { result } = renderHook(() => useAuth());
        
        await act(async () => {
          try {
            await result.current.register('user', 'test@example.com', 'password');
          } catch (e) {
            // Expected to throw
          }
        });
        
        await waitFor(() => {
          expect(result.current.error).toBe('Email already exists');
          expect(result.current.loading).toBe(false);
        });
      });
    });
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
