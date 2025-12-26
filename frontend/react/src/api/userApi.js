import axios from "axios";
import { backendURL } from "../config";

/**
 * Delete current user account
 */
export const deleteUser = async () => {
  await axios.delete(`${backendURL}/api/users/me`);
};

