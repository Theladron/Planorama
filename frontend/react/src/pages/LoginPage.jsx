import React, { useContext, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useContext(AuthContext);

  useEffect(() => {
    login();
  }, [login]);

  return null;
}
