import { backendURL } from "../config";
import React, { createContext, useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import i18n from "../i18n"; // Make sure path is correct

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const { t } = useTranslation();

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Set Axios auth header from localStorage token (if exists)
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
      const res = await axios.get(`${backendURL}/api/users/me`);
      const userData = res.data;
      setUser(userData);
      setIsAuthenticated(true);
      setAuthError(null);

      // Apply user's language preference if it's valid
      if (userData.language_preference && ["en", "de"].includes(userData.language_preference)) {
        i18n.changeLanguage(userData.language_preference);
      }

    } catch (err) {
      if (
        err.response &&
        err.response.status === 401 &&
        err.response.data.detail &&
        err.response.data.detail.toLowerCase().includes("token")
      ) {
        logout(t("authcontext.session_expired"));
      } else {
        console.error("Failed to fetch user:", err);
        setAuthError(t("authcontext.fetch_user_failed"));
      }
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (token) => {
    localStorage.setItem("token", token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    setAuthError(null);
    await fetchUser();
  };

  const logout = (errorMessage = null) => {
    localStorage.removeItem("token");
    delete axios.defaults.headers.common["Authorization"];
    setIsAuthenticated(false);
    setUser(null);
    setAuthError(errorMessage);
    // Do not reset language – browser/localStorage detection will take over
  };

  // Initial auth check on mount
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
