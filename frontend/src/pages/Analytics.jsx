// pages/Analytics.jsx — COMPLETE with real backend data
// Replaces Grafana/demo data with live charts from your backend
// Uses recharts (already available in Vite React projects)

import { useState, useEffect } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://192.168.249.221:8000";
const cfg = { headers: { "ngrok-skip-browser-warning": "true" } };

// Simple bar chart component (no external library needed)
function BarChart({ data, color = "#00e396", label }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div>
      <div className="text-xs text-white/40 mb-2">{label}</div>
      <div className="flex items-end gap-1 h-24">
        {data.map((d, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <div className="text-xs text-white/30" style={{ fontSize: "9px" }}>
              {d.value}
            </div>
            <div
              className="w-full rounded-t transition-all"
              style={{
                height: `${(d.value / max) * 80}px`,
                minHeight: "4px",
                background: color,
                opacity: 0.8,
              }}
            />
            <div className="text-white/30" style={{ fontSize: "8px" }}>
              {d.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Donut chart component
function DonutChart({ segments, size = 120 }) {
  const total = segments.reduce((s, seg) => s + seg.value, 0) || 1;
  let offset  = 0;
  const r     = 45;
  const circ  = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} viewBox="0 0 100 100">
      <circle cx="50" cy="50" r={r} fill="none" stroke="#1f2937" strokeWidth="12" />
      {segments.map((seg, i) => {
        const pct   = seg.value / total;
        const dash  = pct * circ;
        const gap   = circ - dash;
        const rot   = offset * 360 - 90;
        offset     += pct;
        return (
          <circle
            key={i}
            cx="50" cy="50" r={r}
            fill="none"
            stroke={seg.color}
            strokeWidth="12"
            strokeDasharray={`${dash} ${gap}`}
            strokeDashoffset={0}
            transform={`rotate(${rot} 50 50)`}
            style={{ transition: "stroke-dasharray 0.5s" }}
          />
        );
      })}
      <text x="50" y="50" textAnchor="middle" dy="4" fill="white" fontSize="14" fontWeight="bold">
        {total}
      </text>
      <text x="50" y="62" textAnchor="middle" fill="#6b7280" fontSize="7">
        vehicles
      </text>
    </svg>
  );
}

export default function Analytics() {
  const [vehicles,  setVehicles]  = useState([]);
  const [stats,     setStats]     = useState(null);
  const [ueba,      setUeba]      = useState(null);
  const [feedback,  setFeedback]  = useState([]);
  const [loading,   setLoading]   = useState(true);

  useEffect(() => {
    loadAll();
    const iv = setInterval(loadAll, 30000);
    return () => clearInterval(iv);
  }, []);

  async function loadAll() {
    try {
      const [vRes, sRes, uRes] = await Promise.all([
        axios.get(`${API}/vehicles`,        cfg),
        axios.get(`${API}/dashboard/stats`, cfg),
        axios.get(`${API}/ueba/status`,     cfg).catch(() => ({ data: null })),
      ]);
      setVehicles(vRes.data  || []);
      setStats(sRes.data     || null);
      setUeba(uRes.data      || null);
    } catch (e) {
      console.error("Analytics load failed:", e.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return (
    <div className="pt-14 min-h-screen flex items-center justify-center text-white/40">
      Loading analytics...
    </div>
  );

  // ── Derived analytics ────────────────────────────────────────
  const critical = vehicles.filter(v => v.status === "critical");
  const warning  = vehicles.filter(v => v.status === "warning");
  const healthy  = vehicles.filter(v => v.status === "healthy");

  const sensorData = [
    { label: "Brake Temp",  value: stats?.averages?.brake_temp        || 0 },
    { label: "Oil Press",   value: stats?.averages?.oil_pressure       || 0 },
    { label: "Engine Temp", value: stats?.averages?.engine_temp        || 0 },
    { label: "Tire Press",  value: stats?.averages?.tire_pressure      || 0 },
    { label: "Brake Fluid", value: stats?.averages?.brake_fluid_level  || 0 },
  ];

  const brakeTemps = vehicles
    .map(v => ({ label: v.id.replace("VEH", "V"), value: v.brake_temp }))
    .sort((a, b) => b.value - a.value);

  const oilPressures = vehicles
    .map(v => ({ label: v.id.replace("VEH", "V"), value: Math.round(v.oil_pressure) }))
    .sort((a, b) => a.value - b.value);   // lowest first (more critical)

  const mileageData = vehicles
    .map(v => ({ label: v.id.replace("VEH", "V"), value: Math.round(v.mileage / 1000) }))
    .sort((a, b) => b.value - a.value);

  return (
    <div className="pt-14 min-h-screen p-5" style={{ background: "transparent" }}>
      <div className="mb-6">
        <p className="text-xs text-white/30 tracking-widest uppercase mb-1">Live Analytics</p>
        <h1 className="text-2xl font-bold text-white">Fleet Analytics</h1>
        <p className="text-white/30 text-sm mt-1">Real-time data from {vehicles.length} vehicles · Updates every 30s</p>
      </div>

      {/* ── Top Stats ── */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Fleet Size",       value: vehicles.length,                          color: "text-cyan-400",   bg: "bg-cyan-500/10"   },
          { label: "Critical",         value: critical.length,                          color: "text-red-400",    bg: "bg-red-500/10"    },
          { label: "Needs Attention",  value: warning.length,                           color: "text-yellow-400", bg: "bg-yellow-500/10" },
          { label: "Healthy",          value: healthy.length,                           color: "text-green-400",  bg: "bg-green-500/10"  },
        ].map(s => (
          <div key={s.label} className={`${s.bg} border border-white/5 rounded-xl p-4`}>
            <div className={`text-3xl font-black ${s.color}`}>{s.value}</div>
            <div className="text-xs text-white/40 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* ── Row 1: Donut + Brake Temps ── */}
      <div className="grid grid-cols-3 gap-4 mb-4">

        {/* Fleet Status Donut */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <h3 className="font-bold text-sm text-white mb-4">Fleet Health Distribution</h3>
          <div className="flex items-center gap-6">
            <DonutChart segments={[
              { value: critical.length, color: "#ff4560" },
              { value: warning.length,  color: "#ffaa00" },
              { value: healthy.length,  color: "#00e396" },
            ]} size={110} />
            <div className="space-y-2 text-sm">
              {[
                { label: "Critical", count: critical.length, color: "#ff4560" },
                { label: "Warning",  count: warning.length,  color: "#ffaa00" },
                { label: "Healthy",  count: healthy.length,  color: "#00e396" },
              ].map(s => (
                <div key={s.label} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ background: s.color }} />
                  <span className="text-white/60">{s.label}</span>
                  <span className="text-white font-bold ml-auto">{s.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Brake Temp Chart */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <h3 className="font-bold text-sm text-white mb-4">Brake Temperature by Vehicle (°C)</h3>
          <BarChart data={brakeTemps} color="#ff4560" label="°C — threshold: 100°C" />
        </div>

        {/* Oil Pressure Chart */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <h3 className="font-bold text-sm text-white mb-4">Oil Pressure by Vehicle (PSI)</h3>
          <BarChart data={oilPressures} color="#00b4d8" label="PSI — threshold: 25 PSI" />
        </div>
      </div>

      {/* ── Row 2: Sensor Averages + Mileage + UEBA ── */}
      <div className="grid grid-cols-3 gap-4 mb-4">

        {/* Fleet Sensor Averages */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <h3 className="font-bold text-sm text-white mb-4">Fleet Sensor Averages</h3>
          <div className="space-y-3">
            {sensorData.map(s => {
              const max = { "Brake Temp": 130, "Oil Press": 55, "Engine Temp": 115, "Tire Press": 38, "Brake Fluid": 100 }[s.label] || 100;
              const pct = Math.min(100, (s.value / max) * 100);
              const isHigh = (s.label === "Brake Temp" && s.value > 100) ||
                             (s.label === "Oil Press"   && s.value < 25)  ||
                             (s.label === "Engine Temp" && s.value > 105);
              return (
                <div key={s.label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-white/50">{s.label}</span>
                    <span style={{ color: isHigh ? "#ff4560" : "#00e396" }}>{s.value}</span>
                  </div>
                  <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full rounded-full"
                      style={{ width: `${pct}%`, background: isHigh ? "#ff4560" : "#00e396" }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Mileage Distribution */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <h3 className="font-bold text-sm text-white mb-4">Mileage Distribution (× 1000 km)</h3>
          <BarChart data={mileageData} color="#a855f7" label="Thousand km" />
        </div>

        {/* UEBA Security Summary */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <h3 className="font-bold text-sm text-white mb-4">🛡️ UEBA Security Summary</h3>
          {ueba ? (
            <div className="space-y-3">
              <div className={`p-3 rounded-xl text-sm font-bold ${ueba.flagged > 0 ? "bg-red-500/15 text-red-400" : "bg-green-500/15 text-green-400"}`}>
                {ueba.flagged > 0 ? "⚠️ Anomalies Detected" : "✅ System Secure"}
              </div>
              {[
                { label: "Events Monitored", value: ueba.monitored, color: "text-cyan-400" },
                { label: "Anomalies Flagged", value: ueba.flagged,  color: "text-red-400"  },
                { label: "Normal Operations",  value: ueba.normal,   color: "text-green-400"},
                { label: "Agents Active",      value: ueba.agents_active || 8, color: "text-purple-400" },
              ].map(s => (
                <div key={s.label} className="flex justify-between text-sm">
                  <span className="text-white/50">{s.label}</span>
                  <span className={`font-bold ${s.color}`}>{s.value}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-white/30 text-sm text-center py-4">
              Run AI analysis to generate security data
            </div>
          )}
        </div>
      </div>

      {/* ── Row 3: Vehicle Details Table ── */}
      <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
        <h3 className="font-bold text-sm text-white mb-4">All Vehicles — Sensor Details</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-white/10">
                {["Vehicle ID", "Model", "Owner", "Status", "Brake Temp", "Oil Press", "Engine Temp", "Brake Fluid", "Mileage"].map(h => (
                  <th key={h} className="text-left text-white/40 py-2 pr-4 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {vehicles.map(v => (
                <tr key={v.id} className="border-b border-white/5 hover:bg-white/3 transition-colors">
                  <td className="py-2 pr-4 font-mono text-cyan-400">{v.id}</td>
                  <td className="py-2 pr-4 text-white/70">{v.model}</td>
                  <td className="py-2 pr-4 text-white/50">{v.owner_name}</td>
                  <td className="py-2 pr-4">
                    <span className={`px-2 py-0.5 rounded-full font-bold ${
                      v.status === "critical" ? "bg-red-500/20 text-red-400" :
                      v.status === "warning"  ? "bg-yellow-500/20 text-yellow-400" :
                      "bg-green-500/20 text-green-400"
                    }`}>
                      {v.status}
                    </span>
                  </td>
                  <td className="py-2 pr-4" style={{ color: v.brake_temp > 100 ? "#ff4560" : "#00e396" }}>
                    {v.brake_temp}°C
                  </td>
                  <td className="py-2 pr-4" style={{ color: v.oil_pressure < 25 ? "#ff4560" : "#00e396" }}>
                    {v.oil_pressure} psi
                  </td>
                  <td className="py-2 pr-4" style={{ color: v.engine_temp > 105 ? "#ff4560" : "#00e396" }}>
                    {v.engine_temp}°C
                  </td>
                  <td className="py-2 pr-4" style={{ color: v.brake_fluid_level < 65 ? "#ff4560" : "#00e396" }}>
                    {v.brake_fluid_level}%
                  </td>
                  <td className="py-2 pr-4 text-white/50">{v.mileage?.toLocaleString()} km</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}