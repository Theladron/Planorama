import { backendURL } from "../config";

/**
 * Login user and get access token
 */
export const login = async (email, password) => {
  const response = await fetch(`${backendURL}/api/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      username: email,
      password,
    }),
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Login failed");
  }

  const data = await response.json();
  return data.access_token;
};

/**
 * Register a new user
 */
export const register = async (username, email, password) => {
  const response = await fetch(`${backendURL}/api/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Registration failed");
  }

  return await response.json();
};

