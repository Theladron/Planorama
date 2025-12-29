import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export const useAuth = () => {
  const { login, logout, loading, authError } = useContext(AuthContext);
  
  return {
    login: () => {
      throw new Error("useAuth.login is deprecated. Use AuthContext.login() instead.");
    },
    register: () => {
      throw new Error("Registration is now handled by Auth0. Use Auth0's signup flow.");
    },
    loading,
    error: authError,
  };
};

