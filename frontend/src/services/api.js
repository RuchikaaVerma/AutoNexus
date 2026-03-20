import axios from "axios";

// .env file se URL lo
// Agar .env mein nahi hai toh localhost:8000 default use hoga
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Axios instance banao — yeh ek configured HTTP client hai
const api = axios.create({
  baseURL: BASE,
  timeout: 10000, // 10 second mein response nahi aaya toh error
  headers: {
    "Content-Type": "application/json",
  },
});

// ── VEHICLE APIs ──

// Saare vehicles fetch karo
export const getVehicles = () =>
  api.get("/vehicles").then(r => r.data);

// Ek vehicle fetch karo ID se
export const getVehicle = (id) =>
  api.get(`/vehicles/${id}`).then(r => r.data);

// Sensor history fetch karo
export const getSensorHistory = (id) =>
  api.get(`/vehicles/${id}/sensors/history`).then(r => r.data);

// ── PREDICTION APIs ──

// Saari predictions fetch karo
export const getPredictions = () =>
  api.get("/predictions").then(r => r.data);

// Ek vehicle ki predictions
export const getVehiclePredictions = (id) =>
  api.get(`/predictions/${id}`).then(r => r.data);

// ── DASHBOARD APIs ──

// Dashboard stats fetch karo
export const getDashboardStats = () =>
  api.get("/dashboard/stats").then(r => r.data);

// ── APPOINTMENT APIs ──

// Appointment book karo
export const bookAppointment = (data) =>
  api.post("/appointments", data).then(r => r.data);

// ── SECURITY APIs ──

// UEBA alerts fetch karo
export const getSecurityAlerts = () =>
  api.get("/ueba/alerts").then(r => r.data);

// ── ERROR HANDLING ──
// Agar API call fail ho toh yeh interceptor catch karega
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.message);
    return Promise.reject(error);
  }
);

export default api;
