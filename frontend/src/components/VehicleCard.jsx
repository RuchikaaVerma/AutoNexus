import { useNavigate }   from "react-router-dom";
import { statusColor }   from "../utils/helpers";

export default function VehicleCard({ vehicle, selected, onClick }) {
  const navigate = useNavigate();
  const emoji    = { critical: "🔴", warning: "⚠️", healthy: "✅" }[vehicle.status];
  const color    = statusColor(vehicle.status);

  function handleClick() {
    if (onClick) onClick(vehicle);
    navigate(`/vehicle/${vehicle.id}`);
  }

  return (
    <div
      onClick={handleClick}
      className="rounded-xl p-4 border cursor-pointer transition-all duration-200 hover:-translate-y-0.5"
      style={{
        background:   selected ? "rgba(255,255,255,0.07)" : "rgba(255,255,255,0.03)",
        border:       `1px solid ${selected ? "rgba(0,229,255,0.5)" : "rgba(255,255,255,0.06)"}`,
        boxShadow:    selected ? "0 0 20px rgba(0,200,255,0.1)" : "none",
      }}
    >
      {selected && (
        <div className="text-xs text-cyan-400 font-bold tracking-widest mb-2">● SELECTED</div>
      )}

      <div className="h-0.5 rounded-full mb-3" style={{ background: color }} />

      <div className="flex justify-between items-center mb-2">
        <span className="text-xs text-white/30 font-mono">{vehicle.id}</span>
        <span className="text-base">{emoji}</span>
      </div>

      <div className="font-semibold text-sm text-white mb-1">{vehicle.name}</div>
      <div className="text-xs text-white/40 mb-3">👤 {vehicle.owner}</div>

      <div className="rounded-lg p-2.5 mb-3" style={{ background: "rgba(0,0,0,0.3)" }}>
        <div className="text-xs text-white/30 mb-0.5">Brake Temp</div>
        <div className="text-xl font-black" style={{ color }}>{vehicle.sensors.brakeTemp}°C</div>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="rounded-lg p-2" style={{ background: "rgba(0,0,0,0.3)" }}>
          <div className="text-xs text-white/30">Oil</div>
          <div className="text-sm font-bold text-white">{vehicle.sensors.oilPressure} PSI</div>
        </div>
        <div className="rounded-lg p-2" style={{ background: "rgba(0,0,0,0.3)" }}>
          <div className="text-xs text-white/30">Engine</div>
          <div className="text-sm font-bold text-white">{vehicle.sensors.engineTemp}°C</div>
        </div>
      </div>

      <span className="text-xs font-bold px-2.5 py-1 rounded-full uppercase"
        style={{ background: color + "20", color }}>
        {vehicle.status}
      </span>
    </div>
  );
}