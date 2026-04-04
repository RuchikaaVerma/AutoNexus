// pages/Dashboard.jsx — UPDATED
// Keeps ALL of Person 3's existing components (StatsRow, VehicleGrid, etc.)
// Just replaces mockData with REAL backend data
// ─────────────────────────────────────────────────────────────

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getVehicles, getDashboardStats } from "../services/api";

import AutomotiveBackground from "../components/AutomotiveBackground";
import StatsRow       from "../components/StatsRow";
import VehicleGrid    from "../components/VehicleGrid";
import SensorGauges   from "../components/SensorGauges";
import AgentPanel     from "../components/AgentPanel";
import PredictionList from "../components/PredictionList";
import ChatViewer     from "../components/ChatViewer";
import DemoMode       from "../components/DemoMode";

export default function Dashboard() {
  const navigate = useNavigate();

  const [vehicles,         setVehicles]         = useState([]);
  const [dashStats,        setDashStats]         = useState(null);
  const [selectedVehicle,  setSelectedVehicle]   = useState(null);
  const [activeAgent,      setActiveAgent]       = useState(null);
  const [loading,          setLoading]           = useState(true);
  const [error,            setError]             = useState(null);

  useEffect(() => {
    loadData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [vehicleData, statsData] = await Promise.all([
        getVehicles(),
        getDashboardStats(),
      ]);

      // ── Map backend vehicle shape → Person 3's component shape ──────────
      const mapped = vehicleData.map(v => ({
        // Keep all original backend fields
        ...v,
        // Add fields Person 3's components expect
        name:   v.model,
        owner:  v.owner_name,
        health: computeHealth(v),
        sensors: {
          brakeTemp:   v.brake_temp,
          oilPressure: v.oil_pressure,
          engineTemp:  v.engine_temp,
          tirePressure:v.tire_pressure,
          brakeFluid:  v.brake_fluid_level,
        },
        lastService: "Regular maintenance",
        nextService:  v.status === "critical" ? "URGENT" : "In 3 months",
      }));

      // ── Map stats → Person 3's StatsRow shape ───────────────────────────
      const mappedStats = statsData ? [
        { label: "Total Vehicles",  value: statsData.total_vehicles,                    icon: "🚗" },
        { label: "Healthy",         value: statsData.status_distribution.healthy,        icon: "✅", color: "#00e396" },
        { label: "Warning",         value: statsData.status_distribution.warning,        icon: "⚠️", color: "#ffaa00" },
        { label: "Critical",        value: statsData.status_distribution.critical,       icon: "🚨", color: "#ff4560" },
        { label: "Avg Brake Temp",  value: statsData.averages.brake_temp + "°C",         icon: "🌡️" },
        { label: "Avg Oil Pressure",value: statsData.averages.oil_pressure + " psi",     icon: "🛢️" },
      ] : [];

      setVehicles(mapped);
      setDashStats(mappedStats);

      // Auto-select first critical vehicle, else first vehicle
      const critical = mapped.find(v => v.status === "critical");
      setSelectedVehicle(prev => {
        if (prev) return mapped.find(v => v.id === prev.id) || mapped[0];
        return critical || mapped[0];
      });

      setError(null);
    } catch (e) {
      console.error("Dashboard load failed:", e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  // Convert sensor readings to health % for display
  function computeHealth(v) {
    let score = 100;
    if (v.brake_temp        > 100) score -= 30;
    else if (v.brake_temp   > 85)  score -= 15;
    if (v.oil_pressure      < 25)  score -= 30;
    else if (v.oil_pressure < 35)  score -= 10;
    if (v.engine_temp       > 105) score -= 20;
    else if (v.engine_temp  > 100) score -= 10;
    if (v.brake_fluid_level < 65)  score -= 20;
    else if (v.brake_fluid_level < 75) score -= 10;
    return Math.max(0, score);
  }

  // ── Loading state ────────────────────────────────────────────
  if (loading) return (
    <>
      <AutomotiveBackground />
      <div className="pt-14 min-h-screen flex items-center justify-center"
        style={{ background: "transparent", position: "relative", zIndex: 1 }}>
        <div className="text-center text-white/50">
          <div className="text-4xl mb-4">🔄</div>
          <p>Loading fleet data from backend...</p>
          <p className="text-xs mt-2 text-white/30">Connecting to {import.meta.env.VITE_API_URL}</p>
        </div>
      </div>
    </>
  );

  // ── Error state ──────────────────────────────────────────────
  if (error) return (
    <>
      <AutomotiveBackground />
      <div className="pt-14 min-h-screen flex items-center justify-center"
        style={{ background: "transparent", position: "relative", zIndex: 1 }}>
        <div className="text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <p className="text-red-400 font-bold">Cannot connect to backend</p>
          <p className="text-white/40 text-sm mt-2">{error}</p>
          <p className="text-white/30 text-xs mt-1">
            Make sure backend is running at {import.meta.env.VITE_API_URL}
          </p>
          <button onClick={loadData}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm">
            🔄 Retry
          </button>
        </div>
      </div>
    </>
  );

  return (
    <>
      <AutomotiveBackground />
      <div className="pt-14 min-h-screen p-5"
        style={{ background: "transparent", position: "relative", zIndex: 1 }}>

        <div className="mb-5 flex justify-between items-end">
          <div>
            <p className="text-xs text-white/30 tracking-widest uppercase mb-1">Live Fleet</p>
            <h1 className="text-2xl font-bold text-white">Fleet Dashboard</h1>
          </div>
          <button onClick={loadData}
            className="text-xs text-white/40 hover:text-white/70 flex items-center gap-1">
            🔄 Refresh
          </button>
        </div>

        {/* Stats row with real data */}
        {dashStats && <StatsRow stats={dashStats} />}

        <div className="grid grid-cols-12 gap-4">
          <div className="col-span-3 flex flex-col gap-4">
            {selectedVehicle && <SensorGauges vehicle={selectedVehicle} />}
            {/* PredictionList — pass critical vehicles as "predictions" */}
            <PredictionList predictions={
              vehicles
                .filter(v => v.status !== "healthy")
                .map(v => ({
                  id:          v.id,
                  vehicle:     v.name,
                  component:   v.status === "critical" ? "Immediate service needed" : "Maintenance due",
                  probability: v.status === "critical" ? 85 : 45,
                  days:        v.status === "critical" ? 7 : 30,
                  status:      v.status,
                }))
            } />
          </div>

          <div className="col-span-6">
            <VehicleGrid
              vehicles={vehicles}
              selectedId={selectedVehicle?.id}
              onSelect={(v) => {
                setSelectedVehicle(v);
                // Navigate to detail page on click
                navigate(`/vehicle/${v.id}`);
              }}
            />
          </div>

          <div className="col-span-3 flex flex-col gap-4">
            <AgentPanel agents={[
              { name: "DataAnalysisAgent",        status: "active", icon: "📊" },
              { name: "DiagnosisAgent",            status: "active", icon: "🔬" },
              { name: "EngagementAgent",           status: "active", icon: "📞" },
              { name: "SchedulingAgent",           status: "active", icon: "📅" },
              { name: "FeedbackAgent",             status: "active", icon: "⭐" },
              { name: "ManufacturingInsightsAgent",status: "active", icon: "🏭" },
            ]} activeAgent={activeAgent} />
            <ChatViewer />
          </div>
        </div>

        <DemoMode onAgentChange={setActiveAgent} />
      </div>
    </>
  );
}
