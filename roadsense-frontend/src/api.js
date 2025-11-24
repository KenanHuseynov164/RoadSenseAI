import axios from "axios";

const API = "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API,
});

// Automatically add JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// AUTH
export const registerUser = (email, password) =>
  api.post("/auth/register", { email, password });

export const loginUser = (email, password) =>
  api.post("/auth/login", { email, password });

// INCIDENTS
export const submitIncident = (description) =>
  api.post("/api/incidents", { description });

export const fetchIncidents = () => api.get("/api/incidents");

export const healthCheck = () => api.get("/api/health");
