import { useState } from "react";
import { login as loginApi, register as registerApi } from "../api/authApi";

/**
 * Hook for authentication operations
 */
export const useAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const token = await loginApi(email, password);
      return token;
    } catch (err) {
      setError(err.message || "Login failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const user = await registerApi(username, email, password);
      return user;
    } catch (err) {
      setError(err.message || "Registration failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { login, register, loading, error };
};

