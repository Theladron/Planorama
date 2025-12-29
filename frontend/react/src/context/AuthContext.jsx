/* eslint-disable react-refresh/only-export-components */
import { backendURL } from "../config";
import React, { createContext, useState, useEffect, useCallback } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";

export const AuthContext = createContext();

const auth0Audience = import.meta.env.VITE_AUTH0_AUDIENCE;

export function AuthProvider({ children }) {
  const { t } = useTranslation();
  const {
    isAuthenticated: auth0IsAuthenticated,
    isLoading: auth0IsLoading,
    getAccessTokenSilently,
    loginWithRedirect,
    logout: auth0Logout,
    error: auth0Error,
  } = useAuth0();

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  const logout = useCallback((errorMessage = null) => {
    setAuthError(errorMessage);
    auth0Logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
    setIsAuthenticated(false);
    setUser(null);
  }, [auth0Logout]);

  useEffect(() => {
    const setAuthHeader = async () => {
      if (auth0IsAuthenticated) {
        try {
          const token = await getAccessTokenSilently({
          audience: auth0Audience,
        });
          axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        } catch (err) {
          delete axios.defaults.headers.common["Authorization"];
        }
      } else {
        delete axios.defaults.headers.common["Authorization"];
      }
    };

    if (!auth0IsLoading) {
      setAuthHeader();
    }
  }, [auth0IsAuthenticated, auth0IsLoading, getAccessTokenSilently]);

  const fetchUser = useCallback(async () => {
    if (!auth0IsAuthenticated) {
      setLoading(false);
      setIsAuthenticated(false);
      setUser(null);
      return;
    }

    setLoading(true);
    try {
      const token = await getAccessTokenSilently({
        audience: auth0Audience,
      });
      
      if (!token) {
        throw new Error("No access token available");
      }
      
      const res = await axios.get(`${backendURL}/api/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const userData = res.data;
      setUser(userData);
      setIsAuthenticated(true);
      setAuthError(null);

      if (userData.language_preference && ["en", "de"].includes(userData.language_preference)) {
        i18n.changeLanguage(userData.language_preference);
      }
    } catch (err) {
      if (
        err.response &&
        err.response.status === 401
      ) {
        const errorDetail = err.response.data?.detail || "Authentication failed";
        setAuthError(errorDetail);
        logout(errorDetail);
      } else {
        setAuthError(err.response?.data?.detail || t("authcontext.fetch_user_failed"));
      }
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [auth0IsAuthenticated, getAccessTokenSilently, logout, t]);

  useEffect(() => {
    if (!auth0IsLoading) {
      fetchUser();
    }
  }, [auth0IsLoading, fetchUser]);

  useEffect(() => {
    if (auth0Error) {
      setAuthError(auth0Error.message || t("authcontext.auth0_error"));
    }
  }, [auth0Error, t]);

  const login = () => {
    setAuthError(null);
    loginWithRedirect({
      appState: {
        returnTo: window.location.pathname,
      },
    });
  };

  const register = () => {
    setAuthError(null);
    loginWithRedirect({
      screen_hint: "signup",
      appState: {
        returnTo: window.location.pathname,
      },
    });
  };

  const combinedLoading = auth0IsLoading || loading;

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        setUser,
        login,
        register,
        logout,
        loading: combinedLoading,
        authError,
        setAuthError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
