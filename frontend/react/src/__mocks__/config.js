// Mock config for Jest tests
// This replaces the real config.js which uses import.meta.env (not available in Jest)
export const backendURL = process.env.VITE_BACKEND_URL || "http://localhost:8000";
