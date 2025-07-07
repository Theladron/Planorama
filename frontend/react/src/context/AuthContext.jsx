import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // True until we verify auth
  const [authError, setAuthError] = useState(null);


  // Setup axios default Authorization header immediately on mount if token exists
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common["Authorization"];
    }
  }, []);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const res = await axios.get("/api/users/me");
      setUser(res.data);
      setIsAuthenticated(true);
      setAuthError(null);
    } catch (err) {
      if (
        err.response &&
        err.response.status === 401 &&
        err.response.data.detail &&
        err.response.data.detail.toLowerCase().includes("token")
      ) {
        logout("Your login session has expired. Please log in again.");
      } else {
        console.error("Failed to fetch user:", err);
        setAuthError("Failed to fetch user info.");
      }
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Login: save token, update axios headers, fetch user info
  const login = async (token) => {
    localStorage.setItem("token", token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    setAuthError(null);
    await fetchUser();
  };

  // Logout: clear token, reset auth state and axios headers, optionally set error message
  const logout = (errorMessage = null) => {
    localStorage.removeItem("token");
    delete axios.defaults.headers.common["Authorization"];
    setIsAuthenticated(false);
    setUser(null);
    setAuthError(errorMessage);
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        login,
        logout,
        loading,
        authError,
        setAuthError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
