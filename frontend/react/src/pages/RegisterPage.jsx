import React, { useContext, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useContext(AuthContext);

  useEffect(() => {
    register();
  }, [register]);

  return null;
}
