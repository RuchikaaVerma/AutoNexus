// services/api.js — UPDATED
// Adds service booking, feedback, manufacturing endpoints
// Keeps all existing exports Person 3 already uses
// ─────────────────────────────────────────────────────────────

import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://192.168.249.221:8000";

const api = axios.create({
baseURL: BASE,
timeout: 60000,   // 60s — analysis takes time (voice call + 8 agents)
headers: {
"Content-Type": "application/json",
"ngrok-skip-browser-warning": "true", // prevents ngrok browser warning
},
});

// ── VEHICLE APIs (existing — unchanged) ─────────────────────
export const getVehicles = () =>
api.get("/vehicles").then((r) => r.data);

export const getVehicle = (id) =>
api.get(`/vehicles/${id}`).then((r) => r.data);

export const getSensorHistory = (id) =>
api.get(`/vehicles/${id}/sensors/history`).then((r) => r.data);

// ── PREDICTION APIs (existing — unchanged) ──────────────────
export const getPredictions = () =>
api.get("/predictions").then((r) => r.data);

export const mlPredict = (id) =>
api.post(`/ml-predict/${id}`).then((r) => r.data);

// ── AGENTS API — ⭐ MAIN (existing — unchanged) ─────────────
// This triggers: voice call (if daytime+critical) + SMS + 8 agents
export const analyzeVehicle = (id) =>
api.post(`/agents/analyze/${id}`).then((r) => r.data);

export const getAgentsStatus = () =>
api.get("/agents/status").then((r) => r.data);

// ── DASHBOARD APIs (existing — unchanged) ───────────────────
export const getDashboardStats = () =>
api.get("/dashboard/stats").then((r) => r.data);

// ── SERVICE BOOKING (NEW) ────────────────────────────────────
export const bookAppointment = (data) =>
api.post("/service/book", data).then((r) => r.data);

export const getServiceHistory = (vehicleId) =>
api.get(`/service/history/${vehicleId}`).then((r) => r.data);

export const completeService = (bookingId, data) =>
api.post(`/service/complete/${bookingId}`, data).then((r) => r.data);

// ── FEEDBACK (NEW) ───────────────────────────────────────────
export const submitFeedback = (bookingId, data) =>
api.post(`/feedback/submit/${bookingId}`, data).then((r) => r.data);

export const getVehicleFeedback = (vehicleId) =>
api.get(`/feedback/vehicle/${vehicleId}`).then((r) => r.data);

// ── MANUFACTURING INSIGHTS (NEW) ─────────────────────────────
export const getFleetInsights = () =>
api.get("/manufacturing/insights").then((r) => r.data);

export const getVehicleInsights = (vehicleId) =>
api.get(`/manufacturing/insights/${vehicleId}`).then((r) => r.data);

// ── SECURITY APIs (existing — unchanged) ────────────────────
export const getSecurityAlerts = () =>
api.get("/ueba/alerts").then((r) => r.data);

// ── Error handling (existing — unchanged) ───────────────────
api.interceptors.response.use(
(res) => res,
(err) => {
console.error("API Error:", err.message);
return Promise.reject(err);
}
);

export default api;