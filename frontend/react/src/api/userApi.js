import axios from "axios";
import { backendURL } from "../config";

/**
 * Update current user's username
 */
export const updateUsername = async (username) => {
  const response = await axios.patch(`${backendURL}/api/users/me`, {
    username: username,
  });
  return response.data;
};

/**
 * Update current user's password
 */
export const updatePassword = async (password) => {
  const response = await axios.patch(`${backendURL}/api/users/me/password`, {
    password: password,
  });
  return response.data;
};

/**
 * Delete current user account
 */
export const deleteUser = async () => {
  await axios.delete(`${backendURL}/api/users/me`);
};

